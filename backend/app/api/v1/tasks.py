from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_member, require_pm
from backend.app.models.user import User
from backend.app.models.task import Task, TaskStatus, TaskPriority, OwnerStatus, DueDateStatus, TaskComment
from backend.app.models.meeting import Meeting
from backend.app.models.project import Project
from backend.app.models.audit_log import AuditLog
from backend.app.models.integration import ExternalTaskMapping
from backend.app.schemas.task import (
    TaskCreate, TaskUpdate, TaskConfirmOwner, TaskConfirmDueDate,
    TaskResponse, TaskCommentCreate, TaskCommentResponse
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    project_id: Optional[str] = Query(None),
    meeting_id: Optional[str] = Query(None),
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority_filter: Optional[TaskPriority] = Query(None, alias="priority"),
    needs_confirmation: Optional[bool] = Query(None),
    overdue_only: Optional[bool] = Query(False),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Task).join(Project, Task.project_id == Project.id).where(
        Project.organization_id == current_user.organization_id
    )

    if project_id:
        query = query.where(Task.project_id == project_id)
    if meeting_id:
        query = query.where(Task.meeting_id == meeting_id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority_filter:
        query = query.where(Task.priority == priority_filter)
    if needs_confirmation is not None:
        query = query.where(Task.confirmation_required == needs_confirmation)
    if overdue_only:
        today = date.today()
        query = query.where(
            Task.due_date != None,
            Task.due_date < today,
            Task.status.not_in([TaskStatus.COMPLETED, TaskStatus.CANCELLED])
        )
    if search:
        s = f"%{search.strip().lower()}%"
        query = query.where(or_(
            func.lower(Task.title).like(s),
            func.lower(Task.description).like(s),
            func.lower(Task.owner_name).like(s)
        ))

    query = query.order_by(Task.created_at.desc())
    res = await db.execute(query)
    tasks = res.scalars().all()

    today = date.today()
    response_items = []
    for t in tasks:
        p_res = await db.execute(select(Project.name).where(Project.id == t.project_id))
        project_name = p_res.scalar_one_or_none()

        m_res = await db.execute(select(Meeting.title).where(Meeting.id == t.meeting_id))
        meeting_title = m_res.scalar_one_or_none()

        c_count = (await db.execute(select(func.count(TaskComment.id)).where(TaskComment.task_id == t.id))).scalar() or 0

        # External mapping url
        ext_res = await db.execute(select(ExternalTaskMapping.external_url).where(ExternalTaskMapping.task_id == t.id))
        ext_url = ext_res.scalar_one_or_none()

        is_overdue = bool(t.due_date and t.due_date < today and t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED])

        resp = TaskResponse.model_validate(t)
        resp.project_name = project_name
        resp.meeting_title = meeting_title
        resp.comments_count = c_count
        resp.external_sync_url = ext_url
        resp.is_overdue = is_overdue
        response_items.append(resp)

    return response_items

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    req: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member)
):
    task = Task(
        meeting_id=req.meeting_id,
        project_id=req.project_id,
        title=req.title.strip(),
        description=req.description,
        owner_name=req.owner_name,
        owner_user_id=req.owner_user_id,
        owner_status=req.owner_status or OwnerStatus.NOT_STATED,
        due_date=req.due_date,
        due_date_status=req.due_date_status or DueDateStatus.NOT_STATED,
        date_expression=req.date_expression,
        priority=req.priority or TaskPriority.UNSPECIFIED,
        status=req.status or TaskStatus.READY,
        dependencies=req.dependencies or [],
        related_decision_id=req.related_decision_id,
        evidence_passage=req.evidence_passage,
        confirmation_required=req.confirmation_required,
        confirmation_reason=req.confirmation_reason
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskResponse.model_validate(task)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(
        select(Task).join(Project, Task.project_id == Project.id).where(
            Task.id == task_id,
            Project.organization_id == current_user.organization_id
        )
    )
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    p_res = await db.execute(select(Project.name).where(Project.id == task.project_id))
    project_name = p_res.scalar_one_or_none()

    m_res = await db.execute(select(Meeting.title).where(Meeting.id == task.meeting_id))
    meeting_title = m_res.scalar_one_or_none()

    c_count = (await db.execute(select(func.count(TaskComment.id)).where(TaskComment.task_id == task.id))).scalar() or 0
    ext_res = await db.execute(select(ExternalTaskMapping.external_url).where(ExternalTaskMapping.task_id == task.id))
    ext_url = ext_res.scalar_one_or_none()

    today = date.today()
    is_overdue = bool(task.due_date and task.due_date < today and task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED])

    resp = TaskResponse.model_validate(task)
    resp.project_name = project_name
    resp.meeting_title = meeting_title
    resp.comments_count = c_count
    resp.external_sync_url = ext_url
    resp.is_overdue = is_overdue
    return resp

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    req: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member)
):
    res = await db.execute(
        select(Task).join(Project, Task.project_id == Project.id).where(
            Task.id == task_id,
            Project.organization_id == current_user.organization_id
        )
    )
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    old_state = {"status": task.status.value, "owner": task.owner_name, "due_date": str(task.due_date)}
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        entity_type="task",
        entity_id=task.id,
        action="update_task",
        previous_state=old_state,
        new_state={"status": task.status.value, "owner": task.owner_name, "due_date": str(task.due_date)}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(task)
    return TaskResponse.model_validate(task)

@router.post("/{task_id}/confirm-owner", response_model=TaskResponse)
async def confirm_task_owner(
    task_id: str,
    req: TaskConfirmOwner,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    res = await db.execute(
        select(Task).join(Project, Task.project_id == Project.id).where(
            Task.id == task_id,
            Project.organization_id == current_user.organization_id
        )
    )
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    old_owner = task.owner_name
    task.owner_name = req.owner_name.strip()
    task.owner_user_id = req.owner_user_id
    task.owner_status = OwnerStatus.USER_CONFIRMED

    # Re-evaluate confirmation flag
    if task.due_date_status in [DueDateStatus.EXPLICIT, DueDateStatus.RESOLVED_FROM_MEETING_DATE, DueDateStatus.USER_CONFIRMED]:
        task.confirmation_required = False
        task.confirmation_reason = None

    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        entity_type="task",
        entity_id=task.id,
        action="confirm_owner",
        previous_state={"owner": old_owner},
        new_state={"owner": task.owner_name, "confirmed_by": current_user.full_name}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(task)
    return TaskResponse.model_validate(task)

@router.post("/{task_id}/confirm-due-date", response_model=TaskResponse)
async def confirm_task_due_date(
    task_id: str,
    req: TaskConfirmDueDate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    res = await db.execute(
        select(Task).join(Project, Task.project_id == Project.id).where(
            Task.id == task_id,
            Project.organization_id == current_user.organization_id
        )
    )
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    old_due = str(task.due_date)
    task.due_date = req.due_date
    task.due_date_status = DueDateStatus.USER_CONFIRMED

    if task.owner_status in [OwnerStatus.EXPLICIT, OwnerStatus.USER_CONFIRMED]:
        task.confirmation_required = False
        task.confirmation_reason = None

    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        entity_type="task",
        entity_id=task.id,
        action="confirm_due_date",
        previous_state={"due_date": old_due},
        new_state={"due_date": str(task.due_date), "confirmed_by": current_user.full_name}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(task)
    return TaskResponse.model_validate(task)

@router.get("/{task_id}/comments", response_model=List[TaskCommentResponse])
async def list_task_comments(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(TaskComment).where(TaskComment.task_id == task_id).order_by(TaskComment.created_at.asc())
    res = await db.execute(query)
    comments = res.scalars().all()

    items = []
    for c in comments:
        u_res = await db.execute(select(User.full_name).where(User.id == c.user_id))
        user_name = u_res.scalar_one_or_none()
        resp = TaskCommentResponse.model_validate(c)
        resp.user_name = user_name
        items.append(resp)
    return items

@router.post("/{task_id}/comments", response_model=TaskCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_task_comment(
    task_id: str,
    req: TaskCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member)
):
    res = await db.execute(
        select(Task).join(Project, Task.project_id == Project.id).where(
            Task.id == task_id,
            Project.organization_id == current_user.organization_id
        )
    )
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    comment = TaskComment(
        task_id=task.id,
        user_id=current_user.id,
        content=req.content.strip()
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    resp = TaskCommentResponse.model_validate(comment)
    resp.user_name = current_user.full_name
    return resp

