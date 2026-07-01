import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors.exceptions import GeminiError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(GeminiError)
    async def gemini_error_handler(request: Request, exc: GeminiError) -> JSONResponse:
        logger.error("Gemini error on %s: %s", request.url.path, exc)
        return JSONResponse(status_code=502, content={"detail": str(exc)})
