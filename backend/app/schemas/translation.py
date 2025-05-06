from typing import List

from pydantic import BaseModel


class TranslationRequest(BaseModel):
    text: str
    source: str
    target: str


class TranslationResponse(BaseModel):
    translated_text: str


class LanguageDetectionResponse(BaseModel):
    language: str
    confidence: float
    is_reliable: bool


class LanguageInfo(BaseModel):
    language: str
    name: str


class LanguagesResponse(BaseModel):
    languages: List[LanguageInfo]
