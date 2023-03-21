from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import ModuleCallbackFactory
from bot.db_operations import DBUsage
from bot.routers.instanses import router

db = DBUsage()


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    """"""
    modules_markup = await get_modules_keyboard()

    await message.answer("Select a module:", reply_markup=modules_markup.as_markup())


async def get_modules_keyboard():
    modules_keyboard = InlineKeyboardBuilder()
    modules = await db.get_modules()

    for module in modules:
        button = types.InlineKeyboardButton(
            text=module.name,
            callback_data=ModuleCallbackFactory(action="select", value=module.id)
        )
        modules_keyboard.add(button)
    modules_keyboard.adjust(1)

    return modules_keyboard
