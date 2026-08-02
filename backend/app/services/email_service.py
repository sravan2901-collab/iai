import smtplib
import os
import json
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

SENT_EMAILS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sent_emails.json"))

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.sender_email = settings.SENDER_EMAIL or "no-reply@aksharai.com"

    def _save_sent_email(self, recipient: str, subject: str, body: str, otp_code: str = None):
        email_record = {
            "recipient": recipient.strip().lower(),
            "subject": subject,
            "body": body,
            "otp_code": otp_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            records = []
            if os.path.exists(SENT_EMAILS_FILE):
                try:
                    with open(SENT_EMAILS_FILE, "r", encoding="utf-8") as f:
                        records = json.load(f)
                except Exception:
                    records = []
            records.append(email_record)
            with open(SENT_EMAILS_FILE, "w", encoding="utf-8") as f:
                json.dump(records[-50:], f, indent=2)
            print(f"[SECURE EMAIL DISPATCHER] Saved email record to {SENT_EMAILS_FILE}")
        except Exception as e:
            print(f"[SECURE EMAIL DISPATCHER] Error saving email record: {e}")

    def send_password_reset_otp(self, recipient_email: str, otp_code: str):
        clean_recipient = recipient_email.strip().lower()
        subject = "AksharAI - Your 6-Digit Password Reset OTP"
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #0b132b; color: #ffffff; padding: 20px;">
            <div style="max-width: 500px; margin: auto; background-color: #1e293b; border-radius: 12px; padding: 24px; border: 1px solid #334155;">
              <h2 style="color: #10b981; text-align: center;">AksharAI Password Reset</h2>
              <p>Hello,</p>
              <p>You requested to reset your password. Use the following 6-digit OTP code to complete your password reset:</p>
              <div style="background-color: #0f172a; border-radius: 8px; padding: 16px; text-align: center; margin: 20px 0; border: 1px solid #10b981;">
                <span style="font-size: 28px; font-weight: bold; letter-spacing: 6px; color: #f59e0b;">{otp_code}</span>
              </div>
              <p style="font-size: 12px; color: #94a3b8;">This OTP is valid for 15 minutes. If you did not request a password reset, please ignore this email.</p>
            </div>
          </body>
        </html>
        """
        
        print(f"\n[SECURE EMAIL DISPATCHER] Dispatching OTP ({otp_code}) to: {clean_recipient}")
        self._save_sent_email(clean_recipient, subject, html_content, otp_code)

        if self.smtp_user and self.smtp_password and len(self.smtp_password.strip()) > 0:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"AksharAI Security <{self.smtp_user}>"
                msg["To"] = clean_recipient
                msg.attach(MIMEText(html_content, "html"))

                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.smtp_user, clean_recipient, msg.as_string())
                print(f"[SECURE EMAIL DISPATCHER] SUCCESS: Sent email via SMTP to {clean_recipient}")
                return True
            except Exception as e:
                print(f"[SECURE EMAIL DISPATCHER] SMTP delivery exception: {e}")
                return False
        else:
            print(f"[SECURE EMAIL DISPATCHER] SMTP credentials not fully configured. Email logged to sent_emails.json.")
            return True

    def send_email_verification(self, recipient_email: str, token: str):
        clean_recipient = recipient_email.strip().lower()
        subject = "AksharAI - Verify Your Email Address"
        html_content = f"<p>Click link to verify email: http://127.0.0.1:5173/verify?token={token}</p>"
        self._save_sent_email(clean_recipient, subject, html_content, None)
        return True

email_service = EmailService()
