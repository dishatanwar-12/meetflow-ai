from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr
from backend.app.models.meeting import MeetingType, MeetingStatus, AnalysisStatus
from backend.app.schemas.decision import DecisionResponse
from backend.app.schemas.task import TaskResponse
from backend.app.schemas.risk import RiskResponse
from backend.app.schemas.blocker import BlockerResponse
from backend.app.schemas.question import QuestionResponse

class AttendeeBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_external: Optional[bool] = False
    speaker_label: Optional[str] = None

class AttendeeCreate(AttendeeBase):
    pass

class AttendeeResponse(AttendeeBase):
    id: str
    meeting_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    meeting_id: str
    filename: str
    file_size: int
    mime_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    client_id: str
    project_id: str
    meeting_date: Optional[datetime] = None
    timezone: Optional[str] = "UTC"
    meeting_type: Optional[MeetingType] = MeetingType.STATUS_UPDATE
    language: Optional[str] = "en"
    raw_transcript: Optional[str] = None

class MeetingCreate(MeetingBase):
    attendees: Optional[List[AttendeeCreate]] = []

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    client_id: Optional[str] = None
    project_id: Optional[str] = None
    meeting_date: Optional[datetime] = None
    timezone: Optional[str] = None
    meeting_type: Optional[MeetingType] = None
    language: Optional[str] = None
    status: Optional[MeetingStatus] = None
    raw_transcript: Optional[str] = None

class MeetingResponse(MeetingBase):
    id: str
    organization_id: str
    status: MeetingStatus
    client_name: Optional[str] = None
    project_name: Optional[str] = None
    tasks_count: Optional[int] = 0
    decisions_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AnalysisRunResponse(BaseModel):
    id: str
    meeting_id: str
    model_name: str
    status: AnalysisStatus
    prompt_tokens: int
    completion_tokens: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MeetingReviewResponse(BaseModel):
    meeting: MeetingResponse
    attendees: List[AttendeeResponse]
    documents: List[DocumentResponse]
    summary_data: Optional[Any] = None
    decisions: List[DecisionResponse]
    tasks: List[TaskResponse]
    risks: List[RiskResponse]
    blockers: List[BlockerResponse]
    questions: List[QuestionResponse]
    analysis_warnings: List[str] = []
    latest_analysis_run: Optional[AnalysisRunResponse] = None

