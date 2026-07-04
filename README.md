# AI
폴리오프레임 v2 AI 서버

Gemini 2.5 Flash 기반으로 포트폴리오 필드 내용을 첨삭(보완/맞춤법 수정/개선)하는 FastAPI 서버입니다.
FolioFrame_BE(Spring)가 이 서버를 호출해 AI 첨삭 결과를 받아 저장합니다.

## 실행 방법

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt

cp .env.example .env  # GEMINI_API_KEY, AI_SERVICE_API_KEY 채워넣기

uvicorn app.main:app --reload --port 8000
```

`GEMINI_API_KEY`와 `AI_SERVICE_API_KEY`가 비어 있으면 서버가 기동 시점에 바로 실패합니다.

## 인증

`POST /api/v1/feedback`은 `X-API-Key` 헤더로 내부 인증을 요구합니다. 값은 `AI_SERVICE_API_KEY`
환경변수와 동일해야 하며, FolioFrame_BE의 `AI_SERVICE_API_KEY`(`ai-service.api-key`)와 같은 값을
공유해야 합니다. `GET /health`는 인증 없이 접근 가능합니다.

## 테스트

```bash
pip install -r requirements-dev.txt
pytest
```

## 프로젝트 구조

```
app/
├── main.py          # FastAPI 앱 진입점
├── core/
│   ├── config.py    # 환경변수(.env) 로드
│   └── security.py  # BE-AI 내부 API 키 검증
├── routers/          # API 엔드포인트
├── schemas/          # 요청/응답 Pydantic 모델
└── services/          # Gemini 호출 등 비즈니스 로직
tests/                # pytest 테스트
```
