from typing import Tuple, Any, Sequence

from aiogram.types import Message
from sqlalchemy import select, Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from db.models.user import User