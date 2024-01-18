from aiogram.filters.state import State, StatesGroup


class Register(StatesGroup):
    get_numbers = State()
    show_contact = State()
