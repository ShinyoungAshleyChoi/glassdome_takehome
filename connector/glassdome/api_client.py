import logging
import time
from typing import List, Dict, Any

import requests

logger = logging.getLogger(__name__)


class GlassdomeApiClient:

    def __init__(self, cfg: dict):
        self.base_url = cfg["base_url"].rstrip("/")
        self.api_key = cfg["api_key"]
        self.timeout = int(cfg.get("timeout_seconds", 5))
        self.max_retries = int(cfg.get("max_retries", 3))
        self.backoff_seconds = int(cfg.get("backoff_seconds", 2))

    def _headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def ingest_products(self, products: List[Dict[str, Any]]) -> bool:
        if not products:
            logger.info("No products to ingest.")
            return True

        url = f"{self.base_url}/ingest/products"
        logger.info("Sending %d products to %s", len(products), url)
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.post(
                    url,
                    json=products,
                    headers=self._headers(),
                    timeout=self.timeout,
                )
                if 200 <= resp.status_code < 300:
                    logger.info(
                        "Successfully ingested %d products (status=%s)",
                        len(products),
                        resp.status_code,
                    )
                    return True
                else:
                    logger.warning(
                        "Non-2xx response (attempt %d): status=%s body=%s",
                        attempt,
                        resp.status_code,
                        resp.text,
                    )
            except requests.RequestException as e:
                logger.error("Request failed on attempt %d: %s", attempt, e)

            if attempt < self.max_retries:
                logger.info(
                    "Retrying in %s seconds... (attempt %d/%d)",
                    self.backoff_seconds,
                    attempt,
                    self.max_retries,
                )
                time.sleep(self.backoff_seconds)

        logger.error("Failed to ingest products after %d attempts", self.max_retries)
        return False