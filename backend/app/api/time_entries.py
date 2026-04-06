from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, Project, ProjectMember, TimeEntry, Notification
from app.schemas.schemas import (
    TimeEntryCreate, TimeEntryUpdate, TimeEntryApproval, TimeEntryResubmit
)
from app.services.email_service import email_service

router = APIRouter()
def check_admin(user: User) -> bool:
    return any(role.name == "Admin" for role in user.roles)


def check_manager(user: User) -> bool:
    return any(role.name == "Manager" for role in user.roles)


def build_entry_response(entry: TimeEntry, db: Session) -> dict:
    user = db.query(User).filter(User.id == entry.user_id).first()
    project = db.query(Project).filter(Project.id == entry.project_id).first()
    approver = None
    if entry.approved_by_id:
        approver = db.query(User).filter(User.id == entry.approved_by_id).first()
    
    return {
        "id": entry.id,
        "user_id": entry.user_id,
        "user_name": user.name if user else "Unknown",
        "project_id": entry.project_id,
        "project_name": project.name if project else "Unknown",
        "work_date": entry.work_date.isoformat(),
        "hours": float(entry.hours),
        "notes": entry.notes,
        "status": entry.status,
        "approved_by_id": entry.approved_by_id,
        "approved_by_name": approver.name if approver else None,
        "approval_date": entry.approval_date.isoformat() if entry.approval_date else None,
        "rejection_reason": entry.rejection_reason,
        "resubmission_notes": entry.resubmission_notes,
        "created_at": entry.created_at.isoformat()
    }


@router.get("")
async def list_time_entries(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    project_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(TimeEntry)
    
    # Non-admin users can only see their own entries (or managers can see their team)
    if not check_admin(current_user):
        if check_manager(current_user):
            # Managers can see entries of their team members
            team_member_ids = db.query(User.id).filter(User.parent_id == current_user.id).all()
            team_member_ids = [m[0] for m in team_member_ids]
            if team_member_ids:
                query = query.filter(TimeEntry.user_id.in_(team_member_ids))
            else:
                # If no team members, show nothing
                query = query.filter(TimeEntry.user_id == -1)
        else:
            # Regular employees see only their own
            query = query.filter(TimeEntry.user_id == current_user.id)
    
    if start_date:
        query = query.filter(TimeEntry.work_date >= start_date)
    if end_date:
        query = query.filter(TimeEntry.work_date <= end_date)
    if project_id:
        query = query.filter(TimeEntry.project_id == project_id)
    if status_filter:
        query = query.filter(TimeEntry.status == status_filter)
    
    total = query.count()
    entries = query.order_by(TimeEntry.work_date.desc()).offset(
        (page - 1) * size
    ).limit(size).all()
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Time entries retrieved successfully",
        "data": {
            "entries": [build_entry_response(e, db) for e in entries],
            "total": total,
            "page": page,
            "size": size
        },
        "errors": []
    }


@router.post("")
async def create_time_entry(
    request: TimeEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user is member of the project
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == request.project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member and not check_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this project"
        )
    
    # Check for duplicate entry
    existing = db.query(TimeEntry).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.project_id == request.project_id,
        TimeEntry.work_date == request.work_date
    ).first()
    
    if existing:
        return {
            "status": "error",
            "statusCode": 400,
            "message": "Time entry already exists for this date and project",
            "data": None,
            "errors": ["Duplicate entry"]
        }
    
    entry = TimeEntry(
        user_id=current_user.id,
        project_id=request.project_id,
        work_date=request.work_date,
        hours=request.hours,
        notes=request.notes,
        status="PENDING"
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Project Manager Submission Alert
    project = db.query(Project).get(entry.project_id)
    if project and project.manager_id:
        pm = db.query(User).get(project.manager_id)
        if pm:
            try:
                await email_service.send_timesheet_submission_notification(
                    manager_email=pm.email,
                    manager_name=pm.name,
                    employee_name=current_user.name,
                    project_name=project.name,
                    total_hours=float(entry.hours)
                )
            except Exception as e:
                print(f"Failed to send submission email: {e}")
    
    return {
        "status": "success",
        "statusCode": 201,
        "message": "Time entry created successfully",
        "data": build_entry_response(entry, db),
        "errors": []
    }


@router.get("/{entry_id}")
async def get_time_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    # Check access
    if entry.user_id != current_user.id and not check_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Time entry retrieved successfully",
        "data": build_entry_response(entry, db),
        "errors": []
    }


@router.put("/{entry_id}")
async def update_time_entry(
    entry_id: int,
    request: TimeEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Time entry not found"
            )
        
        # Only owner can update
        if entry.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Allow updating PENDING entries and REJECTED entries (for resubmission)
        if entry.status not in ["PENDING", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify approved entries. Only pending or rejected entries can be edited."
            )
        
        # If updating a rejected entry, prepare for resubmission
        is_resubmitting = entry.status == "REJECTED"
        
        # Validate hours if provided
        if request.hours is not None:
            try:
                hours_decimal = request.hours if isinstance(request.hours, type(1.0)) or hasattr(request.hours, '__float__') else float(request.hours)
                if hours_decimal < 0 or hours_decimal > 24:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Hours must be between 0 and 24"
                    )
            except (ValueError, TypeError) as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid hours value: {str(e)}"
                )
        
        if request.project_id is not None:
            # Verify project exists
            project = db.query(Project).filter(Project.id == request.project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid project ID"
                )
            entry.project_id = request.project_id
        
        if request.work_date is not None:
            entry.work_date = request.work_date
        if request.hours is not None:
            entry.hours = request.hours
        if request.notes is not None:
            entry.notes = request.notes
        
        # If this is a resubmission, reset status to PENDING
        if is_resubmitting:
            entry.status = "PENDING"
            entry.rejection_reason = None
            entry.approved_by_id = None
            entry.approval_date = None
        
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        return {
            "status": "success",
            "statusCode": 200,
            "message": "Time entry updated successfully",
            "data": build_entry_response(entry, db),
            "errors": []
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating time entry: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating time entry: {str(e)}"
        )
@router.delete("/{entry_id}")
async def delete_time_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    if entry.user_id != current_user.id and not check_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if entry.status == "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete approved entries"
        )
    
    db.delete(entry)
    db.commit()
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Time entry deleted successfully",
        "data": None,
        "errors": []
    }


@router.post("/{entry_id}/approve")
async def approve_time_entry(
    entry_id: int,
    request: TimeEntryApproval,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    # Get project to check if user is manager
    project = db.query(Project).filter(Project.id == entry.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user can approve (admin or project manager)
    if not check_admin(current_user) and project.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or project manager can approve entries"
        )
    
    if entry.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entry is not pending approval"
        )
    
    if request.status == "APPROVED":
        entry.status = "APPROVED"
        entry.approved_by_id = current_user.id
        entry.approval_date = datetime.utcnow()
    elif request.status == "REJECTED":
        entry.status = "REJECTED"
        entry.rejection_reason = request.rejection_reason
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
    
    db.commit()
    db.refresh(entry)

    # Employee Status Notification
    employee = db.query(User).get(entry.user_id)
    if employee:
        try:
            await email_service.send_timesheet_status_notification(
                employee_email=employee.email,
                employee_name=employee.name,
                status=entry.status,
                entry_id=entry.id,
                hours=float(entry.hours),
                project_name=project.name
            )
        except Exception as e:
            print(f"Failed to send status notification email: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be APPROVED or REJECTED"
        )
    
    db.commit()
    db.refresh(entry)
    
    # Send notification email and create in-app notification
    user = db.query(User).filter(User.id == entry.user_id).first()
    if user:
        # Create In-App Notification
        notification_title = "Time Entry Approved" if entry.status == "APPROVED" else "Time Entry Rejected"
        notification_message = f"Your time entry for {entry.work_date} has been {entry.status.lower()}."
        if entry.rejection_reason:
            notification_message += f" Reason: {entry.rejection_reason}"
            
        new_notification = Notification(
            user_id=user.id,
            title=notification_title,
            message=notification_message,
            type=entry.status,
            link=f"/timesheets"
        )
        db.add(new_notification)
        db.commit()

        # Send Email
        await email_service.send_approval_notification(
            employee_email=user.email,
            employee_name=user.name,
            entry_details=build_entry_response(entry, db),
            status=entry.status,
            rejection_reason=entry.rejection_reason
        )
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": f"Time entry {entry.status.lower()}",
        "data": build_entry_response(entry, db),
        "errors": []
    }


@router.post("/{entry_id}/resubmit")
async def resubmit_time_entry(
    entry_id: int,
    request: TimeEntryResubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )
    
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if entry.status != "REJECTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only rejected entries can be resubmitted"
        )
    
    entry.status = "PENDING"
    entry.rejection_reason = None
    entry.approved_by_id = None
    entry.approval_date = None
    
    if request.hours is not None:
        entry.hours = request.hours
    if request.notes is not None:
        entry.notes = request.notes
    if request.resubmission_notes is not None:
        entry.resubmission_notes = request.resubmission_notes
    
    db.commit()
    db.refresh(entry)
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Time entry resubmitted successfully",
        "data": build_entry_response(entry, db),
        "errors": []
    }


@router.get("/pending/approvals")
async def get_pending_approvals(
    status: str = Query("PENDING"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get entries based on status for projects managed by current user."""
    if not check_admin(current_user) and not check_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    
    # Get projects where user is manager
    managed_projects = db.query(Project).filter(
        Project.manager_id == current_user.id
    ).all()
    
    project_ids = [p.id for p in managed_projects]
    
    # Filter by status (unless 'ALL' is requested)
    status_filter = [status] if status != "ALL" else ["PENDING", "APPROVED", "REJECTED"]
    
    if check_admin(current_user):
        # Admin can see all entries matching status
        entries = db.query(TimeEntry).filter(
            TimeEntry.status.in_(status_filter)
        ).all()
    else:
        # Manager can only see entries for their projects matching status
        entries = db.query(TimeEntry).filter(
            TimeEntry.status.in_(status_filter),
            TimeEntry.project_id.in_(project_ids)
        ).all()
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Pending approvals retrieved successfully",
        "data": [build_entry_response(e, db) for e in entries],
        "errors": []
    }






