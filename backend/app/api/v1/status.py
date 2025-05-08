from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import database_helper
from app.services.response_middleware import ResponseMiddleware
from app.services.status import get_secured_status, get_status


router = APIRouter(tags=["Status"])
security = HTTPBearer()


@router.get("/")
async def check_status():
    return await ResponseMiddleware.response(get_status())


@router.get("/secured_status/")
async def check_secured_status(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(database_helper.session_getter),
):
    return await ResponseMiddleware.response(
        get_secured_status(
            session=session,
            token=credentials.credentials,
        )
    )
