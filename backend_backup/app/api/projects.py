from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, Role, Project, ProjectMember, TimeEntry
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectMemberAdd
from app.services.email_service import email_service

router = APIRouter()
def check_admin(user: User) -> bool:
    return any(role.name == "Admin" for role in user.roles)


def check_manager(user: User) -> bool:
    return any(role.name == "Manager" for role in user.roles)


def check_admin_or_manager(user: User) -> bool:
    return any(role.name in ["Admin", "Manager"] for role in user.roles)


def build_project_response(project: Project, db: Session) -> dict:
    manager_name = None
    if project.manager_id:
        manager = db.query(User).filter(User.id == project.manager_id).first()
        if manager:
            manager_name = manager.name
    
    return {
        "id": project.id,
        "name": project.name,
        "client": project.client,
        "status": project.status,
        "manager_id": project.manager_id,
        "manager_name": manager_name,
        "reporting_area": project.reporting_area,
        "created_at": project.created_at.isoformat()
    }


@router.get("")
async def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=100),
    status_filter: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Project)
    
    # Non-admin users can only see projects they're assigned to
    if not check_admin_or_manager(current_user):
        query = query.join(ProjectMember).filter(
            ProjectMember.user_id == current_user.id
        )
    
    if status_filter is not None:
        query = query.filter(Project.status == status_filter)
    
    total = query.count()
    projects = query.offset((page - 1) * size).limit(size).all()
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Projects retrieved successfully",
        "data": {
            "projects": [build_project_response(p, db) for p in projects],
            "total": total,
            "page": page,
            "size": size
        },
        "errors": []
    }


@router.post("")
async def create_project(
    request: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_admin_or_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Manager access required"
        )
    
    project = Project(
        name=request.name,
        client=request.client,
        manager_id=request.manager_id,
        reporting_area=request.reporting_area
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Add manager as project member
    member = ProjectMember(
        project_id=project.id,
        user_id=request.manager_id
    )
    db.add(member)
    db.commit()
    
    return {
        "status": "success",
        "statusCode": 201,
        "message": "Project created successfully",
        "data": build_project_response(project, db),
        "errors": []
    }


@router.get("/{project_id}")
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check access
    if not check_admin_or_manager(current_user):
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Project retrieved successfully",
        "data": build_project_response(project, db),
        "errors": []
    }


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    request: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_admin_or_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Manager access required"
        )
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if request.name is not None:
        project.name = request.name
    if request.client is not None:
        project.client = request.client
    if request.status is not None:
        project.status = request.status
    if request.manager_id is not None:
        project.manager_id = request.manager_id
    if request.reporting_area is not None:
        project.reporting_area = request.reporting_area
    
    db.commit()
    db.refresh(project)
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Project updated successfully",
        "data": build_project_response(project, db),
        "errors": []
    }


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_admin_or_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project.status = False
    db.commit()
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Project deactivated successfully",
        "data": None,
        "errors": []
    }


@router.get("/{project_id}/members")
async def list_project_members(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check access
    if not check_admin_or_manager(current_user):
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    members = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()
    
    result = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            result.append({
                "user_id": user.id,
                "user_name": user.name,
                "user_email": user.email,
                "bill_rate": float(m.bill_rate) if m.bill_rate else None
            })
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Project members retrieved successfully",
        "data": result,
        "errors": []
    }


@router.post("/{project_id}/members")
async def add_project_member(
    project_id: int,
    request: ProjectMemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Admin or project manager can add members
    if not check_admin(current_user) and project.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or project manager can add members"
        )
    
    # Check if already a member
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == request.user_id
    ).first()
    
    if existing:
        return {
            "status": "error",
            "statusCode": 400,
            "message": "User is already a member of this project",
            "data": None,
            "errors": ["User is already a member"]
        }
    
    member = ProjectMember(
        project_id=project_id,
        user_id=request.user_id,
        bill_rate=request.bill_rate
    )
    db.add(member)
    db.commit()
    
    # Send notification email
    user = db.query(User).filter(User.id == request.user_id).first()
    if user:
        await email_service.send_project_assignment_notification(
            employee_email=user.email,
            employee_name=user.name,
            project_name=project.name
        )
    
    return {
        "status": "success",
        "statusCode": 201,
        "message": "Member added successfully",
        "data": {"user_id": request.user_id, "project_id": project_id},
        "errors": []
    }


@router.delete("/{project_id}/members/{user_id}")
async def remove_project_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if not check_admin(current_user) and project.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or project manager can remove members"
        )
    
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    
    db.delete(member)
    db.commit()
    
    # Send notification email
    if user:
        await email_service.send_project_removal_notification(
            employee_email=user.email,
            employee_name=user.name,
            project_name=project.name
        )
    
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Member removed successfully",
        "data": None,
        "errors": []
    }


@router.post("/import")
async def import_projects(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not check_admin_or_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Manager access required"
        )
    
    import csv
    import io
    
    try:
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        
        success_count = 0
        failure_count = 0
        errors = []
        
        for row in reader:
            try:
                name = row.get('name', '').strip()
                client = row.get('client', '').strip()
                manager_email = row.get('manager_email', '').strip()
                reporting_area = row.get('reporting_area', '').strip()
                
                if not name or not client:
                    failure_count += 1
                    errors.append(f"Row {reader.line_num}: Missing name or client")
                    continue
                
                # Find manager
                manager_id = None
                if manager_email:
                    manager = db.query(User).filter(User.email == manager_email).first()
                    if manager:
                        manager_id = manager.id
                
                project = Project(
                    name=name,
                    client=client,
                    manager_id=manager_id,
                    reporting_area=reporting_area
                )
                db.add(project)
                db.flush()
                
                if manager_id:
                    member = ProjectMember(
                        project_id=project.id,
                        user_id=manager_id
                    )
                    db.add(member)
                
                db.commit()
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
