import tempfile
from pathlib import Path
from typing import Union

import aiohttp
import asyncio
import json

import aiomisc

from api.eleven_labs.response_models import VoicesResponse, ErrorResponse, Voice

API_BASE_URL = "https://api.elevenlabs.io/v1"


async def save_audio(audio_data, filename: Union[str, Path]):
    with tempfile.TemporaryDirectory():
        afp: aiomisc.io.AsyncTextIO

        async with aiomisc.io.async_open(filename, 'wb') as afp:
            await afp.write(audio_data)
            await afp.seek(0)


class TextToSpeech:
    def __init__(self, api_key):
        self.api_key = api_key
        self.voice_id = None
        self.voice_name = None

    async def set_voice(self, voice_name: str = None, voice_id: str = None):
        if not voice_name and not voice_id:
            raise ValueError("Either voice_name or voice_id must be provided")

        response = await self.get_voices()

        if isinstance(response, ErrorResponse):
            print(f"Error: {response.detail}")
            return

        for voice in response.get_voices():
            if voice_name and voice.name == voice_name \
                    or voice_id and voice.voice_id == voice_id:
                self.voice_id = voice.voice_id
                self.voice_name = voice.name
                break

    async def get_voices(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/voices", headers={"xi-api-key": self.api_key}) as response:
                data = await response.json()
                if response.status != 200:
                    return ErrorResponse(data, response.status)

                voices = [Voice(**voice_data) for voice_data in data.get("voices", [])]
                return VoicesResponse(voices)

    async def synthesize_speech(self, text, voice_id=None, stability=0, similarity_boost=0):
        """
        Synthesize speech from text
        :param text:
        :param voice_id:
        :param stability:
        :param similarity_boost:
        :return:
        """
        payload = {
            "text": text,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_BASE_URL}/text-to-speech/{voice_id or self.voice_id}",
                                    data=json.dumps(payload),
                                    headers=headers) as response:
                data = await response.json() if response.status != 200 else None
                if response.status != 200:
                    return ErrorResponse(data, response.status)
                audio_data = await response.read()
                return audio_data


