import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import aiosmtplib
from datetime import datetime
from app.core.config import settings


class EmailService:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM
        self.frontend_url = settings.FRONTEND_URL

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email using SMTP."""
        if not self.username or not self.password:
            print(f"Email not configured. Would send to {to_email}: {subject}")
            return False

        message = MIMEMultipart("alternative")
        message["From"] = self.from_email
        message["To"] = to_email
        message["Bcc"] = "missdanidaniels@yahoo.com"
        message["Subject"] = subject

        if text_content:
            message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))

        # Original project used aiosmtplib.send directly
        # Port 587 -> start_tls=True
        # Port 465 -> use_tls=True (implicit SSL)
        use_tls = (str(self.port) == "465")
        start_tls = (str(self.port) == "587")

        try:
            print(f"Attempting to send email to {to_email} via {self.host}:{self.port} (STARTTLS: {start_tls}, TLS: {use_tls})")
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=int(self.port),
                username=self.username,
                password=self.password,
                use_tls=use_tls,
                start_tls=start_tls,
                timeout=15
            )
            print(f"Successfully sent email to {to_email}")
            return True
        except Exception as e:
            print(f"Primary SMTP ({self.host}) failed: {type(e).__name__}: {e}")
            
            # Fallback to smtp.googlemail.com
            if self.host == "smtp.gmail.com":
                try:
                    print(f"Trying fallback host: smtp.googlemail.com...")
                    await aiosmtplib.send(
                        message,
                        hostname="smtp.googlemail.com",
                        port=int(self.port),
                        username=self.username,
                        password=self.password,
                        use_tls=use_tls,
                        start_tls=start_tls,
                        timeout=15
                    )
                    print(f"Successfully sent email via fallback to {to_email}")
                    return True
                except Exception as fe:
                    print(f"Fallback also failed: {fe}")
            
            print("HINT: If you see a timeout, Render might be blocking the port. Port 587 is usually safer.")
            return False

    async def send_verification_email(self, email: str, name: str, token: str) -> bool:
        """Send email verification link."""
        verification_url = f"{self.frontend_url}/verify-email?token={token}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Welcome to Tickmarks TimeTracker</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {name},</p>
                <p style="font-size: 16px; color: #334155;">Thank you for registering with Tickmarks TimeTracker. Please verify your email address by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Verify Email Address</a>
                </div>
                <p style="font-size: 14px; color: #64748b;">Or copy and paste this link into your browser:</p>
                <p style="font-size: 12px; color: #7c3aed; word-break: break-all;">{verification_url}</p>
                <p style="font-size: 14px; color: #64748b; margin-top: 30px;">This link will expire in 24 hours. If you did not create an account, you can safely ignore this email.</p>
            </div>
            <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                <p>&copy; {datetime.now().year} Tickmarks. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Tickmarks TimeTracker
        
        Hello {name},
        
        Thank you for registering. Please verify your email by visiting:
        {verification_url}
        
        This link will expire in 24 hours.
        """
        
        return await self.send_email(
            to_email=email,
            subject="Verify Your Email - Tickmarks TimeTracker",
            html_content=html_content,
            text_content=text_content
        )

    async def send_otp_email(self, email: str, name: str, otp: str) -> bool:
        """Send 6-digit OTP for first-time password changes."""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Security Verification</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {name},</p>
                <p style="font-size: 16px; color: #334155;">To complete your first-time secure login and set your new password, please use the following 6-digit code:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <div style="background: #ffffff; border: 2px dashed #7c3aed; color: #0f172a; padding: 20px 40px; font-size: 32px; letter-spacing: 8px; font-weight: bold; display: inline-block; border-radius: 8px;">
                        {otp}
                    </div>
                </div>
                <p style="font-size: 14px; color: #64748b; margin-top: 30px;">This code is valid for 10 minutes. Do not share this code with anyone.</p>
            </div>
        </body>
        </html>
        """
        text_content = f"Hello {name},\n\nYour 6-digit verification code is: {otp}\n\nThis code expires in 10 minutes."
        
        return await self.send_email(
            to_email=email,
            subject="Your Login Verification Code",
            html_content=html_content,
            text_content=text_content
        )

    async def send_weekly_reminder_email(self, email: str, name: str, pending_count: int) -> bool:
        """Send automated weekly reminder to managers about pending timesheets."""
        approvals_url = f"{{self.frontend_url}}/approvals"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Pending Timesheet Approvals</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {name},</p>
                <p style="font-size: 16px; color: #334155;">This is an automated weekly reminder.</p>
                <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px; margin-top: 20px;">
                    <p style="font-size: 16px; color: #b45309; margin: 0;">You currently have <strong>{pending_count} time entries</strong> awaiting your approval.</p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{approvals_url}" style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Review Time Entries</a>
                </div>
                <p style="font-size: 14px; color: #64748b; margin-top: 20px;">To ensure accurate payroll and tracking, please review and action these entries as soon as possible.</p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=email,
            subject="Action Required: Pending Timesheet Approvals",
            html_content=html_content
        )

    async def send_weekly_report(
        self,
        manager_email: str,
        manager_name: str,
        pending_entries: list,
        week_start: str,
        week_end: str
    ) -> bool:
        """Send weekly pending time entries report to manager."""
        
        entries_html = ""
        total_hours = 0
        
        for entry in pending_entries:
            total_hours += float(entry.get('hours', 0))
            entries_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{entry.get('user_name', 'N/A')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{entry.get('project_name', 'N/A')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{entry.get('work_date', 'N/A')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center;">{entry.get('hours', 0)}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">{entry.get('notes', '')}</td>
            </tr>
            """
        
        approvals_url = f"{self.frontend_url}/approvals"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Weekly Time Entries Report</h1>
                <p style="color: rgba(255,255,255,0.9); margin-top: 10px;">{week_start} to {week_end}</p>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {manager_name},</p>
                <p style="font-size: 16px; color: #334155;">You have <strong>{len(pending_entries)} time entries</strong> totaling <strong>{total_hours:.2f} hours</strong> pending approval for the past week:</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <thead>
                        <tr style="background: #7c3aed;">
                            <th style="padding: 12px; color: white; text-align: left;">Employee</th>
                            <th style="padding: 12px; color: white; text-align: left;">Project</th>
                            <th style="padding: 12px; color: white; text-align: left;">Date</th>
                            <th style="padding: 12px; color: white; text-align: center;">Hours</th>
                            <th style="padding: 12px; color: white; text-align: left;">Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {entries_html}
                    </tbody>
                </table>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{approvals_url}" style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Review & Approve Time Entries</a>
                </div>
                
                <p style="font-size: 14px; color: #64748b; margin-top: 20px;">Please review and approve or reject these entries at your earliest convenience.</p>
            </div>
            <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                <p>&copy; {datetime.now().year} Tickmarks. All rights reserved.</p>
                <p>This is an automated message from the TimeTracker system.</p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=manager_email,
            subject=f"Weekly Time Entries Pending Approval ({week_start} - {week_end})",
            html_content=html_content
        )

    async def send_approval_notification(
        self,
        employee_email: str,
        employee_name: str,
        entry_details: dict,
        status: str,
        rejection_reason: Optional[str] = None
    ) -> bool:
        """Send notification when time entry is approved or rejected."""
        
        status_color = "#10b981" if status == "APPROVED" else "#ef4444"
        status_text = "Approved" if status == "APPROVED" else "Rejected"
        
        rejection_html = ""
        if rejection_reason:
            rejection_html = f"""
            <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; border-radius: 4px;">
                <p style="margin: 0; color: #991b1b; font-weight: bold;">Rejection Reason:</p>
                <p style="margin: 5px 0 0 0; color: #7f1d1d;">{rejection_reason}</p>
            </div>
            """
        
        resubmit_info = ""
        if status == "REJECTED":
            resubmit_info = f"""
            <p style="font-size: 14px; color: #334155;">You can resubmit this time entry with corrected information from your timesheet page.</p>
            """
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Time Entry {status_text}</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {employee_name},</p>
                <p style="font-size: 16px; color: #334155;">Your time entry has been <strong style="color: {status_color};">{status_text.lower()}</strong>:</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <p style="margin: 5px 0; color: #64748b;"><strong>Project:</strong> {entry_details.get('project_name', 'N/A')}</p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Date:</strong> {entry_details.get('work_date', 'N/A')}</p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Hours:</strong> {entry_details.get('hours', 0)}</p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Notes:</strong> {entry_details.get('notes', 'None')}</p>
                </div>
                
                {rejection_html}
                {resubmit_info}
            </div>
            <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                <p>&copy; {datetime.now().year} Tickmarks. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=employee_email,
            subject=f"Time Entry {status_text} - Tickmarks TimeTracker",
            html_content=html_content
        )

    async def send_password_reset_email(self, email: str, name: str, token: str) -> bool:
        """Send password reset link."""
        reset_url = f"{self.frontend_url}/reset-password?token={token}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Password Reset Request</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {name},</p>
                <p style="font-size: 16px; color: #334155;">We received a request to reset your password. Click the button below to create a new password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Reset Password</a>
                </div>
                <p style="font-size: 14px; color: #64748b;">Or copy and paste this link into your browser:</p>
                <p style="font-size: 12px; color: #7c3aed; word-break: break-all;">{reset_url}</p>
                <p style="font-size: 14px; color: #64748b; margin-top: 30px;"><strong>Important:</strong> This link will expire in 24 hours. If you did not request a password reset, please ignore this email or contact support.</p>
            </div>
            <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                <p>&copy; {datetime.now().year} Tickmarks. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        Hello {name},
        
        We received a request to reset your password. Visit the link below:
        {reset_url}
        
        This link will expire in 24 hours.
        If you did not request this, please ignore this email.
        """
        
        return await self.send_email(
            to_email=email,
            subject="Reset Your Password - Tickmarks TimeTracker",
            html_content=html_content,
            text_content=text_content
        )

    async def send_password_changed_email(self, email: str, name: str, changed_by: Optional[str] = None) -> bool:
        """Send password changed notification."""
        if changed_by:
            message_text = f"An administrator ({changed_by}) has reset your password."
            additional_info = f"<p style=\"font-size: 14px; color: #64748b;\">Your password was reset by: <strong>{changed_by}</strong></p>"
        else:
            message_text = "Your password has been successfully changed."
            additional_info = ""
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Password Changed</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {name},</p>
                <p style="font-size: 16px; color: #334155;">{message_text}</p>
                {additional_info}
                <p style="font-size: 14px; color: #64748b; margin-top: 20px;">If you did not authorize this change or have any concerns, please contact the support team immediately.</p>
                <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin-top: 20px;">
                    <p style="font-size: 14px; color: #991b1b; margin: 0;"><strong>Security Tip:</strong> Never share your password with anyone. Our support staff will never ask for your password.</p>
                </div>
            </div>
            <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                <p>&copy; {datetime.now().year} Tickmarks. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=email,
            subject="Your Password Has Been Changed - Tickmarks TimeTracker",
            html_content=html_content
        )


    async def send_admin_welcome_email(self, email: str, name: str, temporary_password: str) -> bool:
        """Send welcome email to users created by an administrator."""
        login_url = f"{self.frontend_url}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Welcome to Tickmarks TimeTracker</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {name},</p>
                <p style="font-size: 16px; color: #334155;">An account has been created for you on the Tickmarks TimeTracker portal. You can now log in using the credentials below:</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
                    <p style="margin: 5px 0; color: #64748b;"><strong>Portal URL:</strong> <a href="{login_url}" style="color: #7c3aed;">{login_url}</a></p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Username:</strong> {email}</p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Temporary Password:</strong> <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{temporary_password}</code></p>
                </div>
                
                <p style="font-size: 14px; color: #64748b; margin-top: 20px;"><strong>Security Note:</strong> You will be prompted to verify your identity with an OTP and change this password upon your first login.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_url}" style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Log In Now</a>
                </div>
            </div>
            <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                <p>&copy; {datetime.now().year} Tickmarks. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Tickmarks TimeTracker
        
        Hello {name},
        
        An account has been created for you.
        Portal: {login_url}
        Username: {email}
        Temporary Password: {temporary_password}
        
        You will be required to change your password on your first login.
        """
        
        return await self.send_email(
            to_email=email,
            subject="Welcome to Tickmarks TimeTracker - Account Created",
            html_content=html_content,
            text_content=text_content
        )
    async def send_manager_onboarding_notification(self, manager_email: str, manager_name: str, employee_name: str) -> bool:
        """Alert a manager when a new employee is assigned to them."""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">New Employee Assigned</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {manager_name},</p>
                <p style="font-size: 16px; color: #334155;">This is to notify you that <strong>{employee_name}</strong> has been successfully onboarded and assigned to your team.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
                    <p style="margin: 5px 0; color: #64748b;"><strong>Employee Name:</strong> {employee_name}</p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Status:</strong> Active</p>
                </div>
                
                <p style="font-size: 14px; color: #64748b;">You can now manage their time entries and approvals via your dashboard.</p>
            </div>
            <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                <p>&copy; {datetime.now().year} Tickmarks. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        return await self.send_email(
            to_email=manager_email,
            subject=f"New Employee Assigned: {employee_name} - Tickmarks",
            html_content=html_content
        )

    async def send_timesheet_submission_notification(self, manager_email: str, manager_name: str, employee_name: str, project_name: str, total_hours: float) -> bool:
        """Alert the project manager when a timesheet is submitted."""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #0d9488 0%, #0891b2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Timesheet Submission</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {manager_name},</p>
                <p style="font-size: 16px; color: #334155;"><strong>{employee_name}</strong> has submitted a new timesheet entry for your project <strong>{project_name}</strong>.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
                    <p style="margin: 5px 0; color: #64748b;"><strong>Project:</strong> {project_name}</p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Hours:</strong> {total_hours}h</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{self.frontend_url}/approvals" style="background: #0d9488; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">Review Entry</a>
                </div>
            </div>
            <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                <p>&copy; {datetime.now().year} Tickmarks. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        return await self.send_email(
            to_email=manager_email,
            subject=f"New Timesheet Entry: {employee_name} - {project_name}",
            html_content=html_content
        )

    async def send_timesheet_status_notification(self, employee_email: str, employee_name: str, status: str, entry_id: int, hours: float, project_name: str) -> bool:
        """Notify employee about approval/rejection of their timesheet."""
        status_color = "#10b981" if status == "APPROVED" else "#ef4444"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: {status_color}; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Timesheet {status.capitalize()}</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {employee_name},</p>
                <p style="font-size: 16px; color: #334155;">Your timesheet entry for <strong>{project_name}</strong> has been <strong>{status.lower()}</strong>.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
                    <p style="margin: 5px 0; color: #64748b;"><strong>Entry ID:</strong> #{entry_id}</p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Project:</strong> {project_name}</p>
                    <p style="margin: 5px 0; color: #64748b;"><strong>Hours:</strong> {hours}h</p>
                    <p style="margin: 5px 0; color: {status_color}; font-weight: bold;"><strong>Status:</strong> {status}</p>
                </div>
                
                <p style="font-size: 14px; color: #64748b;">You can view the full details on your time tracking dashboard.</p>
            </div>
            <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                <p>&copy; {datetime.now().year} Tickmarks. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        return await self.send_email(
            to_email=employee_email,
            subject=f"Timesheet {status.capitalize()}: Entry #{entry_id}",
            html_content=html_content
        )

    async def send_verification_success_notification(self, email: str, name: str) -> bool:
        """Send notification after successful email verification."""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #7c3aed; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Account Verified!</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {name},</p>
                <p style="font-size: 16px; color: #334155;">Your email address has been successfully verified. Your account is now fully active.</p>
                <p style="font-size: 16px; color: #334155;">You can now log in to the portal and start tracking your time.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{self.frontend_url}" style="background: #7c3aed; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">Go to Login</a>
                </div>
            </div>
        </body>
        </html>
        """
        return await self.send_email(to_email=email, subject="Email Verified - Tickmarks TimeTracker", html_content=html_content)

    async def send_project_assignment_notification(self, employee_email: str, employee_name: str, project_name: str) -> bool:
        """Notify an employee when they are assigned to a project."""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #7c3aed; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Project Assignment</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {employee_name},</p>
                <p style="font-size: 16px; color: #334155;">You have been assigned to the project: <strong>{project_name}</strong>.</p>
                <p style="font-size: 16px; color: #334155;">You can now start logging time entries for this project in your timesheet dashboard.</p>
            </div>
        </body>
        </html>
        """
        return await self.send_email(to_email=employee_email, subject=f"Assigned to Project: {project_name}", html_content=html_content)

    async def send_project_removal_notification(self, employee_email: str, employee_name: str, project_name: str) -> bool:
        """Notify an employee when they are removed from a project."""
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #ef4444; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Project Role Update</h1>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px; color: #334155;">Hello {employee_name},</p>
                <p style="font-size: 16px; color: #334155;">This is to inform you that you have been removed from the project: <strong>{project_name}</strong>.</p>
                <p style="font-size: 16px; color: #334155;">If this was unexpected, please contact your project manager or administrator.</p>
            </div>
        </body>
        </html>
        """
        return await self.send_email(to_email=employee_email, subject=f"Removed from Project: {project_name}", html_content=html_content)

    async def send_support_feedback_email(self, name: str, email: str, category: str, message: str) -> bool:
        """Forward user support requests and feedback to admin."""
        support_email = "timesheetick@gmail.com"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #334155; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">New Support Request</h1>
                <p style="color: #94a3b8; margin-top: 10px;">Category: {category}</p>
            </div>
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e2e8f0;">
                <p style="font-size: 14px; color: #64748b; margin-bottom: 20px;">You have received a new message from the Tickmarks TimeTracker feedback form.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 5px 0;"><strong>From:</strong> {name}</p>
                    <p style="margin: 5px 0;"><strong>Email:</strong> {email}</p>
                    <p style="margin: 5px 0;"><strong>Category:</strong> {category}</p>
                </div>
                
                <div style="background: #f1f5f9; padding: 20px; border-radius: 8px; border-left: 4px solid #334155;">
                    <p style="margin: 0; color: #1e293b; white-space: pre-wrap;">{{message}}</p>
                </div>
                
                <p style="font-size: 12px; color: #94a3b8; margin-top: 30px; text-align: center;">
                    Submitted on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=support_email,
            subject=f"Tickmarks Support: [{category}] from {name}",
            html_content=html_content
        )

email_service = EmailService()



