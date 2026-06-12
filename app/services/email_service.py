import smtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailService:
    def send_report_email(
        self,
        *,
        recipient_email: str,
        subject: str,
        body: str,
    ) -> str:
        if not settings.smtp_host or not settings.smtp_username or not settings.smtp_password or not settings.smtp_from_email:
            raise ValueError(
                "SMTP settings are incomplete. Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, and SMTP_FROM_EMAIL."
            )

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.smtp_from_email
        message["To"] = recipient_email
        message.set_content(body)

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)

        return f"Daily report email sent to {recipient_email}."
