
from collections.abc import Callable
from threading import Event

from datasentinel.scheduler import DataSentinelScheduler


def run_scheduler(
    job: Callable[[], None],
    cron_expression: str,
) -> None:
    """Run a scheduled job until the process is interrupted."""
    scheduler = DataSentinelScheduler()

    scheduler.add_cron_job(
        job=job,
        job_id="datasentinel-validation",
        cron_expression=cron_expression,
    )

    try:
        scheduler.start()
        print(
            f"DataSentinel scheduler running. "
            f"Cron expression: {cron_expression}"
        )
        Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()
