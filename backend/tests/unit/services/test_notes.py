from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class NoteCreate:
    def __init__(self, title, content):
        self.title = title
        self.content = content


class NoteUpdate:
    def __init__(self, title=None, content=None):
        self.title = title
        self.content = content


class NoteResponse:
    def __init__(self, note_id, title, content, user_id, created_at, updated_at):
        self.note_id = note_id
        self.title = title
        self.content = content
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at


class NoteNotFoundError(Exception):
    def __init__(self, note_id):
        self.note_id = note_id
        super().__init__(f"Note with ID {note_id} not found")


async def authenticate_token_service(session, token):
    """Mock auth service that's typically in a different module"""
    pass


class NoteRepo:
    """Mock repository class with method stubs"""

    @staticmethod
    async def create(session, note_data, user_id):
        pass

    @staticmethod
    async def get_by_id(session, note_id, user_id):
        pass

    @staticmethod
    async def get_all_by_user_id(session, user_id):
        pass

    @staticmethod
    async def update(session, note_id, user_id, note_data):
        pass

    @staticmethod
    async def delete(session, note_id, user_id):
        pass


async def create_note_service(session, note_data, token):
    user = await authenticate_token_service(session=session, token=token)
    return await NoteRepo.create(
        session=session, note_data=note_data, user_id=user.user_id
    )


async def get_note_service(session, note_id, token):
    user = await authenticate_token_service(session=session, token=token)
    note = await NoteRepo.get_by_id(
        session=session, note_id=note_id, user_id=user.user_id
    )
    if note is None:
        raise NoteNotFoundError(note_id=note_id)
    return note


async def get_all_notes_service(session, token):
    user = await authenticate_token_service(session=session, token=token)
    return await NoteRepo.get_all_by_user_id(session=session, user_id=user.user_id)


async def update_note_service(session, note_id, note_data, token):
    user = await authenticate_token_service(session=session, token=token)
    updated_note = await NoteRepo.update(
        session=session, note_id=note_id, user_id=user.user_id, note_data=note_data
    )
    if updated_note is None:
        raise NoteNotFoundError(note_id=note_id)
    return updated_note


async def delete_note_service(session, note_id, token):
    user = await authenticate_token_service(session=session, token=token)
    note = await NoteRepo.get_by_id(
        session=session, note_id=note_id, user_id=user.user_id
    )
    if note is None:
        raise NoteNotFoundError(note_id=note_id)
    await NoteRepo.delete(session=session, note_id=note.note_id, user_id=user.user_id)
    return True


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def note_response():
    return NoteResponse(
        note_id=1,
        title="Test Note",
        content="This is a test note",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def user_data():
    user = MagicMock()
    user.user_id = 1
    return user


@patch("tests.unit.services.test_notes.authenticate_token_service")
@patch("tests.unit.services.test_notes.NoteRepo.create")
async def test_create_note(
    mock_repo_create, mock_auth, mock_session, note_response, user_data
):
    note_data = NoteCreate(title="Test Note", content="This is a test note")
    token = "valid_token"
    mock_auth.return_value = user_data
    mock_repo_create.return_value = note_response

    result = await create_note_service(mock_session, note_data, token)

    mock_auth.assert_awaited_once_with(session=mock_session, token=token)
    mock_repo_create.assert_awaited_once_with(
        session=mock_session, note_data=note_data, user_id=user_data.user_id
    )
    assert result == note_response


@patch("tests.unit.services.test_notes.authenticate_token_service")
@patch("tests.unit.services.test_notes.NoteRepo.get_by_id")
async def test_get_note_success(
    mock_repo_get, mock_auth, mock_session, note_response, user_data
):
    note_id = 1
    token = "valid_token"
    mock_auth.return_value = user_data
    mock_repo_get.return_value = note_response

    result = await get_note_service(mock_session, note_id, token)

    mock_auth.assert_awaited_once_with(session=mock_session, token=token)
    mock_repo_get.assert_awaited_once_with(
        session=mock_session, note_id=note_id, user_id=user_data.user_id
    )
    assert result == note_response


@patch("tests.unit.services.test_notes.authenticate_token_service")
@patch("tests.unit.services.test_notes.NoteRepo.get_by_id")
async def test_get_note_not_found(mock_repo_get, mock_auth, mock_session, user_data):
    note_id = 999
    token = "valid_token"
    mock_auth.return_value = user_data
    mock_repo_get.return_value = None

    with pytest.raises(NoteNotFoundError) as exc_info:
        await get_note_service(mock_session, note_id, token)

    assert str(exc_info.value) == f"Note with ID {note_id} not found"
    mock_auth.assert_awaited_once_with(session=mock_session, token=token)
    mock_repo_get.assert_awaited_once_with(
        session=mock_session, note_id=note_id, user_id=user_data.user_id
    )


@patch("tests.unit.services.test_notes.authenticate_token_service")
@patch("tests.unit.services.test_notes.NoteRepo.get_all_by_user_id")
async def test_get_all_notes(
    mock_repo_get_all, mock_auth, mock_session, note_response, user_data
):
    token = "valid_token"
    notes = [note_response, note_response]
    mock_auth.return_value = user_data
    mock_repo_get_all.return_value = notes

    result = await get_all_notes_service(mock_session, token)

    mock_auth.assert_awaited_once_with(session=mock_session, token=token)
    mock_repo_get_all.assert_awaited_once_with(
        session=mock_session, user_id=user_data.user_id
    )
    assert result == notes
    assert len(result) == 2


@patch("tests.unit.services.test_notes.authenticate_token_service")
@patch("tests.unit.services.test_notes.NoteRepo.update")
async def test_update_note_success(
    mock_repo_update, mock_auth, mock_session, note_response, user_data
):
    note_id = 1
    token = "valid_token"
    note_data = NoteUpdate(title="Updated Title")
    mock_auth.return_value = user_data
    mock_repo_update.return_value = note_response

    result = await update_note_service(mock_session, note_id, note_data, token)

    mock_auth.assert_awaited_once_with(session=mock_session, token=token)
    mock_repo_update.assert_awaited_once_with(
        session=mock_session,
        note_id=note_id,
        user_id=user_data.user_id,
        note_data=note_data,
    )
    assert result == note_response


@patch("tests.unit.services.test_notes.authenticate_token_service")
@patch("tests.unit.services.test_notes.NoteRepo.update")
async def test_update_note_not_found(
    mock_repo_update, mock_auth, mock_session, user_data
):
    note_id = 999
    token = "valid_token"
    note_data = NoteUpdate(title="Updated Title")
    mock_auth.return_value = user_data
    mock_repo_update.return_value = None

    with pytest.raises(NoteNotFoundError) as exc_info:
        await update_note_service(mock_session, note_id, note_data, token)

    assert str(exc_info.value) == f"Note with ID {note_id} not found"
    mock_auth.assert_awaited_once_with(session=mock_session, token=token)
    mock_repo_update.assert_awaited_once_with(
        session=mock_session,
        note_id=note_id,
        user_id=user_data.user_id,
        note_data=note_data,
    )


@patch("tests.unit.services.test_notes.authenticate_token_service")
@patch("tests.unit.services.test_notes.NoteRepo.get_by_id")
@patch("tests.unit.services.test_notes.NoteRepo.delete")
async def test_delete_note_success(
    mock_repo_delete, mock_repo_get, mock_auth, mock_session, note_response, user_data
):
    note_id = 1
    token = "valid_token"
    mock_auth.return_value = user_data
    mock_repo_get.return_value = note_response
    mock_repo_delete.return_value = True

    result = await delete_note_service(mock_session, note_id, token)

    assert result is True
    mock_auth.assert_awaited_once_with(session=mock_session, token=token)
    mock_repo_get.assert_awaited_once_with(
        session=mock_session, note_id=note_id, user_id=user_data.user_id
    )
    mock_repo_delete.assert_awaited_once_with(
        session=mock_session, note_id=note_id, user_id=user_data.user_id
    )


@patch("tests.unit.services.test_notes.authenticate_token_service")
@patch("tests.unit.services.test_notes.NoteRepo.get_by_id")
@patch("tests.unit.services.test_notes.NoteRepo.delete")
async def test_delete_note_not_found(
    mock_repo_delete, mock_repo_get, mock_auth, mock_session, user_data
):
    note_id = 999
    token = "valid_token"
    mock_auth.return_value = user_data
    mock_repo_get.return_value = None

    with pytest.raises(NoteNotFoundError) as exc_info:
        await delete_note_service(mock_session, note_id, token)

    assert str(exc_info.value) == f"Note with ID {note_id} not found"
    mock_auth.assert_awaited_once_with(session=mock_session, token=token)
    mock_repo_get.assert_awaited_once_with(
        session=mock_session, note_id=note_id, user_id=user_data.user_id
    )
    mock_repo_delete.assert_not_awaited()
