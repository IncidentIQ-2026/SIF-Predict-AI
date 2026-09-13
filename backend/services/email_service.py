import logging
import smtplib
from email.message import EmailMessage
from ..config import settings

logger = logging.getLogger(__name__)


def send_hazard_email(recipients: list[str], location: str, rule: str, report_text: str, probability: float) -> bool:
    recipients = sorted({email.strip() for email in recipients if email and "@" in email})
    if not recipients or not settings.smtp_host:
        logger.warning("SMTP is not configured; hazard email was not sent")
        return False
    message = EmailMessage()
    message["Subject"] = f"[SIF-Predict AI] Hazard alert: {rule} at {location}"
    message["From"] = settings.smtp_from
    message["To"] = ", ".join(recipients)
    message.set_content(f"A high-risk safety report was submitted.\n\nLocation: {location}\nLife-Saving Rule: {rule}\nSIF confidence: {probability:.0%}\n\nReport:\n{report_text}\n\nDo not begin or continue work until HSE or a Supervisor reviews the control gap.")
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_starttls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return True
    except (OSError, smtplib.SMTPException):
        logger.exception("Unable to send hazard email")
        return False
