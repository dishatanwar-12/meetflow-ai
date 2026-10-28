from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_pm
from backend.app.models.user import User
from backend.app.models.meeting import Meeting
from backend.app.models.project import Project
from backend.app.models.client import Client
from backend.app.models.decision import Decision
from backend.app.models.task import Task
from backend.app.models.risk import Risk
from backend.app.models.question import UnansweredQuestion
from backend.app.schemas.export import (
    GitHubExportPreviewResponse, GitHubExportRequest, GitHubExportResponse
)
from backend.app.services.export_service import ExportService
from backend.app.services.github_tracker import GitHubTrackerService

router = APIRouter(prefix="/exports", tags=["Exports & Integrations"])

async def _fetch_meeting_export_data(meeting_id: str, organization_id: str, db: AsyncSession):
    res = await db.execute(
        select(Meeting).where(
            Meeting.id == meeting_id,
            Meeting.organization_id == organization_id
        )
    )
    meeting = res.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")

    c_res = await db.execute(select(Client.name).where(Client.id == meeting.client_id))
    client_name = c_res.scalar_one_or_none() or "Unknown Client"

    p_res = await db.execute(select(Project.name).where(Project.id == meeting.project_id))
    project_name = p_res.scalar_one_or_none() or "Unknown Project"

    dec_res = await db.execute(select(Decision).where(Decision.meeting_id == meeting.id).order_by(Decision.created_at.asc()))
    decisions = dec_res.scalars().all()

    t_res = await db.execute(select(Task).where(Task.meeting_id == meeting.id).order_by(Task.created_at.asc()))
    tasks = t_res.scalars().all()

    r_res = await db.execute(select(Risk).where(Risk.meeting_id == meeting.id).order_by(Risk.created_at.asc()))
    risks = r_res.scalars().all()

    q_res = await db.execute(select(UnansweredQuestion).where(UnansweredQuestion.meeting_id == meeting.id).order_by(UnansweredQuestion.created_at.asc()))
    questions = q_res.scalars().all()

    return meeting, client_name, project_name, decisions, tasks, risks, questions

@router.get("/meetings/{meeting_id}/csv")
async def export_meeting_csv(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting, _, _, _, tasks, _, _ = await _fetch_meeting_export_data(meeting_id, current_user.organization_id, db)
    csv_content = ExportService.generate_tasks_csv(tasks=tasks, meeting_title=meeting.title)
    filename = f"meetflow-tasks-{meeting.id[:8]}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/meetings/{meeting_id}/json")
async def export_meeting_json(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting, client_name, project_name, decisions, tasks, risks, questions = await _fetch_meeting_export_data(
        meeting_id, current_user.organization_id, db
    )

    meeting_payload = {
        "id": meeting.id,
        "title": meeting.title,
        "client": client_name,
        "project": project_name,
        "meeting_date": meeting.meeting_date.isoformat() if meeting.meeting_date else None,
        "timezone": meeting.timezone,
        "summary": meeting.summary_data,
        "decisions": [
            {
                "id": d.id, "title": d.title, "description": d.description,
                "status": d.status.value, "owner_approver": d.owner_or_approver,
                "evidence": d.evidence_passage
            } for d in decisions
        ],
        "action_items": [
            {
                "id": t.id, "title": t.title, "description": t.description,
                "owner": t.owner_name, "owner_status": t.owner_status.value,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "due_date_status": t.due_date_status.value,
                "date_expression": t.date_expression,
                "priority": t.priority.value, "status": t.status.value,
                "evidence": t.evidence_passage, "confirmation_required": t.confirmation_required
            } for t in tasks
        ],
        "risks": [
            {
                "id": r.id, "description": r.description, "impact": r.potential_impact,
                "mitigation": r.mitigation, "evidence": r.evidence_passage
            } for r in risks
        ],
        "unanswered_questions": [
            {
                "id": q.id, "question": q.question, "reason": q.clarification_reason,
                "status": q.status.value, "answer": q.answer
            } for q in questions
        ]
    }

    json_str = ExportService.generate_meeting_json(meeting_payload)
    filename = f"meetflow-outcomes-{meeting.id[:8]}.json"

    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/meetings/{meeting_id}/markdown", response_class=PlainTextResponse)
async def export_meeting_markdown(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting, _, _, decisions, tasks, risks, questions = await _fetch_meeting_export_data(
        meeting_id, current_user.organization_id, db
    )
    md_content = ExportService.generate_meeting_markdown(
        meeting=meeting,
        decisions=decisions,
        tasks=tasks,
        risks=risks,
        questions=questions
    )
    return md_content

@router.get("/meetings/{meeting_id}/pdf")
async def export_meeting_pdf(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting, client_name, project_name, decisions, tasks, risks, questions = await _fetch_meeting_export_data(
        meeting_id, current_user.organization_id, db
    )
    pdf_bytes = ExportService.generate_meeting_pdf(
        meeting=meeting,
        client_name=client_name,
        project_name=project_name,
        decisions=decisions,
        tasks=tasks,
        risks=risks,
        questions=questions
    )
    filename = f"meetflow-report-{meeting.id[:8]}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/meetings/{meeting_id}/github/preview", response_model=GitHubExportPreviewResponse)
async def preview_github_export(
    meeting_id: str,
    repository: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    res = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.organization_id == current_user.organization_id)
    )
    meeting = res.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")

    t_res = await db.execute(select(Task).where(Task.meeting_id == meeting.id))
    tasks = t_res.scalars().all()

    tracker = GitHubTrackerService(db=db)
    return await tracker.preview_tasks_for_export(repository=repository, tasks=tasks)

@router.post("/meetings/{meeting_id}/github/export", response_model=GitHubExportResponse)
async def execute_github_export(
    meeting_id: str,
    req: GitHubExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    res = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.organization_id == current_user.organization_id)
    )
    meeting = res.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")

    tracker = GitHubTrackerService(db=db)
    try:
        return await tracker.export_tasks_to_github(request=req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

