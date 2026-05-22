
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

from app.core.config import settings


# Load environment variable from `.env` file
load_dotenv()


async_engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    future=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


Base = declarative_base()


# FastAPI dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session