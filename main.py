# -- coding: utf-8 --
#!/bin/shm
import logging
import asyncio
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot
import json

from config import config


logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=config['TOKEN'])
dp = Dispatcher(bot, storage=storage)


if __name__ == '__main__':
    from handlers import *

    executor.start_polling(dp)