from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_pm
from backend.app.models.user import User
from backend.app.models.decision import Decision, DecisionStatus
from backend.app.models.meeting import Meeting
from backend.app.models.audit_log import AuditLog
from backend.app.schemas.decision import DecisionCreate, DecisionUpdate, DecisionResponse

router = APIRouter(prefix="/decisions", tags=["Decisions"])

@router.get("", response_model=List[DecisionResponse])
async def list_decisions(
    meeting_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    status_filter: Optional[DecisionStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Decision).join(Meeting, Decision.meeting_id == Meeting.id).where(
        Meeting.organization_id == current_user.organization_id
    )

    if meeting_id:
        query = query.where(Decision.meeting_id == meeting_id)
    if project_id:
        query = query.where(Decision.project_id == project_id)
    if status_filter:
        query = query.where(Decision.status == status_filter)

    query = query.order_by(Decision.created_at.desc())
    res = await db.execute(query)
    return [DecisionResponse.model_validate(d) for d in res.scalars().all()]

@router.put("/{decision_id}", response_model=DecisionResponse)
async def update_decision(
    decision_id: str,
    req: DecisionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    res = await db.execute(
        select(Decision).join(Meeting, Decision.meeting_id == Meeting.id).where(
            Decision.id == decision_id,
            Meeting.organization_id == current_user.organization_id
        )
    )
    decision = res.scalar_one_or_none()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found.")

    old_state = {"status": decision.status.value, "title": decision.title}
    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(decision, field, value)

    # Log audit
    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        entity_type="decision",
        entity_id=decision.id,
        action="update_decision",
        previous_state=old_state,
        new_state={"status": decision.status.value, "title": decision.title}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(decision)
    return DecisionResponse.model_validate(decision)

@router.post("/{decision_id}/confirm", response_model=DecisionResponse)
async def confirm_decision(
    decision_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    res = await db.execute(
        select(Decision).join(Meeting, Decision.meeting_id == Meeting.id).where(
            Decision.id == decision_id,
            Meeting.organization_id == current_user.organization_id
        )
    )
    decision = res.scalar_one_or_none()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found.")

    decision.status = DecisionStatus.CONFIRMED
    decision.confirmation_required = False
    decision.owner_or_approver = current_user.full_name

    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        entity_type="decision",
        entity_id=decision.id,
        action="confirm_decision",
        new_state={"status": "confirmed", "confirmed_by": current_user.full_name}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(decision)
    return DecisionResponse.model_validate(decision)

@router.post("/{decision_id}/reject", response_model=DecisionResponse)
async def reject_decision(
    decision_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    res = await db.execute(
        select(Decision).join(Meeting, Decision.meeting_id == Meeting.id).where(
            Decision.id == decision_id,
            Meeting.organization_id == current_user.organization_id
        )
    )
    decision = res.scalar_one_or_none()
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found.")

    decision.status = DecisionStatus.REJECTED
    decision.confirmation_required = False

    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        entity_type="decision",
        entity_id=decision.id,
        action="reject_decision",
        new_state={"status": "rejected"}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(decision)
    return DecisionResponse.model_validate(decision)

