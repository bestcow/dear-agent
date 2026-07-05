# CLAUDE.md — web-dashboard

> 에이전트 운영 가이드: 명령·코드지도·함정. 실행법(사람)=README · 왜·범위=PLAN · 현재상태=HANDOFF. (CONVENTIONS §6)

todo-api 소비용 정적 대시보드 — HTML + 바닐라 JS, 빌드 없음.

## 명령어
- 실행: `python3 -m http.server 8080`
- 검증(린트/타입/테스트): _해당 없음_ (정적 페이지 — 브라우저로 확인)

## 코드 지도 · 컨벤션
- `index.html` — 단일 페이지 · `app.js` — 로직 전부 · `config.js` — API 주소
- 외부 라이브러리 추가 금지 (빌드 없는 구조 유지가 목적).

## 함정
- `config.js`의 API 주소는 배포 환경별로 다름 — 로컬 값 커밋 주의.
