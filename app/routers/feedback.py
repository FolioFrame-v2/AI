from fastapi import APIRouter, Depends

from app.core.security import verify_internal_api_key
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.gemini_service import generate_feedback

router = APIRouter(prefix="/api/v1", tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse, dependencies=[Depends(verify_internal_api_key)])
async def create_feedback(request: FeedbackRequest) -> FeedbackResponse:
    return await generate_feedback(request)
