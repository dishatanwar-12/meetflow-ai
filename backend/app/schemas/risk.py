from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from backend.app.models.risk import RiskStatus

class RiskBase(BaseModel):
    description: str
    potential_impact: Optional[str] = None
    likelihood: Optional[str] = None
    mitigation: Optional[str] = None
    responsible_person: Optional[str] = None
    evidence_passage: Optional[str] = None
    source_start: Optional[int] = None
    source_end: Optional[int] = None
    status: Optional[RiskStatus] = RiskStatus.OPEN

class RiskCreate(RiskBase):
    meeting_id: str
    project_id: str

class RiskUpdate(BaseModel):
    description: Optional[str] = None
    potential_impact: Optional[str] = None
    likelihood: Optional[str] = None
    mitigation: Optional[str] = None
    responsible_person: Optional[str] = None
    evidence_passage: Optional[str] = None
    status: Optional[RiskStatus] = None

class RiskResponse(RiskBase):
    id: str
    meeting_id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

