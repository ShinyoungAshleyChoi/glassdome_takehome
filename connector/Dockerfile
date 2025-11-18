FROM python:3.11-slim

WORKDIR /app

COPY connector.py config.yaml /app/
COPY glassdome /app/glassdome

RUN pip install --no-cache-dir psycopg2-binary requests pyyaml

CMD ["python", "connector.py", "--config", "config.yaml"]