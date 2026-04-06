from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    DATABASE_URL: str = ""
    ENVIRONMENT: str = "production"
    
    # JWT Settings
    JWT_SECRET_KEY: str = "7f3b89e2c1d4a0f6b8e2d4c1a0f6b8e2"
    ALGORITHM: str = "HS256"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    FRONTEND_URL: str = "https://hxf-timetracker-app.vercel.app"
    
    # SMTP (Gmail recommends 587 with STARTTLS)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "hexhytfvb <no-reply@hexhytfvb.com>"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"), 
        env_file_encoding="utf-8",
        case_sensitive=False, 
        extra="ignore"
    )

settings = Settings()

# Log configuration on startup
print("\n" + "=" * 50)
print("  hexhytfvb TimeTracker - Configuration Loader")
print("=" * 50)
print(f"  Environment  : {settings.ENVIRONMENT}")
print(f"  Database URL : {'✓ SET' if settings.DATABASE_URL else '✗ NOT SET (Critical)'}")
print(f"  Frontend URL : {settings.FRONTEND_URL}")
print(f"  SMTP Status  : {'✓ Configured' if settings.SMTP_USER and settings.SMTP_PASSWORD else '✗ Incomplete'}")
print("=" * 50 + "\n")
