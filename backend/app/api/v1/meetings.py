from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_member, require_pm
from backend.app.models.user import User
from backend.app.models.meeting import (
    Meeting, MeetingStatus, MeetingAttendee, TranscriptDocument, AnalysisRun, AnalysisStatus
)
from backend.app.models.project import Project
from backend.app.models.client import Client
from backend.app.models.decision import Decision
from backend.app.models.task import Task
from backend.app.models.risk import Risk
from backend.app.models.blocker import BlockerDependency
from backend.app.models.question import UnansweredQuestion
from backend.app.schemas.meeting import (
    MeetingCreate, MeetingUpdate, MeetingResponse, MeetingReviewResponse,
    AttendeeCreate, AttendeeResponse, DocumentResponse, AnalysisRunResponse
)
from backend.app.schemas.decision import DecisionResponse
from backend.app.schemas.task import TaskResponse
from backend.app.schemas.risk import RiskResponse
from backend.app.schemas.blocker import BlockerResponse
from backend.app.schemas.question import QuestionResponse
from backend.app.services.transcript_parser import TranscriptParser, DocumentParseError
from backend.app.services.analysis_pipeline import MeetingAnalysisPipeline, AnalysisPipelineError

router = APIRouter(prefix="/meetings", tags=["Meetings"])

@router.get("", response_model=List[MeetingResponse])
async def list_meetings(
    project_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    status_filter: Optional[MeetingStatus] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Meeting).where(Meeting.organization_id == current_user.organization_id)

    if project_id:
        query = query.where(Meeting.project_id == project_id)
    if client_id:
        query = query.where(Meeting.client_id == client_id)
    if status_filter:
        query = query.where(Meeting.status == status_filter)
    if search:
        s = f"%{search.strip().lower()}%"
        query = query.where(or_(
            func.lower(Meeting.title).like(s),
            func.lower(Meeting.description).like(s),
            func.lower(Meeting.raw_transcript).like(s)
        ))

    query = query.order_by(Meeting.created_at.desc())
    res = await db.execute(query)
    meetings = res.scalars().all()

    items = []
    for m in meetings:
        c_res = await db.execute(select(Client.name).where(Client.id == m.client_id))
        client_name = c_res.scalar_one_or_none()

        p_res = await db.execute(select(Project.name).where(Project.id == m.project_id))
        project_name = p_res.scalar_one_or_none()

        t_count = (await db.execute(select(func.count(Task.id)).where(Task.meeting_id == m.id))).scalar() or 0
        d_count = (await db.execute(select(func.count(Decision.id)).where(Decision.meeting_id == m.id))).scalar() or 0
        a_count = (await db.execute(select(func.count(MeetingAttendee.id)).where(MeetingAttendee.meeting_id == m.id))).scalar() or 0

        resp = MeetingResponse.model_validate(m)
        resp.client_name = client_name
        resp.project_name = project_name
        resp.tasks_count = t_count
        resp.decisions_count = d_count
        resp.attendees_count = a_count
        items.append(resp)

    return items

@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    req: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member)
):
    # Verify project exists
    p_res = await db.execute(
        select(Project).where(
            Project.id == req.project_id,
            Project.organization_id == current_user.organization_id
        )
    )
    project = p_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project not found in organization.")

    meeting = Meeting(
        organization_id=current_user.organization_id,
        project_id=req.project_id,
        client_id=req.client_id,
        title=req.title.strip(),
        description=req.description,
        meeting_date=req.meeting_date,
        timezone=req.timezone or "UTC",
        meeting_type=req.meeting_type,
        language=req.language or "en",
        status=MeetingStatus.DRAFT,
        raw_transcript=req.raw_transcript
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)

    # Add attendees if specified
    if req.attendees:
        for att in req.attendees:
            new_att = MeetingAttendee(
                meeting_id=meeting.id,
                name=att.name.strip(),
                email=att.email,
                role=att.role,
                is_external=att.is_external,
                speaker_label=att.speaker_label
            )
            db.add(new_att)
        await db.commit()

    return MeetingResponse.model_validate(meeting)

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(
        select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.organization_id == current_user.organization_id
        )
    )
    meeting = res.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")

    c_res = await db.execute(select(Client.name).where(Client.id == meeting.client_id))
    client_name = c_res.scalar_one_or_none()

    p_res = await db.execute(select(Project.name).where(Project.id == meeting.project_id))
    project_name = p_res.scalar_one_or_none()

    t_count = (await db.execute(select(func.count(Task.id)).where(Task.meeting_id == meeting.id))).scalar() or 0
    d_count = (await db.execute(select(func.count(Decision.id)).where(Decision.meeting_id == meeting.id))).scalar() or 0

    resp = MeetingResponse.model_validate(meeting)
    resp.client_name = client_name
    resp.project_name = project_name
    resp.tasks_count = t_count
    resp.decisions_count = d_count
    return resp

@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: str,
    req: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member)
):
    res = await db.execute(
        select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.organization_id == current_user.organization_id
        )
    )
    meeting = res.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(meeting, field, value)

    await db.commit()
    await db.refresh(meeting)
    return MeetingResponse.model_validate(meeting)

@router.post("/{meeting_id}/upload", response_model=DocumentResponse)
async def upload_meeting_transcript_document(
    meeting_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member)
):
    """
    Accepts TXT, PDF, and DOCX files.
    Safely parses content, validates size, and appends extracted text to the meeting draft.
    """
    res = await db.execute(
        select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.organization_id == current_user.organization_id
        )
    )
    meeting = res.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")

    filename = file.filename or "unknown"
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    if ext not in ["txt", "pdf", "docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '.{ext}'. Supported formats are: TXT, PDF, DOCX."
        )

    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 15 MB limit."
        )

    # Parse file contents safely
    try:
        if ext == "txt":
            extracted_text = TranscriptParser.parse_txt(file_bytes)
        elif ext == "pdf":
            extracted_text = TranscriptParser.parse_pdf(file_bytes)
        elif ext == "docx":
            extracted_text = TranscriptParser.parse_docx(file_bytes)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")
    except DocumentParseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Append to raw transcript if already exists, else set
    if meeting.raw_transcript and meeting.raw_transcript.strip():
        meeting.raw_transcript = meeting.raw_transcript.strip() + "\n\n" + extracted_text.strip()
    else:
        meeting.raw_transcript = extracted_text.strip()

    # Automatically identify and add detected speakers
    detected_speakers = TranscriptParser.extract_speakers(extracted_text)
    for spk in detected_speakers:
        existing_att = await db.execute(
            select(MeetingAttendee).where(
                MeetingAttendee.meeting_id == meeting.id,
                MeetingAttendee.name == spk
            )
        )
        if not existing_att.scalar_one_or_none():
            db.add(MeetingAttendee(
                meeting_id=meeting.id,
                name=spk,
                speaker_label=spk
            ))

    doc = TranscriptDocument(
        meeting_id=meeting.id,
        filename=filename,
        file_size=file_size,
        mime_type=file.content_type or f"application/{ext}",
        extracted_text=extracted_text
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return DocumentResponse.model_validate(doc)

@router.post("/{meeting_id}/analyze")
async def analyze_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    """
    Triggers AI-powered analysis with real hosted NVIDIA NIM LLM.
    Preserves uncertainty, validates structured Pydantic schema, and extracts outcomes.
    """
    pipeline = MeetingAnalysisPipeline(db=db)
    try:
        updated_meeting = await pipeline.run_analysis(meeting_id=meeting_id, user_id=current_user.id)
        return {
            "success": True,
            "message": "Meeting analysis completed successfully.",
            "meeting_id": updated_meeting.id,
            "status": updated_meeting.status
        }
    except AnalysisPipelineError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=e.message)

@router.get("/{meeting_id}/analysis-status", response_model=Optional[AnalysisRunResponse])
async def get_analysis_status(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(
        select(AnalysisRun).where(AnalysisRun.meeting_id == meeting_id).order_by(AnalysisRun.created_at.desc())
    )
    latest_run = res.scalars().first()
    if not latest_run:
        return None
    return AnalysisRunResponse.model_validate(latest_run)

@router.get("/{meeting_id}/review", response_model=MeetingReviewResponse)
async def get_meeting_review_workspace(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the complete Review Workspace payload (all 6 tabs).
    """
    res = await db.execute(
        select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.organization_id == current_user.organization_id
        )
    )
    meeting = res.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")

    c_res = await db.execute(select(Client.name).where(Client.id == meeting.client_id))
    client_name = c_res.scalar_one_or_none()

    p_res = await db.execute(select(Project.name).where(Project.id == meeting.project_id))
    project_name = p_res.scalar_one_or_none()

    # Attendees
    att_res = await db.execute(select(MeetingAttendee).where(MeetingAttendee.meeting_id == meeting.id))
    attendees = [AttendeeResponse.model_validate(a) for a in att_res.scalars().all()]

    # Documents
    doc_res = await db.execute(select(TranscriptDocument).where(TranscriptDocument.meeting_id == meeting.id))
    documents = [DocumentResponse.model_validate(d) for d in doc_res.scalars().all()]

    # Decisions
    dec_res = await db.execute(select(Decision).where(Decision.meeting_id == meeting.id).order_by(Decision.created_at.asc()))
    decisions = [DecisionResponse.model_validate(d) for d in dec_res.scalars().all()]

    # Tasks
    task_res = await db.execute(select(Task).where(Task.meeting_id == meeting.id).order_by(Task.created_at.asc()))
    tasks = []
    for t in task_res.scalars().all():
        resp = TaskResponse.model_validate(t)
        resp.project_name = project_name
        resp.meeting_title = meeting.title
        tasks.append(resp)

    # Risks
    risk_res = await db.execute(select(Risk).where(Risk.meeting_id == meeting.id).order_by(Risk.created_at.asc()))
    risks = [RiskResponse.model_validate(r) for r in risk_res.scalars().all()]

    # Blockers
    block_res = await db.execute(select(BlockerDependency).where(BlockerDependency.meeting_id == meeting.id).order_by(BlockerDependency.created_at.asc()))
    blockers = [BlockerResponse.model_validate(b) for b in block_res.scalars().all()]

    # Questions
    q_res = await db.execute(select(UnansweredQuestion).where(UnansweredQuestion.meeting_id == meeting.id).order_by(UnansweredQuestion.created_at.asc()))
    questions = [QuestionResponse.model_validate(q) for q in q_res.scalars().all()]

    # Latest analysis run
    run_res = await db.execute(select(AnalysisRun).where(AnalysisRun.meeting_id == meeting.id).order_by(AnalysisRun.created_at.desc()))
    latest_run = run_res.scalars().first()
    latest_run_resp = AnalysisRunResponse.model_validate(latest_run) if latest_run else None

    meeting_resp = MeetingResponse.model_validate(meeting)
    meeting_resp.client_name = client_name
    meeting_resp.project_name = project_name
    meeting_resp.tasks_count = len(tasks)
    meeting_resp.decisions_count = len(decisions)

    return MeetingReviewResponse(
        meeting=meeting_resp,
        attendees=attendees,
        documents=documents,
        summary_data=meeting.summary_data,
        decisions=decisions,
        tasks=tasks,
        risks=risks,
        blockers=blockers,
        questions=questions,
        analysis_warnings=meeting.analysis_warnings or [],
        latest_analysis_run=latest_run_resp
    )

