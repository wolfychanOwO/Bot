from typing import Any

from asyncpg import UniqueViolationError
from sqlalchemy import Column, Boolean, DATE, String, BigInteger, select, Integer, Row
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine
import datetime

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    user_id = Column(BigInteger, unique=True, nullable=False, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True, default='')
    # TODO: под конец обработать и доделать company
    ''' 
    company = relationship("Company", back_populates='user') 
    '''

    admin = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    # registration date
    reg_date = Column(DATE, nullable=False, default=datetime.date.today())
    # last update date
    upd_date = Column(DATE, nullable=False, onupdate=datetime.date.today())

    # TODO: уточнить какие столбцы в бд

    '''
    def __init__(self, first_name, last_name, telephone, company, reg_date):
        self.first_name = first_name
        self.last_name = last_name
        self.telephone = telephone
        self.company = company
        self.reg_date = reg_date
    '''

    def __str__(self):
        return f'<User:{self.id}>'

    def __repr__(self):
        return self.__str__()

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


async def get_user(user_id: int, engine: AsyncEngine):
    async with engine.connect() as conn:
        result = (await conn.execute(select(User).where(User.user_id == user_id))).first()
    return result


async def create_user(user_id: int, first_name: str, last_name: str, phone: str, admin: bool, active: bool,
                      session_maker: async_sessionmaker[AsyncSession]):
    async with session_maker.begin() as session:
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
            # session.expunge(user)
        except UniqueViolationError or Exception:
            print('Случилась ошибка create_user')
            # TODO: сделать логи
    return user


async def clear_users(engine: AsyncEngine):
    async with engine.connect() as conn:
        result = await conn.execute(select(User).where(User.phone == ''))
        print(result.first())
        for row in await conn.execute(select(User).where(User.phone == '')):
            print(row)
