# Init database session
from typing import Union, Any

from sqlalchemy import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

import settings

from .models.base import BaseModel
from .models.user import User, get_user, create_user


def create_async_engine(url: Union[URL, str]) -> AsyncEngine:
    return _create_async_engine(
        settings.DB_CONNECTION_STRING,
        echo=True,
        pool_pre_ping=True
    )


@DeprecationWarning
async def proceed_schemas(engine: AsyncEngine, metadata) -> None:
    # async with engine.begin() as conn:
    #   await conn.run_sync(metadata.create_all)
    ...


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession | Any] | async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
