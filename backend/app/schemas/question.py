from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from backend.app.models.question import QuestionStatus

class QuestionBase(BaseModel):
    question: str
    clarification_reason: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    evidence_passage: Optional[str] = None
    suggested_person: Optional[str] = None
    status: Optional[QuestionStatus] = QuestionStatus.OPEN

class QuestionCreate(QuestionBase):
    meeting_id: str
    project_id: str

class QuestionUpdate(BaseModel):
    question: Optional[str] = None
    clarification_reason: Optional[str] = None
    status: Optional[QuestionStatus] = None
    answer: Optional[str] = None

class QuestionAnswer(BaseModel):
    answer: str

class QuestionResponse(QuestionBase):
    id: str
    meeting_id: str
    project_id: str
    answer: Optional[str] = None
    answered_by_name: Optional[str] = None
    answered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

