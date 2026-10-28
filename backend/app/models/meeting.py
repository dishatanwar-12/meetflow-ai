import enum
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models import generate_uuid, utc_now

class MeetingType(str, enum.Enum):
    DISCOVERY = "discovery"
    STATUS_UPDATE = "status_update"
    CLIENT_REVIEW = "client_review"
    PLANNING = "planning"
    RETROSPECTIVE = "retrospective"
    OTHER = "other"

class MeetingStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"

class AnalysisStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    meeting_date = Column(DateTime(timezone=True), nullable=True)
    timezone = Column(String(100), default="UTC", nullable=False)
    meeting_type = Column(Enum(MeetingType, native_enum=False), default=MeetingType.STATUS_UPDATE, nullable=False)
    language = Column(String(50), default="en", nullable=False)
    status = Column(Enum(MeetingStatus, native_enum=False), default=MeetingStatus.DRAFT, nullable=False)
    raw_transcript = Column(Text, nullable=True)
    summary_data = Column(JSON, nullable=True)  # Store meeting_summary, topics, etc.
    analysis_warnings = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    project = relationship("Project", back_populates="meetings")
    client = relationship("Client", back_populates="meetings")
    attendees = relationship("MeetingAttendee", back_populates="meeting", cascade="all, delete-orphan")
    documents = relationship("TranscriptDocument", back_populates="meeting", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="meeting", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="meeting", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="meeting", cascade="all, delete-orphan")
    blockers = relationship("BlockerDependency", back_populates="meeting", cascade="all, delete-orphan")
    questions = relationship("UnansweredQuestion", back_populates="meeting", cascade="all, delete-orphan")

class MeetingAttendee(Base):
    __tablename__ = "meeting_attendees"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    role = Column(String(100), nullable=True)
    is_external = Column(Boolean, default=False, nullable=False)
    speaker_label = Column(String(100), nullable=True)  # E.g. "Speaker 1", "Alex"
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    meeting = relationship("Meeting", back_populates="attendees")

class TranscriptDocument(Base):
    __tablename__ = "transcript_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    extracted_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    meeting = relationship("Meeting", back_populates="documents")

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    model_name = Column(String(150), nullable=False)
    status = Column(Enum(AnalysisStatus, native_enum=False), default=AnalysisStatus.QUEUED, nullable=False)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    raw_response = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    meeting = relationship("Meeting", back_populates="analysis_runs")

