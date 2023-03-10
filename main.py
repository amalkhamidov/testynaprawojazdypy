import logging

import aiomisc

log = logging.getLogger(__name__)


async def main():
    ...


if __name__ == '__main__':
    with aiomisc.entrypoint(log_level="info", log_format="color") as loop:
        loop.run_until_complete(main())
