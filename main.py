import asyncio
import logging
import os

from aiogram import Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from aiogram_dialog import DialogManager
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine

from botinstance import bot_instance
from bot import register_user_commands, bot_commands
from db import create_async_engine, get_session_maker, proceed_schemas, BaseModel
from settings import DB_CONNECTION_STRING
from loader import dp

filepath = '/home/wolfychan/logs/'
if not os.path.exists(filepath):
    os.mkdir(filepath)

# dp = Dispatcher()
''' Разобраться с DialogManager '''


async def main() -> None:
    register_user_commands(dp)

    command_for_bot = []
    for cmd in bot_commands:
        command_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))
    await bot_instance.set_my_commands(commands=command_for_bot)

    async_engine = create_async_engine(DB_CONNECTION_STRING)
    session_maker = get_session_maker(async_engine)
    # оставлена на alembic
    # await proceed_schemas(async_engine, BaseModel.metadata)

    await dp.start_polling(bot_instance)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
