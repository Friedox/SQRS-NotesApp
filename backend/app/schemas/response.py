from typing import Any

from pydantic import BaseModel


class Response(BaseModel):
    ok: bool = False
    detail: Any


class SuccessResponse(Response):
    ok: bool = True


class ErrorResponse(Response):
    ok: bool = False
    detail: str
