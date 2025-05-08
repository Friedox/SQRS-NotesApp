from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import database_helper
from app.schemas.translation import (
    LanguageDetectionResponse,
    LanguagesResponse,
    TranslationRequest,
    TranslationResponse,
)
from app.services.response_middleware import ResponseMiddleware
from app.services.translation import translation_service


router = APIRouter(tags=["Translation"])
security = HTTPBearer()


@router.post("/", status_code=status.HTTP_200_OK)
async def translate_text_endpoint(
    request: TranslationRequest,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(database_helper.session_getter),
):
    translated_text = await translation_service.translate_text(
        text=request.text, source=request.source, target=request.target
    )
    return await ResponseMiddleware.response(
        TranslationResponse(translated_text=translated_text)
    )


@router.post("/detection", status_code=status.HTTP_200_OK)
async def detect_language_endpoint(
    text: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(database_helper.session_getter),
):
    detection = await translation_service.detect_language(text=text)
    return await ResponseMiddleware.response(
        LanguageDetectionResponse(
            language=detection["language"],
            confidence=detection["confidence"],
            is_reliable=detection["isReliable"],
        )
    )


@router.get("/languages", status_code=status.HTTP_200_OK)
async def get_languages_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(database_helper.session_getter),
):
    languages = await translation_service.get_languages()
    return await ResponseMiddleware.response(
        LanguagesResponse(languages=languages)
    )
