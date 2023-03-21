from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ModuleCallbackFactory(CallbackData, prefix="module"):
    action: str
    value: Optional[int]


class SlideCallbackFactory(CallbackData, prefix="slide"):
    action: str
    value: Optional[int]

