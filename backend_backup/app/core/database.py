from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Initialize database connection safely
engine = None
SessionLocal = None

try:
    if settings.DATABASE_URL:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.ENVIRONMENT == "development"
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print("✓ Database engine initialized")
    else:
        print("⚠ DATABASE_URL not configured - API will run but database features unavailable")
except Exception as e:
    print(f"✗ Database initialization error: {str(e)}")
    print("  API will still start but database operations will fail")

Base = declarative_base()


def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not configured. Set DATABASE_URL environment variable.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



