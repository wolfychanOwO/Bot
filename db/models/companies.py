from asyncpg import UniqueViolationError
from sqlalchemy import Column, Boolean, DATE, String, BigInteger, select, Integer, Row, ForeignKey, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import relationship

from .base import BaseModel
from loader import logger


class Company(BaseModel):
    __tablename__ = 'companies'

    name = Column(String, nullable=False)
    location = relationship("Location", back_populates='company', cascade="all, delete-orphan")

    def __repr__(self):
        return f'{self.name}'


class Location(BaseModel):
    __tablename__ = 'locations'

    address = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company", back_populates='location')
    users = relationship("User", back_populates='location')

    def __repr__(self):
        return f'{self.address}, {self.company}, {self.company_id}'


async def show_companies(session: async_sessionmaker[AsyncSession]):
    companies_list = list(await session.execute(text('SELECT id, name FROM companies WHERE name != \'BaseCompany\'')))[0]
    return companies_list


async def show_location_on_company(company: str, session: async_sessionmaker[AsyncSession]):
    company_id = (await session.execute(text(f"SELECT id FROM companies WHERE name = \'{company}\'"))).first()[0]
    location_list = (await session.execute(text(f"SELECT address FROM locations WHERE company_id = {company_id}"))).scalars().all()
    return location_list


async def get_company(name: str, session: async_sessionmaker[AsyncSession]):
    result = (await session.execute(select(Company).where(Company.name == name))).first()
    if not result:
        return None
    return result[0]


async def get_company_by_id(company_id: int, session: async_sessionmaker[AsyncSession]):
    result = (await session.execute(select(Company).where(Company.id == company_id))).first()
    if not result:
        return None
    return result[0]


async def get_company_by_user_sql_id(user_id: int, session: async_sessionmaker[AsyncSession]):
    result = (await session.execute(text(f"SELECT name FROM companies JOIN locations ON locations.company_id = "
                                         f"companies.id JOIN users ON users.location_id = locations.id WHERE "
                                         f"users.id = {user_id}"))).first()[0]
    return result


async def get_location_by_user_sql_id(user_id: int, session: async_sessionmaker[AsyncSession]):
    result = (await session.execute(text(f"SELECT address FROM locations JOIN users ON users.location_id = "
                                         f"locations.id WHERE users.id = {user_id}"))).first()[0]
    return result


async def delete_company(name: str, session: async_sessionmaker[AsyncSession]):
    company = await get_company(name, session)
    try:
        await session.delete(company)
        await session.commit()
    except Exception as e:
        logger.warning(f'Случилось ошибка: {e}')
    return company


async def add_company(name, session: async_sessionmaker[AsyncSession]):
    company = Company(
        name=name
    )
    try:
        session.add(company)
        await session.commit()
    except Exception as e:
        logger.warning(f'Случилось ошибка: {e}')
    return company


async def add_location(address, company_id, session: async_sessionmaker[AsyncSession]):
    location = Location(
        address=address,
        company_id=company_id,
    )
    try:
        session.add(location)
        await session.commit()
    except Exception as e:
        logger.warning(f'Случилось ошибка: {e}')
    return location


'''
async def add_location(address, company_id, session: async_sessionmaker[AsyncSession]):
    try:
        await session.execute(text(f'INSERT INTO locations (address, company_id) VALUES (\'{address}\', {company_id})'))
        await session.commit()
    except Exception as e:
        print(f'Случяилась ошибка: {e}')
'''


async def delete_location(id: int, session: AsyncSession):
    location_name = (await session.execute(text(f"SELECT * FROM locations WHERE id = {id}"))).first()[0]
    logger.info(f'LOCATION_NAME: {location_name}')
    try:
        await session.execute(text(f'DELETE FROM locations WHERE address = \'{location_name}\''))
        await session.commit()
    except Exception as e:
        logger.warning(f'Случилось ошибка: {e}')
    return location_name
