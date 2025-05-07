from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from exc import NoteNotFoundError

sys.modules['app.services.auth'] = MagicMock()
sys.modules['app.repository.note'] = MagicMock()

from app.services.notes import (
    create_note,
    get_note,
    get_all_notes,
    update_note,
    delete_note
)

mock_auth = sys.modules['app.services.auth']
mock_note_repo = sys.modules['app.repository.note']

@pytest.fixture(autouse=True)
def reset_mocks():
    mock_auth.reset_mock()
    mock_note_repo.reset_mock()
    yield


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

@pytest.fixture
def auth_patch():
    with patch("app.services.notes.authenticate_token") as mock:
        async def mock_auth(*args, **kwargs):
            user = MagicMock()
            user.user_id = 1
            return user

        mock.side_effect = mock_auth
        yield mock


@pytest.fixture
def repo_patch():
    with patch("app.services.notes.note_repo") as mock:
        mock.create = AsyncMock()
        mock.get_by_id = AsyncMock()
        mock.get_all_by_user_id = AsyncMock()
        mock.update = AsyncMock()
        mock.delete = AsyncMock()
        yield mock


async def test_create_note(mock_session, note_response, auth_patch, repo_patch):
    note_data = NoteCreate(title="Test Note", content="This is a test note")
    token = "valid_token"
    repo_patch.create.return_value = note_response

    result = await create_note(mock_session, note_data, token)

    auth_patch.assert_called_once()
    assert auth_patch.call_args.kwargs["session"] == mock_session
    assert auth_patch.call_args.kwargs["token"] == token

    repo_patch.create.assert_called_once()
    assert repo_patch.create.call_args.kwargs["session"] == mock_session
    assert repo_patch.create.call_args.kwargs["note_data"] == note_data
    assert repo_patch.create.call_args.kwargs["user_id"] == 1

    assert result == note_response


async def test_get_note_success(mock_session, note_response, auth_patch, repo_patch):
    note_id = 1
    token = "valid_token"
    repo_patch.get_by_id.return_value = note_response

    result = await get_note(mock_session, note_id, token)

    auth_patch.assert_called_once()
    assert auth_patch.call_args.kwargs["session"] == mock_session
    assert auth_patch.call_args.kwargs["token"] == token

    repo_patch.get_by_id.assert_called_once()
    assert repo_patch.get_by_id.call_args.kwargs["session"] == mock_session
    assert repo_patch.get_by_id.call_args.kwargs["note_id"] == note_id
    assert repo_patch.get_by_id.call_args.kwargs["user_id"] == 1

    assert result == note_response


async def test_get_note_not_found(mock_session, auth_patch, repo_patch):
    note_id = 999
    token = "valid_token"
    repo_patch.get_by_id.return_value = None

    with pytest.raises(NoteNotFoundError) as exc_info:
        await get_note(mock_session, note_id, token)

    assert str(exc_info.value) == f"Note with ID {note_id} not found"
    auth_patch.assert_called_once()
    assert auth_patch.call_args.kwargs["session"] == mock_session
    assert auth_patch.call_args.kwargs["token"] == token

    repo_patch.get_by_id.assert_called_once()
    assert repo_patch.get_by_id.call_args.kwargs["session"] == mock_session
    assert repo_patch.get_by_id.call_args.kwargs["note_id"] == note_id
    assert repo_patch.get_by_id.call_args.kwargs["user_id"] == 1


async def test_get_all_notes(mock_session, note_response, auth_patch, repo_patch):
    token = "valid_token"
    notes = [note_response, note_response]
    repo_patch.get_all_by_user_id.return_value = notes

    result = await get_all_notes(mock_session, token)

    auth_patch.assert_called_once()
    assert auth_patch.call_args.kwargs["session"] == mock_session
    assert auth_patch.call_args.kwargs["token"] == token

    repo_patch.get_all_by_user_id.assert_called_once()
    assert repo_patch.get_all_by_user_id.call_args.kwargs["session"] == mock_session
    assert repo_patch.get_all_by_user_id.call_args.kwargs["user_id"] == 1

    assert result == notes
    assert len(result) == 2


async def test_update_note_success(mock_session, note_response, auth_patch, repo_patch):
    note_id = 1
    token = "valid_token"
    note_data = NoteUpdate(title="Updated Title")
    repo_patch.update.return_value = note_response

    result = await update_note(mock_session, note_id, note_data, token)

    auth_patch.assert_called_once()
    assert auth_patch.call_args.kwargs["session"] == mock_session
    assert auth_patch.call_args.kwargs["token"] == token

    repo_patch.update.assert_called_once()
    assert repo_patch.update.call_args.kwargs["session"] == mock_session
    assert repo_patch.update.call_args.kwargs["note_id"] == note_id
    assert repo_patch.update.call_args.kwargs["user_id"] == 1
    assert repo_patch.update.call_args.kwargs["note_data"] == note_data

    assert result == note_response


async def test_update_note_not_found(mock_session, auth_patch, repo_patch):
    note_id = 999
    token = "valid_token"
    note_data = NoteUpdate(title="Updated Title")
    repo_patch.update.return_value = None

    with pytest.raises(NoteNotFoundError) as exc_info:
        await update_note(mock_session, note_id, note_data, token)

    assert str(exc_info.value) == f"Note with ID {note_id} not found"
    auth_patch.assert_called_once()
    assert auth_patch.call_args.kwargs["session"] == mock_session
    assert auth_patch.call_args.kwargs["token"] == token

    repo_patch.update.assert_called_once()
    assert repo_patch.update.call_args.kwargs["session"] == mock_session
    assert repo_patch.update.call_args.kwargs["note_id"] == note_id
    assert repo_patch.update.call_args.kwargs["user_id"] == 1
    assert repo_patch.update.call_args.kwargs["note_data"] == note_data


async def test_delete_note_success(mock_session, note_response, auth_patch, repo_patch):

    note_id = 1
    token = "valid_token"
    repo_patch.get_by_id.return_value = note_response

    result = await delete_note(mock_session, note_id, token)

    assert result is True
    auth_patch.assert_called_once()
    assert auth_patch.call_args.kwargs["session"] == mock_session
    assert auth_patch.call_args.kwargs["token"] == token

    repo_patch.get_by_id.assert_called_once()
    assert repo_patch.get_by_id.call_args.kwargs["session"] == mock_session
    assert repo_patch.get_by_id.call_args.kwargs["note_id"] == note_id
    assert repo_patch.get_by_id.call_args.kwargs["user_id"] == 1

    repo_patch.delete.assert_called_once()
    assert repo_patch.delete.call_args.kwargs["session"] == mock_session
    assert repo_patch.delete.call_args.kwargs["note_id"] == note_id
    assert repo_patch.delete.call_args.kwargs["user_id"] == 1


async def test_delete_note_not_found(mock_session, auth_patch, repo_patch):

    note_id = 999
    token = "valid_token"
    repo_patch.get_by_id.return_value = None

    with pytest.raises(NoteNotFoundError) as exc_info:
        await delete_note(mock_session, note_id, token)

    assert str(exc_info.value) == f"Note with ID {note_id} not found"
    auth_patch.assert_called_once()
    assert auth_patch.call_args.kwargs["session"] == mock_session
    assert auth_patch.call_args.kwargs["token"] == token

    repo_patch.get_by_id.assert_called_once()
    assert repo_patch.get_by_id.call_args.kwargs["session"] == mock_session
    assert repo_patch.get_by_id.call_args.kwargs["note_id"] == note_id
    assert repo_patch.get_by_id.call_args.kwargs["user_id"] == 1

    repo_patch.delete.assert_not_called()
