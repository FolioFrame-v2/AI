from typing import List, Optional

from pydantic import BaseModel, Field


class FieldInput(BaseModel):
    field_id: int = Field(..., description="포트폴리오 필드 ID (PortfolioField.id)")
    title: str = Field(..., description="필드 제목 (예: 프로젝트, 경력, 협업 경험 등 자유 구성)")
    description: Optional[str] = Field(
        default=None, description="관리자가 템플릿 필드 생성 시 남긴 작성 안내 (TemplateField.description)"
    )
    content: str = Field(..., description="사용자가 작성한 필드 내용")


class FeedbackRequest(BaseModel):
    fields: List[FieldInput] = Field(..., min_length=1)


class FieldRevision(BaseModel):
    field_id: int = Field(..., description="요청받은 field_id 그대로 반환")
    ai_revised_text: str = Field(..., description="AI가 다듬은 수정본")


class FeedbackResponse(BaseModel):
    comment: str = Field(..., description="포트폴리오 전반에 대한 총평 (잘된 점과 개선점을 종합한 코멘트)")
    score: int = Field(..., ge=0, le=100, description="종합 점수 (0~100)")
    fields: List[FieldRevision]
