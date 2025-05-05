import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user import user_repo
from app.schemas.user import (
    UserCreateScheme,
    UserCredentialsScheme,
    UserRegisterScheme,
    UserScheme,
)
from app.services.security import token_mgr
from config import settings
from exc import EmailAlreadyInUseError, InvalidCredentialsError
from logger import get_logger


logger = get_logger(__name__, debug=settings.run.debug)


async def register_user(session: AsyncSession, user_creds: UserRegisterScheme):
    if await user_repo.is_email_in_table(session=session, email=user_creds.email):
        raise EmailAlreadyInUseError(email=user_creds.email)

    password_hash = hash_password(user_creds.password.get_secret_value())

    new_user = UserCreateScheme(
        email=user_creds.email, password_hash=password_hash, name=user_creds.name
    )

    user = await user_repo.create(session=session, new_user=new_user)

    auth_token = await token_mgr.issue_token(user=user)

    return {"new_user": user, "auth_token": auth_token}


async def login_user(session: AsyncSession, user_creds: UserCredentialsScheme):
    if not await user_repo.is_email_in_table(session=session, email=user_creds.email):
        raise InvalidCredentialsError

    stored_hash = await user_repo.get_pass_hash_by_email(
        session=session, email=user_creds.email
    )

    await authenticate(
        stored_hash=stored_hash.get_secret_value(),
        input_password=user_creds.password.get_secret_value(),
    )

    user = await user_repo.login_user(
        session=session,
        email=user_creds.email,
        password_hash=stored_hash.get_secret_value(),
    )

    auth_token = await token_mgr.issue_token(user=user)

    return {"new_user": user, "auth_token": auth_token}


async def authenticate_token(session: AsyncSession, token: str) -> UserScheme:
    payload = await token_mgr.decrypt(token)

    user = await user_repo.get(session=session, user_id=payload["user_id"])

    return user


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()


async def authenticate(stored_hash: str, input_password: str):
    if not bcrypt.checkpw(input_password.encode(), stored_hash.encode()):
        raise InvalidCredentialsError
