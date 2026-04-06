from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, Project, ProjectMember, TimeEntry
from decimal import Decimal

router = APIRouter()
def check_admin(user: User) -> bool:
    return any(role.name == "Admin" for role in user.roles)


def check_manager(user: User) -> bool:
    return any(role.name == "Manager" for role in user.roles)


@router.get("/summary")
async def get_report_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    project_id: Optional[int] = None,
    user_id: Optional[int] = None,
    reporting_area: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate time entry summary report."""
    
    # Default to current month if no dates provided
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    query = db.query(TimeEntry).filter(
        TimeEntry.work_date >= start_date,
        TimeEntry.work_date <= end_date,
        TimeEntry.status == "APPROVED"
    )
    
    # Handle access control
    is_admin = check_admin(current_user)
    is_manager = check_manager(current_user)
    
    if is_admin:
        # Admin can see all entries
        pass
    elif is_manager:
        # Manager can see entries of their team members
        team_member_ids = db.query(User.id).filter(User.parent_id == current_user.id).all()
        team_member_ids = [m[0] for m in team_member_ids]
        if team_member_ids:
            query = query.filter(TimeEntry.user_id.in_(team_member_ids))
        else:
            # If no team members, show nothing
            query = query.filter(TimeEntry.user_id == -1)
    else:
        # Regular users see only their own entries
        query = query.filter(TimeEntry.user_id == current_user.id)
    
    if project_id:
        query = query.filter(TimeEntry.project_id == project_id)
    if user_id and is_admin:
        query = query.filter(TimeEntry.user_id == user_id)
    
    entries = query.all()
    
    # Group by project
    project_summary = {}
    for entry in entries:
        if entry.project_id not in project_summary:
            project = db.query(Project).filter(Project.id == entry.project_id).first()
            project_summary[entry.project_id] = {
                "project_id": entry.project_id,
                "project_name": project.name if project else "Unknown",
                "client": project.client if project else "Unknown",
                "reporting_area": project.reporting_area if project else None,
                "total_hours": Decimal(0),
                "user_hours": {}
            }
        
        project_summary[entry.project_id]["total_hours"] += entry.hours
        
        if entry.user_id not in project_summary[entry.project_id]["user_hours"]:
            user = db.query(User).filter(User.id == entry.user_id).first()
            project_summary[entry.project_id]["user_hours"][entry.user_id] = {
                "user_id": entry.user_id,
                "user_name": user.name if user else "Unknown",
                "hours": Decimal(0)
            }
        
        project_summary[entry.project_id]["user_hours"][entry.user_id]["hours"] += entry.hours
    
    # Convert user_hours to list
    result = []
    for pid, pdata in project_summary.items():
        if reporting_area and pdata["reporting_area"] != reporting_area:
            continue
        result.append({
            **pdata,
            "user_hours": list(pdata["user_hours"].values())
        })
    
    # Calculate totals
    total_hours = sum(float(p["total_hours"]) for p in result)
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Report generated successfully",
        "data": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_hours": total_hours,
            "total_projects": len(result),
            "project_summary": result
        },
        "errors": []
    }


@router.get("/daily")
async def get_daily_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily time entry breakdown."""
    
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    query = db.query(TimeEntry).filter(
        TimeEntry.work_date >= start_date,
        TimeEntry.work_date <= end_date
    )
    
    # Handle access control
    is_admin = check_admin(current_user)
    is_manager = check_manager(current_user)
    
    if is_admin:
        # Admin can see all entries
        pass
    elif is_manager:
        # Manager can see entries of their team members
        team_member_ids = db.query(User.id).filter(User.parent_id == current_user.id).all()
        team_member_ids = [m[0] for m in team_member_ids]
        if team_member_ids:
            query = query.filter(TimeEntry.user_id.in_(team_member_ids))
        else:
            # If no team members, show nothing
            query = query.filter(TimeEntry.user_id == -1)
    else:
        # Regular users see only their own entries
        query = query.filter(TimeEntry.user_id == current_user.id)
    
    entries = query.order_by(TimeEntry.work_date).all()
    
    # Group by date
    daily_summary = {}
    for entry in entries:
        date_str = entry.work_date.isoformat()
        if date_str not in daily_summary:
            daily_summary[date_str] = {
                "date": date_str,
                "total_hours": Decimal(0),
                "entries": []
            }
        
        daily_summary[date_str]["total_hours"] += entry.hours
        
        user = db.query(User).filter(User.id == entry.user_id).first()
        project = db.query(Project).filter(Project.id == entry.project_id).first()
        approver = db.query(User).filter(User.id == entry.approved_by_id).first() if entry.approved_by_id else None
        
        daily_summary[date_str]["entries"].append({
            "id": entry.id,
            "user_name": user.name if user else "Unknown",
            "project_name": project.name if project else "Unknown",
            "hours": float(entry.hours),
            "status": entry.status,
            "notes": entry.notes,
            "approved_by_name": approver.name if approver else None
        })
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Daily report generated successfully",
        "data": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily_summary": list(daily_summary.values())
        },
        "errors": []
    }


@router.get("/by-reporting-area")
async def get_report_by_area(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get time entries grouped by reporting area."""
    
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    # Get all projects with their reporting areas
    projects = db.query(Project).all()
    project_areas = {p.id: p.reporting_area for p in projects}
    
    query = db.query(TimeEntry).filter(
        TimeEntry.work_date >= start_date,
        TimeEntry.work_date <= end_date,
        TimeEntry.status == "APPROVED"
    )
    
    # Handle access control
    is_admin = check_admin(current_user)
    is_manager = check_manager(current_user)
    
    if is_admin:
        # Admin can see all entries
        pass
    elif is_manager:
        # Manager can see entries of their team members
        team_member_ids = db.query(User.id).filter(User.parent_id == current_user.id).all()
        team_member_ids = [m[0] for m in team_member_ids]
        if team_member_ids:
            query = query.filter(TimeEntry.user_id.in_(team_member_ids))
        else:
            # If no team members, show nothing
            query = query.filter(TimeEntry.user_id == -1)
    else:
        # Regular users see only their own entries
        query = query.filter(TimeEntry.user_id == current_user.id)
    
    entries = query.all()
    
    # Group by reporting area
    area_summary = {}
    for entry in entries:
        area = project_areas.get(entry.project_id, "Other")
        if area is None:
            area = "Other"
        
        if area not in area_summary:
            area_summary[area] = {
                "reporting_area": area,
                "total_hours": Decimal(0),
                "projects": {}
            }
        
        area_summary[area]["total_hours"] += entry.hours
        
        if entry.project_id not in area_summary[area]["projects"]:
            project = db.query(Project).filter(Project.id == entry.project_id).first()
            area_summary[area]["projects"][entry.project_id] = {
                "project_id": entry.project_id,
                "project_name": project.name if project else "Unknown",
                "hours": Decimal(0)
            }
        
        area_summary[area]["projects"][entry.project_id]["hours"] += entry.hours
    
    # Convert projects to list
    result = []
    for area, data in area_summary.items():
        result.append({
            **data,
            "projects": list(data["projects"].values())
        })
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Report by area generated successfully",
        "data": result,
        "errors": []
    }


@router.get("/user/{user_id}")
async def get_user_report(
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed report for a specific user."""
    
    # Users can only see their own reports unless admin
    if user_id != current_user.id and not check_admin(current_user):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    entries = db.query(TimeEntry).filter(
        TimeEntry.user_id == user_id,
        TimeEntry.work_date >= start_date,
        TimeEntry.work_date <= end_date
    ).all()
    
    total_hours = sum(float(e.hours) for e in entries)
    approved_hours = sum(float(e.hours) for e in entries if e.status == "APPROVED")
    pending_hours = sum(float(e.hours) for e in entries if e.status == "PENDING")
    rejected_hours = sum(float(e.hours) for e in entries if e.status == "REJECTED")
    
    # Group by project
    project_hours = {}
    for entry in entries:
        if entry.project_id not in project_hours:
            project = db.query(Project).filter(Project.id == entry.project_id).first()
            project_hours[entry.project_id] = {
                "project_id": entry.project_id,
                "project_name": project.name if project else "Unknown",
                "client": project.client if project else "Unknown",
                "hours": Decimal(0)
            }
        project_hours[entry.project_id]["hours"] += entry.hours
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "User report generated successfully",
        "data": {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            },
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_hours": total_hours,
            "approved_hours": approved_hours,
            "pending_hours": pending_hours,
            "rejected_hours": rejected_hours,
            "project_breakdown": list(project_hours.values())
        },
        "errors": []
    }






