class AIServiceError(Exception):
    """AI 서버 내부에서 발생하는 예외의 기반 클래스"""


class GeminiError(AIServiceError):
    """Gemini 호출 또는 응답 처리 중 발생한 오류"""
