import os

os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("AI_SERVICE_API_KEY", "test-internal-key")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app

TEST_API_KEY = os.environ["AI_SERVICE_API_KEY"]


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
