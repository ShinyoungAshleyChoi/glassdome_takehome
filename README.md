# 해결 방법
- MES(DB)에서 mvke + mara 데이터를 조인하여 SKU 기반 product 데이터를 생성
- 배치 단위로 데이터를 읽어오고, Glassdome API(`/ingest/products`)로 POST 요청을 보내도록 커넥터를 구현
- 인증 헤더(`X-API-Key`)를 포함하고, 요청 실패 시 재시도 및 backoff 로직을 추가
- 실행 시 config.yaml을 로드하여 DB 연결 정보, API 설정, 배치 크기 등을 유연하게 조정할 수 있도록 했다

# 문제 해결 허들
- 제공된 mes-db 스키마에는 `production_orders`가 존재하지 않아, 실제 어떤 데이터를 product로 변환해야 하는지 혼란이 있었다.
- SAP 스타일 스키마(mara, mvke 등)를 처음 분석해봐서 각 데이터의 의미를 파악하는데 시간이 걸렸다.
- updated_at 컬럼이 없어 incremental sync를 구현하기 힘들었다.

# 개선점
- 실제 환경에서는 incremental sync를 위해 mvke 테이블에 updated_at 트리거/컬럼을 추가하는 것이 필요하다.
- 커넥터 실행 상태 및 동기화 이력을 DB나 Redis 같은 외부 저장소에 남기면 운영 안정성을 높일 수 있다.