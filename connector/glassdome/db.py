import logging
from typing import List, Optional, Any, Dict
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class MesDbClient:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.conn = None

    def connect(self) -> None:
        if self.conn is not None:
            return

        logger.info(
            "Connecting to mes-db host=%s port=%s db=%s",
            self.cfg["host"],
            self.cfg["port"],
            self.cfg["database"],
        )

        self.conn = psycopg2.connect(
            host=self.cfg["host"],
            port=self.cfg["port"],
            user=self.cfg["user"],
            password=self.cfg["password"],
            dbname=self.cfg["database"],
        )

    def fetch_products(self, limit: int = 500, offset: int = 0) -> List[Dict[str, Any]]:
        if self.conn is None:
            self.connect()

        sql = """
              SELECT
                  matnr AS matnr,
                  sku   AS sku,
                  status AS status
              FROM mvke
              ORDER BY matnr, vkorg, vtweg
                  LIMIT %s OFFSET %s \
              """
        params: List[Any] = [limit, offset]

        logger.debug("Executing SQL: %s params=%s", sql, params)

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        logger.info("Fetched %d product rows from mes-db", len(rows))
        return rows

    def close(self) -> None:
        if self.conn:
            logger.info("Closing mes-db connection")
            self.conn.close()
            self.conn = None