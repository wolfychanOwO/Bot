from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from botinstance import bot_instance
from db import create_async_engine, get_session_maker
from settings import DB_CONNECTION_STRING

# storage = MemoryStorage()
dp = Dispatcher()
