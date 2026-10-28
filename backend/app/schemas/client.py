from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

class ClientBase(BaseModel):
    name: str
    organization_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    organization_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    is_archived: Optional[bool] = None

class ClientResponse(ClientBase):
    id: str
    organization_id: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    projects_count: Optional[int] = 0

    class Config:
        from_attributes = True

