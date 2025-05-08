from typing import cast

from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.user import UserCreateScheme, UserScheme
from exc import UserNotFoundError


class UserRepository:
    @staticmethod
    async def is_email_in_table(session: AsyncSession, email: str) -> bool:
        return (
            await session.scalar(
                select(User).where(User.email == email),
            )
        ) is not None

    @staticmethod
    async def get_pass_hash_by_email(
            session: AsyncSession,
            email: str
    ) -> SecretStr:
        stored_user = await session.scalar(
            select(User).where(User.email == email)
        )

        if not stored_user:
            raise UserNotFoundError

        return SecretStr(
            secret_value=(cast(str, stored_user.password_hash))
        )

    @staticmethod
    async def create(
            session: AsyncSession,
            new_user: UserCreateScheme
    ) -> UserScheme:
        user = User(
            email=new_user.email,
            name=new_user.name,
            password_hash=new_user.password_hash,
        )

        session.add(user)
        await session.flush()
        await session.refresh(user)
        return UserScheme.model_validate(user, from_attributes=True)

    @staticmethod
    async def login_user(
        session: AsyncSession, email: str, password_hash: str
    ) -> UserScheme:
        stored_user = await session.scalar(
            select(User).where(
                User.email == email,
                User.password_hash == password_hash,
            )
        )

        if not stored_user:
            raise UserNotFoundError

        return UserScheme.model_validate(stored_user, from_attributes=True)

    @staticmethod
    async def get(session: AsyncSession, user_id: int) -> UserScheme:
        stored_user = await session.scalar(
            select(User).where(User.user_id == user_id)
        )

        if not stored_user:
            raise UserNotFoundError

        return UserScheme.model_validate(stored_user, from_attributes=True)


user_repo: UserRepository = UserRepository()
