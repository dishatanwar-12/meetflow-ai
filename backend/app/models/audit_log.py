from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models import generate_uuid, utc_now

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    entity_type = Column(String(100), nullable=False)  # meeting, task, decision, client, project
    entity_id = Column(String(36), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # create, update, delete, confirm_owner, confirm_due_date, approve
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    user = relationship("User")

