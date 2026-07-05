# CLAUDE.md — todo-api

> 에이전트 운영 가이드: 명령·코드지도·함정. 실행법(사람)=README · 왜·범위=PLAN · 현재상태=HANDOFF. (CONVENTIONS §6)

팀 내부용 할 일 API — FastAPI + SQLite.

## 명령어
- 실행: `uv run fastapi dev main.py`
- 검증(린트/타입/테스트): `uv run ruff check . && uv run pytest`

## 코드 지도 · 컨벤션
- `main.py` — 앱 진입점 · `routers/` — 엔드포인트 · `models.py` — DB 모델
- 응답 스키마는 `schemas.py`에만 정의한다 (라우터에 인라인 금지).

## 함정
- SQLite 파일(`app.db`)은 커밋 금지 — `.gitignore`에 있음.
