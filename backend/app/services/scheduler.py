from datetime import datetime, timedelta, date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import User, Project, TimeEntry
from app.services.email_service import email_service

scheduler = AsyncIOScheduler()


def get_week_date_range():
    """Get the start and end dates of the current week."""
    today = date.today()
    start = today - timedelta(days=today.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday
    return start, end


async def send_weekly_manager_reports():
    """Send weekly pending time entries report to all project managers."""
    db = SessionLocal()
    try:
        week_start, week_end = get_week_date_range()
        
        # Get all active projects with managers
        projects = db.query(Project).filter(Project.status == True).all()
        
        # Group entries by manager
        manager_entries = {}
        
        for project in projects:
            # Get pending entries for this project in the current week
            entries = db.query(TimeEntry).filter(
                TimeEntry.project_id == project.id,
                TimeEntry.status == "PENDING",
                TimeEntry.work_date >= week_start,
                TimeEntry.work_date <= week_end
            ).all()
            
            for entry in entries:
                user = db.query(User).filter(User.id == entry.user_id).first()
                
                entry_data = {
                    "user_name": user.name if user else "Unknown",
                    "project_name": project.name,
                    "work_date": entry.work_date.isoformat(),
                    "hours": float(entry.hours),
                    "notes": entry.notes or ""
                }
                
                if project.manager_id not in manager_entries:
                    manager = db.query(User).filter(User.id == project.manager_id).first()
                    manager_entries[project.manager_id] = {
                        "manager_email": manager.email if manager else "",
                        "manager_name": manager.name if manager else "",
                        "entries": []
                    }
                
                manager_entries[project.manager_id]["entries"].append(entry_data)
        
        # Send emails to each manager
        for manager_id, data in manager_entries.items():
            if data["manager_email"] and data["entries"]:
                await email_service.send_weekly_report(
                    manager_email=data["manager_email"],
                    manager_name=data["manager_name"],
                    pending_entries=data["entries"],
                    week_start=week_start.strftime("%Y-%m-%d"),
                    week_end=week_end.strftime("%Y-%m-%d")
                )
                
    finally:
        db.close()


def start_scheduler():
    """Start the APScheduler for scheduled tasks."""
    # Schedule weekly report every Sunday at 9 AM
    scheduler.add_job(
        send_weekly_manager_reports,
        CronTrigger(day_of_week="sun", hour=9, minute=0),
        id="weekly_manager_report",
        replace_existing=True
    )
    
    scheduler.start()
    print("Scheduler started. Weekly reports will be sent on Sundays at 9 AM.")


def stop_scheduler():
    """Stop the scheduler."""
    scheduler.shutdown()



