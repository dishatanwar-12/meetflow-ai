from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re

from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.core.dependencies import get_current_user
from backend.app.models.user import User, Organization, UserRole
from backend.app.schemas.auth import LoginRequest, RegisterRequest, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if email is already taken
    existing_user = await db.execute(select(User).where(User.email == req.email.lower()))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Slugify organization name
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", req.organization_name.strip().lower()).strip("-")
    if not slug:
        slug = "workspace"

    # Check or create organization
    org_res = await db.execute(select(Organization).where(Organization.slug == slug))
    org = org_res.scalar_one_or_none()
    if not org:
        org = Organization(name=req.organization_name.strip(), slug=slug)
        db.add(org)
        await db.commit()
        await db.refresh(org)

    # First user in an organization is automatically an admin
    user_count_res = await db.execute(select(User).where(User.organization_id == org.id))
    is_first_user = len(user_count_res.scalars().all()) == 0
    assigned_role = UserRole.ADMIN if is_first_user else (req.role or UserRole.MEMBER)

    new_user = User(
        organization_id=org.id,
        email=req.email.lower(),
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name.strip(),
        role=assigned_role,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token(subject=new_user.id)
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=Token)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.email == req.email.lower()))
    user = res.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    token = create_access_token(subject=user.id)
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

