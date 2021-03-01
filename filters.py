from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery

class Button_call_back(BoundFilter):
    def __init__(self, key):
        self.key = key

    async def check(self, message) -> bool:
        return self.key in message.data