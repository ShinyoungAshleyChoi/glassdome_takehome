import argparse
import sys
import json
from pathlib import Path

import yaml  # pyyaml

from glassdome.logging_utils import setup_logging
from glassdome.sync import run_sync


def load_config(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    text = p.read_text(encoding="utf-8")

    if path.endswith((".yaml", ".yml")):
        return yaml.safe_load(text)
    elif path.endswith(".json"):
        return json.loads(text)
    else:
        return yaml.safe_load(text)


def main():
    parser = argparse.ArgumentParser(description="Glassdome MES connector")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config file (YAML or JSON). Default: config.yaml",
    )
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="full",
        help="Override sync mode. Default: full",
    )

    args = parser.parse_args()

    config = load_config(args.config)

    if args.mode:
        config.setdefault("sync", {})
        config["sync"]["mode"] = args.mode

    setup_logging(config.get("logging", {}))

    try:
        total = run_sync(config)
        print(f"Sync finished. Total products sent: {total}")
    except Exception as e:
        print(f"Sync failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()