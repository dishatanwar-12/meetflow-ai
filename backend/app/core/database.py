from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.app.core.config import settings

# Construct engine args based on DB dialect
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining database sessions per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initializes database tables directly (useful for local dev/testing)."""
    # Import all models before calling create_all
    import backend.app.models.user # noqa
    import backend.app.models.client # noqa
    import backend.app.models.project # noqa
    import backend.app.models.meeting # noqa
    import backend.app.models.decision # noqa
    import backend.app.models.task # noqa
    import backend.app.models.risk # noqa
    import backend.app.models.blocker # noqa
    import backend.app.models.question # noqa
    import backend.app.models.audit_log # noqa
    import backend.app.models.integration # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

