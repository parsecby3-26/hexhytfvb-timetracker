from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.config import settings
from app.models.models import User, Role, UserRole
from app.schemas.schemas import (
    LoginRequest, RegisterRequest, LoginResponse, UserProfileResponse, 
    TokenResponse, APIResponse, FirstLoginOTPRequest
)
from app.services.email_service import email_service
import secrets

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def get_user_profile(user: User, db: Session) -> dict:
    """Build user profile response with roles."""
    manager_name = None
    if user.parent_id:
        manager = db.query(User).filter(User.id == user.parent_id).first()
        if manager:
            manager_name = manager.name
    
    roles = []
    for role in user.roles:
        roles.append({"id": str(role.id), "value": role.name})
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "status": user.status,
        "parent_id": user.parent_id,
        "manager_name": manager_name,
        "created_at": user.created_at,
        "roles": roles
    }


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user or not verify_password(request.password, user.password_hash):
            return LoginResponse(
                status="error",
                statusCode=401,
                message="Invalid email or password",
                data=None,
                errors=["Invalid email or password"]
            )
        
        if not user.status:
            return LoginResponse(
                status="error",
                statusCode=403,
                message="Account is deactivated",
                data=None,
                errors=["Account is deactivated"]
            )
        
        if not user.email_verified:
            return LoginResponse(
                status="error",
                statusCode=403,
                message="Please verify your email address",
                data=None,
                errors=["Email not verified"]
            )
        
        if getattr(user, "requires_password_change", False):
            import random
            from datetime import timedelta
            otp = str(random.randint(100000, 999999))
            user.otp_code = otp
            user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
            db.commit()
            
            try:
                await email_service.send_otp_email(user.email, user.name, otp)
            except Exception as e:
                print(f"Failed to send OTP email: {str(e)}")
            
            return LoginResponse(
                status="otp_required",
                statusCode=403,
                message="First-time login detected. Please check your email for the OTP.",
                data=None,
                errors=[]
            )
        
        access_token = create_access_token(data={"sub": str(user.id)})
        profile = get_user_profile(user, db)
        
        return LoginResponse(
            status="success",
            statusCode=200,
            message="Login successful",
            data=TokenResponse(token=access_token, profile=UserProfileResponse(**profile)),
            errors=[]
        )
    except Exception as e:
        import traceback
        print(f"Login error: {str(e)}")
        traceback.print_exc()
        return LoginResponse(
            status="error",
            statusCode=500,
            message=f"Server error: {str(e)}",
            data=None,
            errors=[str(e)]
        )


import re

@router.post("/verify-first-login", response_model=LoginResponse)
async def verify_first_login(request: FirstLoginOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return LoginResponse(status="error", statusCode=404, message="User not found", data=None, errors=["User not found"])
    
    if not getattr(user, "requires_password_change", False):
        return LoginResponse(status="error", statusCode=400, message="Password change not required", data=None, errors=["Not required"])
        
    if not user.otp_code or user.otp_code != request.otp:
        return LoginResponse(status="error", statusCode=400, message="Invalid OTP", data=None, errors=["Invalid OTP"])
        
    if not user.otp_expires_at or user.otp_expires_at < datetime.utcnow():
        return LoginResponse(status="error", statusCode=400, message="OTP expired", data=None, errors=["OTP expired"])
        
    pwd = request.new_password
    if len(pwd) < 8 or not re.search(r"[A-Z]", pwd) or not re.search(r"\d", pwd) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd):
        msg = "Password must be at least 8 characters, with 1 uppercase, 1 number, and 1 special character."
        return LoginResponse(status="error", statusCode=400, message=msg, data=None, errors=[msg])
    
    # Policy: Cannot match default password
    if pwd == "Tickmarks@123":
        return LoginResponse(status="error", statusCode=400, message="New password cannot be the default password.", data=None, errors=["Invalid password"])
        
    # Policy: Cannot match current password
    if verify_password(pwd, user.password_hash):
        return LoginResponse(status="error", statusCode=400, message="New password cannot be the same as the current password.", data=None, errors=["Invalid password"])
        
    user.password_hash = hash_password(pwd)
    user.requires_password_change = False
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    
    access_token = create_access_token(data={"sub": str(user.id)})
    profile = get_user_profile(user, db)
    return LoginResponse(
        status="success",
        statusCode=200,
        message="Password changed successfully",
        data=TokenResponse(token=access_token, profile=UserProfileResponse(**profile)),
        errors=[]
    )


@router.post("/register", response_model=LoginResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        return LoginResponse(
            status="error",
            statusCode=400,
            message="Email already registered",
            data=None,
            errors=["Email already registered"]
        )
    
    # Create user with fixed indentation
    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        status=True,
        email_verified=False,  # SOC2 Compliance: must click email link
        verification_token=secrets.token_urlsafe(32)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign roles
    if request.roles:
        for role_name in request.roles:
            role = db.query(Role).filter(Role.name == role_name).first()
            if role:
                user_role = UserRole(user_id=user.id, role_id=role.id)
                db.add(user_role)
    else:
        # Default role is Member
        member_role = db.query(Role).filter(Role.name == "Member").first()
        if member_role:
            user_role = UserRole(user_id=user.id, role_id=member_role.id)
            db.add(user_role)
    
    db.commit()
    
    # Send verification email
    try:
        await email_service.send_verification_email(
            email=user.email,
            name=user.name,
            token=user.verification_token
        )
    except Exception as e:
        # Log error but don't crash registration; user can resend later
        print(f"Email error: {str(e)}")
    
    return LoginResponse(
        status="success",
        statusCode=201,
        message="Registration successful. Please check your email to verify your account.",
        data=None,
        errors=[]
    )


@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    user.email_verified = True
    user.verification_token = None
    db.commit()
    
    # Send success email
    from app.services.email_service import email_service
    await email_service.send_verification_success_notification(
        email=user.email,
        name=user.name
    )
    
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Standard security practice: don't reveal if email exists
        return {"message": "If the email exists, a verification link has been sent."}
    
    if user.email_verified:
        return {"message": "Email is already verified."}
    
    user.verification_token = secrets.token_urlsafe(32)
    db.commit()
    
    await email_service.send_verification_email(
        email=user.email,
        name=user.name,
        token=user.verification_token
    )
    
    return {"message": "Verification email sent."}


@router.post("/request-password-reset")
async def request_password_reset(request: dict, db: Session = Depends(get_db)):
    email = request.get('email')
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Standard security practice: don't reveal if email exists
        return {
            "status": "success",
            "message": "If the email exists, a password reset link has been sent."
        }
    
    # Generate a password reset token (valid for 24 hours)
    reset_token = secrets.token_urlsafe(32)
    user.password_reset_token = reset_token
    user.password_reset_token_expires = datetime.utcnow() + timedelta(hours=24)
    db.commit()
    
    # Send password reset email
    try:
        await email_service.send_password_reset_email(
            email=user.email,
            name=user.name,
            token=reset_token
        )
    except Exception as e:
        print(f"Failed to send password reset email: {str(e)}")
    
    return {
        "status": "success",
        "message": "If the email exists, a password reset link has been sent."
    }


@router.post("/reset-password")
async def reset_password(request: dict, db: Session = Depends(get_db)):
    token = request.get('token')
    new_password = request.get('new_password')
    
    if not token or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token and new password are required"
        )
    
    user = db.query(User).filter(
        User.password_reset_token == token,
        User.password_reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Policy: Password Strength & Checks
    if not isinstance(new_password, str) or len(new_password) < 8 or not re.search(r"[A-Z]", new_password) or not re.search(r"\d", new_password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters, with 1 uppercase, 1 number, and 1 special character."
        )

    # Policy: Cannot match default password
    if new_password == "Tickmarks@123":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the default password."
        )
        
    # Policy: Cannot match current password
    if verify_password(new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current password."
        )
        
    # Update password
    user.password_hash = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    user.requires_password_change = False  # Password is newly set, clear the force flag
    db.commit()
    
    # Send confirmation email
    try:
        await email_service.send_password_changed_email(
            email=user.email,
            name=user.name
        )
    except Exception as e:
        print(f"Failed to send password changed email: {str(e)}")
    
    return {
        "status": "success",
        "message": "Password has been reset successfully"
    }








