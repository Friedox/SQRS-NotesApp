from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.user import UserCreateScheme, UserScheme


class UserRepository:
    @staticmethod
    async def is_email_in_table(session: AsyncSession, email: str) -> bool:
        return (
            await session.scalar(
                select(User).where(User.email == email),
            )
        ) is not None

    @staticmethod
    async def create(session: AsyncSession, new_user: UserCreateScheme) -> UserScheme:
        user = User(
            email=new_user.email,
            name=new_user.name,
            password_hash=new_user.password_hash,
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserScheme.model_validate(user, from_attributes=True)


user_repo: UserRepository = UserRepository()
