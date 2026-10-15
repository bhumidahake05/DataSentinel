
"""Email and Slack notifications for DataSentinel."""

import os
import smtplib
from email.message import EmailMessage

import httpx


class AlertService:
    """Send data-quality alerts through email and Slack."""

    def send_email(
        self,
        subject: str,
        summary: str,
        recipient: str,
    ) -> None:
        """Send an email using SMTP environment configuration."""
        smtp_host = os.getenv("DATASENTINEL_SMTP_HOST")
        smtp_port = os.getenv("DATASENTINEL_SMTP_PORT", "587")
        smtp_user = os.getenv("DATASENTINEL_SMTP_USER")
        smtp_password = os.getenv("DATASENTINEL_SMTP_PASSWORD")
        sender = os.getenv("DATASENTINEL_EMAIL_FROM")

        if not all(
            (
                smtp_host,
                smtp_user,
                smtp_password,
                sender,
            )
        ):
            raise ValueError(
                "Configure DATASENTINEL_SMTP_HOST, "
                "DATASENTINEL_SMTP_USER, "
                "DATASENTINEL_SMTP_PASSWORD, and "
                "DATASENTINEL_EMAIL_FROM."
            )

        try:
            port = int(smtp_port)
        except ValueError as error:
            raise ValueError(
                "DATASENTINEL_SMTP_PORT must be an integer."
            ) from error

        # The configuration check above guarantees these values exist.
        assert smtp_host is not None
        assert smtp_user is not None
        assert smtp_password is not None
        assert sender is not None

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = recipient
        message.set_content(summary)

        with smtplib.SMTP(
            smtp_host,
            port,
            timeout=15,
        ) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)

    def send_slack(self, summary: str) -> None:
        """Send a message to a Slack incoming webhook."""
        webhook_url = os.getenv("DATASENTINEL_SLACK_WEBHOOK")

        if not webhook_url:
            raise ValueError(
                "Configure the DATASENTINEL_SLACK_WEBHOOK "
                "environment variable."
            )

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                webhook_url,
                json={"text": summary},
            )
            response.raise_for_status()
