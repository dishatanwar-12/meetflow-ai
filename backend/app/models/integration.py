from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models import generate_uuid, utc_now

class ExternalIntegration(Base):
    __tablename__ = "external_integrations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # github, trello, jira
    credentials = Column(JSON, nullable=False)  # encrypted or masked tokens
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class ExternalTaskMapping(Base):
    __tablename__ = "external_task_mappings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # github, trello
    external_task_id = Column(String(255), nullable=False)
    external_url = Column(String(500), nullable=False)
    sync_status = Column(String(50), default="synced", nullable=False)
    synced_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    task = relationship("Task", back_populates="external_mappings")

