from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Note
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate


class NoteRepository:
    @staticmethod
    async def create(
        session: AsyncSession, note_data: NoteCreate, user_id: int
    ) -> NoteResponse:
        note = Note(
            title=note_data.title,
            content=note_data.content,
            user_id=user_id,
        )

        session.add(note)
        await session.commit()
        await session.refresh(note)

        return NoteResponse.model_validate(note, from_attributes=True)

    @staticmethod
    async def get_by_id(
        session: AsyncSession, note_id: int, user_id: int
    ) -> NoteResponse | None:
        note = await session.scalar(
            select(Note).where(
                Note.note_id == note_id,
                Note.user_id == user_id
            )
        )

        if note is None:
            return None

        return NoteResponse.model_validate(note, from_attributes=True)

    @staticmethod
    async def get_all_by_user_id(
        session: AsyncSession, user_id: int
    ) -> list[NoteResponse]:
        notes = await session.scalars(
            select(Note).where(Note.user_id == user_id)
        )

        return [
            NoteResponse.model_validate(note, from_attributes=True)
            for note in notes
        ]

    @staticmethod
    async def update(
        session: AsyncSession,
        note_id: int,
        user_id: int,
        note_data: NoteUpdate
    ) -> NoteResponse | None:
        note = await session.scalar(
            select(Note).where(
                Note.note_id == note_id,
                Note.user_id == user_id
            )
        )

        if note is None:
            return None

        update_data = note_data.model_dump(exclude_unset=True)

        if update_data:
            await session.execute(
                update(Note)
                .where(
                    Note.note_id == note_id,
                    Note.user_id == user_id
                )
                .values(**update_data)
            )
            await session.commit()
            await session.refresh(note)

        return NoteResponse.model_validate(note, from_attributes=True)

    @staticmethod
    async def delete(
            session: AsyncSession,
            note_id: int,
            user_id: int
    ) -> None:
        await session.execute(
            delete(Note).where(
                Note.note_id == note_id,
                Note.user_id == user_id
            )
        )

        await session.commit()


note_repo: NoteRepository = NoteRepository()
