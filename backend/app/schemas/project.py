from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel
from backend.app.models.project import ProjectStatus

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    goals: Optional[str] = None
    client_id: str
    manager_id: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    status: Optional[ProjectStatus] = ProjectStatus.ACTIVE
    tags: Optional[List[str]] = []

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    goals: Optional[str] = None
    client_id: Optional[str] = None
    manager_id: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    status: Optional[ProjectStatus] = None
    tags: Optional[List[str]] = None

class ProjectResponse(ProjectBase):
    id: str
    organization_id: str
    client_name: Optional[str] = None
    manager_name: Optional[str] = None
    meetings_count: Optional[int] = 0
    tasks_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TimelineItem(BaseModel):
    id: str
    type: str  # meeting, decision, task
    title: str
    timestamp: datetime
    status: Optional[str] = None
    details: Optional[str] = None
    meeting_id: Optional[str] = None
    meeting_title: Optional[str] = None

class ContradictionConflict(BaseModel):
    id: str
    type: str  # deadline_conflict, decision_conflict, status_conflict
    title: str
    description: str
    first_meeting_title: str
    first_meeting_date: Optional[datetime] = None
    first_statement: str
    second_meeting_title: str
    second_meeting_date: Optional[datetime] = None
    second_statement: str
    suggested_resolution: Optional[str] = None
    status: str = "unresolved"  # unresolved, resolved

