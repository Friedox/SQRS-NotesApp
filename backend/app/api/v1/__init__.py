from fastapi import APIRouter

from config import settings

from .auth import router as auth_router
from .status import router as status_router


router = APIRouter(prefix=settings.api.v1.prefix)


router.include_router(status_router, prefix=settings.api.v1.status_prefix)
router.include_router(auth_router, prefix=settings.api.v1.status_prefix)
