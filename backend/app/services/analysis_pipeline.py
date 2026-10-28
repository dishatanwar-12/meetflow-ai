import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.meeting import Meeting, MeetingStatus, AnalysisRun, AnalysisStatus, MeetingAttendee
from backend.app.models.decision import Decision, DecisionStatus
from backend.app.models.task import Task, OwnerStatus, DueDateStatus, TaskPriority, TaskStatus
from backend.app.models.risk import Risk, RiskStatus
from backend.app.models.blocker import BlockerDependency
from backend.app.models.question import UnansweredQuestion, QuestionStatus
from backend.app.models.project import Project, ProjectMembership
from backend.app.models.audit_log import AuditLog
from backend.app.schemas.analysis import LLMMeetingAnalysisOutput
from backend.app.services.nvidia_llm import NvidiaLLMService, NvidiaLLMError
from backend.app.services.transcript_parser import TranscriptParser
from backend.app.services.date_resolver import DateResolver
from backend.app.services.identity_resolver import IdentityResolver
from backend.app.prompts.meeting_analysis import build_meeting_analysis_prompt

logger = logging.getLogger(__name__)

class AnalysisPipelineError(Exception):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details

class MeetingAnalysisPipeline:
    def __init__(self, db: AsyncSession, nvidia_service: Optional[NvidiaLLMService] = None):
        self.db = db
        self.nvidia_service = nvidia_service or NvidiaLLMService()

    @staticmethod
    def _clean_json_content(content: str) -> str:
        """Strips markdown code fences and extraneous pre/post text from LLM response."""
        content = content.strip()
        # If wrapped in ```json ... ``` or ``` ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if fence_match:
            return fence_match.group(1).strip()
        # If there are leading chars before the first '{'
        start_idx = content.find("{")
        end_idx = content.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return content[start_idx:end_idx + 1].strip()
        return content

    @staticmethod
    def _find_source_offsets(source_text: str, quote: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
        """Finds start and end character offsets of evidence quote in transcript."""
        if not source_text or not quote or len(quote.strip()) < 5:
            return None, None
        clean_quote = quote.strip()
        pos = source_text.find(clean_quote)
        if pos != -1:
            return pos, pos + len(clean_quote)
        # Try case-insensitive search
        pos = source_text.lower().find(clean_quote.lower())
        if pos != -1:
            return pos, pos + len(clean_quote)
        return None, None

    async def run_analysis(self, meeting_id: str, user_id: Optional[str] = None) -> Meeting:
        """
        Executes the full AI analysis pipeline for a given meeting.
        """
        # 1. Fetch meeting and related entities
        res = await self.db.execute(select(Meeting).where(Meeting.id == meeting_id))
        meeting = res.scalar_one_or_none()
        if not meeting:
            raise AnalysisPipelineError(f"Meeting with ID '{meeting_id}' not found.")

        raw_transcript = meeting.raw_transcript or ""
        normalized_transcript = TranscriptParser.normalize_text(raw_transcript)
        if not normalized_transcript or len(normalized_transcript.strip()) < 10:
            raise AnalysisPipelineError("Meeting transcript is empty or too short for analysis.")

        # Fetch attendees and project members for identity resolution
        att_res = await self.db.execute(select(MeetingAttendee).where(MeetingAttendee.meeting_id == meeting_id))
        attendees = att_res.scalars().all()
        attendee_list = [{"name": a.name, "email": a.email, "user_id": None} for a in attendees]
        attendee_names = [a.name for a in attendees]

        pm_res = await self.db.execute(select(ProjectMembership).where(ProjectMembership.project_id == meeting.project_id))
        members = pm_res.scalars().all()
        member_list = [{"name": "", "email": None, "user_id": m.user_id} for m in members]

        # Update meeting status to processing
        meeting.status = MeetingStatus.PROCESSING
        await self.db.commit()

        # Create analysis run record
        analysis_run = AnalysisRun(
            meeting_id=meeting.id,
            model_name=self.nvidia_service.model,
            status=AnalysisStatus.PROCESSING
        )
        self.db.add(analysis_run)
        await self.db.commit()
        await self.db.refresh(analysis_run)

        # 2. Build prompt with strict prompt-injection defenses and uncertainty instructions
        meeting_date_str = meeting.meeting_date.strftime("%Y-%m-%d %H:%M") if meeting.meeting_date else "Unknown"
        messages = build_meeting_analysis_prompt(
            transcript=normalized_transcript,
            meeting_title=meeting.title,
            meeting_date=meeting_date_str,
            timezone=meeting.timezone or "UTC",
            attendees=attendee_names
        )

        # 3. Call NVIDIA NIM
        try:
            llm_response = await self.nvidia_service.generate_chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=4096
            )
        except NvidiaLLMError as e:
            analysis_run.status = AnalysisStatus.FAILED
            analysis_run.error_message = e.message
            meeting.status = MeetingStatus.DRAFT
            await self.db.commit()
            raise AnalysisPipelineError(f"NVIDIA NIM error: {e.message}", details=e.details)

        # 4. Extract tokens and content
        usage = llm_response.get("usage", {})
        analysis_run.prompt_tokens = usage.get("prompt_tokens", 0)
        analysis_run.completion_tokens = usage.get("completion_tokens", 0)
        analysis_run.raw_response = llm_response

        choices = llm_response.get("choices", [])
        if not choices:
            analysis_run.status = AnalysisStatus.FAILED
            analysis_run.error_message = "Empty response received from NVIDIA NIM."
            meeting.status = MeetingStatus.DRAFT
            await self.db.commit()
            raise AnalysisPipelineError("Empty response received from NVIDIA NIM.")

        raw_content = choices[0].get("message", {}).get("content", "")
        cleaned_json = self._clean_json_content(raw_content)

        # 5. Parse and validate with Pydantic
        try:
            parsed_dict = json.loads(cleaned_json)
            validated_output = LLMMeetingAnalysisOutput.model_validate(parsed_dict)
        except Exception as e:
            logger.error(f"Failed to validate LLM output schema: {str(e)}\nRaw: {raw_content[:500]}")
            analysis_run.status = AnalysisStatus.FAILED
            analysis_run.error_message = f"Structured schema validation failed: {str(e)}"
            meeting.status = MeetingStatus.DRAFT
            await self.db.commit()
            raise AnalysisPipelineError(f"AI response did not conform to the expected structured schema: {str(e)}")

        # 6. Save extracted entities with deterministic resolution
        try:
            # Clear previous extracted items for this meeting to avoid duplicates on re-analysis
            for old_dec in (await self.db.execute(select(Decision).where(Decision.meeting_id == meeting.id))).scalars().all():
                await self.db.delete(old_dec)
            for old_task in (await self.db.execute(select(Task).where(Task.meeting_id == meeting.id))).scalars().all():
                await self.db.delete(old_task)
            for old_risk in (await self.db.execute(select(Risk).where(Risk.meeting_id == meeting.id))).scalars().all():
                await self.db.delete(old_risk)
            for old_blocker in (await self.db.execute(select(BlockerDependency).where(BlockerDependency.meeting_id == meeting.id))).scalars().all():
                await self.db.delete(old_blocker)
            for old_q in (await self.db.execute(select(UnansweredQuestion).where(UnansweredQuestion.meeting_id == meeting.id))).scalars().all():
                await self.db.delete(old_q)

            # Store summary and warnings
            meeting.summary_data = {
                "meeting_summary": validated_output.meeting_summary,
                "topics": validated_output.topics,
                "follow_up_topics": validated_output.follow_up_topics,
                "contradictions": [c.model_dump() for c in validated_output.contradictions]
            }
            meeting.analysis_warnings = validated_output.analysis_warnings

            # Save Decisions
            for dec in validated_output.decisions:
                start_off, end_off = self._find_source_offsets(normalized_transcript, dec.evidence)
                new_dec = Decision(
                    meeting_id=meeting.id,
                    project_id=meeting.project_id,
                    title=dec.title,
                    description=dec.description,
                    status=dec.status,
                    decision_date=datetime.strptime(dec.decision_date, "%Y-%m-%d").date() if dec.decision_date else None,
                    owner_or_approver=dec.owner_or_approver,
                    evidence_passage=dec.evidence,
                    source_start=start_off,
                    source_end=end_off,
                    confirmation_required=dec.confirmation_required,
                )
                self.db.add(new_dec)

            # Save Action Items (Tasks)
            for item in validated_output.action_items:
                # Resolve owner identity
                owner_name, owner_uid, owner_status, owner_reason = IdentityResolver.resolve_task_owner(
                    raw_owner_name=item.owner_name,
                    attendees=attendee_list,
                    project_members=member_list
                )
                # If LLM itself marked not_stated, honor it
                if item.owner_status == OwnerStatus.NOT_STATED:
                    owner_name = None
                    owner_status = OwnerStatus.NOT_STATED

                # Resolve due date
                due_date, due_date_status, date_reason = DateResolver.resolve_deadline(
                    date_expression=item.date_expression,
                    meeting_datetime=meeting.meeting_date,
                    explicit_date_str=item.due_date
                )
                if item.due_date_status == DueDateStatus.NOT_STATED and not item.date_expression:
                    due_date = None
                    due_date_status = DueDateStatus.NOT_STATED

                start_off, end_off = self._find_source_offsets(normalized_transcript, item.evidence)

                # Determine if confirmation is required
                needs_confirm = (
                    owner_status in [OwnerStatus.NOT_STATED, OwnerStatus.AMBIGUOUS, OwnerStatus.CONFLICTING] or
                    due_date_status in [DueDateStatus.NOT_STATED, DueDateStatus.AMBIGUOUS, DueDateStatus.CONFLICTING] or
                    item.confirmation_required
                )

                reasons = []
                if owner_reason:
                    reasons.append(owner_reason)
                if date_reason:
                    reasons.append(date_reason)
                if item.confirmation_reason:
                    reasons.append(item.confirmation_reason)

                new_task = Task(
                    meeting_id=meeting.id,
                    project_id=meeting.project_id,
                    title=item.title,
                    description=item.description,
                    owner_name=owner_name,
                    owner_user_id=owner_uid,
                    owner_status=owner_status,
                    due_date=due_date,
                    due_date_status=due_date_status,
                    date_expression=item.date_expression,
                    priority=item.priority,
                    status=item.task_status,
                    dependencies=item.dependencies,
                    evidence_passage=item.evidence,
                    source_start=start_off,
                    source_end=end_off,
                    confirmation_required=needs_confirm,
                    confirmation_reason="; ".join(reasons) if reasons else None
                )
                self.db.add(new_task)

            # Save Risks
            for r in validated_output.risks:
                start_off, end_off = self._find_source_offsets(normalized_transcript, r.evidence)
                new_risk = Risk(
                    meeting_id=meeting.id,
                    project_id=meeting.project_id,
                    description=r.description,
                    potential_impact=r.potential_impact,
                    likelihood=r.likelihood,
                    mitigation=r.mitigation,
                    responsible_person=r.responsible_person,
                    evidence_passage=r.evidence,
                    source_start=start_off,
                    source_end=end_off,
                    status=RiskStatus.OPEN
                )
                self.db.add(new_risk)

            # Save Blockers
            for b in validated_output.blockers:
                new_blocker = BlockerDependency(
                    meeting_id=meeting.id,
                    project_id=meeting.project_id,
                    description=b.description,
                    dependency_type=b.dependency_type,
                    responsible_party=b.responsible_party,
                    evidence_passage=b.evidence,
                    resolution_question=b.resolution_question,
                    is_resolved=False
                )
                self.db.add(new_blocker)

            # Save Unanswered Questions
            for q in validated_output.unanswered_questions:
                new_q = UnansweredQuestion(
                    meeting_id=meeting.id,
                    project_id=meeting.project_id,
                    question=q.question,
                    clarification_reason=q.why_clarification_needed,
                    related_entity_type="task" if q.related_entity else None,
                    evidence_passage=q.evidence,
                    suggested_person=q.suggested_person_to_ask,
                    status=QuestionStatus.OPEN
                )
                self.db.add(new_q)

            # Update meeting & analysis run status
            meeting.status = MeetingStatus.REVIEWED
            analysis_run.status = AnalysisStatus.COMPLETED

            # Add audit log
            audit = AuditLog(
                organization_id=meeting.organization_id,
                user_id=user_id,
                entity_type="meeting",
                entity_id=meeting.id,
                action="analyze_meeting",
                new_state={"status": "reviewed", "model": self.nvidia_service.model}
            )
            self.db.add(audit)

            await self.db.commit()
            await self.db.refresh(meeting)
            return meeting

        except Exception as e:
            await self.db.rollback()
            logger.exception("Error saving extracted meeting analysis to database")
            analysis_run.status = AnalysisStatus.FAILED
            analysis_run.error_message = f"Database persistence error: {str(e)}"
            meeting.status = MeetingStatus.DRAFT
            await self.db.commit()
            raise AnalysisPipelineError(f"Failed to persist analysis outcomes: {str(e)}")
