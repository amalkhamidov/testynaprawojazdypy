from dataclasses import dataclass
from io import BytesIO
from typing import Optional
import aiohttp


@dataclass
class TextToSpeech:
    api_key: str
    voice_code: str = "EXAVITQu4vr4xnSDxMaL"
    API_ENDPOINT = "https://api.elevenlabs.io/v1/text-to-speech/"

    async def generate_audio(self, text: str, save_in_buffer: bool = False, buffer: Optional[BytesIO] = None) -> Optional[bytes]:
        """
        This function sends a HTTP POST request to the Eleven Labs Text-to-Speech API, which converts a given text input to an MP3 audio output. The API requires an api_key for authentication, which should be passed as an argument. The user can choose to either save the MP3 audio output to a BytesIO buffer or return the output as bytes.

        Parameters
        :param text : The input text that needs to be converted to MP3 audio.
        :param save_in_buffer : Determines whether the MP3 audio output should be saved in a BytesIO buffer. Default is False.
        :param buffer : The buffer in which to save the MP3 audio output, if save_in_buffer is True. If save_in_buffer is False, this argument is ignored.

        :return:
        If save_in_buffer is True, the function returns None and writes the audio in the provided buffer.
        If save_in_buffer is False, the function returns the MP3 audio output as bytes.

        Example of usage:
        buffer = BytesIO()
        tts = TextToSpeech(api_key="api_key")
        await tts.generate_audio("Hello world", save_in_buffer=True, buffer=buffer)
        audio_data = buffer.getvalue()

        :todo: Make function more elegant, add more error handling.
        """

        url = self.API_ENDPOINT + self.voice_code
        headers = {
            'accept': 'audio/mpeg',
            'xi-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        data = {
            'text': text,
            'voice_settings': {
                'stability': 0,
                'similarity_boost': 0
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data, ssl=False) as response:
                if response.status != 200:
                    raise ValueError(f'Request failed with status {response.status}')
                if save_in_buffer:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        buffer.write(chunk)
                    return
                else:
                    return await response.read()
