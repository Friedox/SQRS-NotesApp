from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    title: str
    content: str


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class NoteResponse(NoteBase):
    note_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
