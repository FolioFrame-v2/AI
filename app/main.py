import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.errors.handlers import register_exception_handlers
from app.routers import feedback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 서버 시작 중... (env=%s)", settings.app_env)
    yield
    logger.info("🛑 서버 종료 중...")


app = FastAPI(
    title="FolioFrame AI Server",
    version="0.1.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(feedback.router)


@app.get("/health")
async def health_check():
    """Docker 헬스체크용 엔드포인트"""
    return {"status": "healthy", "service": "FolioFrame AI Server", "env": settings.app_env}
