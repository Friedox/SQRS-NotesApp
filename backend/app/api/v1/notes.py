from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, database_helper
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.services.notes import (
    create_note,
    delete_note,
    get_all_notes,
    get_note,
    update_note
)

router = APIRouter(tags=["Notes"])

HARDCODED_USER_ID = 1


async def get_hardcoded_user():
    mock_user = User()
    mock_user.user_id = HARDCODED_USER_ID
    return mock_user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NoteResponse)
async def create_note_endpoint(
        note_data: NoteCreate,
        session: AsyncSession = Depends(database_helper.session_getter),
):
    user = await get_hardcoded_user()
    return await create_note(session=session, note_data=note_data, user=user)


@router.get("/", response_model=list[NoteResponse])
async def get_all_notes_endpoint(
        session: AsyncSession = Depends(database_helper.session_getter),
):
    user = await get_hardcoded_user()
    return await get_all_notes(session=session, user=user)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note_endpoint(
        note_id: int = Path(title="The ID of the note to get"),
        session: AsyncSession = Depends(database_helper.session_getter),
):
    user = await get_hardcoded_user()

    return await get_note(session=session, note_id=note_id, user=user)


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note_endpoint(
        note_data: NoteUpdate,
        note_id: int = Path(title="The ID of the note to update"),
        session: AsyncSession = Depends(database_helper.session_getter),
):
    user = await get_hardcoded_user()

    return await update_note(
        session=session,
        note_id=note_id,
        note_data=note_data,
        user=user
    )


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_endpoint(
        note_id: int = Path(title="The ID of the note to delete"),
        session: AsyncSession = Depends(database_helper.session_getter),
):
    user = await get_hardcoded_user()

    await delete_note(session=session, note_id=note_id, user=user)
    return None
