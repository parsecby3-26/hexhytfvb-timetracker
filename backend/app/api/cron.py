from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.models import User, Project, TimeEntry
from app.services.email_service import email_service
import os

router = APIRouter()

# Simple secret to prevent unauthorized execution from the public internet
CRON_SECRET = os.getenv("CRON_SECRET", "super-secret-cron-key-12345")

@router.post("/weekly-reminders")
async def send_weekly_reminders(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if authorization != f"Bearer {CRON_SECRET}":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid cron secret")
    
    # Query all users who manage projects that contain pending timesheets
    pending_entries = db.query(
        Project.manager_id, 
        func.count(TimeEntry.id).label('pending_count')
    ).join(
        TimeEntry, Project.id == TimeEntry.project_id
    ).filter(
        TimeEntry.status == 'PENDING'
    ).group_by(
        Project.manager_id
    ).all()
    
    results = []
    
    for manager_id, count in pending_entries:
        manager = db.query(User).filter(User.id == manager_id).first()
        if manager and manager.status:
            try:
                await email_service.send_weekly_reminder_email(
                    email=manager.email,
                    name=manager.name,
                    pending_count=count
                )
                results.append({"manager": manager.email, "count": count, "status": "sent"})
            except Exception as e:
                results.append({"manager": manager.email, "count": count, "status": "failed", "error": str(e)})
                
    return {
        "status": "success",
        "message": f"Processed {len(pending_entries)} manager reminders",
        "details": results
    }
