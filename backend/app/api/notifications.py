from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, Notification
from app.schemas.schemas import NotificationResponse, NotificationSummary, APIResponse

router = APIRouter()

@router.get("", response_model=APIResponse)
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all notifications for the current user."""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    # Process return
    data = {
        "notifications": [
            {
                "id": n.id,
                "user_id": n.user_id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "is_read": n.is_read,
                "link": n.link,
                "created_at": n.created_at
            } for n in notifications
        ],
        "unread_count": unread_count
    }
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Notifications retrieved",
        "data": data,
        "errors": []
    }

@router.patch("/{notification_id}/read", response_model=APIResponse)
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Notification marked as read",
        "data": None,
        "errors": []
    }

@router.post("/read-all", response_model=APIResponse)
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current user."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "All notifications marked as read",
        "data": None,
        "errors": []
    }
