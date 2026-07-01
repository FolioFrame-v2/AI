import logging
from functools import lru_cache

from google import genai
from google.genai import types as genai_types

from app.core.config import get_settings
from app.errors.exceptions import GeminiError
from app.schemas.feedback import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)

settings = get_settings()


@lru_cache
def _get_client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)

SYSTEM_INSTRUCTION = """당신은 채용 담당자에게 보여줄 포트폴리오를 첨삭하는 전문가입니다.
사용자가 포트폴리오 템플릿의 각 필드를 작성했습니다. 이 필드들은 기본정보/프로젝트/경력/학력/
자격증처럼 정해진 항목이 아니라, 관리자가 템플릿을 만들 때 자유롭게 구성한 항목입니다
(예: 협업 경험, 어려움을 극복한 경험, 향후 계획 등). 각 필드에는 제목과, 관리자가 남긴 작성
안내(description)가 있을 수 있습니다.

각 필드에 대해 다음을 수행하세요.
1. 필드 제목과 작성 안내(description, 있는 경우)를 보고 해당 필드에 어떤 내용이 담겨야 하는지
   파악합니다.
2. 사용자가 작성한 내용의 맞춤법과 문법을 교정하고, 더 구체적이고 설득력 있는 표현으로 다듬어
   ai_revised_text를 작성합니다. ai_revised_text에는 실제 포트폴리오에 그대로 들어갈 최종
   수정본 "텍스트만" 담습니다. "~하면 좋습니다", "~를 설명해 주시면" 같은 제안·안내 문구나
   "[~를 작성해주세요]" 같은 대괄호 placeholder, 그 밖의 메타 코멘트는 절대 포함하지 않습니다.
3. 원문에 없는 숫자, 고유명사, 기술 스택 등 사실 관계를 임의로 창작하지 않습니다.
4. 내용이 비어 있거나 지나치게 짧아 구체화하기 어려운 필드는 원문의 표현만 자연스럽게 다듬고
   내용을 억지로 지어내지 않습니다. 해당 필드에 보완이 필요하다는 점은 ai_revised_text가 아니라
   아래 총평(comment)에서 언급합니다.

모든 필드의 수정을 마친 뒤, 포트폴리오 전체에 대한 총평(comment)과 0~100점 사이의 종합 점수
(score)를 작성합니다. comment는 잘된 점과 개선점을 나누지 말고 하나의 자연스러운 코멘트로
작성합니다. 점수는 자기소개서/포트폴리오 평가 기준에 따라 아래 다섯 가지 항목의 배점을
각각 채점한 뒤 합산합니다.
- 구체성 (25점): 경험이 추상적 표현이 아니라 구체적인 상황, 행동, 결과로 서술되어 있는가
- 정량적 성과 (15점): 가능한 경우 수치·성과·지표로 임팩트를 보여주는가. 필드 특성상 수치화가
  어려운 내용(예: 향후 계획, 소감)이라면 이 항목을 과도하게 낮추지 않습니다.
- 논리적 흐름 (25점): 상황(Situation)-과제(Task)-행동(Action)-결과(Result) 흐름이 자연스러운가
- 직무 연관성 (20점): 서술 내용이 지원 직무/역량과 관련되어 있는가
- 표현력·가독성 (15점): 문장이 간결하고 맞춤법/어투가 자연스러운가

각 항목을 배점 범위 안에서 채점한 뒤 합산해 최종 score(0~100)를 산출합니다. 항목이 부실할수록
해당 항목 배점에서 크게 감점하고, 우수할수록 배점에 가깝게 부여합니다.
"""


def _build_prompt(request: FeedbackRequest) -> str:
    lines = ["아래는 사용자가 작성한 포트폴리오 필드 목록입니다. 각 필드를 첨삭해 주세요.\n"]
    for field in request.fields:
        block = f"[field_id={field.field_id}] 제목: {field.title}\n"
        if field.description:
            block += f"작성 안내: {field.description}\n"
        block += f"내용: {field.content}\n"
        lines.append(block)
    return "\n".join(lines)


async def generate_feedback(request: FeedbackRequest) -> FeedbackResponse:
    prompt = _build_prompt(request)

    try:
        response = await _get_client().aio.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=FeedbackResponse,
                temperature=0.4,
            ),
        )
    except Exception as exc:
        logger.exception("Gemini 호출 실패")
        raise GeminiError("AI 첨삭 생성에 실패했습니다.") from exc

    if response.parsed is not None:
        return response.parsed

    logger.warning("Gemini response.parsed is None, falling back to manual JSON parsing")
    try:
        return FeedbackResponse.model_validate_json(response.text)
    except Exception as exc:
        logger.exception("Gemini 응답 파싱 실패")
        raise GeminiError("AI 응답을 처리하는 데 실패했습니다.") from exc
