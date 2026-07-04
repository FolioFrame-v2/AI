import secrets
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_internal_api_key(api_key: Optional[str] = Security(_api_key_header)) -> None:
    settings = get_settings()
    if not api_key or not secrets.compare_digest(api_key, settings.ai_service_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 API 키입니다.")
