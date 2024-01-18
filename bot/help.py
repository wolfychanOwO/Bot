from aiogram.filters import CommandObject
from aiogram.types import Message

from bot.bot_commands import bot_commands


async def help(message: Message, command: CommandObject) -> Message:
    if command.args:
        for cmd in bot_commands:
            if cmd[0] == command.args:
                return await message.answer(
                    f'{cmd[0]} - {cmd[1]}\n'
                )
            else:
                return await message.answer('Команда не найдена')
    return await help_descr(message)


async def help_descr(message: Message):
    return await message.answer(
        'Справка о боте\n'
        'Для того, чтобы получить информацию о команде используй /help <команда>'
    )