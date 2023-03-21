from typing import Optional, Any

import aiomisc
from aiogram import Bot, Dispatcher

import bot.routers.instanses
from bot.routers import db
from config import settings


class BotService(aiomisc.Service):
    dp: Dispatcher = Dispatcher()
    bot = Bot(settings.bot_token, parse_mode="HTML")

    async def start(self):
        await db.init()

        self.dp.include_router(bot.routers.instanses.router)
        await self.dp.start_polling(self.bot)

    async def stop(self, exception: Optional[Exception] = None) -> Any:
        ...


with aiomisc.entrypoint(
    BotService(),
) as loop:
    pass
