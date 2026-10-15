
from collections.abc import Callable

from datasentinel.scheduler import DataSentinelScheduler


def test_add_cron_job() -> None:
    scheduler = DataSentinelScheduler()

    def sample_job() -> None:
        pass

    scheduler.add_cron_job(
        job=sample_job,
        job_id="test-job",
        cron_expression="0 9 * * *",
    )

    jobs = scheduler.scheduler.get_jobs()

    assert len(jobs) == 1
    assert jobs[0].id == "test-job"
    assert jobs[0].coalesce is True

    scheduler.shutdown()


def test_invalid_cron_expression() -> None:
    import pytest

    scheduler = DataSentinelScheduler()

    def sample_job() -> None:
        pass

    with pytest.raises(ValueError):
        scheduler.add_cron_job(
            job=sample_job,
            job_id="invalid-job",
            cron_expression="invalid",
        )

