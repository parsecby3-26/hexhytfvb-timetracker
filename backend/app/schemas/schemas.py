from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from decimal import Decimal


# Role Schemas
class RoleBase(BaseModel):
    name: str


class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class RoleValueResponse(BaseModel):
    id: str
    value: str


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: Optional[str] = None  # Make password optional
    parent_id: Optional[int] = None
    roles: List[str] = []


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[bool] = None
    parent_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    status: bool
    parent_id: Optional[int]
    manager_name: Optional[str] = None
    created_at: datetime
    roles: List[RoleValueResponse] = []

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    status: bool
    parent_id: Optional[int]
    manager_name: Optional[str] = None
    created_at: datetime
    roles: List[RoleValueResponse] = []

    class Config:
        from_attributes = True


# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    parent_id: Optional[int] = None
    roles: List[str] = []


class FirstLoginOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class TokenResponse(BaseModel):
    token: str
    profile: UserProfileResponse


class LoginResponse(BaseModel):
    status: str
    statusCode: int
    message: str
    data: Optional[TokenResponse]
    errors: List[str] = []


# Project Schemas
class ProjectBase(BaseModel):
    name: str
    client: str
    manager_id: int
    reporting_area: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client: Optional[str] = None
    status: Optional[bool] = None
    manager_id: Optional[int] = None
    reporting_area: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    client: str
    status: bool
    manager_id: int
    manager_name: Optional[str] = None
    reporting_area: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectMemberAdd(BaseModel):
    user_id: int
    bill_rate: Optional[Decimal] = None


class ProjectMemberResponse(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    bill_rate: Optional[Decimal]

    class Config:
        from_attributes = True


# Time Entry Schemas
class TimeEntryBase(BaseModel):
    project_id: int
    work_date: date
    hours: Decimal
    notes: Optional[str] = None


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(BaseModel):
    project_id: Optional[int] = None
    work_date: Optional[date] = None
    hours: Optional[Decimal] = None
    notes: Optional[str] = None
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }


class TimeEntryResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    project_id: int
    project_name: str
    work_date: date
    hours: Decimal
    notes: Optional[str]
    status: str
    approved_by_id: Optional[int]
    approved_by_name: Optional[str] = None
    approval_date: Optional[datetime]
    rejection_reason: Optional[str]
    resubmission_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TimeEntryApproval(BaseModel):
    status: str  # APPROVED or REJECTED
    rejection_reason: Optional[str] = None


class TimeEntryResubmit(BaseModel):
    hours: Optional[Decimal] = None
    notes: Optional[str] = None
    resubmission_notes: Optional[str] = None


# Report Schemas
class ReportFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_id: Optional[int] = None
    user_id: Optional[int] = None
    reporting_area: Optional[str] = None


class DailySummary(BaseModel):
    date: date
    total_hours: Decimal
    entries: List[TimeEntryResponse]


class ProjectSummary(BaseModel):
    project_id: int
    project_name: str
    client: str
    reporting_area: Optional[str]
    total_hours: Decimal
    user_summaries: List[dict]


class UserHoursSummary(BaseModel):
    user_id: int
    user_name: str
    total_hours: Decimal
    project_breakdown: List[dict]


# Pagination
class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int


# Notification Schemas
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: Optional[str]
    is_read: bool
    link: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationSummary(BaseModel):
    notifications: List[NotificationResponse]
    unread_count: int


# Standard API Response
class APIResponse(BaseModel):
    status: str
    statusCode: int
    message: str
    data: Optional[dict] = None
    errors: List[str] = []


# Feedback Schemas
class FeedbackCreate(BaseModel):
    name: str
    email: EmailStr
    category: str
    message: str



