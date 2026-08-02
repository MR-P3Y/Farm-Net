import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import signal
import sys
from threading import Event


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


shutdown_requested = Event()


def request_shutdown(_signum: int, _frame: object) -> None:
    shutdown_requested.set()


def dispatcher_for(channel: str, db):
    if channel == "email":
        from app.modules.notifications.email_dispatcher import EmailDeliveryDispatcher

        return EmailDeliveryDispatcher(db)
    if channel == "sms":
        from app.modules.notifications.sms_dispatcher import SmsDeliveryDispatcher

        return SmsDeliveryDispatcher(db)
    if channel == "push":
        from app.modules.notifications.push_dispatcher import PushDeliveryDispatcher

        return PushDeliveryDispatcher(db)
    raise ValueError("Unsupported notification channel")


def emit(event: str, **details: object) -> None:
    print(
        json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": event,
                **details,
            },
            sort_keys=True,
        ),
        flush=True,
    )


def write_heartbeat(path: Path, *, consecutive_failures: int) -> None:
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(
            {
                "updated_at_epoch": datetime.now(UTC).timestamp(),
                "consecutive_failures": consecutive_failures,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    temporary_path.replace(path)


def main() -> int:
    from app.db.session import SessionLocal

    parser = argparse.ArgumentParser(description="Run a Farm-Net notification worker")
    parser.add_argument("--channel", choices=("email", "sms", "push"), required=True)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument(
        "--heartbeat-file",
        type=Path,
        default=Path("/tmp/farmnet-worker-heartbeat"),
    )
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.limit < 1 or args.limit > 500:
        parser.error("--limit must be between 1 and 500")
    if args.poll_seconds < 0.1 or args.poll_seconds > 300:
        parser.error("--poll-seconds must be between 0.1 and 300")

    signal.signal(signal.SIGTERM, request_shutdown)
    signal.signal(signal.SIGINT, request_shutdown)
    emit("worker_started", channel=args.channel)
    consecutive_failures = 0

    while not shutdown_requested.is_set():
        write_heartbeat(
            args.heartbeat_file,
            consecutive_failures=consecutive_failures,
        )
        db = SessionLocal()
        try:
            from app.modules.farms.toolbox_service import FarmToolboxService

            reminder_count = FarmToolboxService(db).dispatch_due_reminders(
                limit=args.limit
            )
            result = dispatcher_for(args.channel, db).run_once(limit=args.limit)
            consecutive_failures = 0
            emit(
                "worker_batch",
                channel=args.channel,
                farm_plan_reminders=reminder_count,
                **result.__dict__,
            )
        except Exception as exc:
            db.rollback()
            consecutive_failures += 1
            emit(
                "worker_batch_failed",
                channel=args.channel,
                error_type=type(exc).__name__,
            )
        finally:
            db.close()
            write_heartbeat(
                args.heartbeat_file,
                consecutive_failures=consecutive_failures,
            )

        if args.once or shutdown_requested.wait(args.poll_seconds):
            break

    emit("worker_stopped", channel=args.channel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
