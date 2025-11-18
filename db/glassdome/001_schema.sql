-- Glassdome internal canonical product table
CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY,                 -- internal id provided by caller
  external_id TEXT NOT NULL,           -- source system id (e.g., SAP MATNR)
  company_id TEXT NOT NULL,
  sku TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('ACTIVE','INACTIVE','DISCONTINUED')),
  create_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  update_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  delete_time TIMESTAMPTZ NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_products_company_external ON products(company_id, external_id);
CREATE UNIQUE INDEX IF NOT EXISTS ux_products_company_sku ON products(company_id, sku);

-- SEED
INSERT INTO products (id, external_id, company_id, sku, status)
VALUES
  ('prod_1', 'MAT-1001', 'company_1', 'SKU-ALPHA', 'ACTIVE')
ON CONFLICT DO NOTHING;