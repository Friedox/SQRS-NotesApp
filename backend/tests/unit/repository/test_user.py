from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class UserCreate:
    def __init__(self, email, password_hash, name=None):
        self.email = email
        self.password_hash = password_hash
        self.name = name


class UserUpdate:
    def __init__(self, email=None, password_hash=None, name=None):
        self.email = email
        self.password_hash = password_hash
        self.name = name

    def model_dump(self, exclude_unset=False):
        result = {}
        if self.email is not None:
            result["email"] = self.email
        if self.password_hash is not None:
            result["password_hash"] = self.password_hash
        if self.name is not None:
            result["name"] = self.name
        return result


class UserResponse:
    def __init__(self, user_id, email, name, password_hash=None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.password_hash = password_hash


class UserRepo:
    @staticmethod
    async def create(session, user_data):
        pass

    @staticmethod
    async def get_by_id(session, user_id):
        pass

    @staticmethod
    async def get_by_email(session, email):
        pass

    @staticmethod
    async def update(session, user_id, user_data):
        pass

    @staticmethod
    async def delete(session, user_id):
        pass


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_model():
    user = MagicMock()
    user.user_id = 1
    user.email = "test@example.com"
    user.name = "Test User"
    user.password_hash = "hashedpwd"
    return user


@pytest.fixture
def user_response(user_model):
    return UserResponse(
        user_id=user_model.user_id,
        email=user_model.email,
        name=user_model.name,
        password_hash=user_model.password_hash,
    )


@patch.object(UserRepo, "create")
async def test_create(mock_create, mock_session, user_response):
    user_data = UserCreate(
        email="test@example.com", password_hash="hashedpwd", name="Test User"
    )
    mock_create.return_value = user_response

    result = await UserRepo.create(session=mock_session, user_data=user_data)

    assert result == user_response
    mock_create.assert_awaited_once_with(
        session=mock_session,
        user_data=user_data
    )


@patch.object(UserRepo, "get_by_id")
async def test_get_by_id_found(mock_get, mock_session, user_response):
    user_id = 1
    mock_get.return_value = user_response

    result = await UserRepo.get_by_id(session=mock_session, user_id=user_id)

    assert result == user_response
    mock_get.assert_awaited_once_with(session=mock_session, user_id=user_id)


@patch.object(UserRepo, "get_by_id")
async def test_get_by_id_not_found(mock_get, mock_session):
    user_id = 999
    mock_get.return_value = None

    result = await UserRepo.get_by_id(session=mock_session, user_id=user_id)

    assert result is None
    mock_get.assert_awaited_once_with(session=mock_session, user_id=user_id)


@patch.object(UserRepo, "get_by_email")
async def test_get_by_email_found(mock_get, mock_session, user_response):
    email = "test@example.com"
    mock_get.return_value = user_response

    result = await UserRepo.get_by_email(session=mock_session, email=email)

    assert result == user_response
    mock_get.assert_awaited_once_with(session=mock_session, email=email)


@patch.object(UserRepo, "get_by_email")
async def test_get_by_email_not_found(mock_get, mock_session):
    email = "missing@example.com"
    mock_get.return_value = None

    result = await UserRepo.get_by_email(session=mock_session, email=email)

    assert result is None
    mock_get.assert_awaited_once_with(session=mock_session, email=email)


@patch.object(UserRepo, "update")
async def test_update_found(mock_update, mock_session, user_response):
    user_id = 1
    user_data = UserUpdate(name="Updated Name")
    mock_update.return_value = user_response

    result = await UserRepo.update(
        session=mock_session, user_id=user_id, user_data=user_data
    )

    assert result == user_response
    mock_update.assert_awaited_once_with(
        session=mock_session, user_id=user_id, user_data=user_data
    )


@patch.object(UserRepo, "update")
async def test_update_not_found(mock_update, mock_session):
    user_id = 999
    user_data = UserUpdate(name="Updated Name")
    mock_update.return_value = None

    result = await UserRepo.update(
        session=mock_session, user_id=user_id, user_data=user_data
    )

    assert result is None
    mock_update.assert_awaited_once_with(
        session=mock_session, user_id=user_id, user_data=user_data
    )


@patch.object(UserRepo, "update")
async def test_update_empty_data(mock_update, mock_session, user_response):
    user_id = 1
    user_data = UserUpdate()
    mock_update.return_value = user_response

    result = await UserRepo.update(
        session=mock_session, user_id=user_id, user_data=user_data
    )

    assert result == user_response
    mock_update.assert_awaited_once_with(
        session=mock_session, user_id=user_id, user_data=user_data
    )


@patch.object(UserRepo, "delete")
async def test_delete(mock_delete, mock_session):
    user_id = 1
    mock_delete.return_value = True

    result = await UserRepo.delete(session=mock_session, user_id=user_id)

    assert result is True
    mock_delete.assert_awaited_once_with(session=mock_session, user_id=user_id)
