# todo-api

> 소개·실행법·환경변수. 의사결정·범위는 PLAN. (CONVENTIONS §6)

팀 내부용 할 일 관리 API (FastAPI + SQLite).

## 실행
```
uv sync
uv run fastapi dev main.py
```

## 환경변수
- `JWT_SECRET` — 토큰 서명 키 (`.env`에 설정)
