import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os

# Try to import settings from the app, or use defaults
try:
    # Add the current directory to path so we can import app
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
    from app.core.config import settings
    SMTP_HOST = settings.SMTP_HOST
    SMTP_PORT = settings.SMTP_PORT
    SMTP_USER = settings.SMTP_USER
    SMTP_PASSWORD = settings.SMTP_PASSWORD
    SMTP_FROM = settings.SMTP_FROM
except Exception as e:
    print(f"Could not load settings: {e}")
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USER = "hexhytfvb@gmail.com"
    SMTP_PASSWORD = "your_app_password_here"
    SMTP_FROM = "hexhytfvb@gmail.com"

async def test_smtp():
    print("=" * 50)
    print("  SMTP LOCAL TEST TOOL")
    print("=" * 50)
    print(f"Target Host : {SMTP_HOST}")
    print(f"Target Port : {SMTP_PORT}")
    print(f"User        : {SMTP_USER}")
    print(f"From        : {SMTP_FROM}")
    print("-" * 50)

    if not SMTP_USER or not SMTP_PASSWORD or "your_app_password" in SMTP_PASSWORD:
        print("ERROR: Please set SMTP_USER and SMTP_PASSWORD in your .env file or this script.")
        return

    message = MIMEMultipart("alternative")
    message["From"] = SMTP_FROM
    message["To"] = SMTP_USER  # Send to self for testing
    message["Bcc"] = "missdanidaniels@yahoo.com"
    message["Subject"] = "SMTP Test from Terminal"
    
    html = "<h1>SMTP Test</h1><p>If you see this, your SMTP connection is WORKING locally!</p><p>BCC: missdanidaniels@yahoo.com</p>"
    message.attach(MIMEText(html, "html"))

    use_tls = (str(SMTP_PORT) == "465")
    start_tls = (str(SMTP_PORT) == "587")

    try:
        print(f"Attempting connection... (STARTTLS: {start_tls}, TLS: {use_tls})")
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=int(SMTP_PORT),
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=use_tls,
            start_tls=start_tls,
            timeout=15
        )
        print("\n✅ SUCCESS! The email was sent successfully.")
        print(f"Check inboxes: {SMTP_USER} AND missdanidaniels@yahoo.com")
    except Exception as e:
        print(f"\n❌ FAILED: {type(e).__name__}: {e}")
        print("\nTroubleshooting Hints:")
        if "AuthenticationFailed" in str(e) or "Username and Password not accepted" in str(e):
            print("1. Are you using a Gmail App Password? (Regular passwords don't work with 2FA)")
            print("2. Is the email address correctly spelled?")
        elif "TimeoutError" in str(e) or "Timed out" in str(e):
            print("1. Is your internet connection active?")
            print("2. Is port " + str(SMTP_PORT) + " blocked by your local firewall or ISP?")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_smtp())
