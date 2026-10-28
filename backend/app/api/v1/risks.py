from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_member
from backend.app.models.user import User
from backend.app.models.risk import Risk, RiskStatus
from backend.app.models.meeting import Meeting
from backend.app.schemas.risk import RiskCreate, RiskUpdate, RiskResponse

router = APIRouter(prefix="/risks", tags=["Risks"])

@router.get("", response_model=List[RiskResponse])
async def list_risks(
    meeting_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    status_filter: Optional[RiskStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Risk).join(Meeting, Risk.meeting_id == Meeting.id).where(
        Meeting.organization_id == current_user.organization_id
    )

    if meeting_id:
        query = query.where(Risk.meeting_id == meeting_id)
    if project_id:
        query = query.where(Risk.project_id == project_id)
    if status_filter:
        query = query.where(Risk.status == status_filter)

    query = query.order_by(Risk.created_at.desc())
    res = await db.execute(query)
    return [RiskResponse.model_validate(r) for r in res.scalars().all()]

@router.put("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: str,
    req: RiskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member)
):
    res = await db.execute(
        select(Risk).join(Meeting, Risk.meeting_id == Meeting.id).where(
            Risk.id == risk_id,
            Meeting.organization_id == current_user.organization_id
        )
    )
    risk = res.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found.")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(risk, field, value)

    await db.commit()
    await db.refresh(risk)
    return RiskResponse.model_validate(risk)

@router.post("/{risk_id}/resolve", response_model=RiskResponse)
async def resolve_risk(
    risk_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member)
):
    res = await db.execute(
        select(Risk).join(Meeting, Risk.meeting_id == Meeting.id).where(
            Risk.id == risk_id,
            Meeting.organization_id == current_user.organization_id
        )
    )
    risk = res.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found.")

    risk.status = RiskStatus.MITIGATED
    await db.commit()
    await db.refresh(risk)
    return RiskResponse.model_validate(risk)

