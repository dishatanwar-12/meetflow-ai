from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class BlockerBase(BaseModel):
    description: str
    dependency_type: Optional[str] = "external"
    responsible_party: Optional[str] = None
    evidence_passage: Optional[str] = None
    resolution_question: Optional[str] = None
    is_resolved: Optional[bool] = False

class BlockerCreate(BlockerBase):
    meeting_id: str
    project_id: str
    task_id: Optional[str] = None

class BlockerUpdate(BaseModel):
    description: Optional[str] = None
    dependency_type: Optional[str] = None
    responsible_party: Optional[str] = None
    evidence_passage: Optional[str] = None
    resolution_question: Optional[str] = None
    is_resolved: Optional[bool] = None

class BlockerResponse(BlockerBase):
    id: str
    meeting_id: str
    project_id: str
    task_id: Optional[str] = None
    task_title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

