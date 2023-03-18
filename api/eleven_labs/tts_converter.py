import asyncio
import logging
from pathlib import Path
from typing import Union, Any

import aiomisc
from sqlalchemy import MetaData, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from api.eleven_labs.response_models import ErrorResponse
from api.eleven_labs.voice_synth import TextToSpeech, save_audio
from database.models import Slide, AudioDubbing


class TTSConverter(aiomisc.Service):
    def __init__(
            self, api_key: str, voice: str = "Antoni", pguser: str = None, pgpass: str = None,
            host: str = None, database: str = None,
            meta=MetaData, echo: bool = False, save_folder: Union[Path, str] = "files", **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.meta = meta

        # create an engine that connects to the PostgreSQL database
        self.engine = create_async_engine(
            "postgresql+asyncpg://"
            f"{pguser}:{pgpass}@{host}"
            f"/{database}",
            echo=echo,
        )

        # set the save location for the audio files
        if isinstance(save_folder, str):
            save_folder = Path(save_folder)
        self.save_location = save_folder

        # set the API key and voice to be used
        self.api_key = api_key
        self.voice = voice

    async def get_audioless_slides(self):
        """
        Get slides without audio dubbing

        Returns:
            list: List of `Slide` objects without audio dubbing
        """
        async with self.engine.connect() as conn:
            # retrieve all `Slide` objects that have not been dubbed with audio
                stmt = (
                    select(Slide)
                    .outerjoin(AudioDubbing, Slide.id == AudioDubbing.slide_id)
                    .where(AudioDubbing.id == None)
                )
                result = await conn.execute(stmt)
                slides_without_audio = result.all()
                return slides_without_audio

    def create_save_folder(self):
        """
        Create the save folder for the audio files
        """
        current_folder = Path(__file__).parent
        save_location = current_folder / self.save_location
        save_location.mkdir(exist_ok=True)

    async def start(self):
        """
        Start the TTS conversion process for slides without audio dubbing
        """
        # retrieve all `Slide` objects without audio dubbing
        slides_without_audio = await self.get_audioless_slides()
        # create the save folder for the audio files
        self.create_save_folder()

        tasks = []
        # create a semaphore to limit the number of concurrent tasks
        semaphore = asyncio.Semaphore(10)  # Adjust the number according to your system capabilities
        for slide in slides_without_audio:
            slide: Slide
            filename = f"{slide.id}.mp3"

            # skip slides without formatted content
            if not slide.formatted_content:
                continue

            # add the TTS conversion task to the list of tasks to be executed
            tasks.append(self.process_single_text(slide.formatted_content, filename, semaphore))
            # create a new database session and add a reference to the saved audio file
            async_session = async_sessionmaker(self.engine, expire_on_commit=False)
            async with async_session() as session:
                async with session.begin():
                    session.add(AudioDubbing(
                        slide_id=slide.id,
                        audio=filename,
                    ))

        # execute all TTS conversion tasks concurrently
        await asyncio.gather(*tasks)

    async def process_single_text(self, text_content, filename, semaphore):
        """
        Process a single slide's formatted content and save the resulting audio file

        Args:
            text_content (str): The formatted content of the slide
            filename (str): The filename to save the audio as
            semaphore (asyncio.Semaphore): A semaphore to limit the number of concurrent tasks

        :param text_content:
        :param filename:
        :param semaphore:
        :return:
        """
        async with semaphore:
            await self.voice_process(text_content, filename)

    async def voice_process(self, text: str, filename: str):
        """
        Perform text-to-speech conversion on a given text and save the resulting audio file

        Args:
            text (str): The text to be converted to speech
            filename (str): The filename to save the audio as
        """
        # create a new TextToSpeech object using the API key and selected voice
        tts = TextToSpeech(self.api_key)
        await tts.set_voice(voice_name=self.voice)

        # synthesize speech for the given text
        speech_response = await tts.synthesize_speech(text)
        if isinstance(speech_response, ErrorResponse):
            # log any errors that occur during the TTS conversion
            logging.error("Error while synthesizing speech:")
            for error in speech_response.get_errors():
                logging.error(f"{error['msg']} (Type: {error['type']})")

            return

        # save the resulting audio file
        await save_audio(
            speech_response,
            (self.save_location / filename)
        )
        logging.info(f"Saved audio to {self.save_location / filename}")

    async def stop(self, exception: Exception = None) -> Any:
        await self.engine.dispose()
