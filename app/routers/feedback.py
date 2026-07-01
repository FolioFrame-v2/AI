from fastapi import APIRouter

from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.gemini_service import generate_feedback

router = APIRouter(prefix="/api/v1", tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(request: FeedbackRequest) -> FeedbackResponse:
    return await generate_feedback(request)
