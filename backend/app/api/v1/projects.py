from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_pm
from backend.app.models.user import User
from backend.app.models.project import Project, ProjectStatus
from backend.app.models.client import Client
from backend.app.models.meeting import Meeting
from backend.app.models.task import Task
from backend.app.models.decision import Decision, DecisionStatus
from backend.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, TimelineItem, ContradictionConflict

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    client_id: Optional[str] = Query(None),
    status_filter: Optional[ProjectStatus] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Project).where(Project.organization_id == current_user.organization_id)

    if client_id:
        query = query.where(Project.client_id == client_id)
    if status_filter:
        query = query.where(Project.status == status_filter)
    if search:
        s = f"%{search.strip().lower()}%"
        query = query.where(or_(
            func.lower(Project.name).like(s),
            func.lower(Project.description).like(s)
        ))

    query = query.order_by(Project.created_at.desc())
    res = await db.execute(query)
    projects = res.scalars().all()

    response_items = []
    for p in projects:
        # Client name
        c_res = await db.execute(select(Client.name).where(Client.id == p.client_id))
        client_name = c_res.scalar_one_or_none()

        # Manager name
        manager_name = None
        if p.manager_id:
            m_res = await db.execute(select(User.full_name).where(User.id == p.manager_id))
            manager_name = m_res.scalar_one_or_none()

        # Counts
        m_count = (await db.execute(select(func.count(Meeting.id)).where(Meeting.project_id == p.id))).scalar() or 0
        t_count = (await db.execute(select(func.count(Task.id)).where(Task.project_id == p.id))).scalar() or 0

        resp = ProjectResponse.model_validate(p)
        resp.client_name = client_name
        resp.manager_name = manager_name
        resp.meetings_count = m_count
        resp.tasks_count = t_count
        response_items.append(resp)

    return response_items

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    req: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    # Verify client exists within organization
    c_res = await db.execute(
        select(Client).where(
            Client.id == req.client_id,
            Client.organization_id == current_user.organization_id
        )
    )
    if not c_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client not found in organization.")

    project = Project(
        organization_id=current_user.organization_id,
        client_id=req.client_id,
        name=req.name.strip(),
        description=req.description,
        goals=req.goals,
        manager_id=req.manager_id or current_user.id,
        start_date=req.start_date,
        target_date=req.target_date,
        status=req.status or ProjectStatus.ACTIVE,
        tags=req.tags or []
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == current_user.organization_id
        )
    )
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    c_res = await db.execute(select(Client.name).where(Client.id == project.client_id))
    client_name = c_res.scalar_one_or_none()

    manager_name = None
    if project.manager_id:
        m_res = await db.execute(select(User.full_name).where(User.id == project.manager_id))
        manager_name = m_res.scalar_one_or_none()

    m_count = (await db.execute(select(func.count(Meeting.id)).where(Meeting.project_id == project.id))).scalar() or 0
    t_count = (await db.execute(select(func.count(Task.id)).where(Task.project_id == project.id))).scalar() or 0

    resp = ProjectResponse.model_validate(project)
    resp.client_name = client_name
    resp.manager_name = manager_name
    resp.meetings_count = m_count
    resp.tasks_count = t_count
    return resp

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    req: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    res = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == current_user.organization_id
        )
    )
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)

@router.get("/{project_id}/timeline", response_model=List[TimelineItem])
async def get_project_timeline(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns an aggregated chronological timeline of meetings, decisions, and tasks
    created across the project lifecycle.
    """
    res = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == current_user.organization_id
        )
    )
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    timeline: List[TimelineItem] = []

    # 1. Meetings
    meetings_res = await db.execute(select(Meeting).where(Meeting.project_id == project_id).order_by(Meeting.created_at.desc()))
    meetings = meetings_res.scalars().all()
    meeting_map = {m.id: m.title for m in meetings}

    for m in meetings:
        timeline.append(TimelineItem(
            id=m.id,
            type="meeting",
            title=f"Meeting: {m.title}",
            timestamp=m.meeting_date or m.created_at,
            status=m.status.value if hasattr(m.status, "value") else str(m.status),
            details=m.description or f"Meeting Type: {m.meeting_type}",
            meeting_id=m.id,
            meeting_title=m.title
        ))

    # 2. Decisions
    decisions_res = await db.execute(select(Decision).where(Decision.project_id == project_id).order_by(Decision.created_at.desc()))
    for d in decisions_res.scalars().all():
        timeline.append(TimelineItem(
            id=d.id,
            type="decision",
            title=f"Decision: {d.title}",
            timestamp=d.created_at,
            status=d.status.value if hasattr(d.status, "value") else str(d.status),
            details=d.evidence_passage or d.description,
            meeting_id=d.meeting_id,
            meeting_title=meeting_map.get(d.meeting_id)
        ))

    # 3. Tasks
    tasks_res = await db.execute(select(Task).where(Task.project_id == project_id).order_by(Task.created_at.desc()))
    for t in tasks_res.scalars().all():
        due_str = f" | Due: {t.due_date}" if t.due_date else ""
        owner_str = f" | Owner: {t.owner_name}" if t.owner_name else ""
        timeline.append(TimelineItem(
            id=t.id,
            type="task",
            title=f"Task: {t.title}",
            timestamp=t.created_at,
            status=t.status.value if hasattr(t.status, "value") else str(t.status),
            details=f"Status: {t.status}{owner_str}{due_str}",
            meeting_id=t.meeting_id,
            meeting_title=meeting_map.get(t.meeting_id)
        ))

    # Sort descending by timestamp
    timeline.sort(key=lambda x: x.timestamp, reverse=True)
    return timeline

@router.get("/{project_id}/conflicts", response_model=List[ContradictionConflict])
async def detect_project_conflicts(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Detects potential contradictions between multiple meetings within the project:
    e.g., conflicting deadlines, conflicting decisions, or contradictory commitments.
    Never assumes the later statement automatically supersedes the earlier one.
    """
    meetings_res = await db.execute(
        select(Meeting).where(Meeting.project_id == project_id).order_by(Meeting.meeting_date.asc())
    )
    meetings = meetings_res.scalars().all()
    if len(meetings) < 2:
        return []

    conflicts: List[ContradictionConflict] = []

    # 1. Collect decisions across meetings and compare titles/topics
    decisions_res = await db.execute(
        select(Decision).where(Decision.project_id == project_id)
    )
    decisions = decisions_res.scalars().all()

    for i in range(len(decisions)):
        for j in range(i + 1, len(decisions)):
            d1 = decisions[i]
            d2 = decisions[j]
            if d1.meeting_id != d2.meeting_id:
                # Compare title similarity or conflicting status
                words1 = set(d1.title.lower().split())
                words2 = set(d2.title.lower().split())
                common = words1.intersection(words2)
                # If they discuss the same core words and one is disputed or superseded
                if len(common) >= 3 and (d1.status != d2.status or "not" in d2.title.lower() or "cancel" in d2.title.lower()):
                    m1 = next((m for m in meetings if m.id == d1.meeting_id), None)
                    m2 = next((m for m in meetings if m.id == d2.meeting_id), None)
                    conflicts.append(ContradictionConflict(
                        id=f"conflict-dec-{d1.id}-{d2.id}",
                        type="decision_conflict",
                        title=f"Potential Decision Discrepancy: '{d1.title}'",
                        description=f"Meeting '{m1.title if m1 else ''}' marked this decision as {d1.status}, while meeting '{m2.title if m2 else ''}' marked related decision '{d2.title}' as {d2.status}.",
                        first_meeting_title=m1.title if m1 else "Earlier Meeting",
                        first_meeting_date=m1.meeting_date if m1 else None,
                        first_statement=d1.evidence_passage or d1.title,
                        second_meeting_title=m2.title if m2 else "Later Meeting",
                        second_meeting_date=m2.meeting_date if m2 else None,
                        second_statement=d2.evidence_passage or d2.title,
                        suggested_resolution="Confirm with the project manager whether the second decision officially supersedes the first.",
                        status="unresolved"
                    ))

    # 2. Check for task deadline conflicts
    tasks_res = await db.execute(select(Task).where(Task.project_id == project_id))
    tasks = tasks_res.scalars().all()
    for i in range(len(tasks)):
        for j in range(i + 1, len(tasks)):
            t1 = tasks[i]
            t2 = tasks[j]
            if t1.meeting_id != t2.meeting_id and t1.title.strip().lower() == t2.title.strip().lower():
                if t1.due_date and t2.due_date and t1.due_date != t2.due_date:
                    m1 = next((m for m in meetings if m.id == t1.meeting_id), None)
                    m2 = next((m for m in meetings if m.id == t2.meeting_id), None)
                    conflicts.append(ContradictionConflict(
                        id=f"conflict-task-{t1.id}-{t2.id}",
                        type="deadline_conflict",
                        title=f"Conflicting Task Deadline: '{t1.title}'",
                        description=f"Task '{t1.title}' was scheduled for {t1.due_date} in '{m1.title if m1 else ''}', but listed for {t2.due_date} in '{m2.title if m2 else ''}'.",
                        first_meeting_title=m1.title if m1 else "Earlier Meeting",
                        first_meeting_date=m1.meeting_date if m1 else None,
                        first_statement=f"Deadline: {t1.due_date} ({t1.date_expression or 'stated'})",
                        second_meeting_title=m2.title if m2 else "Later Meeting",
                        second_meeting_date=m2.meeting_date if m2 else None,
                        second_statement=f"Deadline: {t2.due_date} ({t2.date_expression or 'stated'})",
                        suggested_resolution="Confirm the current binding deadline with the task owner.",
                        status="unresolved"
                    ))

    return conflicts

