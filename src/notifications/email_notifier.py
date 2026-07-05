import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import time
from dotenv import load_dotenv
from ..utils.logger import setup_logger

logger = setup_logger()

load_dotenv()


class EmailNotifier:
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587,
                 email_address: str = None, email_password: str = None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = email_address or os.getenv("EMAIL_ADDRESS")
        self.email_password = email_password or os.getenv("EMAIL_PASSWORD")
        self.pending_requests = {}

    def send_notification(self, subject: str, body: str, request_id: str = None) -> bool:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_address
            msg["To"] = self.email_address
            msg["Subject"] = f"[CertAgent] {subject}"

            full_body = body + "\n\n---\nReply to this email to provide your answer."
            msg.attach(MIMEText(full_body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)

            if request_id:
                self.pending_requests[request_id] = {
                    "sent_at": datetime.now(),
                    "subject": subject,
                    "answered": False
                }

            logger.info(f"Email notification sent: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def check_for_replies(self, request_id: str = None, timeout_minutes: int = 30) -> str:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.email_address, self.email_password)
            mail.select("INBOX")

            since = (datetime.now() - timedelta(minutes=timeout_minutes)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'(SINCE "{since}")')

            if status != "OK":
                return None

            msg_ids = messages[0].split()

            for msg_id in reversed(msg_ids[-10:]):
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue

                email_message = email.message_from_bytes(msg_data[0][1])

                if "re:" in email_message["subject"].lower():
                    body = self._get_email_body(email_message)
                    if body:
                        answer = body.strip().upper()
                        if len(answer) <= 3:
                            logger.info(f"Received reply: {answer}")
                            mail.logout()
                            return answer

            mail.logout()
            return None

        except Exception as e:
            logger.error(f"Error checking email: {e}")
            return None

    def _get_email_body(self, email_message) -> str:
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return email_message.get_payload(decode=True).decode()
        return ""

    def wait_for_reply(self, request_id: str, timeout_minutes: int = 30,
                       check_interval: int = 60) -> str:
        logger.info(f"Waiting for email reply (timeout: {timeout_minutes}min)...")
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout_minutes * 60:
            reply = self.check_for_replies(request_id, timeout_minutes=2)
            if reply:
                return reply
            time.sleep(check_interval)

        logger.warning("Timeout waiting for email reply")
        return None

    def send_completion_notification(self, course_name: str, certificate_path: str = None):
        subject = f"Course Completed: {course_name}"
        body = f"Congratulations!\n\nYou've completed: {course_name}\n\n"
        if certificate_path:
            body += f"Certificate saved to: {certificate_path}\n"
        body += "\nKeep up the great work!"
        self.send_notification(subject, body)

    def send_progress_update(self, stats: dict):
        subject = "Daily Progress Update"
        body = f"CertAgent Progress Report:\n\n"
        body += f"Total courses: {stats.get('total', 0)}\n"
        body += f"Completed: {stats.get('completed', 0)}\n"
        body += f"In progress: {stats.get('in_progress', 0)}\n"
        body += f"Enrolled: {stats.get('enrolled', 0)}\n"
        body += f"Discovered: {stats.get('discovered', 0)}\n"
        self.send_notification(subject, body)
