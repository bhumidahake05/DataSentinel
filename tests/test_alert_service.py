
import pytest

from datasentinel.alerts.service import AlertService


def test_email_requires_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATASENTINEL_SMTP_HOST", raising=False)
    monkeypatch.delenv("DATASENTINEL_SMTP_USER", raising=False)
    monkeypatch.delenv("DATASENTINEL_SMTP_PASSWORD", raising=False)
    monkeypatch.delenv("DATASENTINEL_EMAIL_FROM", raising=False)

    with pytest.raises(ValueError, match="Configure"):
        AlertService().send_email(
            subject="Data quality summary",
            summary="Validation completed.",
            recipient="test@example.com",
        )


def test_slack_requires_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATASENTINEL_SLACK_WEBHOOK", raising=False)

    with pytest.raises(ValueError, match="Configure"):
        AlertService().send_slack("Validation completed.")
