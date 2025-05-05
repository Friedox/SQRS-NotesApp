import logging
from typing import Dict, List

import httpx

from config import settings


logger = logging.getLogger(__name__)


class TranslationService:
    def __init__(self):
        self.base_url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"
        self.headers = {
            "Content-Type": "application/json",
            "x-rapidapi-host": "deep-translate1.p.rapidapi.com",
            "x-rapidapi-key": settings.translation.api_key.get_secret_value(),
        }

    async def translate_text(self, text: str, source: str, target: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=self.headers,
                json={"q": text, "source": source, "target": target},
            )
            response.raise_for_status()
            data = response.json()
            logger.info("Translation API response: {}", data)

            if not data.get("data", {}).get("translations", {}).get("translatedText"):
                error_msg = "No translation found in response: {}".format(data)
                raise ValueError(error_msg)

            translations = data["data"]["translations"]["translatedText"]
            if not isinstance(translations, list) or not translations:
                error_msg = "Invalid translations format in response: {}".format(data)
                raise ValueError(error_msg)

            return translations[0]

    async def detect_language(self, text: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/detect", headers=self.headers, json={"q": text}
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
