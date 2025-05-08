import uuid
from unittest.mock import AsyncMock

import bcrypt
import pytest
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import (
    UserCreateScheme,
    UserCredentialsScheme,
    UserRegisterScheme,
    UserScheme,
)
from app.services.auth import (
    authenticate,
    authenticate_token,
    hash_password,
    login_user,
    logout_user,
    register_user,
)
from exc import EmailAlreadyInUseError, InvalidCredentialsError


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def register_creds():
    return UserRegisterScheme(
        email="test1@example.com",
        password=SecretStr("pwd"),
        name="Test User",
    )


@pytest.fixture
def login_creds():
    return UserCredentialsScheme(
        email="test1@example.com",
        password=SecretStr("pwd"),
    )


@pytest.fixture
def user_obj():
    return UserScheme(
        user_id=1,
        email="test1@example.com",
        password_hash="hashedpwd",
        name="Test User",
    )


@pytest.mark.asyncio
async def test_register_user_success(
    monkeypatch, mock_session, register_creds, user_obj
):
    fake_repo = AsyncMock()
    fake_repo.is_email_in_table.return_value = False
    fake_repo.create.return_value = user_obj
    monkeypatch.setattr("app.services.auth.user_repo", fake_repo)

    fake_issue = AsyncMock(return_value="fake-token")
    monkeypatch.setattr("app.services.auth.token_mgr.issue_token", fake_issue)

    result = await register_user(
        session=mock_session,
        user_creds=register_creds
    )

    fake_repo.is_email_in_table.assert_awaited_once_with(
        session=mock_session,
        email=register_creds.email,
    )
    fake_repo.create.assert_awaited_once()
    new_user_arg = fake_repo.create.call_args.kwargs["new_user"]
    assert isinstance(new_user_arg, UserCreateScheme)
    assert new_user_arg.email == register_creds.email
    assert new_user_arg.name == register_creds.name
    assert bcrypt.checkpw(
        register_creds.password.get_secret_value().encode(),
        new_user_arg.password_hash.encode(),
    )

    fake_issue.assert_awaited_once_with(
        session=mock_session,
        user=user_obj,
    )
    assert result == {
        "new_user": user_obj,
        "auth_token": "fake-token",
    }


@pytest.mark.asyncio
async def test_register_user_email_in_use(
    monkeypatch,
    mock_session,
    register_creds
):
    fake_repo = AsyncMock()
    fake_repo.is_email_in_table.return_value = True
    monkeypatch.setattr("app.services.auth.user_repo", fake_repo)

    with pytest.raises(EmailAlreadyInUseError):
        await register_user(session=mock_session, user_creds=register_creds)


@pytest.mark.asyncio
async def test_hash_password_and_authenticate():
    password = "mypassword"
    hashed = hash_password(password)
    assert isinstance(hashed, str)

    await authenticate(stored_hash=hashed, input_password=password)

    with pytest.raises(InvalidCredentialsError):
        await authenticate(stored_hash=hashed, input_password="wrong")


@pytest.mark.asyncio
async def test_login_user_success(
    monkeypatch,
    mock_session,
    login_creds,
    user_obj
):
    fake_repo = AsyncMock()
    fake_repo.is_email_in_table.return_value = True
    fake_repo.get_pass_hash_by_email.return_value = login_creds.password
    fake_repo.login_user.return_value = user_obj
    monkeypatch.setattr("app.services.auth.user_repo", fake_repo)

    fake_auth = AsyncMock()
    monkeypatch.setattr("app.services.auth.authenticate", fake_auth)

    fake_issue = AsyncMock(return_value="fake-token")
    monkeypatch.setattr("app.services.auth.token_mgr.issue_token", fake_issue)

    result = await login_user(session=mock_session, user_creds=login_creds)

    fake_repo.is_email_in_table.assert_awaited_once_with(
        session=mock_session, email=login_creds.email
    )
    fake_repo.get_pass_hash_by_email.assert_awaited_once_with(
        session=mock_session, email=login_creds.email
    )
    fake_auth.assert_awaited_once_with(
        stored_hash=login_creds.password.get_secret_value(),
        input_password=login_creds.password.get_secret_value(),
    )
    fake_repo.login_user.assert_awaited_once_with(
        session=mock_session,
        email=login_creds.email,
        password_hash=login_creds.password.get_secret_value(),
    )
    fake_issue.assert_awaited_once_with(session=mock_session, user=user_obj)
    assert result == {"new_user": user_obj, "auth_token": "fake-token"}


@pytest.mark.asyncio
async def test_login_user_invalid_email(
    monkeypatch,
    mock_session,
    login_creds
):
    fake_repo = AsyncMock()
    fake_repo.is_email_in_table.return_value = False
    monkeypatch.setattr("app.services.auth.user_repo", fake_repo)

    with pytest.raises(InvalidCredentialsError):
        await login_user(session=mock_session, user_creds=login_creds)


@pytest.mark.asyncio
async def test_login_user_bad_password(monkeypatch, mock_session, login_creds):
    fake_repo = AsyncMock()
    fake_repo.is_email_in_table.return_value = True
    fake_repo.get_pass_hash_by_email.return_value = SecretStr("hashedpwd")
    monkeypatch.setattr("app.services.auth.user_repo", fake_repo)

    fake_auth = AsyncMock(side_effect=InvalidCredentialsError())
    monkeypatch.setattr("app.services.auth.authenticate", fake_auth)

    with pytest.raises(InvalidCredentialsError):
        await login_user(session=mock_session, user_creds=login_creds)


@pytest.mark.asyncio
async def test_authenticate_token_success(monkeypatch, mock_session):
    fake_decrypt = AsyncMock(return_value={"user_id": 1})
    monkeypatch.setattr("app.services.auth.token_mgr.decrypt", fake_decrypt)

    expected_user = UserScheme(
        user_id=1,
        email="e",
        password_hash="h",
        name=None
    )
    
    fake_repo = AsyncMock(get=AsyncMock(return_value=expected_user))
    monkeypatch.setattr("app.services.auth.user_repo", fake_repo)

    result = await authenticate_token(session=mock_session, token="tok")

    fake_decrypt.assert_awaited_once_with(session=mock_session, token="tok")
    fake_repo.get.assert_awaited_once_with(session=mock_session, user_id=1)
    assert result == expected_user


@pytest.mark.asyncio
async def test_logout_user(monkeypatch, mock_session):
    fake_auth_token = AsyncMock()
    monkeypatch.setattr(
        "app.services.auth.authenticate_token",
        fake_auth_token
    )

    jti_val = str(uuid.uuid4())
    fake_decrypt = AsyncMock(return_value={"jti": jti_val})
    fake_logout = AsyncMock()
    monkeypatch.setattr("app.services.auth.token_mgr.decrypt", fake_decrypt)
    monkeypatch.setattr("app.services.auth.token_mgr.logout", fake_logout)

    result = await logout_user(session=mock_session, token="tok")

    fake_auth_token.assert_awaited_once_with(session=mock_session, token="tok")
    fake_decrypt.assert_awaited_once_with(session=mock_session, token="tok")
    fake_logout.assert_awaited_once_with(session=mock_session, jti=jti_val)
    assert result == {"logged_out": True}
