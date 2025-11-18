"""Email notification system."""
import logging
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

from src.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class EmailManager:
    """Manage email notifications."""

    def __init__(self):
        self.smtp_host = getattr(settings, 'smtp_host', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_user = getattr(settings, 'smtp_user', '')
        self.smtp_password = getattr(settings, 'smtp_password', '')
        self.from_email = getattr(settings, 'from_email', 'noreply@moneyapi.example.com')

    def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send email.

        Args:
            to: Recipient email
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text fallback

        Returns:
            Success status
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to
            msg['Subject'] = subject

            # Add text part
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))

            # Add HTML part
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_welcome_email(self, to: str, name: str) -> bool:
        """Send welcome email to new user."""
        subject = "Welcome to Money API Service!"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>Welcome to Money API Service, {name}!</h1>

            <p>Thank you for signing up. You've been granted <strong>$5 in free credits</strong> to get started.</p>

            <h2>Quick Start Guide:</h2>
            <ol>
                <li>Create your first API key in the dashboard</li>
                <li>Check out our <a href="https://docs.moneyapi.example.com">documentation</a></li>
                <li>Try our example applications</li>
            </ol>

            <h2>What's Next?</h2>
            <ul>
                <li>Explore our Text, Image, Audio, and Document AI APIs</li>
                <li>Upgrade to a paid plan for higher rate limits</li>
                <li>Join our community Discord</li>
            </ul>

            <p>If you have any questions, feel free to reply to this email.</p>

            <p>Happy coding!<br>
            The Money API Team</p>
        </body>
        </html>
        """

        text_body = f"Welcome to Money API Service, {name}! You've been granted $5 in free credits."

        return self.send_email(to, subject, html_body, text_body)

    def send_low_credit_alert(self, to: str, balance: float) -> bool:
        """Send low credit alert."""
        subject = "⚠️ Low Credit Balance Alert"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>Low Credit Balance</h1>

            <p>Your Money API credit balance is running low:</p>

            <p style="font-size: 24px; color: #ff6b6b;">
                <strong>${balance:.2f}</strong>
            </p>

            <p>To avoid service interruption, please add more credits:</p>

            <a href="https://dashboard.moneyapi.example.com/billing"
               style="display: inline-block; padding: 12px 24px; background-color: #4CAF50;
                      color: white; text-decoration: none; border-radius: 4px;">
                Add Credits
            </a>

            <p style="margin-top: 20px;">
                Or <a href="https://dashboard.moneyapi.example.com/plans">upgrade your plan</a>
                for included credits each month.
            </p>
        </body>
        </html>
        """

        return self.send_email(to, subject, html_body)

    def send_api_key_created(self, to: str, key_name: str, key_prefix: str) -> bool:
        """Send notification when API key is created."""
        subject = "🔑 New API Key Created"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>New API Key Created</h1>

            <p>A new API key has been created for your account:</p>

            <table style="border: 1px solid #ddd; padding: 10px;">
                <tr>
                    <td><strong>Name:</strong></td>
                    <td>{key_name}</td>
                </tr>
                <tr>
                    <td><strong>Key Prefix:</strong></td>
                    <td>{key_prefix}...</td>
                </tr>
            </table>

            <p>If you didn't create this key, please <a href="https://dashboard.moneyapi.example.com/security">
            review your account security</a> immediately.</p>
        </body>
        </html>
        """

        return self.send_email(to, subject, html_body)

    def send_usage_report(
        self,
        to: str,
        period: str,
        total_requests: int,
        total_cost: float,
        by_endpoint: dict
    ) -> bool:
        """Send monthly usage report."""
        subject = f"📊 Your {period} Usage Report"

        # Build endpoint breakdown
        endpoint_rows = ""
        for endpoint, stats in by_endpoint.items():
            endpoint_rows += f"""
            <tr>
                <td>{endpoint}</td>
                <td>{stats['requests']}</td>
                <td>${stats['cost']:.2f}</td>
            </tr>
            """

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h1>Usage Report - {period}</h1>

            <h2>Summary</h2>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <td style="padding: 10px;"><strong>Total Requests:</strong></td>
                    <td style="padding: 10px;">{total_requests:,}</td>
                </tr>
                <tr>
                    <td style="padding: 10px;"><strong>Total Cost:</strong></td>
                    <td style="padding: 10px;">${total_cost:.2f}</td>
                </tr>
            </table>

            <h2>By Endpoint</h2>
            <table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd;">
                <thead>
                    <tr style="background-color: #4CAF50; color: white;">
                        <th style="padding: 10px; text-align: left;">Endpoint</th>
                        <th style="padding: 10px; text-align: left;">Requests</th>
                        <th style="padding: 10px; text-align: left;">Cost</th>
                    </tr>
                </thead>
                <tbody>
                    {endpoint_rows}
                </tbody>
            </table>

            <p style="margin-top: 20px;">
                <a href="https://dashboard.moneyapi.example.com/usage">View Full Report</a>
            </p>
        </body>
        </html>
        """

        return self.send_email(to, subject, html_body)


# Global email manager instance
email_manager = EmailManager()
