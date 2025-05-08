from fastapi import APIRouter

from config import settings

from .auth import router as auth_router
from .notes import router as notes_router
from .status import router as status_router
from .translation import router as translation_router


router = APIRouter(prefix=settings.api.v1.prefix)

router.include_router(status_router, prefix=settings.api.v1.status_prefix)
router.include_router(auth_router, prefix=settings.api.v1.auth_prefix)
router.include_router(notes_router, prefix=settings.api.v1.notes_prefix)
router.include_router(translation_router, prefix=settings.api.v1.translation_prefix)
