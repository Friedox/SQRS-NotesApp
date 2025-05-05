from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api import router as main_router
from config import settings
from logger import get_logger


logger = get_logger(name=__name__, debug=settings.run.debug)


@asynccontextmanager
async def lifespan(app: FastAPI):
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
