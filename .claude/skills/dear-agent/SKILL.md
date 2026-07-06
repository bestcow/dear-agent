---
name: dear-agent
description: 이 워크스페이스의 문서 규약(프로젝트당 md 5종·HANDOFF 단일 원본·목차 생성) 실행 절차. 프로젝트 작업을 시작할 때, 코드를 수정한 세션을 끝낼 때, 새 프로젝트나 분류 폴더를 만들 때, 폴더 구조가 바뀔 때, HANDOFF·_INDEX·OVERVIEW를 다룰 때 반드시 사용한다. Use when starting or finishing work on any project in this workspace, when creating a project or category folder, or when the folder structure changes.
---

# dear-agent 문서 규약 실행 절차

단일 기준은 루트 [CONVENTIONS.md](../../../CONVENTIONS.md)다. 이 스킬은 그 규약을 "언제 무엇을 하나"로 압축한 체크리스트다.

## 세션 시작 — 프로젝트 작업 전

1. 대상 프로젝트의 `HANDOFF.md`를 읽는다 — 마지막 작업 / 다음 할 일 / 막힌 것.
2. 필요하면 `PLAN.md`(왜·범위)·`CLAUDE.md`(명령·함정)도 읽는다.
3. `OVERVIEW.md`·`_INDEX.md`는 지도일 뿐이며 **생성물** — 직접 편집 금지.

## 세션 종료 — 코드/기능을 수정했다면 (필수)

1. 해당 프로젝트 `HANDOFF.md` 본문 갱신: 마지막 작업 / 다음 할 일 / 막힌 것.
2. frontmatter 갱신: `status`(기획|개발|운영|보류) · `updated`(오늘, YYYY-MM-DD) · `summary`(한 줄).
3. 굵직한 변경(기능 완성·버그 수정·버전업)이면 `LOG.md`에 한 줄 추가.
4. Stop 훅(handoff_guard)이 이 갱신을 검사한다 — 갱신 없이 끝내면 종료가 차단된다.

## 새 프로젝트 만들기

1. 분류 폴더 아래 프로젝트 폴더를 만든다 (분류는 미리 깔지 않는다 — CONVENTIONS §2).
2. `_templates/`의 md 5종(PLAN·HANDOFF·LOG·README·CLAUDE)만 복사한다. `.remember/`·`.claude/`는 복사 금지.
3. 최소 PLAN·HANDOFF·CLAUDE를 먼저 채운다. 빈 섹션은 `_해당 없음_`.
4. 아래 "목차 재생성"을 실행한다.

## 목차 재생성 — 폴더 구조·상태가 바뀔 때마다

- Windows: `powershell -ExecutionPolicy Bypass -File ./build-index.ps1`
- PowerShell 없음: `python3 build-index.py` (동일 출력)

생성기 경고(placeholder 미충전·status 오타·날짜 형식)가 나오면 그 자리에서 고친다.

## 문서 경계 (중복 금지 — CONVENTIONS §6)

README=실행법 · PLAN=왜/범위 · HANDOFF=현재 상태 · CLAUDE=에이전트 운영 · LOG=변경 연대기.
