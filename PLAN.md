# dear-agent — PLAN

> 목표·범위·의사결정. 실행법·환경변수는 README. (CONVENTIONS §6)

## 목표 / 범위
AI 코딩 에이전트와 만드는 프로젝트를 위한 초소형 문서 체계 — 다음 세션의 에이전트에게 남기는 편지. 세션 간 맥락 소실을 프로젝트당 md 5종(PLAN·HANDOFF·LOG·README·CLAUDE, 역할 중복 없음)으로 푼다. **Tier 1** = 레포 하나에 `_templates/` 5종 복사 · **Tier 2** = 워크스페이스 template(분류 폴더 + `_INDEX`/`OVERVIEW` 생성기).

범위 밖: meta·워크스페이스 밖 폴더(§1). `_INDEX.md`·`OVERVIEW.md`는 생성물 — 손 편집 금지(§4). 스킬·훅 계층은 Claude Code 전용(다른 에이전트는 md + `AGENTS.md` 복사). 문서는 KO 정본·EN 미러.

## 기술 결정
- **파일 5종, 역할 1개씩** — 큰 CLAUDE.md 하나는 갱신 주기가 섞여 전부 다시 쓰거나 아무것도 안 쓰게 된다(README FAQ에서 기각). 상태의 단일 원본은 HANDOFF frontmatter(§4·§5).
- **생성기 2본**(`build-index.ps1`/`build-index.py`) — 의존성 0, **바이트 동일 출력**(CI 강제). PowerShell 5.1+/Python 3.7+ 어느 쪽만 있어도 동작.
- **강제 3중 계층**(§9) — CLAUDE.md 상시 컨텍스트 · 스킬(절차 + `/handoff`) · 훅(SessionStart 주입 + Stop 게이트). Python 없으면 훅만 조용히 비활성.
- **훅 스코프 디스패처** — 세션 cwd로 project/root 판정, 해당 프로젝트만 주입·게이트. 변경 감지는 git-aware(무시 파일 오탐 제거).
- **HANDOFF 갱신 강제 = 회수 방식** — 매 응답 Stop block 폐기 → dirty 플래그, 다음 SessionStart가 git log/diff로 회수 유도.

## 마일스톤
- [x] 템플릿 5종·생성기·`_example/` 데모
- [x] 강제 3중 계층(스킬+훅+CI)·영어 미러
- [x] 훅 스코프 디스패처·git-aware 변경 감지
- [x] HANDOFF 갱신 강제를 회수 방식으로 재설계
- [ ] Claude Code 플러그인 패키징
- [ ] 데모 GIF
- [ ] `_templates/`에 AGENTS.md 동봉
