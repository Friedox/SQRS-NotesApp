import hashlib
from unittest.mock import AsyncMock
from uuid import uuid4

import jwt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.token import TokenScheme
from app.services.security import TokenManager, _fingerprint
from config import settings
from exc import InvalidCredentialsError


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_payload():
    return {"user_id": 1}


@pytest.mark.asyncio
async def test_generate_token(monkeypatch, mock_session, sample_payload):
    fake_jti = uuid4()
    monkeypatch.setattr("app.services.security.uuid4", lambda: fake_jti)

    fake_repo = AsyncMock()
    monkeypatch.setattr("app.services.security.token_repo", fake_repo)
    monkeypatch.setattr(
        "app.services.security.jwt.encode",
        lambda payload, key, algorithm: "jwt_token",
    )

    settings.security.jwt_expires_in = 3600
    settings.security.jwt_issuer_name = "issuer"
    settings.security.jwt_private_key.get_secret_value = lambda: "private_key"

    payload = sample_payload.copy()
    token = await TokenManager.generate_token(
        session=mock_session,
        payload=payload,
        user_id=1,
        expires_in=100,
    )

    assert token == "jwt_token"
    assert "exp" in payload and "iss" in payload and "jti" in payload

    fake_repo.save.assert_awaited_once()
    saved = fake_repo.save.call_args.kwargs["token"]
    assert isinstance(saved, TokenScheme)
    assert saved.jti == fake_jti
    assert saved.user_id == 1


@pytest.mark.asyncio
async def test_decrypt_success(monkeypatch, mock_session):
    monkeypatch.setattr(
        "app.services.security.jwt.decode",
        lambda token, key, algorithms, options: {"user_id": 1},
    )
    fake_repo = AsyncMock()
    fake_repo.is_allowed.return_value = True
    monkeypatch.setattr("app.services.security.token_repo", fake_repo)

    result = await TokenManager.decrypt(session=mock_session, token="token")

    assert result == {"user_id": 1}
    fake_repo.is_allowed.assert_awaited_once()


@pytest.mark.asyncio
async def test_decrypt_expired(monkeypatch, mock_session):
    monkeypatch.setattr(
        "app.services.security.jwt.decode",
        lambda *args, **kwargs: (_ for _ in ()).throw(jwt.ExpiredSignatureError()),
    )

    with pytest.raises(ValueError) as exc:
        await TokenManager.decrypt(session=mock_session, token="tok")
    assert str(exc.value) == "Token expired"


@pytest.mark.asyncio
async def test_decrypt_invalid(monkeypatch, mock_session):
    monkeypatch.setattr(
        "app.services.security.jwt.decode",
        lambda *args, **kwargs: (_ for _ in ()).throw(jwt.InvalidTokenError()),
    )

    with pytest.raises(ValueError) as exc:
        await TokenManager.decrypt(session=mock_session, token="tok")
    assert str(exc.value) == "Invalid token"


@pytest.mark.asyncio
async def test_decrypt_not_allowed(monkeypatch, mock_session):
    monkeypatch.setattr(
        "app.services.security.jwt.decode",
        lambda token, key, algorithms, options: {"user_id": 1},
    )
    fake_repo = AsyncMock()
    fake_repo.is_allowed.return_value = False
    monkeypatch.setattr("app.services.security.token_repo", fake_repo)

    with pytest.raises(InvalidCredentialsError):
        await TokenManager.decrypt(session=mock_session, token="tok")


@pytest.mark.asyncio
async def test_fingerprint_issue_and_logout(monkeypatch, mock_session):
    token_str = "header.payload.signature"
    unhashed = "header.payload"
    expected = hashlib.sha256(unhashed.encode()).hexdigest()
    assert _fingerprint(token_str) == expected

    manager = TokenManager()
    manager.generate_token = AsyncMock(return_value="new_tok")
    user = AsyncMock(user_id=1)
    issued = await manager.issue_token(session=mock_session, user=user)
    assert issued == "new_tok"

    fake_repo = AsyncMock()
    monkeypatch.setattr("app.services.security.token_repo", fake_repo)
    fake_jti = uuid4()
    await manager.logout(session=mock_session, jti=str(fake_jti))
    fake_repo.revoke.assert_awaited_once_with(session=mock_session, jti=fake_jti)
