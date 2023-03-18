import logging

import aiomisc

from api.testClass import TestyNaprawoJazdyApi
from config import settings

log = logging.getLogger(__name__)


async def main():
    testPravo = TestyNaprawoJazdyApi("39b1a9a3-f78b-4f94-9344-7489d64eefed")
    token = await testPravo.authenticate("akoteykula@gmail.com", settings.test_pravo_pass)
    modules = await testPravo.get_modules()
    for i in modules:
        subjects = await testPravo.get_subjects(i.id)
        for subject in subjects:
            logging.info(subject)

            slides = await testPravo.get_slides(subject.id)
            print("*"*30)
            for slide in slides:
                print(f"{slide.name}\n{slide.content}")
                ...


if __name__ == '__main__':
    with aiomisc.entrypoint(log_level="info", log_format="color") as loop:
        loop.run_until_complete(main())
