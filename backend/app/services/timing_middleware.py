import time

from config import settings
from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from logger import get_logger


logger = get_logger(name=__name__, debug=settings.run.debug)


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        process_time_ms = round(process_time * 1000, 2)

        endpoint = f"{request.method} {request.url.path}"

        if process_time_ms > 200:
            logger.warning(
                "SLOW API: %s took %sms (exceeds 200ms threshold)",
                endpoint,
                process_time_ms,
            )
        else:
            logger.warning("API TIMING: %s - %sms", endpoint, process_time_ms)

        # Add response time header
        response.headers["X-Process-Time"] = str(process_time_ms)

        return response
