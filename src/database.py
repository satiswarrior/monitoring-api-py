from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from src.config import settings

# Асинхронные engine и фабрика сессий
# - echo=True полезно в разработке; убрать в продакшене
engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency. Yields an async SQLAlchemy session."""
    async with async_session() as session:
        yield session
