import enum
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Enum, Boolean, Integer
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models import generate_uuid, utc_now

class DecisionStatus(str, enum.Enum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    DISPUTED = "disputed"

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(DecisionStatus, native_enum=False), default=DecisionStatus.PROPOSED, nullable=False)
    decision_date = Column(Date, nullable=True)
    owner_or_approver = Column(String(255), nullable=True)
    evidence_passage = Column(Text, nullable=True)
    source_start = Column(Integer, nullable=True)
    source_end = Column(Integer, nullable=True)
    evidence_type = Column(String(50), default="explicit", nullable=False)  # explicit, inferred, unconfirmed
    confirmation_required = Column(Boolean, default=True, nullable=False)
    superseded_by_id = Column(String(36), ForeignKey("decisions.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    meeting = relationship("Meeting", back_populates="decisions")
    project = relationship("Project", back_populates="decisions")
    superseded_by = relationship("Decision", remote_side=[id])
    tasks = relationship("Task", back_populates="related_decision")

