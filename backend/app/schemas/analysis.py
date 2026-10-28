from typing import Optional, List
from pydantic import BaseModel, Field
from backend.app.models.decision import DecisionStatus
from backend.app.models.task import OwnerStatus, DueDateStatus, TaskPriority, TaskStatus

class ExtractedDecision(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: DecisionStatus = DecisionStatus.PROPOSED
    decision_date: Optional[str] = None
    owner_or_approver: Optional[str] = None
    evidence: Optional[str] = None
    source_start: Optional[int] = None
    source_end: Optional[int] = None
    confirmation_required: bool = True

class ExtractedActionItem(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    owner_name: Optional[str] = None
    owner_status: OwnerStatus = OwnerStatus.NOT_STATED
    due_date: Optional[str] = None
    due_date_status: DueDateStatus = DueDateStatus.NOT_STATED
    date_expression: Optional[str] = None
    priority: TaskPriority = TaskPriority.UNSPECIFIED
    task_status: TaskStatus = TaskStatus.NEEDS_CLARIFICATION
    dependencies: List[str] = Field(default_factory=list)
    evidence: Optional[str] = None
    source_start: Optional[int] = None
    source_end: Optional[int] = None
    confirmation_required: bool = True
    confirmation_reason: Optional[str] = None

class ExtractedRisk(BaseModel):
    description: str
    potential_impact: Optional[str] = None
    likelihood: Optional[str] = None
    mitigation: Optional[str] = None
    responsible_person: Optional[str] = None
    evidence: Optional[str] = None
    status: str = "open"

class ExtractedBlocker(BaseModel):
    description: str
    dependency_type: str = "external"
    related_task: Optional[str] = None
    responsible_party: Optional[str] = None
    evidence: Optional[str] = None
    resolution_question: Optional[str] = None

class ExtractedQuestion(BaseModel):
    question: str
    why_clarification_needed: Optional[str] = None
    related_entity: Optional[str] = None
    evidence: Optional[str] = None
    suggested_person_to_ask: Optional[str] = None

class ExtractedContradiction(BaseModel):
    topic: str
    statement_a: str
    statement_b: str
    evidence: Optional[str] = None
    resolution_needed: str

class LLMMeetingAnalysisOutput(BaseModel):
    meeting_summary: str = Field(description="Executive summary of the meeting")
    topics: List[str] = Field(default_factory=list, description="Key discussion topics")
    decisions: List[ExtractedDecision] = Field(default_factory=list, description="Extracted decisions")
    action_items: List[ExtractedActionItem] = Field(default_factory=list, description="Extracted action items")
    risks: List[ExtractedRisk] = Field(default_factory=list, description="Extracted risks")
    blockers: List[ExtractedBlocker] = Field(default_factory=list, description="Extracted blockers and dependencies")
    dependencies: List[str] = Field(default_factory=list, description="General dependencies")
    unanswered_questions: List[ExtractedQuestion] = Field(default_factory=list, description="Unanswered questions requiring clarification")
    follow_up_topics: List[str] = Field(default_factory=list, description="Items suggested for future follow up")
    contradictions: List[ExtractedContradiction] = Field(default_factory=list, description="Contradicting statements")
    analysis_warnings: List[str] = Field(default_factory=list, description="Data uncertainty warnings")

