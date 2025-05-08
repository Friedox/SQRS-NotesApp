import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TokenCreate:
    def __init__(self, user_id, fp, expires_at):
        self.user_id = user_id
        self.fp = fp
        self.expires_at = expires_at


class TokenResponse:
    def __init__(
        self,
        jti,
        user_id,
        fp,
        expires_at,
        created_at,
        revoked=False
    ):
        self.jti = jti
        self.user_id = user_id
        self.fp = fp
        self.expires_at = expires_at
        self.created_at = created_at
        self.revoked = revoked


class TokenRepo:
    @staticmethod
    async def create(session, token_data):
        pass

    @staticmethod
    async def get_by_jti(session, jti):
        pass

    @staticmethod
    async def revoke(session, jti):
        pass

    @staticmethod
    async def is_revoked(session, jti):
        pass

    @staticmethod
    async def delete_expired(session):
        pass


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def token_model():
    token = MagicMock()
    token.jti = uuid.uuid4()
    token.user_id = 1
    token.fp = "fingerprint"
    token.created_at = datetime.now()
    token.expires_at = token.created_at + timedelta(hours=1)
    token.revoked = False
    return token


@pytest.fixture
def token_response(token_model):
    return TokenResponse(
        jti=token_model.jti,
        user_id=token_model.user_id,
        fp=token_model.fp,
        expires_at=token_model.expires_at,
        created_at=token_model.created_at,
        revoked=token_model.revoked,
    )


@patch.object(TokenRepo, "create")
async def test_create(mock_create, mock_session, token_response):
    token_data = TokenCreate(
        user_id=1,
        fp="fingerprint",
        expires_at=token_response.expires_at,
    )
    mock_create.return_value = token_response

    result = await TokenRepo.create(
        session=mock_session,
        token_data=token_data
    )

    assert result == token_response
    mock_create.assert_awaited_once_with(
        session=mock_session,
        token_data=token_data
    )


@patch.object(TokenRepo, "get_by_jti")
async def test_get_by_jti_found(mock_get, mock_session, token_response):
    jti = token_response.jti
    mock_get.return_value = token_response

    result = await TokenRepo.get_by_jti(session=mock_session, jti=jti)

    assert result == token_response
    mock_get.assert_awaited_once_with(session=mock_session, jti=jti)


@patch.object(TokenRepo, "get_by_jti")
async def test_get_by_jti_not_found(mock_get, mock_session):
    jti = uuid.uuid4()
    mock_get.return_value = None

    result = await TokenRepo.get_by_jti(session=mock_session, jti=jti)

    assert result is None
    mock_get.assert_awaited_once_with(session=mock_session, jti=jti)


@patch.object(TokenRepo, "revoke")
async def test_revoke(mock_revoke, mock_session):
    jti = uuid.uuid4()
    mock_revoke.return_value = True

    result = await TokenRepo.revoke(session=mock_session, jti=jti)

    assert result is True
    mock_revoke.assert_awaited_once_with(session=mock_session, jti=jti)


@patch.object(TokenRepo, "is_revoked")
async def test_is_revoked(mock_is_revoked, mock_session):
    jti = uuid.uuid4()
    mock_is_revoked.return_value = False

    result = await TokenRepo.is_revoked(session=mock_session, jti=jti)

    assert result is False
    mock_is_revoked.assert_awaited_once_with(session=mock_session, jti=jti)


@patch.object(TokenRepo, "delete_expired")
async def test_delete_expired(mock_delete, mock_session):
    mock_delete.return_value = 3

    result = await TokenRepo.delete_expired(session=mock_session)

    assert result == 3
    mock_delete.assert_awaited_once_with(session=mock_session)
