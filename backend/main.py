from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from logger import get_logger
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.api import router as main_router
from config import settings


logger = get_logger(name=__name__, debug=settings.run.debug)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


middleware = [
    Middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=settings.run.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]


app = FastAPI(
    title="Simple Notes API",
    description="Simple Notes API",
    version="0.1.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs/",
    lifespan=lifespan,
    middleware=middleware,
)


app.include_router(main_router)

if __name__ == "__main__":
    logger.info("🚀 Starting up...")
    logger.debug(settings.database.db_url)

    uvicorn.run("main:app", host=settings.run.host, port=settings.run.port, reload=True)
