import asyncio
import logging
from pathlib import Path
from typing import Any, Union

import aiomisc
from sqlalchemy import MetaData, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from api.eleven_labs.response_models import ErrorResponse
from api.eleven_labs.voice_synth import TextToSpeech, save_audio
from config import settings
from database.models import Slide, AudioDubbing


class TTSConverter(aiomisc.Service):
    def __init__(
            self, api_key: str, voice: str = "Antoni", pguser: str = None, pgpass: str = None,
            host: str = None, database: str = None,
            meta=MetaData, echo: bool = False, save_folder: Union[Path, str] = "files", **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.meta = meta
        self.engine = create_async_engine(
            "postgresql+asyncpg://"
            f"{pguser}:{pgpass}@{host}"
            f"/{database}",
            echo=echo,
        )

        if isinstance(save_folder, str):
            save_folder = Path(save_folder)
        self.save_location = save_folder
        self.api_key = api_key
        self.voice = voice

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

    def create_save_folder(self):
        current_folder = Path(__file__).parent
        save_location = current_folder / self.save_location
        save_location.mkdir(exist_ok=True)

    async def start(self):
        slides_without_audio = await self.get_audioless_slides()
        self.create_save_folder()

        tasks = []
        semaphore = asyncio.Semaphore(10)  # Adjust the number according to your system capabilities
        for slide in slides_without_audio:
            slide: Slide
            filename = f"{slide.id}.mp3"

            if not slide.formatted_content:
                continue

            tasks.append(self.process_single_text(slide.formatted_content, filename, semaphore))
            async_session = async_sessionmaker(self.engine, expire_on_commit=False)
            async with async_session() as session:
                async with session.begin():
                    session.add(AudioDubbing(
                        slide_id=slide.id,
                        audio=filename,
                    ))

        await asyncio.gather(*tasks)

    async def process_single_text(self, text_content, filename, semaphore):
        async with semaphore:
            await self.voice_process(text_content, filename)

    async def voice_process(self, text: str, filename: str):
        tts = TextToSpeech(self.api_key)
        await tts.set_voice(voice_name=self.voice)

        speech_response = await tts.synthesize_speech(text)
        if isinstance(speech_response, ErrorResponse):
            logging.error("Error while synthesizing speech:")
            for error in speech_response.get_errors():
                logging.error(f"{error['msg']} (Type: {error['type']})")

            return

        await save_audio(
            speech_response,
            (self.save_location / filename)
        )
        logging.info(f"Saved audio to {self.save_location / filename}")


    async def stop(self, exception: Exception = None) -> Any:
        await self.engine.dispose()


with aiomisc.entrypoint(
        TTSConverter(
            api_key=settings.e11_labs_key,
            voice="Antoni",
            pguser=settings.PG_LOGIN,
            pgpass=settings.PG_PASS,
            host=settings.PG_HOST,
            database=settings.PG_DATABASE,
        ),

) as loop:
    pass
