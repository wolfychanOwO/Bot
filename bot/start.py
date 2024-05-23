import asyncio
import asyncpg


from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from db import create_async_engine, get_session_maker
from db.models.user import User, create_user, get_user, clear_users, show_users, get_user_by_id, is_admin, show_admins, \
    show_all_users
from db.models.companies import show_companies, show_location_on_company, add_company, get_company, delete_company, \
    add_location, delete_location, get_company_by_user_sql_id, get_location_by_user_sql_id, get_company_by_id
from .states import Register, Report, Several, Admin, CompanyPanelClass, UserPanelClass
from settings import DB_CONNECTION_STRING


async def start(msg: Message, state: FSMContext):
    async with get_session_maker(create_async_engine(DB_CONNECTION_STRING)).begin() as session:
        user_tg = msg.from_user
        user = await get_user(user_tg.id, session)
        if not user:
            user = await create_user(
                user_id=user_tg.id,
                first_name=user_tg.first_name,
                last_name=user_tg.last_name,
                phone='',
                admin=False,
                active=True,
                session=session
            )

        if not user.active:
            await msg.reply('Вы были удалены из системы, свяжитесь с администратором, для восстановления доступа.')
            return

        if user.admin:
            await state.set_state(Admin.choice)
            kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                     keyboard=[
                                         [
                                             KeyboardButton(text='Компании'),
                                             KeyboardButton(text='Пользователи'),
                                         ]
                                     ])
            await msg.answer('Выберите действие', reply_markup=kb)
            ...
        else:
            if not user.location_id:
                await state.set_state(Register.get_company)
                await msg.answer('Выберите \'привязать компанию\', чтобы указать, в какой вы работаете',
                                 reply_markup=ReplyKeyboardMarkup(
                                     resize_keyboard=True,
                                     keyboard=[
                                         [
                                             KeyboardButton(text='Привязать компанию'),
                                         ]
                                     ]
                                 ))
            elif user.phone == '':
                await state.set_state(Register.get_numbers)
                await msg.answer("Чтобы завершить определение, поделитесь контактом с нами,"
                                 "для этого нажмите кнопку \"Отправить контакт\"",
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
                await state.set_state(Report.topic)
                kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                         keyboard=[
                                             [
                                                 KeyboardButton(text='Отправить репорт'),
                                                 KeyboardButton(text='Помощь')
                                             ]
                                         ])
                await msg.answer('Выберите действие', reply_markup=kb)


def back_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True,
                             keyboard=[
                                 [
                                     KeyboardButton(text='Назад')
                                 ]
                             ])
    return kb


async def admin_choice(msg: Message, state: FSMContext):
    choice = msg.text
    if choice == 'Компании':
        choice = await state.update_data(admin_choice=choice)
        await company_panel(msg, state)
    elif choice == 'Пользователи':
        choice = await state.update_data(admin_choice=choice)
        await user_panel(msg, state)
    else:
        await msg.answer('Такой функции нет, попробуйте еще раз')
        await start(msg, state)


# Блок пользователя ----------------------------

async def user_panel(msg: Message, state: FSMContext):
    choice = (await state.get_data())['admin_choice']
    await state.set_state(UserPanelClass.lock_panel)
    await msg.reply(f'{choice}', reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text='Список пользователей'),
                KeyboardButton(text='Список админов'),
                KeyboardButton(text='Выбрать пользователя'),
            ],
            [
                KeyboardButton(text='Назад'),
            ]
        ]
    ))


async def user_change_lock(msg: Message, state: FSMContext):
    if msg.text == 'Назад':
        await start(msg, state)
        return
    if msg.text == 'Список пользователей':
        await user_list(msg, state)
    elif msg.text == 'Список админов':
        await admin_list(msg, state)
    elif msg.text == 'Выбрать пользователя':
        await select_user_from_list(msg, state)
    else:
        await msg.reply('Такой команды нет, попробуйте еще раз')
        await user_panel(msg, state)


async def user_list(msg: Message, state: FSMContext):
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        users_list = await show_users(session)
    await msg.answer(f'Список пользователей:\n{users_list}')
    try:
        msg.text = (await state.get_data())['admin_choice']
    except Exception:
        pass


async def admin_list(msg: Message, state: FSMContext):
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        admins_list = await show_admins(session)
    await msg.answer(f'Список админов:\n{admins_list}')
    try:
        msg.text = (await state.get_data())['admin_choice']
    except Exception:
        pass


async def select_user_from_list(msg: Message, state: FSMContext):
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        users_list = await show_all_users(session)
    await state.set_state(UserPanelClass.selecting_user)
    await msg.answer(f'Введите пользователя из списка (введите id):\n{users_list}', reply_markup=back_kb())


async def select_user(msg: Message, state: FSMContext):
    if msg.text == 'Назад':
        await user_panel(msg, state)
        return
    selected_user_id = int(msg.text)
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        user = await get_user_by_id(selected_user_id, session)
        if not user:
            await msg.reply('Такого пользователя не существует, попробуйте еще раз')
            await select_user_from_list(msg, state)
            return
    await state.update_data(selected_user_id=selected_user_id)
    await state.set_state(UserPanelClass.select_step)
    await msg.reply(f'Выберите действие', reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text='Дать права'),
                KeyboardButton(text='Отнять права'),
                KeyboardButton(text='Удалить'),
                KeyboardButton(text='Инфо'),
            ],
            [
                KeyboardButton(text='Назад'),
            ]
        ]
    ))


async def user_selected_step(msg: Message, state: FSMContext):
    if msg.text == 'Назад':
        await user_panel(msg, state)
        return
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        user_sql_id = (await state.get_data())['selected_user_id']
        user: User = await get_user_by_id(user_sql_id, session)
        if msg.text == 'Дать права':
            user.admin = True
            await msg.reply(f'Пользователь {user.first_name} {user.last_name} {user.id} получил права Администратора')
            await session.commit()
        elif msg.text == 'Отнять права':
            user.admin = False
            await msg.reply(f'Пользователь {user.first_name} {user.last_name} {user.id} больше не Aдминистратор')
            await session.commit()
        elif msg.text == 'Удалить':
            await state.set_state(UserPanelClass.delete_action)
            await msg.reply(
                f'Вы уверены, что хотите удалить пользователя {user.id}, {user.first_name} {user.last_name}',
                reply_markup=ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    keyboard=[
                        [
                            KeyboardButton(text='Да'),
                            KeyboardButton(text='Нет'),
                        ]
                    ]
                ))
        elif msg.text == 'Инфо':
            company = await get_company_by_user_sql_id(user_sql_id, session)
            location = await get_location_by_user_sql_id(user_sql_id, session)
            await msg.answer(f'Никнейм: {user.first_name} {user.last_name}\n'
                             f'телеграмм id: {user.user_id}\n'
                             f'SQL id: {user.id}\n'
                             f'Телефон: {user.phone}\n'
                             f'Права: {await is_admin(user_sql_id, session)}\n'
                             f'Компания: {company}\n'
                             f'Локация: {location}')
        else:
            await msg.answer('Такой функции нет, попробуйте еще раз')
            await user_panel(msg, state)
            return


async def delete_certificated_user(msg: Message, state: FSMContext):
    if msg.text == 'Да':
        async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
            user_sql_id = (await state.get_data())['selected_user_id']
            user = await get_user_by_id(user_sql_id, session)
            user.active = False
            await msg.reply(f'Пользователь {user.first_name} {user.last_name} {user.id} был удален (более не активен)')
            await session.commit()
            await select_user(msg, state)
            return
    elif msg.text == 'Нет':
        await select_user(msg, state)
        return
    else:
        await msg.reply('Такой функции нет, попробуйте еще раз')
        await select_user(msg, state)
        return


# ----------------------------------------------

# Блок компании --------------------------------

async def company_panel(msg: Message, state: FSMContext):
    choice = (await state.get_data())['admin_choice']
    await state.set_state(CompanyPanelClass.lock_panel)
    await msg.answer(f'{choice}', reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text='Список компаний'),
                KeyboardButton(text='Выбрать компанию'),
                KeyboardButton(text='Добавить компанию'),
            ],
            [
                KeyboardButton(text='Назад'),
            ]
        ]
    ))


async def company_change_lock(msg: Message, state: FSMContext):
    if msg.text == 'Назад':
        await start(msg, state)
        return
    if msg.text == 'Список компаний':
        await company_list(msg, state)
    elif msg.text == 'Добавить компанию':
        await typing_company_name(msg, state)
    elif msg.text == 'Выбрать компанию':
        await select_company_from_list(msg, state)
    else:
        await msg.reply('Такой команды нет, попробуйте еще раз')
        await company_panel(msg, state)


async def company_list(msg: Message, state: FSMContext):
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        companies_list = await show_companies(session)
    await msg.answer(f'Список компаний:\n{companies_list}')
    try:
        msg.text = (await state.get_data())['admin_choice']
    except Exception:
        pass


async def typing_company_name(msg: Message, state: FSMContext):
    await state.set_state(CompanyPanelClass.adding_company_name)
    await msg.answer('Введите название компании: ', reply_markup=back_kb())


async def adding_company(msg: Message, state: FSMContext):
    if msg.text == 'Назад':
        await company_panel(msg, state)
        return
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        company = await add_company(msg.text, session)
    await msg.reply(f'{company} была добавлена')
    await company_panel(msg, state)


async def select_company_from_list(msg: Message, state: FSMContext):
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        companies_list = await show_companies(session)
    await state.set_state(CompanyPanelClass.selecting_company)
    await msg.answer(f'Введите id компании из списка:\n{companies_list}', reply_markup=back_kb())


async def select_company(msg: Message, state: FSMContext):
    if msg.text == 'Назад':
        await company_panel(msg, state)
        return
    company_id = int(msg.text)
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        company = await get_company_by_id(company_id, session)
        if not company or company.id == 1:
            await msg.reply('такой компании не существует, попробуйте еще раз')
            await select_company_from_list(msg, state)
            return
        company_name = await get_company(company.name, session)
    await state.update_data(company_name=company_name)
    await state.set_state(CompanyPanelClass.select_step)
    await msg.reply(f'{company_name}', reply_markup=ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text='Удалить компанию'),
                KeyboardButton(text='Удалить локацию'),
                KeyboardButton(text='Добавить локацию'),
                KeyboardButton(text='Список локаций'),
            ],
            [
                KeyboardButton(text='Назад'),
            ]
        ]
    ))


async def company_select_step(msg: Message, state: FSMContext):
    if msg.text == 'Назад':
        await company_panel(msg, state)
        return
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        item_list = None
        name = (await state.get_data())['company_name']
        if msg.text == 'Удалить компанию':
            item_list = await delete_company(name, session)
            await msg.answer(f'Компания \'{item_list}\' была удалена')
        elif msg.text == 'Добавить локацию':
            await state.update_data(select_step_choice=msg.text)
            await state.set_state(CompanyPanelClass.action)
            await msg.answer('Введитие адрес новой локации')
        elif msg.text == 'Список локаций':
            item_list = await show_location_on_company(name, session)
            await msg.reply(f'Список локаций компании {name}:\n{item_list}')
        elif msg.text == 'Удалить локацию':
            await state.update_data(select_step_choice=msg.text)
            await state.set_state(CompanyPanelClass.action)
            id_location_list = list(await session.execute(text(f"SELECT locations.id, locations.address FROM locations "
                                                               f"JOIN companies ON companies.name = \'{name}\'"
                                                               f"AND locations.address != \'BaseLocation\'")))
            await msg.answer(f'Введите id локации из списка, которую вы хотите удалить:\n{id_location_list}')
        else:
            await msg.answer('Такой функции нет, попробуйте еще раз')
            await company_panel(msg, state)
            return


async def action_commit(msg: Message, state: FSMContext):
    data = await state.get_data()
    choice = data['select_step_choice']
    company_name = data['company_name']
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        if choice == 'Добавить локацию':
            address = msg.text
            company_id = (await session.execute(text(f'SELECT id FROM companies WHERE name = \'{company_name}\''))).first()[0]
            await add_location(address, company_id, session)
            await msg.answer(f'Локация \'{address}\' была добавлена')
        elif choice == 'Удалить локацию':
            location_id = int(msg.text)
            location_name = await delete_location(location_id, session)
            # location_name = (await session.execute(text(f"SELECT address FROM locations WHERE id = {location_id}"))).first()[0]
            await msg.answer(f'Локация \'{location_name}\' была успешно удалена')
        else:
            await msg.reply('Такой функции нет, попробуйте еще раз')
            await company_panel(msg, state)
            return
    await company_panel(msg, state)
    return


# ----------------------------------------------


async def getting_company(msg: Message, state: FSMContext):
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        companies_list = await show_companies(session)
        await state.update_data(companies_list=companies_list)
    await state.set_state(Register.get_location)
    await msg.reply(f'выберите название компании:\n{companies_list}')


async def getting_location(msg: Message, state: FSMContext):
    company_name = msg.text if msg.text[-1] != ' ' else msg.text[:-1]
    companies_list = (await state.get_data())['companies_list']
    if company_name in companies_list:
        async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
            # await state.update_data(company_name_selected=company_name)
            locations_to_company = (list(await session.execute(
                text(f"SELECT locations.address FROM locations JOIN companies ON companies.name = '{company_name}'"))
                                         )[0])
        await state.set_state(Register.attachment)
        await msg.reply(f'Компания: {company_name}')
        await msg.answer(f'Выберите адрес:\n{locations_to_company}', reply_markup=back_kb())
    else:
        await msg.reply('Такой компании не существует, попробуйте еще раз')
        await getting_company(msg, state)
        return


async def user_attachment(msg: Message, state: FSMContext):
    if msg.text == 'Назад':
        await getting_company(msg, state)
        return
    location = msg.text
    async with async_sessionmaker(create_async_engine(DB_CONNECTION_STRING))() as session:
        user = (await session.execute(select(User).where(User.user_id == msg.from_user.id))).first()[0]
        user.location_id = \
            (await session.execute(text(f"SELECT id FROM locations WHERE address = '{location}'"))).first()[0]
        await session.commit()
    await state.set_state(Register.get_numbers)
    await msg.answer("Чтобы завершить определение, поделитесь контактом с нами,"
                     "для этого нажмите кнопку \"Отправить контакт\"",
                     reply_markup=ReplyKeyboardMarkup(
                         keyboard=[
                             [
                                 KeyboardButton(text='Отправить контакт', request_contact=True),
                             ]
                         ],
                         resize_keyboard=True,
                     ),
                     )


async def get_contact(msg: Message, state: FSMContext):
    async with get_session_maker(create_async_engine(DB_CONNECTION_STRING)).begin() as session:
        user: User = await get_user(msg.from_user.id, session)
        if not msg.contact:
            await start(msg, state)
            return
        user.phone = msg.contact.phone_number
        await session.commit()
    await show_contact(msg, state)
    await state.clear()


async def show_contact(msg: Message, state: FSMContext):
    await msg.answer(f'Твой контакт успешно получен:\n'
                     f'phone: {msg.contact.phone_number}',
                     reply_markup=ReplyKeyboardRemove())
    await start(msg, state)


async def get_topic(msg: Message, state: FSMContext):
    await state.set_state(Several.get_topic_description)
    kb = ReplyKeyboardMarkup(resize_keyboard=True, selective=True,
                             keyboard=[
                                 [
                                     KeyboardButton(text='техника'),
                                     KeyboardButton(text='материалы'),
                                 ]
                             ]
                             )
    await msg.answer('с чем у вас проблема?', reply_markup=kb, resize_keyboard=True)


async def topic_description(msg: Message, state: FSMContext):
    choice = msg.text
    if choice in ['техника', 'материалы']:
        await state.update_data(choice=choice)
        await msg.reply('введите id устройства', reply_markup=back_kb())
        await state.set_state(Several.get_printer_id)
    else:
        await get_topic(msg, state)


async def printer_id_input(msg: Message, state: FSMContext):
    if msg.text == 'Назад':
        await get_topic(msg, state)
        return
    user_input = msg.text
    await msg.reply(f'Введенный id: {user_input}')
    await state.update_data(printer_id=user_input)
    await get_data(msg, state)


async def get_data(msg: Message, state: FSMContext):
    await state.set_state(Several.get_issue_description)
    await msg.reply('детально опишите проблему', reply_markup=back_kb())


async def issue_description(msg: Message, state: FSMContext):
    user_input = msg.text
    if user_input == 'Назад':
        await topic_description(msg, state)
        return
    await state.update_data(description=user_input)
    await state.set_state(Report.issue)
    topic = (await state.get_data())['choice']
    await msg.reply(f'Проблема: {topic}\n'
                    f'Описание:\n{user_input}',
                    reply_markup=ReplyKeyboardMarkup(
                        resize_keyboard=True,
                        keyboard=[
                            [
                                KeyboardButton(text='Назад'),
                                KeyboardButton(text='Отправить')
                            ]
                        ]
                    )
                    )


async def report_issue(msg: Message, state: FSMContext):
    if msg.text == 'Назад':
        await get_data(msg, state)
        return
    elif msg.text == 'Отправить':
        data = await state.get_data()
        topic = data['choice']
        printer_id = data['printer_id']
        description = data['description']
        # TODO: заменить msg.reply на bot_instance.send_message
        await msg.reply(f'----репорт отправлен----\n'
                        f'КЛИЕНТ: {msg.from_user.first_name} {msg.from_user.last_name} (id: {msg.from_user.id})\n'
                        f'ТИП ПРОБЛЕМЫ: {topic}\n'
                        f'ID УСТРОЙСТВА: {printer_id}\n'
                        f'ОПИСАНИЕ:\n{description}')
    else:
        await msg.reply('Такой функции нет, попробуйте еще раз')
        await get_topic(msg, state)
        return
