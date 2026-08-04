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

    def send_account_registration_notification(self, recipient_email: str, username: str, first_name: str = ""):
        clean_recipient = recipient_email.strip().lower()
        display_name = first_name.strip() if first_name else username.strip()
        subject = "AksharAI — Account Successfully Registered!"
        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #0b132b; color: #ffffff; padding: 20px;">
            <div style="max-width: 520px; margin: auto; background-color: #1e293b; border-radius: 12px; padding: 28px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
              <div style="text-align: center; margin-bottom: 20px;">
                <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #10b981, #14b8a6); border-radius: 12px; margin: 0 auto; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; color: #ffffff;">A</div>
                <h2 style="color: #10b981; margin-top: 10px; font-size: 22px;">Welcome to AksharAI!</h2>
              </div>
              <p style="font-size: 15px; color: #e2e8f0;">Dear <strong>{display_name}</strong>,</p>
              <p style="font-size: 14px; color: #cbd5e1; line-height: 1.6;">
                This email is to confirm that a new <strong>AksharAI Neo-Learner Account</strong> has been successfully registered using your email address:
              </p>
              <div style="background-color: #0f172a; border-radius: 8px; padding: 16px; margin: 20px 0; border-left: 4px solid #10b981;">
                <p style="margin: 4px 0; font-size: 13px; color: #94a3b8;">Registered Email: <strong style="color: #ffffff;">{clean_recipient}</strong></p>
                <p style="margin: 4px 0; font-size: 13px; color: #94a3b8;">Username: <strong style="color: #10b981;">{username}</strong></p>
                <p style="margin: 4px 0; font-size: 13px; color: #94a3b8;">Registration Date: <strong style="color: #cbd5e1;">{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</strong></p>
              </div>
              <p style="font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                You can now log in, take your initial bilingual diagnostic test, and start your personalized adaptive language literacy journey.
              </p>
              <hr style="border: 0; border-top: 1px solid #334155; margin: 24px 0;" />
              <p style="font-size: 11px; color: #64748b; text-align: center;">
                Security Notice: If you did not register this account, please contact AksharAI support or reset your password immediately.
              </p>
            </div>
          </body>
        </html>
        """

        print(f"\n[SECURE EMAIL DISPATCHER] Dispatching Account Registration Intimation Email to: {clean_recipient}")
        self._save_sent_email(clean_recipient, subject, html_content)

        if self.smtp_user and self.smtp_password and len(self.smtp_password.strip()) > 0:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"AksharAI Platform <{self.smtp_user}>"
                msg["To"] = clean_recipient
                msg.attach(MIMEText(html_content, "html"))

                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.smtp_user, clean_recipient, msg.as_string())
                print(f"[SECURE EMAIL DISPATCHER] SUCCESS: Sent Registration Intimation Email via SMTP to {clean_recipient}")
                return True
            except Exception as e:
                print(f"[SECURE EMAIL DISPATCHER] SMTP delivery exception: {e}")
                return False
        else:
            print(f"[SECURE EMAIL DISPATCHER] SMTP credentials not fully configured. Email record saved to sent_emails.json.")
            return True

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
