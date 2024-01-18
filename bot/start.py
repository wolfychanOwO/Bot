import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardBuilder
from aiogram_dialog import DialogManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db import create_async_engine
from db.models.user import User, create_user, get_user, clear_users
from .states import Register
from settings import DB_CONNECTION_STRING

'''
async def start(msg: Message) -> None:
    menu_builder = ReplyKeyboardBuilder()

    if msg.from_user is None:
        msg_user = msg.from_user
        user = User(msg_user.first_name, msg_user.last_name, msg_user.full_name, msg_user.id)
        msg_user.answer(msg_user.first_name, msg_user.last_name)

    menu_builder.add(
        KeyboardButton(text='Помощь'),
        KeyboardButton(text='Регистрация'))
    await msg.answer('Меню', reply_markup=menu_builder.as_markup(resize_keyboard=True))
'''


'''
async def start(msg: Message, state: FSMContext) -> None:
    user = get_user(msg, sessionmaker())
    if user:
        await state.set_state(Register.show_contact)
        await msg.answer(f'Привет, {str(msg.from_user.first_name)} {str(msg.from_user.last_name)}!\n'
                         f'Чтобы зарегистрироваться нажмите кнопку \"Отправить контакт\"',
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[
                                 [
                                     KeyboardButton(text='Отправить контакт', request_contact=True),
                                 ]
                             ],
                             resize_keyboard=True,
                         ),
                         )
    else:
        await msg.answer(f'Вы уже заригестрированны')

'''


async def start(msg: Message, state: FSMContext):
    print(f'CLEAR ALL:')
    await clear_users(create_async_engine(DB_CONNECTION_STRING))
    user_tg = msg.from_user
    user = await get_user(user_tg.id, create_async_engine(DB_CONNECTION_STRING))
    print(f'\nGET USER:', user, '\n')
    if not user:
        user = await create_user(
            user_id=user_tg.id,
            first_name=user_tg.first_name,
            last_name=user_tg.last_name,
            phone='6',
            admin=False,
            active=True,
            session_maker=async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))
        )
        print(f'\nAFTER CREATE_USER\n')

        await state.set_state(Register.get_numbers)
        await msg.answer(f'Добро пожаловать, {msg.from_user.first_name}'
                         f'Чтобы зарегистрироваться нажмите кнопку \"Отправить контакт\"',
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[
                                 [
                                     KeyboardButton(text='Отправить контакт', request_contact=True),
                                 ]
                             ],
                             resize_keyboard=True,
                         ),
                         )

    if not user.active:
        # TODO: сделать логи
        return await msg.reply('Вы были удалены из системы, свяжитесь с администратором, для восстановления доступа.')

    if not user.admin:
        #TODO: импортировать клавиатуру для юзера
        ...


async def get_contact(msg: Message, state: FSMContext):
    user: User = await get_user(msg.from_user.id, async_sessionmaker(create_async_engine(DB_CONNECTION_STRING)))
    # user.phone = msg.contact.phone_number


async def show_contact(msg: Message, state: FSMContext):
    await msg.answer(f'Твой номер успешно получен:\n'
                     f'first name: {msg.contact.first_name}\n'
                     f'last name : {msg.contact.last_name}\n'
                     f'phone: {msg.contact.phone_number}'
                     f'id: {msg.contact.user_id}'
                     f'id from user: {msg.from_user.id}',
                     reply_markup=ReplyKeyboardRemove())

