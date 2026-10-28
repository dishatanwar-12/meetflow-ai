from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models import generate_uuid, utc_now

class BlockerDependency(Base):
    __tablename__ = "blocker_dependencies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(Text, nullable=False)
    dependency_type = Column(String(100), default="external", nullable=False)  # technical, external, approval, resource
    responsible_party = Column(String(255), nullable=True)
    evidence_passage = Column(Text, nullable=True)
    resolution_question = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    meeting = relationship("Meeting", back_populates="blockers")
    project = relationship("Project")
    task = relationship("Task")

