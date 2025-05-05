from datetime import UTC, datetime


async def get_status() -> dict[str, str]:
    now = datetime.now(UTC).strftime("%d.%m.%Y %H:%M:%S")

    return {"status": "ok", "time": now}
