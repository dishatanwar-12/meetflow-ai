import enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models import generate_uuid, utc_now

class QuestionStatus(str, enum.Enum):
    OPEN = "open"
    ANSWERED = "answered"
    DEFERRED = "deferred"

class UnansweredQuestion(Base):
    __tablename__ = "unanswered_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    clarification_reason = Column(Text, nullable=True)
    related_entity_type = Column(String(50), nullable=True)  # task, decision, risk
    related_entity_id = Column(String(36), nullable=True)
    evidence_passage = Column(Text, nullable=True)
    suggested_person = Column(String(255), nullable=True)  # only if stated
    status = Column(Enum(QuestionStatus, native_enum=False), default=QuestionStatus.OPEN, nullable=False)
    answer = Column(Text, nullable=True)
    answered_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    meeting = relationship("Meeting", back_populates="questions")
    project = relationship("Project")
    answered_by = relationship("User")

