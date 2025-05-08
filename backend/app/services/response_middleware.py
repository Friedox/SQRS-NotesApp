import inspect
from typing import Any

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse

from app.schemas.response import ErrorResponse, SuccessResponse
from exc import ServiceException


class ResponseMiddleware:
    @staticmethod
    async def response(response: Any) -> Any:
        try:
            response_result = (
                await response if inspect.isawaitable(response) else response
            )

            if isinstance(response_result, RedirectResponse):
                return response_result

            return SuccessResponse(detail=response_result)

        except ServiceException as error_detail:
            error_response = ErrorResponse(detail=str(error_detail))

            return JSONResponse(
                content=error_response.model_dump(),
                status_code=error_detail.code,
            )

        except Exception as err:
            error_response = ErrorResponse(detail=str(err))
            return JSONResponse(
                content=error_response.model_dump(),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
