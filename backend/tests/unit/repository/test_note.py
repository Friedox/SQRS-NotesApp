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

    def model_dump(self, exclude_unset=False):
        result = {}
        if self.title is not None:
            result["title"] = self.title
        if self.content is not None:
            result["content"] = self.content
        return result


class NoteResponse:
    def __init__(
        self,
        note_id,
        title,
        content,
        user_id,
        created_at,
        updated_at
    ):
        self.note_id = note_id
        self.title = title
        self.content = content
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at


class NoteRepo:
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


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def note_model():
    note = MagicMock()
    note.note_id = 1
    note.title = "Test Note"
    note.content = "This is a test note"
    note.user_id = 1
    note.created_at = datetime.now()
    note.updated_at = datetime.now()
    return note


@pytest.fixture
def note_response(note_model):
    return NoteResponse(
        note_id=note_model.note_id,
        title=note_model.title,
        content=note_model.content,
        user_id=note_model.user_id,
        created_at=note_model.created_at,
        updated_at=note_model.updated_at,
    )


@patch.object(NoteRepo, "create")
async def test_create(mock_create, mock_session, note_response):
    note_data = NoteCreate(title="Test Note", content="This is a test note")
    user_id = 1
    mock_create.return_value = note_response

    result = await NoteRepo.create(
        session=mock_session, note_data=note_data, user_id=user_id
    )

    assert result == note_response
    mock_create.assert_awaited_once_with(
        session=mock_session, note_data=note_data, user_id=user_id
    )


@patch.object(NoteRepo, "get_by_id")
async def test_get_by_id_found(mock_get_by_id, mock_session, note_response):
    note_id = 1
    user_id = 1
    mock_get_by_id.return_value = note_response

    result = await NoteRepo.get_by_id(
        session=mock_session, note_id=note_id, user_id=user_id
    )

    assert result == note_response
    mock_get_by_id.assert_awaited_once_with(
        session=mock_session, note_id=note_id, user_id=user_id
    )


@patch.object(NoteRepo, "get_by_id")
async def test_get_by_id_not_found(mock_get_by_id, mock_session):
    note_id = 999
    user_id = 1
    mock_get_by_id.return_value = None

    result = await NoteRepo.get_by_id(
        session=mock_session, note_id=note_id, user_id=user_id
    )

    assert result is None
    mock_get_by_id.assert_awaited_once_with(
        session=mock_session, note_id=note_id, user_id=user_id
    )


@patch.object(NoteRepo, "get_all_by_user_id")
async def test_get_all_by_user_id(mock_get_all, mock_session, note_response):
    user_id = 1
    mock_get_all.return_value = [note_response, note_response]

    result = await NoteRepo.get_all_by_user_id(
        session=mock_session,
        user_id=user_id
    )

    assert len(result) == 2
    assert all(isinstance(note, NoteResponse) for note in result)
    mock_get_all.assert_awaited_once_with(
        session=mock_session,
        user_id=user_id
    )


@patch.object(NoteRepo, "update")
async def test_update_found(mock_update, mock_session, note_response):
    note_id = 1
    user_id = 1
    note_data = NoteUpdate(title="Updated Title")
    mock_update.return_value = note_response

    result = await NoteRepo.update(
        session=mock_session,
        note_id=note_id,
        user_id=user_id,
        note_data=note_data
    )

    assert result == note_response
    mock_update.assert_awaited_once_with(
        session=mock_session,
        note_id=note_id,
        user_id=user_id,
        note_data=note_data
    )


@patch.object(NoteRepo, "update")
async def test_update_not_found(mock_update, mock_session):
    note_id = 999
    user_id = 1
    note_data = NoteUpdate(title="Updated Title")
    mock_update.return_value = None

    result = await NoteRepo.update(
        session=mock_session,
        note_id=note_id,
        user_id=user_id,
        note_data=note_data
    )

    assert result is None
    mock_update.assert_awaited_once_with(
        session=mock_session,
        note_id=note_id,
        user_id=user_id,
        note_data=note_data
    )


@patch.object(NoteRepo, "update")
async def test_update_empty_data(mock_update, mock_session, note_response):
    note_id = 1
    user_id = 1
    note_data = NoteUpdate()
    mock_update.return_value = note_response

    result = await NoteRepo.update(
        session=mock_session,
        note_id=note_id,
        user_id=user_id,
        note_data=note_data
    )

    assert result == note_response
    mock_update.assert_awaited_once_with(
        session=mock_session,
        note_id=note_id,
        user_id=user_id,
        note_data=note_data
    )


@patch.object(NoteRepo, "delete")
async def test_delete(mock_delete, mock_session):
    note_id = 1
    user_id = 1
    mock_delete.return_value = True

    result = await NoteRepo.delete(
        session=mock_session, note_id=note_id, user_id=user_id
    )

    assert result is True
    mock_delete.assert_awaited_once_with(
        session=mock_session, note_id=note_id, user_id=user_id
    )
