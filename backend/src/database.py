from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import text
from typing import AsyncGenerator
from .config import config

# Create async engine
engine = create_async_engine(
    config.database_url,
    echo=config.database_echo,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


# Database dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Database initialization
async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Verify tables exist
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        )
        tables = [row[0] for row in result.fetchall()]
        print(f"Database initialized with tables: {tables}")


# Database cleanup
async def close_db():
    await engine.dispose()
