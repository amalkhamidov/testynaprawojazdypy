import logging
import os
from gzip import GzipFile
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import aiomisc

from config import settings


class GzipLogFile(GzipFile):
    def write(self, data) -> int:
        if isinstance(data, str):
            data = data.encode()
        return super().write(data)


class RotatingGzipFileHandler(RotatingFileHandler):
    """ Really added just for example you have to test it properly """

    def shouldRollover(self, record):
        if not os.path.isfile(self.baseFilename):
            return False
        if self.stream is None:
            self.stream = self._open()
        return 0 < self.maxBytes < os.stat(self.baseFilename).st_size

    def _open(self):
        return GzipLogFile(filename=self.baseFilename, mode=self.mode)


class SetupService(aiomisc.Service):
    current_folder = Path().cwd()

    save_logs: bool = False
    logs_name = "app.log.gz"
    logging_format = "[%(asctime)s] <%(levelname)s> %(filename)s:%(lineno)d " \
                     "(%(threadName)s): %(message)s"
    logging_level = logging.INFO

    async def start(self) -> Any:
        image_folder = self.current_folder / settings.image_path
        image_folder.mkdir(exist_ok=True)

        if self.save_logs:
            self.setup_logs()

    @property
    def logs_path(self):
        logs_folder = self.current_folder / "logs"
        logs_folder.mkdir(exist_ok=True)

        return logs_folder / self.logs_name

    def setup_logs(self):
        gzip_handler = RotatingGzipFileHandler(
            self.logs_path,
            # Максимум 100 файлов по 10 мегабайт
            maxBytes=10 * 2 ** 20, backupCount=100
        )
        stream_handler = logging.StreamHandler()

        formatter = logging.Formatter(self.logging_format)

        gzip_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logging.basicConfig(
            level=self.logging_level,
            handlers=map(
                aiomisc.log.wrap_logging_handler,
                (gzip_handler, stream_handler)
            )
        )
