from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from backend.app.models.decision import DecisionStatus

class DecisionBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[DecisionStatus] = DecisionStatus.PROPOSED
    decision_date: Optional[date] = None
    owner_or_approver: Optional[str] = None
    evidence_passage: Optional[str] = None
    source_start: Optional[int] = None
    source_end: Optional[int] = None
    evidence_type: Optional[str] = "explicit"
    confirmation_required: Optional[bool] = True

class DecisionCreate(DecisionBase):
    meeting_id: str
    project_id: str

class DecisionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DecisionStatus] = None
    decision_date: Optional[date] = None
    owner_or_approver: Optional[str] = None
    evidence_passage: Optional[str] = None
    confirmation_required: Optional[bool] = None
    superseded_by_id: Optional[str] = None

class DecisionResponse(DecisionBase):
    id: str
    meeting_id: str
    project_id: str
    superseded_by_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

