from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from config import settings


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=settings.database.naming_convention)
