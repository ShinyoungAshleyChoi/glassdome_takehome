import logging
from logging.handlers import RotatingFileHandler


def setup_logging(cfg: dict) -> None:
    level_name = cfg.get("level", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    )

    if cfg.get("log_to_file"):
        file_path = cfg.get("file_path", "connector.log")
        handler = RotatingFileHandler(
            file_path,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
        )
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)