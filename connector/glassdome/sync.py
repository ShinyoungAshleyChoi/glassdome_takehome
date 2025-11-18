# glassdome/sync.py
import logging
from typing import Dict, Any

from .db import MesDbClient
from .api_client import GlassdomeApiClient

logger = logging.getLogger(__name__)


def map_row_to_product(row: dict) -> dict:
    return {
        "id": row["matnr"],
        "sku": row["sku"],
        "status": row["status"],
    }


def run_sync(config: Dict[str, Any]) -> int:
    db_cfg = config["db"]
    api_cfg = config["api"]
    sync_cfg = config.get("sync", {})

    batch_size = sync_cfg.get("batch_size", 500)

    db_client = MesDbClient(db_cfg)
    api_client = GlassdomeApiClient(api_cfg)

    total_sent = 0
    offset = 0

    try:
        while True:
            rows = db_client.fetch_products(limit=batch_size, offset=offset)
            if not rows:
                break

            products = [map_row_to_product(r) for r in rows]
            ok = api_client.ingest_products(products)
            if not ok:
                logger.error("Stopping sync due to API failure.")
                break

            total_sent += len(products)
            offset += batch_size

        logger.info("Sync finished. Total products sent: %d", total_sent)
        return total_sent
    finally:
        db_client.close()