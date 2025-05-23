from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import database_helper
from app.schemas.user import UserCredentialsScheme, UserRegisterScheme
from app.services.auth import login_user, logout_user, register_user
from app.services.response_middleware import ResponseMiddleware
from config import settings


router = APIRouter(tags=["Auth"])
security = HTTPBearer()


@router.get("/public_key/")
async def get_public_key():
    return await ResponseMiddleware.response(settings.security.jwt_public_key)


@router.post("/register/")
async def register(
    user_creds: UserRegisterScheme,
    session: AsyncSession = Depends(database_helper.session_getter),
):
    return await ResponseMiddleware.response(
        register_user(session=session, user_creds=user_creds)
    )


@router.post("/login/")
async def login(
    user_creds: UserCredentialsScheme,
    session: AsyncSession = Depends(database_helper.session_getter),
):
    return await ResponseMiddleware.response(
        login_user(session=session, user_creds=user_creds)
    )


@router.post("/logout/")
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(database_helper.session_getter),
):
    return await ResponseMiddleware.response(
        logout_user(session=session, token=credentials.credentials)
    )
