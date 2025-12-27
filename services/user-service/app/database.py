from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from .config import settings

Base = declarative_base()
engine = create_async_engine(settings.database_url, echo=settings.echo_sql, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def get_session_with_rls(
    user_email: str | None = None,
    user_role: str | None = None,
    tenant_id: str | None = None,
) -> AsyncSession:
    """
    Get database session with RLS (Row-Level Security) context.

    Sets PostgreSQL session variables for RLS policies:
    - app.user_email: Current user's email
    - app.user_role: Current user's role (admin, recruiter, candidate)
    - app.tenant_id: Current user's tenant ID

    These variables are used by RLS policies to filter rows.
    """
    async with AsyncSessionLocal() as session:
        # Set RLS context variables (PostgreSQL session variables)
        if user_email:
            await session.execute(text(f"SET LOCAL app.user_email = '{user_email}';"))
        if user_role:
            await session.execute(text(f"SET LOCAL app.user_role = '{user_role}';"))
        if tenant_id:
            await session.execute(text(f"SET LOCAL app.tenant_id = '{tenant_id}';"))

        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
