from typing import List, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.models.meeting import Meeting, MeetingStatus
from backend.app.models.project import Project
from backend.app.models.client import Client
from backend.app.models.task import Task, TaskStatus, OwnerStatus, DueDateStatus
from backend.app.models.risk import Risk, RiskStatus
from backend.app.models.blocker import BlockerDependency
from backend.app.models.question import UnansweredQuestion, QuestionStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    org_id = current_user.organization_id
    today = date.today()

    # 1. Meeting counts
    total_meetings = (await db.execute(
        select(func.count(Meeting.id)).where(Meeting.organization_id == org_id)
    )).scalar() or 0

    analyzed_meetings = (await db.execute(
        select(func.count(Meeting.id)).where(
            Meeting.organization_id == org_id,
            Meeting.status == MeetingStatus.REVIEWED
        )
    )).scalar() or 0

    # 2. Task metrics
    base_task_query = select(Task).join(Project, Task.project_id == Project.id).where(
        Project.organization_id == org_id
    )

    total_tasks = (await db.execute(
        select(func.count(Task.id)).join(Project, Task.project_id == Project.id).where(
            Project.organization_id == org_id
        )
    )).scalar() or 0

    open_tasks = (await db.execute(
        select(func.count(Task.id)).join(Project, Task.project_id == Project.id).where(
            Project.organization_id == org_id,
            Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.CANCELLED])
        )
    )).scalar() or 0

    tasks_needing_owner = (await db.execute(
        select(func.count(Task.id)).join(Project, Task.project_id == Project.id).where(
            Project.organization_id == org_id,
            Task.owner_status.in_([OwnerStatus.NOT_STATED, OwnerStatus.AMBIGUOUS, OwnerStatus.CONFLICTING])
        )
    )).scalar() or 0

    tasks_needing_deadline = (await db.execute(
        select(func.count(Task.id)).join(Project, Task.project_id == Project.id).where(
            Project.organization_id == org_id,
            Task.due_date_status.in_([DueDateStatus.NOT_STATED, DueDateStatus.AMBIGUOUS, DueDateStatus.CONFLICTING])
        )
    )).scalar() or 0

    overdue_tasks = (await db.execute(
        select(func.count(Task.id)).join(Project, Task.project_id == Project.id).where(
            Project.organization_id == org_id,
            Task.due_date != None,
            Task.due_date < today,
            Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.CANCELLED])
        )
    )).scalar() or 0

    # 3. Risks, Blockers, Questions
    unresolved_risks = (await db.execute(
        select(func.count(Risk.id)).join(Meeting, Risk.meeting_id == Meeting.id).where(
            Meeting.organization_id == org_id,
            Risk.status == RiskStatus.OPEN
        )
    )).scalar() or 0

    open_blockers = (await db.execute(
        select(func.count(BlockerDependency.id)).join(Meeting, BlockerDependency.meeting_id == Meeting.id).where(
            Meeting.organization_id == org_id,
            BlockerDependency.is_resolved == False
        )
    )).scalar() or 0

    open_questions = (await db.execute(
        select(func.count(UnansweredQuestion.id)).join(Meeting, UnansweredQuestion.meeting_id == Meeting.id).where(
            Meeting.organization_id == org_id,
            UnansweredQuestion.status == QuestionStatus.OPEN
        )
    )).scalar() or 0

    # 4. Recent projects
    p_res = await db.execute(
        select(Project).where(Project.organization_id == org_id).order_by(Project.updated_at.desc()).limit(5)
    )
    recent_projects = []
    for p in p_res.scalars().all():
        c_res = await db.execute(select(Client.name).where(Client.id == p.client_id))
        client_name = c_res.scalar_one_or_none()
        recent_projects.append({
            "id": p.id,
            "name": p.name,
            "client_name": client_name,
            "status": p.status.value,
            "updated_at": p.updated_at.isoformat()
        })

    # 5. Recent meetings
    m_res = await db.execute(
        select(Meeting).where(Meeting.organization_id == org_id).order_by(Meeting.created_at.desc()).limit(5)
    )
    recent_meetings = []
    for m in m_res.scalars().all():
        recent_meetings.append({
            "id": m.id,
            "title": m.title,
            "status": m.status.value,
            "meeting_date": m.meeting_date.isoformat() if m.meeting_date else None,
            "created_at": m.created_at.isoformat()
        })

    return {
        "total_meetings": total_meetings,
        "analyzed_meetings": analyzed_meetings,
        "total_tasks": total_tasks,
        "open_tasks": open_tasks,
        "tasks_needing_owner_confirmation": tasks_needing_owner,
        "tasks_needing_deadline_confirmation": tasks_needing_deadline,
        "overdue_tasks": overdue_tasks,
        "unresolved_risks": unresolved_risks,
        "open_blockers": open_blockers,
        "open_questions": open_questions,
        "recent_projects": recent_projects,
        "recent_meetings": recent_meetings
    }

