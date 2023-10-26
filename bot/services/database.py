from dataclasses import dataclass
from typing import Optional

from aiogram.types import User
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.enums import Locale
from bot.models import Base, DBUser
from utils.loggers import database


def create_pool(dsn: PostgresDsn) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(url=dsn.unicode_string())
    maker = async_sessionmaker(engine, expire_on_commit=False)

    return maker


@dataclass(kw_only=True)
class Repository:
    session: AsyncSession

    async def get_user(self, pk: int) -> Optional[DBUser]:
        return await self.session.get(entity=DBUser, ident=pk)

    async def create_user(self, user: User) -> DBUser:
        db_user = DBUser(
            id=user.id, name=user.full_name, locale=Locale.resolve(user.language_code)
        )
        await self.save(db_user)
        database.info("New user in database: %s (%d)", user.full_name, user.id)
        return db_user

    async def save(self, model: Base) -> None:
        self.session.add(model)
        await self.session.commit()
