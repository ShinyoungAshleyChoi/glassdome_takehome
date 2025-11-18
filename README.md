# Glassdome Take‑Home

At Glassdome, integration engineers develop data connectors that extract data from customer MES/ERP systems and push it to the Glassdome API.

Your task is to build a Python connector that integrates the provided mock MES/ERP database (mes-db) with the Glassdome API (/ingest/products).

## Objective
Develop a Python script that:
 1. Reads records from the mes-db.production_orders table.
 2. Sends the data to the Flask API at http://localhost:8000/ingest/products.
 3. Uses the provided X-API-Key header for authentication.
 4. Handles retries, errors, and configuration via a JSON/YAML file.

Bonus:
- Add basic logging.
- Support incremental syncs (fetch only new/updated records).
- Containerize your connector.

## Start the stack

``
docker compose up --build
``

This starts:
- mes-db on port 5433
- glassdome-db on port 5434
- glassdome-api on port 8000

##  Test the API

Health check: `curl http://localhost:8000/health`

List products:
```
curl -s "http://localhost:8000/products?limit=5&offset=0" \
  -H "X-API-Key: pat_cp1_xoxo" | jq
```

## Your connector script (what to build)
Write a Python program (connector.py) that:
 1. Connects to the mes-db using the credentials in .env.
 2. Queries data from the mes-db.
 3. Sends the records to http://localhost:8000/ingest/products.
 4. Authenticates using the header: `X-API-Key: pat_cp1_xoxo`
 5. Handles failures with retries and logging.
 6. Prints a summary of how many records were sent successfully.

 ## Bonus ideas
- Dockerize your connector.
- Add YAML/JSON configuration.
- Include logging (to file and stdout).
- Implement incremental sync (based on updated_at).
- Add simple tests using pytest.


## API Documentation

All endpoints require authentication:

```
X-API-Key: pat_cp1_xoxo
```

Base URL: http://localhost:8000


### Insert Products

Endpoint:
```
POST /ingest/products
```

Description:
Insert new products for the authenticated company. Each product must have unique (company_id, external_id) and (company_id, sku) combinations.

Request Headers:
```
Content-Type: application/json
X-API-Key: pat_cp1_xoxo
```

Request Body:
```
[
  {
    "id": "MAT-1003",
    "sku": "SKU-GAMMA",
    "status": "ACTIVE"
  }
]
```

### List Products

Endpoint:
```
GET /products
```

Description:
Retrieve a paginated list of products for the authenticated company.

Request Headers:
```
X-API-Key: pat_cp1_xoxo
```

Query Parameters:
- limit:	int	50	Number of records to return (max 200)
- offset:	int	0	Records to skip before listing
- include_deleted:	bool	false	Include soft-deleted records

Example Request:
```
curl -s "http://localhost:8000/products?limit=5&offset=0" \
  -H "X-API-Key: pat_cp1_xoxo" | jq
```

### Batch Update Products

Endpoint:
```
PATCH /products
```

Description:
Update existing products in bulk. Matches rows by (company_id, external_id) and updates provided fields (sku, status).

Request Headers:
```
Content-Type: application/json
X-API-Key: pat_cp1_xoxo
```

Request Body:
```
[
  {
    "id": "MAT-1001",
    "sku": "SKU-ALPHA-NEW",
    "status": "INACTIVE"
  },
  {
    "id": "MAT-1003",
    "status": "DISCONTINUED"
  }
]
```
# glassdome_takehome
