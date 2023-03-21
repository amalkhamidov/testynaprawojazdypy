from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import ModuleCallbackFactory, SlideCallbackFactory
from bot.routers import router, db


@router.callback_query(ModuleCallbackFactory.filter())
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: ModuleCallbackFactory
):
    await callback.answer()

    slides_markup = await get_slides_keyboard(callback_data.value)
    await callback.message.edit_reply_markup(
        inline_message_id=callback.inline_message_id,
        reply_markup=slides_markup.as_markup()
    )


async def get_slides_keyboard(slide_id: int):
    slides_markup = InlineKeyboardBuilder()
    slides = await db.get_slides(slide_id)

    for slide in slides:
        button = types.InlineKeyboardButton(
            text=slide.name,
            callback_data=SlideCallbackFactory(action="select", value=slide.id)
        )
        slides_markup.add(button)
    slides_markup.adjust(1)

    return slides_markup
