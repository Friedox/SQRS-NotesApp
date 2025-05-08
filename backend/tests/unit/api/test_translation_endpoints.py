import logging
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.v1.translation import router


@pytest.fixture(autouse=True)
def disable_logging():
    logging_level = logging.getLogger("httpx").level
    logging.getLogger("httpx").setLevel(logging.CRITICAL)
    yield
    logging.getLogger("httpx").setLevel(logging_level)


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_translate_text_endpoint(monkeypatch):
    mock_translate = AsyncMock(return_value="Привет мир")
    monkeypatch.setattr(
        "app.services.translation.translation_service.translate_text", mock_translate
    )

    mock_response = AsyncMock(return_value={"translated_text": "Привет мир"})
    monkeypatch.setattr(
        "app.services.response_middleware.ResponseMiddleware.response", mock_response
    )

    mock_auth = AsyncMock(return_value={"token": "valid_token"})
    monkeypatch.setattr("app.api.v1.translation.security", mock_auth)

    app = FastAPI()

    mock_session = AsyncMock()

    with patch("app.models.database_helper.session_getter", return_value=mock_session):
        app.include_router(router)
        client = TestClient(app)

        response = client.post(
            "/",
            json={"text": "Hello world", "source": "en", "target": "ru"},
            headers={"Authorization": "Bearer token"},
        )

        assert response.status_code == status.HTTP_200_OK
        mock_translate.assert_awaited_once_with(
            text="Hello world", source="en", target="ru"
        )
        mock_response.assert_awaited_once()


@pytest.mark.asyncio
async def test_detect_language_endpoint(monkeypatch):
    mock_detection = AsyncMock(
        return_value={"language": "en", "confidence": 0.98, "isReliable": True}
    )
    monkeypatch.setattr(
        "app.services.translation.translation_service.detect_language", mock_detection
    )

    mock_response = AsyncMock(
        return_value={"language": "en", "confidence": 0.98, "is_reliable": True}
    )
    monkeypatch.setattr(
        "app.services.response_middleware.ResponseMiddleware.response", mock_response
    )

    mock_auth = AsyncMock(return_value={"token": "valid_token"})
    monkeypatch.setattr("app.api.v1.translation.security", mock_auth)

    app = FastAPI()

    mock_session = AsyncMock()

    with patch("app.models.database_helper.session_getter", return_value=mock_session):
        app.include_router(router)
        client = TestClient(app)

        response = client.post(
            "/detection?text=Hello%20world", headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == status.HTTP_200_OK
        mock_detection.assert_awaited_once_with(text="Hello world")
        mock_response.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_languages_endpoint(monkeypatch):
    mock_languages = AsyncMock(
        return_value=[
            {"language": "en", "name": "English"},
            {"language": "ru", "name": "Russian"},
        ]
    )
    monkeypatch.setattr(
        "app.services.translation.translation_service.get_languages", mock_languages
    )

    mock_response = AsyncMock(
        return_value={
            "languages": [
                {"language": "en", "name": "English"},
                {"language": "ru", "name": "Russian"},
            ]
        }
    )
    monkeypatch.setattr(
        "app.services.response_middleware.ResponseMiddleware.response", mock_response
    )

    mock_auth = AsyncMock(return_value={"token": "valid_token"})
    monkeypatch.setattr("app.api.v1.translation.security", mock_auth)

    app = FastAPI()

    mock_session = AsyncMock()

    with patch("app.models.database_helper.session_getter", return_value=mock_session):
        app.include_router(router)
        client = TestClient(app)

        response = client.get("/languages", headers={"Authorization": "Bearer token"})

        assert response.status_code == status.HTTP_200_OK
        mock_languages.assert_awaited_once()
        mock_response.assert_awaited_once()
