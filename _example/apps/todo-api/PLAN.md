# todo-api — PLAN

> 목표·범위·의사결정. 실행법·환경변수는 README. (CONVENTIONS §6)

## 목표 / 범위
팀 내부용 할 일 관리 API. 웹 프론트는 범위 밖(별도 프로젝트 web-dashboard가 소비).

## 기술 결정
FastAPI + SQLite — 내부용 소규모라 충분하고, 배포가 파일 하나로 끝난다. PostgreSQL은 사용자 100명 넘으면 재검토.

## 마일스톤
- [x] CRUD API
- [ ] JWT 인증
- [ ] 배포
