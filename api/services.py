import logging
from typing import Any

import aiomisc
from sqlalchemy import MetaData, select
from sqlalchemy.ext.asyncio import create_async_engine

from config import settings
from database.models import Slide, AudioDubbing


class TTSConverter(aiomisc.Service):
    def __init__(
            self, pguser: str = None, pgpass: str = None,
            host: str = None, database: str = None,
            meta=MetaData, echo: bool = False, **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.meta = meta
        self.engine = create_async_engine(
            "postgresql+asyncpg://"
            f"{pguser}:{pgpass}@{host}"
            f"/{database}",
            echo=echo,
        )

    async def get_audioless_slides(self):
        """Get slides without audio dubbing"""
        async with self.engine.connect() as conn:
                stmt = (
                    select(Slide)
                    .outerjoin(AudioDubbing, Slide.id == AudioDubbing.slide_id)
                    .where(AudioDubbing.id == None)
                )
                result = await conn.execute(stmt)
                slides_without_audio = result.all()
                return slides_without_audio

    async def start(self):
        slides_without_audio = await self.get_audioless_slides()
        for slide in slides_without_audio:
            print(slide.id)

    async def stop(self, exception: Exception = None) -> Any:
        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        await self.engine.dispose()


with aiomisc.entrypoint(
        TTSConverter(
            pguser=settings.PG_LOGIN,
            pgpass=settings.PG_PASS,
            host=settings.PG_HOST,
            database=settings.PG_DATABASE,
        ),

) as loop:
    pass