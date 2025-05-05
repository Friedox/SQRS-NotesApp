from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import database_helper
from app.schemas.user import UserCredentialsScheme
from app.services.auth import register_user
from app.services.response_middleware import ResponseMiddleware


router = APIRouter(tags=["Auth"])


@router.post("/register/")
async def register(
    user_creds: UserCredentialsScheme,
    session: AsyncSession = Depends(database_helper.session_getter),
):
    return await ResponseMiddleware.response(
        register_user(session=session, user_creds=user_creds)
    )
