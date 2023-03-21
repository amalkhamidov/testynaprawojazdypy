import logging
import typing
from dataclasses import dataclass
from typing import List

import aiohttp

from models.request import CourseModule, User, Subject, Slaid, ErrorResponse


@dataclass
class TestyNaprawoJazdyApi:
    jsessionid: str = None
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.testynaprawojazdy.eu/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/110.0.0.0 Safari/537.36',
    }
    base_url = 'https://api.testynaprawojazdy.eu/learning/course/'
    image_url = "https://eprawko.eu/platforma/_files/"

    def __post_init__(self):
        self.headers.update(jsessionid=self.jsessionid) if self.jsessionid else None

    async def authenticate(self, username: str, password: str) -> User:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            auth_data = {
                'userName': username,
                'password': password
            }
            async with session.post(
                    'https://api.testynaprawojazdy.eu/eprawko-rest/login/',
                    headers=self.headers,
                    data=auth_data,
            ) as response:
                response = await response.json()
                if not response:
                    raise Exception('Authentication failed')

                logging.debug("Authentication response: %s", response)
                model_data = User(**response)
                self.jsessionid = model_data.uuid
                self.headers.update(jsessionid=self.jsessionid)
                return model_data

    async def get_modules(self) -> List[CourseModule]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                    f'{self.base_url}'
                    f'modules/196',
                    headers=self.headers,
            ) as response:
                courses_data = await response.json()

                return [
                    CourseModule(
                        id=course['id'],
                        moduleNumber=course['moduleNumber'],
                        name=course['name'],
                        subjectsNumber=course['subjectsNumber'],
                    )
                    for course in courses_data
                ]

    async def get_subjects(self, module_id: int) -> List[Subject]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                    f'{self.base_url}'
                    f'subjects/{module_id}',
                    headers=self.headers,
            ) as response:
                subjects_data = await response.json()

                return [
                    Subject(
                        id=subject['id'],
                        name=subject['name'],
                        slaidsNumber=subject['slaidsNumber']
                    )
                    for subject in subjects_data
                ]

    async def get_slides(self, subject_id: int, method_code=196) -> List[Slaid]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                    f'{self.base_url}'
                    f'slaids/{subject_id}/{method_code}',
                    headers=self.headers,
            ) as response:
                slides_data = await response.json()

                return [
                    Slaid(**slide)
                    for slide in slides_data
                ]

    async def get_slide(self, subject_id: int, slide_id: int) -> typing.Union[Slaid, ErrorResponse]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                    f'{self.base_url}'
                    f'slaid/{subject_id}/{slide_id}',
                    headers=self.headers,
            ) as response:
                slide_data = await response.json()
                if slide_data.get("error"):
                    return ErrorResponse(**slide_data)

                return Slaid(**slide_data)

    async def get_image(self, image_url: str) -> bytes:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                    self.image_url + image_url,
                    headers=self.headers,
            ) as response:
                return await response.read()