# Version: 1.0.1-stabilized
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api import auth, users, projects, time_entries, reports, cron, notifications, support
from app.core.database import engine, Base

app = FastAPI(title="hexhytfvb TimeTracker API")

# CORS configuration - specific origins to prevent browser blocking
origins = [
    "https://timesheetick.vercel.app",
    "https://ticksheet-app.netlify.app",
    "http://localhost:3000",
    "http://localhost:3005",
    "http://localhost:8000",
    "https://hexhytfvb-timesheet.vercel.app",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Custom handler to force 422 errors into your specific format
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "statusCode": 422,
            "message": "Validation Error",
            "data": None,
            "errors": exc.errors()
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    # Log the full error for debugging
    import traceback
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "statusCode": 500,
            "message": "An unexpected internal error occurred",
            "data": None,
            "errors": [str(exc)]
        },
    )

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(time_entries.router, prefix="/api/time-entries", tags=["Time Entries"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(cron.router, prefix="/api/cron", tags=["Cron Jobs"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(support.router, prefix="/api/support", tags=["Support"])
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup (non-blocking)"""
    try:
        if engine:
            # Create all tables defined in models
            Base.metadata.create_all(bind=engine)
            print("✓ Database tables initialized")
            
            # Ensure critical columns exist (for migrations)
            from sqlalchemy import text, inspect
            
            with engine.begin() as connection:
                # Check if columns exist before adding them
                inspector = inspect(engine)
                columns = [col['name'] for col in inspector.get_columns('users')]
                
                if 'password_reset_token' not in columns:
                    try:
                        connection.execute(text(
                            "ALTER TABLE users ADD COLUMN password_reset_token VARCHAR(255)"
                        ))
                        print("✓ Added password_reset_token column")
                    except Exception as e:
                        print(f"⚠ password_reset_token column: {str(e)}")
                
                if 'password_reset_token_expires' not in columns:
                    try:
                        connection.execute(text(
                            "ALTER TABLE users ADD COLUMN password_reset_token_expires TIMESTAMP"
                        ))
                        print("✓ Added password_reset_token_expires column")
                    except Exception as e:
                        print(f"⚠ password_reset_token_expires column: {str(e)}")

                if 'requires_password_change' not in columns:
                    try:
                        connection.execute(text(
                            "ALTER TABLE users ADD COLUMN requires_password_change BOOLEAN NOT NULL DEFAULT FALSE"
                        ))
                        print("✓ Added requires_password_change column")
                    except Exception as e:
                        print(f"⚠ requires_password_change column: {str(e)}")

                if 'otp_code' not in columns:
                    try:
                        connection.execute(text(
                            "ALTER TABLE users ADD COLUMN otp_code VARCHAR(6)"
                        ))
                        print("✓ Added otp_code column")
                    except Exception as e:
                        print(f"⚠ otp_code column: {str(e)}")

                if 'otp_expires_at' not in columns:
                    try:
                        connection.execute(text(
                            "ALTER TABLE users ADD COLUMN otp_expires_at TIMESTAMP"
                        ))
                        print("✓ Added otp_expires_at column")
                    except Exception as e:
                        print(f"⚠ otp_expires_at column: {str(e)}")

                # Check for notifications table
                try:
                    result = connection.execute(text(
                        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'notifications')"
                    ))
                    exists = result.scalar()
                    if not exists:
                        print("Creating notifications table...")
                        connection.execute(text("""
                            CREATE TABLE notifications (
                                id BIGSERIAL PRIMARY KEY,
                                user_id BIGINT REFERENCES users(id),
                                title VARCHAR(255) NOT NULL,
                                message TEXT NOT NULL,
                                type VARCHAR(50),
                                is_read BOOLEAN DEFAULT FALSE,
                                link VARCHAR(255),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """))
                        print("✓ Notifications table created")
                except Exception as e:
                    print(f"⚠ Notifications table check/create: {str(e)}")
        else:
            print("⚠ Skipping database initialization - engine not available")
    except Exception as e:
        print(f"✗ Database initialization error during startup: {str(e)}")
        # Don't crash the app, just log the error
        import traceback
        traceback.print_exc()

@app.get("/")
def read_root():
    return {"status": "online", "message": "hexhytfvb TimeTracker API"}

# Health check endpoint
@app.get("/health")
def health_check():
    from app.core.database import engine
    db_status = "healthy" if engine else "not_configured"
    return {
        "status": "healthy",
        "message": "API is running",
        "database": db_status
    }

@app.get("/api/ping")
def ping():
    return {"status": "success", "message": "pong"}

