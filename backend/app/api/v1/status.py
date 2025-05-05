from fastapi import APIRouter

from app.services.response_middleware import ResponseMiddleware
from app.services.status import get_status


router = APIRouter(tags=["Statu"])


@router.get("/")
async def check_status():
    return await ResponseMiddleware.response(get_status())
