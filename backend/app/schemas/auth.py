from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from backend.app.models.user import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserResponse"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: str
    role: Optional[UserRole] = UserRole.MEMBER

class UserResponse(BaseModel):
    id: str
    organization_id: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

Token.model_rebuild()

