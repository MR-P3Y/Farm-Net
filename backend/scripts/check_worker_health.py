import argparse
import json
from pathlib import Path
import time


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Farm-Net worker heartbeat")
    parser.add_argument("heartbeat_file", type=Path)
    parser.add_argument("--max-age-seconds", type=float, default=60)
    parser.add_argument("--max-consecutive-failures", type=int, default=5)
    args = parser.parse_args()

    if not args.heartbeat_file.is_file():
        return 1
    try:
        heartbeat = json.loads(args.heartbeat_file.read_text(encoding="utf-8"))
        age = time.time() - float(heartbeat["updated_at_epoch"])
        failures = int(heartbeat["consecutive_failures"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError):
        return 1
    if age < 0 or age > args.max_age_seconds:
        return 1
    return 0 if failures < args.max_consecutive_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
