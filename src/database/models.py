import os
from dotenv import load_dotenv
from sqlalchemy import ForeignKey, String, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.schema import CreateSchema, DropSchema

from datetime import datetime

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

SCHEMA_NAME = "evening_tg"
engine = create_async_engine(url=DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': SCHEMA_NAME}

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, nullable=False)
    tg_name = mapped_column(String(255))
    user_full_name = mapped_column(String(255), default="")
    register_dt = mapped_column(DateTime, default=func.now(), nullable=False)
    points = mapped_column(BigInteger)


class Action(Base):
    __tablename__ = 'actions'
    __table_args__ = {'schema': SCHEMA_NAME}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(f'{SCHEMA_NAME}.users.id'), nullable=False)
    action_type: Mapped[String] = mapped_column(String(255), nullable=False)
    user_description = mapped_column(String(255))
    action_dt = mapped_column(DateTime, default=func.now(), nullable=False)


async def async_main():
    async with engine.begin() as conn:
        await conn.execute(CreateSchema(SCHEMA_NAME, if_not_exists=True))
        await conn.run_sync(Base.metadata.create_all)
