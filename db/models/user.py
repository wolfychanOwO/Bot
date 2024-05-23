from typing import Any

from asyncpg import UniqueViolationError
from sqlalchemy import Column, Boolean, DATE, String, BigInteger, select, Integer, Row, ForeignKey, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine
import datetime

from sqlalchemy.orm import relationship

from loader import logger
from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    user_id = Column(BigInteger, unique=True, nullable=False, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=False, unique=True, default='')
    location = relationship("Location", back_populates='users')
    location_id = Column(Integer, ForeignKey('locations.id'), default=0)

    admin = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    # registration date
    reg_date = Column(DATE, nullable=False, default=datetime.date.today())
    # last update date
    upd_date = Column(DATE, nullable=False, onupdate=datetime.date.today(), default=datetime.date.today())

    def __str__(self):
        return f'{self.user_id, self.phone, self.first_name, self.last_name, self.admin, self.active, self.reg_date, self.upd_date}'

    def __repr__(self):
        return self.__str__()

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


async def get_user(user_id: int, session: async_sessionmaker[AsyncSession]):
    result = (await session.execute(select(User).where(User.user_id == user_id))).first()
    if not result:
        return None
    return result[0]


async def get_admin(session: async_sessionmaker[AsyncSession]):
    async with session() as session:
        result = (await session.execute(select(User).where(User.admin is True))).first()[0]
    return result


async def set_admin(user_id: int, session: async_sessionmaker[AsyncSession]):
    async with session.begin() as session:
        user = (await session.execute(select(User).where(User.user_id == user_id))).first()[0]
        user.admin = True
        await session.commit()
    return user


async def is_admin(user_id: int, session: async_sessionmaker[AsyncSession]):
    user = await get_user_by_id(user_id, session)
    if user.admin:
        return "Администратор"
    return "Пользователь"


async def remove_admin(user_id: int, session: async_sessionmaker[AsyncSession]):
    async with session.begin() as session:
        user = (await session.execute(select(User).where(User.user_id == user_id))).first()[0]
        user.admin = False
        await session.commit()
    return user


async def create_user(user_id: int, first_name: str, last_name: str, phone: str, admin: bool, active: bool,
                      session: async_sessionmaker[AsyncSession]):
    try:
        user: User = User(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            admin=admin,
            active=active
        )
        session.add(user)
        await session.commit()
    except UniqueViolationError or Exception as e:
        logger.warning(f'Случилось ошибка: {e}')
        return None
        # TODO: сделать логи
    return user


async def clear_users(session: async_sessionmaker[AsyncSession]):
    for row in await session.execute(text('SELECT * FROM users')):
        print(row)


async def show_users(session: async_sessionmaker[AsyncSession]):
    users_list = list(await session.execute(text('SELECT id, first_name, last_name FROM users WHERE admin = \'f\' AND '
                                                 'active = \'t\'')))
    return users_list


async def show_all_users(session: async_sessionmaker[AsyncSession]):
    all_users_list = list(await session.execute(text('SELECT id, first_name, last_name FROM users '
                                                     'WHERE active = \'t\'')))
    return all_users_list


async def show_admins(session: async_sessionmaker[AsyncSession]):
    admins_list = list(await session.execute(text('SELECT  id, user_id, first_name, last_name FROM users '
                                                  'WHERE admin = \'t\'')))
    return admins_list


async def get_user_by_id(user_id: int, session: async_sessionmaker[AsyncSession]):
    result = (await session.execute(select(User).where(User.id == user_id))).first()
    if not result:
        return None
    return result[0]


async def delete_user(user_id: int, session: async_sessionmaker[AsyncSession]):
    user = await get_user(user_id, session)
    async with session() as session:
        await session.delete(user)
        await session.commit()
    return user
