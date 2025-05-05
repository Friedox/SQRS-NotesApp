import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user import user_repo
from app.schemas.user import UserCreateScheme, UserCredentialsScheme
from config import settings
from exc import EmailAlreadyInUseError
from logger import get_logger


logger = get_logger(__name__, debug=settings.run.debug)


async def register_user(session: AsyncSession, user_creds: UserCredentialsScheme):
    if await user_repo.is_email_in_table(session=session, email=user_creds.email):
        raise EmailAlreadyInUseError(email=user_creds.email)

    password_hash = hash_password(user_creds.password.get_secret_value())

    new_user = UserCreateScheme(
        email=user_creds.email, password_hash=password_hash, name=user_creds.name
    )

    user = await user_repo.create(session=session, new_user=new_user)

    return user


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()
