
from collections.abc import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class DataSentinelScheduler:
    """Schedule DataSentinel jobs using cron expressions."""

    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler()

    def add_cron_job(
        self,
        job: Callable[[], None],
        job_id: str,
        cron_expression: str,
    ) -> None:
        """Register a job using a five-field cron expression."""
        trigger = CronTrigger.from_crontab(cron_expression)

        self.scheduler.add_job(
            job,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        """Stop the scheduler safely."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
