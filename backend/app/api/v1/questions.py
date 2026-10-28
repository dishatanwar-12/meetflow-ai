from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_member
from backend.app.models.user import User
from backend.app.models.question import UnansweredQuestion, QuestionStatus
from backend.app.models.meeting import Meeting
from backend.app.schemas.question import QuestionCreate, QuestionUpdate, QuestionAnswer, QuestionResponse

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.get("", response_model=List[QuestionResponse])
async def list_questions(
    meeting_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    status_filter: Optional[QuestionStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(UnansweredQuestion).join(Meeting, UnansweredQuestion.meeting_id == Meeting.id).where(
        Meeting.organization_id == current_user.organization_id
    )

    if meeting_id:
        query = query.where(UnansweredQuestion.meeting_id == meeting_id)
    if project_id:
        query = query.where(UnansweredQuestion.project_id == project_id)
    if status_filter:
        query = query.where(UnansweredQuestion.status == status_filter)

    query = query.order_by(UnansweredQuestion.created_at.desc())
    res = await db.execute(query)
    questions = res.scalars().all()

    items = []
    for q in questions:
        answered_name = None
        if q.answered_by_id:
            u_res = await db.execute(select(User.full_name).where(User.id == q.answered_by_id))
            answered_name = u_res.scalar_one_or_none()

        resp = QuestionResponse.model_validate(q)
        resp.answered_by_name = answered_name
        items.append(resp)
    return items

@router.post("/{question_id}/answer", response_model=QuestionResponse)
async def answer_question(
    question_id: str,
    req: QuestionAnswer,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_member)
):
    res = await db.execute(
        select(UnansweredQuestion).join(Meeting, UnansweredQuestion.meeting_id == Meeting.id).where(
            UnansweredQuestion.id == question_id,
            Meeting.organization_id == current_user.organization_id
        )
    )
    question = res.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")

    question.answer = req.answer.strip()
    question.status = QuestionStatus.ANSWERED
    question.answered_by_id = current_user.id
    question.answered_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(question)

    resp = QuestionResponse.model_validate(question)
    resp.answered_by_name = current_user.full_name
    return resp

