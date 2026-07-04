from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FieldType(str, Enum):
    CUSTOM_FIELD = "CUSTOM_FIELD"
    PORTFOLIO_ONE_LINER = "PORTFOLIO_ONE_LINER"
    PORTFOLIO_DESCRIPTION = "PORTFOLIO_DESCRIPTION"
    PROFILE_ONE_LINER = "PROFILE_ONE_LINER"
    PROJECT_SUMMARY = "PROJECT_SUMMARY"


class FieldInput(BaseModel):
    field_id: int = Field(
        ...,
        description=(
            "대상 컬럼의 ID. field_type=CUSTOM_FIELD면 PortfolioField.id, "
            "PROJECT_SUMMARY면 PortfolioProject.id, 그 외 고정 컬럼(포트폴리오 한줄소개/"
            "상세설명/프로필 소개)은 Portfolio.id 또는 TalentProfile.id"
        ),
    )
    field_type: FieldType = Field(
        default=FieldType.CUSTOM_FIELD,
        description="첨삭 대상 컬럼 종류 (관리자 템플릿 커스텀 필드 또는 포트폴리오/프로필 고정 컬럼)",
    )
    title: str = Field(..., description="필드 제목 (예: 프로젝트, 경력, 협업 경험 등 자유 구성)")
    description: Optional[str] = Field(
        default=None, description="관리자가 템플릿 필드 생성 시 남긴 작성 안내 (TemplateField.description)"
    )
    content: str = Field(..., description="사용자가 작성한 필드 내용")


class FeedbackRequest(BaseModel):
    portfolio_title: Optional[str] = Field(
        default=None, description="포트폴리오 제목 (Portfolio.title). 직무 연관성 평가에 참고"
    )
    job_role: Optional[str] = Field(
        default=None,
        description="지원 직군 (Portfolio.jobRole, 예: BACKEND/FRONTEND 또는 한글 라벨). 직무 연관성 평가에 참고",
    )
    fields: List[FieldInput] = Field(..., min_length=1)


class FieldRevision(BaseModel):
    field_id: int = Field(..., description="요청받은 field_id 그대로 반환")
    field_type: FieldType = Field(..., description="요청받은 field_type 그대로 반환")
    ai_revised_text: str = Field(..., description="AI가 다듬은 수정본")


class FeedbackResponse(BaseModel):
    comment: str = Field(..., description="포트폴리오 전반에 대한 총평 (잘된 점과 개선점을 종합한 코멘트)")
    score: int = Field(..., ge=0, le=100, description="종합 점수 (0~100)")
    fields: List[FieldRevision]
