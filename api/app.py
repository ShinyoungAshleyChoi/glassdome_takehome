import os
import uuid

from datetime import datetime
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text

# API key -> company_id mapping, ormat: "key1:company_1,key2:company_2" or provided via env API_KEY_MAP
_api_map_raw = os.getenv("API_KEY_MAP", "pat_cp1_xoxo:company_1")
API_KEY_MAP: dict[str, str] = {}
for pair in _api_map_raw.split(','):
    if ':' in pair:
        k, v = pair.split(':', 1)
        API_KEY_MAP[k.strip()] = v.strip()
DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT", "8000"))

app = Flask(__name__)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@app.before_request
def verify_api_key():
    if request.endpoint == 'health':
        return  # health endpoint is public
    provided_key = request.headers.get("X-API-Key")
    company_id = API_KEY_MAP.get(provided_key)
    if not company_id:
        return jsonify({"error": "Unauthorized: invalid or missing X-API-Key"}), 401
    # Stash company_id on request context
    request.company_id = company_id

@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

@app.post("/ingest/products")
def ingest_products():
    """
    Accepts a JSON array of orders like:
    [
      {
        "id": "MAT-1009",            # string (internal id)
        "sku": "SKU-XYZ",            # string
        "status": "ACTIVE"           # ACTIVE | INACTIVE | DISCONTINUED
      }
    ]
    """

    payload = request.get_json(silent=True)
    if not isinstance(payload, list):
        return jsonify({"error": "Expected a JSON array of products"}), 400

    # Basic validation
    rows: List[dict] = []
    required = {"id", "sku", "status"}
    for i, rec in enumerate(payload):
        if not isinstance(rec, dict) or not required.issubset(rec.keys()):
            return jsonify({
                "error": f"Invalid record at index {i} - required fields: {sorted(required)}"
            }), 400
        rows.append({
            "id": str(uuid.uuid1()),
            "external_id": str(rec["id"]),
            "company_id": request.company_id,
            "sku": str(rec["sku"]),
            "status": str(rec["status"]).upper(),
            "create_time": datetime.utcnow().isoformat(),
            "update_time": datetime.utcnow().isoformat(),
            "delete_time": None
        })

    stmt = text(
        """
        INSERT INTO products(id, external_id, company_id, sku, status, create_time, update_time, delete_time)
        VALUES (:id, :external_id, :company_id, :sku, :status, :create_time, :update_time, :delete_time)
        """
    )

    try:
        with engine.begin() as conn:
            conn.execute(stmt, rows)
        return jsonify({"inserted": len(rows)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/products")
def list_products():
    """
    List products for the authenticated company.
    Query params:
      - limit: int (default 50, max 200)
      - offset: int (default 0)
      - include_deleted: bool (default false)
    """
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        include_deleted = request.args.get("include_deleted", "false").lower() in ("1", "true", "yes")
        limit = max(1, min(limit, 200))
        offset = max(0, offset)
    except ValueError:
        return jsonify({"error": "Invalid query parameters"}), 400

    base_sql = (
        "SELECT id, external_id, company_id, sku, status, create_time, update_time, delete_time "
        "FROM products WHERE company_id = :company_id "
    )
    if not include_deleted:
        base_sql += "AND delete_time IS NULL "
    base_sql += "ORDER BY update_time DESC LIMIT :limit OFFSET :offset"

    stmt = text(base_sql)

    try:
        with engine.connect() as conn:
            rows = conn.execute(
                stmt,
                {"company_id": request.company_id, "limit": limit, "offset": offset},
            ).mappings().all()
        return jsonify({"items": [dict(r) for r in rows], "limit": limit, "offset": offset}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.patch("/products")
def batch_update_products():
    """
    Batch update existing products for the authenticated company.
    Accepts a JSON array of product objects with fields to update:
    [
      {"id": "MAT-1001", "sku": "SKU-ALPHA-NEW", "status": "INACTIVE"},
      {"id": "MAT-1003", "status": "DISCONTINUED"}
    ]

    - Updates sku, status, and update_time.
    - Ignores unknown or invalid ids.
    - Returns a summary of updated and skipped records.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, list):
        return jsonify({"error": "Expected a JSON array of products"}), 400

    updates = []
    now = datetime.utcnow().isoformat()
    for i, rec in enumerate(payload):
        ext_id = rec.get("id")
        if not ext_id:
            return jsonify({"error": f"Missing external_id at index {i}"}), 400
        updates.append({
            "external_id": str(ext_id),
            "company_id": request.company_id,
            "sku": rec.get("sku"),
            "status": rec.get("status"),
            "update_time": now
        })

    try:
        with engine.begin() as conn:
            updated_count = 0
            for u in updates:
                stmt = text("""
                    UPDATE products
                    SET
                      sku = COALESCE(:sku, sku),
                      status = COALESCE(:status, status),
                      update_time = :update_time
                    WHERE company_id = :company_id AND external_id = :external_id
                """)
                result = conn.execute(stmt, u)
                updated_count += result.rowcount
        return jsonify({
            "updated": updated_count,
            "skipped": len(updates) - updated_count
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
