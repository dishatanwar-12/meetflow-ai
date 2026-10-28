from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user, require_pm
from backend.app.models.user import User
from backend.app.models.client import Client
from backend.app.models.project import Project
from backend.app.schemas.client import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.get("", response_model=List[ClientResponse])
async def list_clients(
    search: Optional[str] = Query(None, description="Search client name or industry"),
    include_archived: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Client).where(Client.organization_id == current_user.organization_id)
    if not include_archived:
        query = query.where(Client.is_archived == False)

    if search:
        s = f"%{search.strip().lower()}%"
        query = query.where(or_(
            func.lower(Client.name).like(s),
            func.lower(Client.organization_name).like(s),
            func.lower(Client.industry).like(s)
        ))

    query = query.order_by(Client.created_at.desc())
    res = await db.execute(query)
    clients = res.scalars().all()

    # Calculate project counts
    response_items = []
    for c in clients:
        p_count_res = await db.execute(select(func.count(Project.id)).where(Project.client_id == c.id))
        p_count = p_count_res.scalar() or 0
        resp = ClientResponse.model_validate(c)
        resp.projects_count = p_count
        response_items.append(resp)

    return response_items

@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    req: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    client = Client(
        organization_id=current_user.organization_id,
        name=req.name.strip(),
        organization_name=req.organization_name,
        contact_name=req.contact_name,
        contact_email=req.contact_email,
        industry=req.industry,
        website=req.website,
        notes=req.notes
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return ClientResponse.model_validate(client)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.organization_id == current_user.organization_id
        )
    )
    client = res.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found.")

    p_count_res = await db.execute(select(func.count(Project.id)).where(Project.client_id == client.id))
    resp = ClientResponse.model_validate(client)
    resp.projects_count = p_count_res.scalar() or 0
    return resp

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    req: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    res = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.organization_id == current_user.organization_id
        )
    )
    client = res.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found.")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    await db.commit()
    await db.refresh(client)
    return ClientResponse.model_validate(client)

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_pm)
):
    res = await db.execute(
        select(Client).where(
            Client.id == client_id,
            Client.organization_id == current_user.organization_id
        )
    )
    client = res.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found.")

    client.is_archived = True
    await db.commit()

