-- MES (customer) schema to simulate SAP-style split product data
-- MARA: General material data
CREATE TABLE IF NOT EXISTS mara (
  matnr TEXT PRIMARY KEY,              -- material number (external id)
  mtart TEXT NOT NULL,                 -- material type
  meins TEXT NOT NULL DEFAULT 'EA',    -- base unit of measure
  ersda DATE NOT NULL DEFAULT CURRENT_DATE
);

-- MAKT: Material descriptions (language dependent)
CREATE TABLE IF NOT EXISTS makt (
  matnr TEXT NOT NULL,
  spras TEXT NOT NULL,                 -- language key, e.g., 'EN'
  maktx TEXT NOT NULL,                 -- short description
  PRIMARY KEY (matnr, spras),
  FOREIGN KEY (matnr) REFERENCES mara(matnr)
);

-- MVKE: Sales data (sales org level SKU / status)
CREATE TABLE IF NOT EXISTS mvke (
  matnr TEXT NOT NULL,
  vkorg TEXT NOT NULL,                 -- sales org
  vtweg TEXT NOT NULL,                 -- distribution channel
  sku TEXT NOT NULL,                   -- sellable SKU
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  PRIMARY KEY (matnr, vkorg, vtweg),
  FOREIGN KEY (matnr) REFERENCES mara(matnr)
);

-- MARM: Alternative units of measure
CREATE TABLE IF NOT EXISTS marm (
  matnr TEXT NOT NULL,
  umrez INTEGER NOT NULL DEFAULT 1,    -- numerator
  umren INTEGER NOT NULL DEFAULT 1,    -- denominator
  altuom TEXT NOT NULL,                -- e.g., 'BOX'
  PRIMARY KEY (matnr, altuom),
  FOREIGN KEY (matnr) REFERENCES mara(matnr)
);

-- SEED

INSERT INTO mara (matnr, mtart, meins) VALUES
  ('MAT-1001', 'FERT', 'EA'),
  ('MAT-1002', 'HALB', 'EA'),
  ('MAT-1003', 'FERT', 'EA')
ON CONFLICT (matnr) DO NOTHING;

INSERT INTO makt (matnr, spras, maktx) VALUES
  ('MAT-1001', 'EN', 'Widget Alpha'),
  ('MAT-1001', 'DE', 'Widget Alpha DE'),
  ('MAT-1002', 'EN', 'Widget Beta'),
  ('MAT-1003', 'EN', 'Widget Gamma')
ON CONFLICT (matnr, spras) DO NOTHING;

INSERT INTO mvke (matnr, vkorg, vtweg, sku, status) VALUES
  ('MAT-1001', '1000', '10', 'SKU-ALPHA', 'ACTIVE'),
  ('MAT-1002', '1000', '10', 'SKU-BETA',  'ACTIVE'),
  ('MAT-1002', '2000', '10', 'SKU-BETA',  'INACTIVE'),
  ('MAT-1003', '1000', '20', 'SKU-GAMMA-ALT', 'ACTIVE')
ON CONFLICT (matnr, vkorg, vtweg) DO NOTHING;

INSERT INTO marm (matnr, umrez, umren, altuom) VALUES
  ('MAT-1001', 10, 1, 'BOX'),
  ('MAT-1002', 6, 1, 'PACK')
ON CONFLICT (matnr, altuom) DO NOTHING;