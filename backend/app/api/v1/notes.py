from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import database_helper
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.notes import (
    create_note,
    delete_note,
    get_all_notes,
    get_note,
    update_note,
)
from app.services.response_middleware import ResponseMiddleware


router = APIRouter(tags=["Notes"])
security = HTTPBearer()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_note_endpoint(
    note_data: NoteCreate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(database_helper.session_getter),
):
    return await ResponseMiddleware.response(
        create_note(session=session, note_data=note_data, token=credentials.credentials)
    )


@router.get("/")
async def get_all_notes_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(database_helper.session_getter),
):
    return await ResponseMiddleware.response(
        get_all_notes(session=session, token=credentials.credentials)
    )


@router.get("/{note_id}")
async def get_note_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    note_id: int = Path(title="The ID of the note to get"),
    session: AsyncSession = Depends(database_helper.session_getter),
):
    return await ResponseMiddleware.response(
        get_note(session=session, note_id=note_id, token=credentials.credentials)
    )


@router.patch("/{note_id}")
async def update_note_endpoint(
    note_data: NoteUpdate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    note_id: int = Path(title="The ID of the note to update"),
    session: AsyncSession = Depends(database_helper.session_getter),
):
    return await ResponseMiddleware.response(
        update_note(
            session=session,
            note_id=note_id,
            note_data=note_data,
            token=credentials.credentials,
        )
    )


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    note_id: int = Path(title="The ID of the note to delete"),
    session: AsyncSession = Depends(database_helper.session_getter),
):
    return await ResponseMiddleware.response(
        delete_note(session=session, note_id=note_id, token=credentials.credentials)
    )
