from app.errors.exceptions import GeminiQuotaExceededError
from app.schemas.feedback import FeedbackResponse, FieldRevision, FieldType
from tests.conftest import TEST_API_KEY

VALID_PAYLOAD = {
    "fields": [
        {
            "field_id": 1,
            "field_type": "CUSTOM_FIELD",
            "title": "협업 경험",
            "content": "4명이서 웹서비스 프로젝트를 진행했습니다.",
        }
    ]
}


async def test_feedback_requires_api_key(client):
    response = await client.post("/api/v1/feedback", json=VALID_PAYLOAD)
    assert response.status_code == 401


async def test_feedback_rejects_wrong_api_key(client):
    response = await client.post(
        "/api/v1/feedback", json=VALID_PAYLOAD, headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401


async def test_feedback_success(client, monkeypatch):
    fake_response = FeedbackResponse(
        comment="총평입니다.",
        score=80,
        fields=[
            FieldRevision(
                field_id=1,
                field_type=FieldType.CUSTOM_FIELD,
                ai_revised_text="수정된 내용입니다.",
            )
        ],
    )

    async def fake_generate_feedback(request):
        return fake_response

    monkeypatch.setattr("app.routers.feedback.generate_feedback", fake_generate_feedback)

    response = await client.post(
        "/api/v1/feedback",
        json=VALID_PAYLOAD,
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["score"] == 80
    assert body["fields"][0]["ai_revised_text"] == "수정된 내용입니다."


async def test_feedback_quota_exceeded_returns_429(client, monkeypatch):
    async def fake_generate_feedback(request):
        raise GeminiQuotaExceededError("할당량 초과")

    monkeypatch.setattr("app.routers.feedback.generate_feedback", fake_generate_feedback)

    response = await client.post(
        "/api/v1/feedback",
        json=VALID_PAYLOAD,
        headers={"X-API-Key": TEST_API_KEY},
    )

    assert response.status_code == 429
