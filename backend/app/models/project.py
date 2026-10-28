import enum
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models import generate_uuid, utc_now

class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    goals = Column(Text, nullable=True)
    manager_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    start_date = Column(Date, nullable=True)
    target_date = Column(Date, nullable=True)
    status = Column(Enum(ProjectStatus, native_enum=False), default=ProjectStatus.ACTIVE, nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    organization = relationship("Organization", back_populates="projects")
    client = relationship("Client", back_populates="projects")
    manager = relationship("User", foreign_keys=[manager_id])
    meetings = relationship("Meeting", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="project", cascade="all, delete-orphan")
    memberships = relationship("ProjectMembership", back_populates="project", cascade="all, delete-orphan")

class ProjectMembership(Base):
    __tablename__ = "project_memberships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_project = Column(String(100), default="member", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    project = relationship("Project", back_populates="memberships")
    user = relationship("User")

