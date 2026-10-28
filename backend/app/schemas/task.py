from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel
from backend.app.models.task import OwnerStatus, DueDateStatus, TaskPriority, TaskStatus

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    owner_name: Optional[str] = None
    owner_user_id: Optional[str] = None
    owner_status: Optional[OwnerStatus] = OwnerStatus.NOT_STATED
    due_date: Optional[date] = None
    due_date_status: Optional[DueDateStatus] = DueDateStatus.NOT_STATED
    date_expression: Optional[str] = None
    priority: Optional[TaskPriority] = TaskPriority.UNSPECIFIED
    status: Optional[TaskStatus] = TaskStatus.NEEDS_CLARIFICATION
    dependencies: Optional[List[str]] = []
    related_decision_id: Optional[str] = None
    evidence_passage: Optional[str] = None
    source_start: Optional[int] = None
    source_end: Optional[int] = None
    evidence_type: Optional[str] = "explicit"
    confirmation_required: Optional[bool] = True
    confirmation_reason: Optional[str] = None

class TaskCreate(TaskBase):
    meeting_id: str
    project_id: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner_name: Optional[str] = None
    owner_user_id: Optional[str] = None
    owner_status: Optional[OwnerStatus] = None
    due_date: Optional[date] = None
    due_date_status: Optional[DueDateStatus] = None
    date_expression: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    dependencies: Optional[List[str]] = None
    related_decision_id: Optional[str] = None
    evidence_passage: Optional[str] = None
    confirmation_required: Optional[bool] = None
    confirmation_reason: Optional[str] = None

class TaskConfirmOwner(BaseModel):
    owner_name: str
    owner_user_id: Optional[str] = None

class TaskConfirmDueDate(BaseModel):
    due_date: date

class TaskCommentCreate(BaseModel):
    content: str

class TaskCommentResponse(BaseModel):
    id: str
    task_id: str
    user_id: str
    user_name: Optional[str] = None
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class TaskResponse(TaskBase):
    id: str
    meeting_id: str
    project_id: str
    project_name: Optional[str] = None
    meeting_title: Optional[str] = None
    is_overdue: Optional[bool] = False
    comments_count: Optional[int] = 0
    external_sync_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

