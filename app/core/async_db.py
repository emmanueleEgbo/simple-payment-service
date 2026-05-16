from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

from app.core.config import settings

# Load environment variable from `.env` file
load_dotenv()

# Connection string for the async database
ASYNC_DATABASE_URL = settings.async_database_url