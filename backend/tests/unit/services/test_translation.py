from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.translation import translation_service


@pytest.fixture(autouse=True)
def disable_logging():
    with patch("app.services.translation.logger.info"), patch(
        "app.services.translation.logger.debug"
    ):
        yield


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_http_response():
    response = MagicMock(spec=Response)
    response.json.return_value = {
        "data": {"translations": {"translatedText": ["Привет мир"]}}
    }
    response.raise_for_status.return_value = response
    return response


@pytest.fixture
def mock_language_response():
    response = MagicMock(spec=Response)
    response.json.return_value = {
        "data": {
            "detections": [{"language": "en", "confidence": 0.98, "isReliable": True}]
        }
    }
    response.raise_for_status.return_value = response
    return response


@pytest.fixture
def mock_languages_response():
    response = MagicMock(spec=Response)
    response.json.return_value = {
        "languages": [
            {"language": "en", "name": "English"},
            {"language": "ru", "name": "Russian"},
        ]
    }
    response.raise_for_status.return_value = response
    return response


@pytest.mark.asyncio
async def test_translate_text_from_api(monkeypatch, mock_session, mock_http_response):
    mock_cache_get = AsyncMock(return_value=None)
    monkeypatch.setattr("app.services.cache.cache_service.get", mock_cache_get)

    mock_cache_set = AsyncMock()
    monkeypatch.setattr("app.services.cache.cache_service.set", mock_cache_set)

    mock_post = AsyncMock(return_value=mock_http_response)

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = mock_post

        result = await translation_service.translate_text(
            text="Hello world", source="en", target="ru"
        )

        mock_cache_get.assert_awaited_once()
        mock_post.assert_awaited_once()
        assert mock_post.call_args[1]["json"] == {
            "q": "Hello world",
            "source": "en",
            "target": "ru",
        }
        mock_cache_set.assert_awaited_once()
        assert result == "Привет мир"


@pytest.mark.asyncio
async def test_translate_text_from_cache(monkeypatch, mock_session):
    cached_response = "Привет мир".encode()
    mock_cache_get = AsyncMock(return_value=cached_response)
    monkeypatch.setattr("app.services.cache.cache_service.get", mock_cache_get)

    mock_post = AsyncMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = mock_post

        result = await translation_service.translate_text(
            text="Hello world", source="en", target="ru"
        )

        mock_cache_get.assert_awaited_once()
        mock_post.assert_not_awaited()
        assert result == "Привет мир"


@pytest.mark.asyncio
async def test_translation_api_error(monkeypatch, mock_session):
    mock_cache_get = AsyncMock(return_value=None)
    monkeypatch.setattr("app.services.cache.cache_service.get", mock_cache_get)

    invalid_response = MagicMock(spec=Response)
    invalid_response.json.return_value = {"data": {"invalid": "structure"}}
    invalid_response.raise_for_status.return_value = invalid_response

    mock_post = AsyncMock(return_value=invalid_response)

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = mock_post

        with pytest.raises(ValueError):
            await translation_service.translate_text(
                text="Hello world", source="en", target="ru"
            )

        mock_cache_get.assert_awaited_once()
        mock_post.assert_awaited_once()


@pytest.mark.asyncio
async def test_detect_language(monkeypatch, mock_session, mock_language_response):
    mock_post = AsyncMock(return_value=mock_language_response)

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = mock_post

        result = await translation_service.detect_language(text="Hello world")

        mock_post.assert_awaited_once()
        assert result == {"language": "en", "confidence": 0.98, "isReliable": True}


@pytest.mark.asyncio
async def test_get_languages(monkeypatch, mock_session, mock_languages_response):
    mock_get = AsyncMock(return_value=mock_languages_response)

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = mock_get

        result = await translation_service.get_languages()

        mock_get.assert_awaited_once()
        assert result == [
            {"language": "en", "name": "English"},
            {"language": "ru", "name": "Russian"},
        ]
