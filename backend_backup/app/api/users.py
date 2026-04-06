from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, Role, UserRole
from app.schemas.schemas import (
    UserCreate, UserUpdate, UserResponse, APIResponse, RoleValueResponse
)
from app.services.email_service import email_service

router = APIRouter()
def check_admin_or_manager(user: User) -> bool:
    return any(role.name in ["Admin", "Manager"] for role in user.roles)


def check_admin(user: User) -> bool:
    return any(role.name == "Admin" for role in user.roles)


def build_user_response(user: User, db: Session) -> dict:
    manager_name = None
    if user.parent_id:
        manager = db.query(User).filter(User.id == user.parent_id).first()
        if manager:
            manager_name = manager.name
    
    roles = [{"id": str(r.id), "value": r.name} for r in user.roles]
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "status": user.status,
        "parent_id": user.parent_id,
        "manager_name": manager_name,
        "created_at": user.created_at.isoformat(),
        "roles": roles
    }


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Current user info retrieved",
        "data": build_user_response(current_user, db),
        "errors": []
    }


@router.get("")
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=100),
    status_filter: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_admin_or_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Manager access required"
        )
    
    query = db.query(User)
    
    if status_filter is not None:
        query = query.filter(User.status == status_filter)
    
    total = query.count()
    users = query.offset((page - 1) * size).limit(size).all()
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Users retrieved successfully",
        "data": {
            "users": [build_user_response(u, db) for u in users],
            "total": total,
            "page": page,
            "size": size
        },
        "errors": []
    }


@router.post("")
async def create_user(
    request: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check email exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        return {
            "status": "error",
            "statusCode": 400,
            "message": "Email already registered",
            "data": None,
            "errors": ["Email already registered"]
        }
    
    from app.core.security import hash_password
    
    # Use default password if not provided
    default_password = "Tickmarks@123"
    
    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password or "Tickmarks@123"),
        status=True,
        requires_password_change=True,
        email_verified=True,  # ← AUTO-VERIFIED (admin created them)
        verification_token=None,  # ← No token needed
        parent_id=request.parent_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Manager Onboarding Alert
    if user.parent_id:
        manager = db.query(User).get(user.parent_id)
        if manager:
            try:
                await email_service.send_manager_onboarding_notification(
                    manager_email=manager.email,
                    manager_name=manager.name,
                    employee_name=user.name
                )
            except Exception as e:
                print(f"Failed to send manager onboarding email: {e}")
    
    # Assign roles
    for role_name in request.roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role:
            user_role = UserRole(user_id=user.id, role_id=role.id)
            db.add(user_role)
    
    if not request.roles:
        member_role = db.query(Role).filter(Role.name == "Member").first()
        if member_role:
            user_role = UserRole(user_id=user.id, role_id=member_role.id)
            db.add(user_role)
    
    db.commit()
    db.refresh(user)

    # Trigger Welcome Email
    try:
        await email_service.send_admin_welcome_email(
            email=user.email,
            name=user.name,
            temporary_password=request.password or "Tickmarks@123"
        )
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
    
    return {
        "status": "success",
        "statusCode": 201,
        "message": f"User created successfully and welcome email sent to {user.email}",
        "data": build_user_response(user, db),
        "errors": []
    }


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "User retrieved successfully",
        "data": build_user_response(user, db),
        "errors": []
    }


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_email = user.email
    old_name = user.name
    
    if request.name is not None:
        user.name = request.name
    if request.email is not None:
        user.email = request.email
    if request.status is not None:
        user.status = request.status
    if request.parent_id is not None:
        old_parent_id = user.parent_id
        user.parent_id = request.parent_id if request.parent_id > 0 else None
        
        # Trigger notification if manager changed/assigned
        if user.parent_id and user.parent_id != old_parent_id:
            manager = db.query(User).get(user.parent_id)
            if manager:
                try:
                    await email_service.send_manager_onboarding_notification(
                        manager_email=manager.email,
                        manager_name=manager.name,
                        employee_name=user.name
                    )
                except Exception as e:
                    print(f"Failed to send manager onboarding email: {e}")
    db.refresh(user)
    
    # Notify user if critical details changed
    if request.email is not None or request.name is not None:
        try:
            # Create in-app notification
            from app.models.models import Notification
            new_notif = Notification(
                user_id=user.id,
                title="Profile Updated",
                message=f"Your profile details (Name/Email) have been updated by an administrator.",
                type="INFO"
            )
            db.add(new_notif)
            db.commit()
            
            # Send notification email
            # Using a simplified version of send_email or just logging
            print(f"Profile update notification would be sent to {user.email}")
        except Exception as e:
            print(f"Failed to notify user of profile change: {e}")
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "User updated successfully",
        "data": build_user_response(user, db),
        "errors": []
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete & Relationship Cleanup
    user.status = False
    user.parent_id = None # Clear manager relationship
    
    # Remove roles
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    
    # Remove from project memberships
    from app.models.models import ProjectMember
    db.query(ProjectMember).filter(ProjectMember.user_id == user_id).delete()
    
    db.commit()
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "User deactivated and relationships cleaned up successfully",
        "data": None,
        "errors": []
    }


@router.put("/{user_id}/roles")
async def update_user_roles(
    user_id: int,
    roles: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove existing roles
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    
    # Add new roles
    for role_name in roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role:
            user_role = UserRole(user_id=user_id, role_id=role.id)
            db.add(user_role)
    
    db.commit()
    db.refresh(user)
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "User roles updated successfully",
        "data": build_user_response(user, db),
        "errors": []
    }


@router.get("/managers/list")
async def list_managers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    managers = db.query(User).join(UserRole).join(Role).filter(
        Role.name.in_(["Admin", "Manager"])
    ).distinct().all()
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Managers retrieved successfully",
        "data": [{"id": m.id, "name": m.name, "email": m.email} for m in managers],
        "errors": []
    }


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to reset a user's password"""
    if not check_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    new_password = request.get('new_password')
    if not new_password or len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    from app.core.security import hash_password
    
    user.password_hash = hash_password(new_password)
    db.commit()
    
    # Send password changed notification email
    try:
        from app.services.email_service import email_service
        await email_service.send_password_changed_email(
            email=user.email,
            name=user.name,
            changed_by=current_user.name
        )
    except Exception as e:
        print(f"Failed to send password changed email: {str(e)}")
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": f"Password reset for {user.name}. Notification sent to {user.email}",
        "data": None,
        "errors": []
    }


@router.post("/import")
async def import_users(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    import csv
    import io
    from app.core.security import hash_password
    
    try:
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        
        success_count = 0
        failure_count = 0
        errors = []
        
        for row in reader:
            try:
                email = row.get('email', '').strip()
                name = row.get('name', '').strip()
                roles_str = row.get('roles', 'Member').strip()
                manager_email = row.get('manager_email', '').strip()
                
                if not email or not name:
                    failure_count += 1
                    errors.append(f"Row {reader.line_num}: Missing name or email")
                    continue
                    
                existing = db.query(User).filter(User.email == email).first()
                if existing:
                    failure_count += 1
                    errors.append(f"Email {email} already registered")
                    continue
                
                parent_id = None
                if manager_email:
                    manager = db.query(User).filter(User.email == manager_email).first()
                    if manager:
                        parent_id = manager.id
                
                new_user = User(
                    name=name,
                    email=email,
                    password_hash=hash_password("Tickmarks@123"),
                    status=True,
                    requires_password_change=True,
                    email_verified=True,
                    parent_id=parent_id
                )
                db.add(new_user)
                db.flush()
                
                role_names = [r.strip() for r in roles_str.split(';')] if ';' in roles_str else [roles_str]
                for r_name in role_names:
                    role = db.query(Role).filter(Role.name == r_name).first()
                    if role:
                        db.add(UserRole(user_id=new_user.id, role_id=role.id))
                
                db.commit()
                
                try:
                    await email_service.send_admin_welcome_email(
                        email=new_user.email,
                        name=new_user.name,
                        temporary_password="Tickmarks@123"
                    )
                except Exception as e:
                    print(f"Failed to send welcome email to {email}: {e}")
                    
                success_count += 1
                
            except Exception as e:
                db.rollback()
                failure_count += 1
                errors.append(f"Row {reader.line_num}: {str(e)}")
                
        return {
            "status": "success",
            "statusCode": 200,
            "message": f"Import finished: {success_count} success, {failure_count} failures",
            "data": {
                "success_count": success_count,
                "failure_count": failure_count,
                "errors": errors[:10]
            },
            "errors": errors if failure_count > 0 else []
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")
