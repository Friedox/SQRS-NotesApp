from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.note import note_repo
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.services.auth import authenticate_token
from exc import NoteNotFoundError


async def create_note(
    session: AsyncSession, note_data: NoteCreate, token: str
) -> NoteResponse:
    user = await authenticate_token(session=session, token=token)

    return await note_repo.create(
        session=session, note_data=note_data, user_id=user.user_id
    )


async def get_note(session: AsyncSession, note_id: int, token: str) -> NoteResponse:
    user = await authenticate_token(session=session, token=token)

    note = await note_repo.get_by_id(
        session=session, note_id=note_id, user_id=user.user_id
    )

    if note is None:
        raise NoteNotFoundError(note_id=note_id)

    return note


async def get_all_notes(session: AsyncSession, token: str) -> list[NoteResponse]:
    user = await authenticate_token(session=session, token=token)

    return await note_repo.get_all_by_user_id(session=session, user_id=user.user_id)


async def update_note(
    session: AsyncSession, note_id: int, note_data: NoteUpdate, token: str
) -> NoteResponse:
    user = await authenticate_token(session=session, token=token)

    updated_note = await note_repo.update(
        session=session, note_id=note_id, user_id=user.user_id, note_data=note_data
    )

    if updated_note is None:
        raise NoteNotFoundError(note_id=note_id)

    return updated_note


async def delete_note(session: AsyncSession, note_id: int, token: str) -> bool:
    user = await authenticate_token(session=session, token=token)

    note = await note_repo.get_by_id(
        session=session, note_id=note_id, user_id=user.user_id
    )

    if note is None:
        raise NoteNotFoundError(note_id=note_id)

    await note_repo.delete(session=session, note_id=note.note_id, user_id=user.user_id)

    return True
