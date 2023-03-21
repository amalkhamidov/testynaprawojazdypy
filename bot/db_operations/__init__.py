import asyncio
from dataclasses import dataclass
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload

from config import settings
from database.models import Module, Slide


@dataclass
class DBUsage:
    engine = None
    async_session = None

    async def init(self) -> None:
        self.engine = create_async_engine(
            "postgresql+asyncpg://"
            f"{settings.PG_LOGIN}:{settings.PG_PASS}@{settings.PG_HOST}"
            f"/{settings.PG_DATABASE}",
        )

        # async_sessionmaker: a factory for new AsyncSession objects.
        # expire_on_commit - don't expire objects after transaction commit
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def get_modules(self) -> Optional[List[Module]]:
        async with self.async_session() as session:
            stmt = select(Module)  # .options(selectinload(Module.slides))
            result = await session.execute(stmt)

            return [i for i in result.scalars()]

    async def get_slides(self, slide_id: int):
        async with self.async_session() as session:
            slides = await session.execute(select(Slide).where(Slide.module_id == slide_id))
            return [i for i in slides.scalars()]
