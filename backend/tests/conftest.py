import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.core.security import get_password_hash, create_access_token
from backend.app.models.user import User, Organization, UserRole

# Use an in-memory SQLite database for test isolation
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def test_org(db_session: AsyncSession) -> Organization:
    org = Organization(name="Acme Corp", slug="acme-corp")
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    return org

@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        organization_id=test_org.id,
        email="admin@acme.com",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Admin Alice",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function")
async def pm_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        organization_id=test_org.id,
        email="pm@acme.com",
        hashed_password=get_password_hash("PMPass123!"),
        full_name="PM Peter",
        role=UserRole.PROJECT_MANAGER,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function")
async def member_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        organization_id=test_org.id,
        email="member@acme.com",
        hashed_password=get_password_hash("MemberPass123!"),
        full_name="Member Mike",
        role=UserRole.MEMBER,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function")
async def viewer_user(db_session: AsyncSession, test_org: Organization) -> User:
    user = User(
        organization_id=test_org.id,
        email="viewer@acme.com",
        hashed_password=get_password_hash("ViewerPass123!"),
        full_name="Viewer Victor",
        role=UserRole.VIEWER,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers():
    def _headers(user: User):
        token = create_access_token(subject=user.id)
        return {"Authorization": f"Bearer {token}"}
    return _headers

