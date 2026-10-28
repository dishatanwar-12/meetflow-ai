import enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models import generate_uuid, utc_now

class RiskStatus(str, enum.Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    CLOSED = "closed"

class Risk(Base):
    __tablename__ = "risks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    potential_impact = Column(String(255), nullable=True)
    likelihood = Column(String(100), nullable=True)  # Low, Medium, High (only if stated)
    mitigation = Column(Text, nullable=True)
    responsible_person = Column(String(255), nullable=True)
    evidence_passage = Column(Text, nullable=True)
    source_start = Column(Integer, nullable=True)
    source_end = Column(Integer, nullable=True)
    status = Column(Enum(RiskStatus, native_enum=False), default=RiskStatus.OPEN, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    meeting = relationship("Meeting", back_populates="risks")
    project = relationship("Project")

