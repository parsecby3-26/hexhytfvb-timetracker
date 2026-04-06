from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, ForeignKey, Text, DECIMAL, Date, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    parent_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    email_verified = Column(Boolean, nullable=False, default=False)
    verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expires = Column(DateTime, nullable=True)
    requires_password_change = Column(Boolean, nullable=False, default=False)
    otp_code = Column(String(6), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)

    # Relationships
    manager = relationship("User", remote_side=[id], backref="subordinates")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    projects = relationship("Project", secondary="project_members", back_populates="members")
    time_entries = relationship("TimeEntry", back_populates="user", foreign_keys="[TimeEntry.user_id]")
    managed_projects = relationship("Project", back_populates="manager")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


class Role(Base):
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    role_id = Column(BigInteger, ForeignKey("roles.id"), primary_key=True)

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class Project(Base):
    __tablename__ = "projects"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    client = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    manager_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    reporting_area = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    manager = relationship("User", back_populates="managed_projects")
    members = relationship("User", secondary="project_members", back_populates="projects")
    time_entries = relationship("TimeEntry", back_populates="project")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', client='{self.client}')>"


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id = Column(BigInteger, ForeignKey("projects.id"), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    bill_rate = Column(DECIMAL(10, 2), nullable=True)

    def __repr__(self):
        return f"<ProjectMember(project_id={self.project_id}, user_id={self.user_id})>"


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=False)
    work_date = Column(Date, nullable=False)
    hours = Column(DECIMAL(5, 2), nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="PENDING")
    approved_by_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    resubmission_notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="time_entries")
    project = relationship("Project", back_populates="time_entries")
    approved_by = relationship("User", foreign_keys=[approved_by_id])

    __table_args__ = (
        UniqueConstraint("user_id", "project_id", "work_date", name="uq_time_entries_user_project_date"),
        CheckConstraint("hours >= 0 AND hours <= 24", name="check_hours_range"),
    )

    def __repr__(self):
        return f"<TimeEntry(id={self.id}, user_id={self.user_id}, date={self.work_date}, hours={self.hours})>"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=True) # e.g., 'APPROVAL', 'REJECTION'
    is_read = Column(Boolean, default=False)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, title='{self.title}')>"



