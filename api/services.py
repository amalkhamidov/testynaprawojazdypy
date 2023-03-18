import aiomisc

from api.eleven_labs.tts_converter import TTSConverter
from config import settings

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
