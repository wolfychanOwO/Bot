from aiogram import Router, F
from aiogram.filters import CommandStart, Command

from .start import start, show_contact, get_contact
from .help import help, help_descr
from .bot_commands import bot_commands
from .states import Register


def register_user_commands(router: Router) -> None:
    router.message.register(start, CommandStart())
    router.message.register(help, Command(commands=['help']))
    router.message.register(help_descr, F.text == 'Помощь')
    router.message.register(show_contact, Register.show_contact)
    router.message.register(get_contact, Register.get_numbers)
