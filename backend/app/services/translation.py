import logging
from typing import Dict, List

import httpx

from app.services.cache import cache_service
from config import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TranslationService:
    def __init__(self):
        self.base_url = (
            "https://deep-translate1.p.rapidapi.com/language/translate/v2"
        )
        self.headers = {
            "Content-Type": "application/json",
            "x-rapidapi-host": "deep-translate1.p.rapidapi.com",
            "x-rapidapi-key": (
                settings.translation.api_key.get_secret_value()
            ),
        }
        logger.debug(
            "Translation service initialized with cache TTL: %d seconds",
            settings.translation.cache_ttl,
        )

    def _get_cache_key(self, text: str, source: str, target: str) -> str:
        return f"translation:{source}:{target}:{text}"

    async def translate_text(self, text: str, source: str, target: str) -> str:
        cache_key = self._get_cache_key(text, source, target)
        cached = await cache_service.get(cache_key)

        if cached:
            logger.debug(
                "Cache hit: translation found in cache for key '%s'",
                cache_key
            )
            return cached.decode()

        logger.debug(
            (
                "Cache miss: translation not found in cache for key '%s', "
                "calling API"
            ),
            cache_key,
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=self.headers,
                json={"q": text, "source": source, "target": target},
            )
            response.raise_for_status()
            data = response.json()
            logger.info("Translation API response: {}", data)

            if not data.get("data", {}).get("translations", {}).get(
                "translatedText"
            ):
                error_msg = f"No translation found in response: {data}"
                raise ValueError(error_msg)

            translations = data["data"]["translations"]["translatedText"]
            if not isinstance(translations, list) or not translations:
                error_msg = f"Invalid translations format in response: {data}"
                raise ValueError(error_msg)

            translation = translations[0]
            await cache_service.set(
                cache_key, translation, settings.translation.cache_ttl
            )
            logger.debug(
                "Translation cached with key '%s' for %d seconds",
                cache_key,
                settings.translation.cache_ttl,
            )
            return translation

    async def detect_language(self, text: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/detect",
                headers=self.headers,
                json={"q": text}
            )
            response.raise_for_status()
            return response.json()["data"]["detections"][0]

    async def get_languages(self) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/languages", headers=self.headers
            )
            response.raise_for_status()
            return response.json()["languages"]


translation_service = TranslationService()
