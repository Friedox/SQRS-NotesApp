from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import authenticate_token


async def get_status() -> dict[str, str]:
    now = datetime.now(UTC).strftime("%d.%m.%Y %H:%M:%S")

    return {"status": "ok", "time": now}


async def get_secured_status(session: AsyncSession, token: str):
    user = await authenticate_token(session=session, token=token)

    now = datetime.now(UTC).strftime("%d.%m.%Y %H:%M:%S")

    return {"status": "ok", "time": now, "user": user}
