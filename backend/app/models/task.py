import enum
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Enum, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models import generate_uuid, utc_now

class OwnerStatus(str, enum.Enum):
    EXPLICIT = "explicit"
    USER_CONFIRMED = "user_confirmed"
    NOT_STATED = "not_stated"
    AMBIGUOUS = "ambiguous"
    CONFLICTING = "conflicting"

class DueDateStatus(str, enum.Enum):
    EXPLICIT = "explicit"
    RESOLVED_FROM_MEETING_DATE = "resolved_from_meeting_date"
    USER_CONFIRMED = "user_confirmed"
    NOT_STATED = "not_stated"
    AMBIGUOUS = "ambiguous"
    CONFLICTING = "conflicting"

class TaskPriority(str, enum.Enum):
    UNSPECIFIED = "unspecified"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(str, enum.Enum):
    NEEDS_CLARIFICATION = "needs_clarification"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Owner resolution & uncertainty
    owner_name = Column(String(255), nullable=True)
    owner_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    owner_status = Column(Enum(OwnerStatus, native_enum=False), default=OwnerStatus.NOT_STATED, nullable=False)
    
    # Due date resolution & uncertainty
    due_date = Column(Date, nullable=True)
    due_date_status = Column(Enum(DueDateStatus, native_enum=False), default=DueDateStatus.NOT_STATED, nullable=False)
    date_expression = Column(String(255), nullable=True)  # e.g., "next Friday", "by end of month"
    
    # Priority & Lifecycle
    priority = Column(Enum(TaskPriority, native_enum=False), default=TaskPriority.UNSPECIFIED, nullable=False)
    status = Column(Enum(TaskStatus, native_enum=False), default=TaskStatus.NEEDS_CLARIFICATION, nullable=False)
    
    # Relationships & Evidence
    dependencies = Column(JSON, default=list, nullable=False)
    related_decision_id = Column(String(36), ForeignKey("decisions.id", ondelete="SET NULL"), nullable=True)
    evidence_passage = Column(Text, nullable=True)
    source_start = Column(Integer, nullable=True)
    source_end = Column(Integer, nullable=True)
    evidence_type = Column(String(50), default="explicit", nullable=False)
    
    # Confirmation workflow
    confirmation_required = Column(Boolean, default=True, nullable=False)
    confirmation_reason = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    meeting = relationship("Meeting", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    owner_user = relationship("User", foreign_keys=[owner_user_id])
    related_decision = relationship("Decision", back_populates="tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    external_mappings = relationship("ExternalTaskMapping", back_populates="task", cascade="all, delete-orphan")

class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    task = relationship("Task", back_populates="comments")
    user = relationship("User")

