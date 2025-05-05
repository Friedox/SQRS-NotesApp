from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api import router as main_router
from app.models import User, database_helper
from config import settings
from logger import get_logger

logger = get_logger(name=__name__, debug=settings.run.debug)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database_helper.session_factory() as session:
        existing_user = await session.get(User, 1)

        if not existing_user:
            logger.info("Creating test user with ID 1")

            test_user = User(
                user_id=1,
                email="test@example.com",
                password_hash="not_a_real_hash",
                name="Test User"
            )
            session.add(test_user)
            await session.commit()
            logger.info("Test user created successfully")

    yield


app = FastAPI(
    title="Simple Notes API",
    description="Simple Notes API",
    version="0.1.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs/",
    lifespan=lifespan,
)

app.include_router(main_router)

if __name__ == "__main__":
    logger.info("🚀 Starting up...")

    uvicorn.run("main:app", host=settings.run.host, port=settings.run.port, reload=True)
