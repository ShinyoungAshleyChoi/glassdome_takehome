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

# 문제 해결 허들
- 제공된 mes-db 스키마에는 `production_orders`가 존재하지 않아, 실제 어떤 데이터를 product로 변환해야 하는지 혼란이 있었다.
- SAP 스타일 스키마(mara, mvke 등)를 분석해보니 mvke의 SKU가 실제 "판매 가능한 제품 단위"임을 파악하는 데 시간이 걸렸다.
- updated_at 컬럼이 없어 incremental sync를 구현할 수 없었기 때문에 full sync 전략으로 접근해야 했다.
- API 응답 실패 시 정확한 재시도 조건, 로깅, 예외 안전성 확보가 필요했다.

# 개선점
- mvke/mara 외에도 makt(다국어 텍스트), marm(대체 단위)을 활용해 더 풍부한 product payload를 만들 수 있다.
- 실제 환경에서는 incremental sync를 위해 mvke 테이블에 updated_at 트리거/컬럼을 추가하는 것이 필요하다.
- 커넥터 실행 상태 및 동기화 이력을 DB나 Redis 같은 외부 저장소에 남기면 운영 안정성을 높일 수 있다.
- 테스트 코드(pytest) 및 각 계층(db, api_client, sync)의 유닛테스트를 추가해 신뢰성을 강화할 수 있다.