from aiogram.filters import CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.bot_commands import bot_commands
from .start import get_topic


async def get_report(msg: Message, command: CommandObject, state: FSMContext):
    await get_topic(msg, state)
    return
