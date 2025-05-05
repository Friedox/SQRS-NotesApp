from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repository.note import note_repo
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate


async def create_note(session: AsyncSession, note_data: NoteCreate, user: User) -> NoteResponse:
    return await note_repo.create(session=session, note_data=note_data, user_id=user.user_id)


async def get_note(session: AsyncSession, note_id: int, user: User) -> NoteResponse:
    note = await note_repo.get_by_id(session=session, note_id=note_id, user_id=user.user_id)

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found"
        )

    return note


async def get_all_notes(session: AsyncSession, user: User) -> list[NoteResponse]:
    """Get all notes for the current user"""
    return await note_repo.get_all_by_user_id(session=session, user_id=user.user_id)


async def update_note(
        session: AsyncSession,
        note_id: int,
        note_data: NoteUpdate,
        user: User
) -> NoteResponse:
    updated_note = await note_repo.update(
        session=session,
        note_id=note_id,
        user_id=user.user_id,
        note_data=note_data
    )

    if updated_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found"
        )

    return updated_note


async def delete_note(session: AsyncSession, note_id: int, user: User) -> bool:
    result = await note_repo.delete(session=session, note_id=note_id, user_id=user.user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found"
        )

    return True
