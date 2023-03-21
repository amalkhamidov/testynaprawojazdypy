from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_pagination_buttons(current_page: int, total_pages: int, page_callback_prefix: str):
    markup = InlineKeyboardBuilder()

    # Define button labels
    first_page = '«1'
    previous_page = f'‹ {current_page - 1}'
    current_page_label = f'• {current_page} •'
    next_page = f'{current_page + 1} ›'
    last_page = f'{total_pages}»'

    # Add buttons based on the current page
    if current_page > 1:
        markup.add(
            types.InlineKeyboardButton(text=first_page, callback_data=f'{page_callback_prefix}:1'),
            types.InlineKeyboardButton(text=previous_page, callback_data=f'{page_callback_prefix}:{current_page - 1}')
        )

    markup.add(types.InlineKeyboardButton(text=current_page_label, callback_data='current_page'))

    if current_page < total_pages:
        markup.add(
            types.InlineKeyboardButton(text=next_page, callback_data=f'{page_callback_prefix}:{current_page + 1}'),
            types.InlineKeyboardButton(text=last_page, callback_data=f'{page_callback_prefix}:{total_pages}')
        )

    return markup

