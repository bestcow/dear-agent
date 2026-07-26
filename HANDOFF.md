---
status: 운영
updated: 2026-07-26
summary: 규약 3중 강제(스킬+훅+CI)·스코프 디스패처·영어 미러. HANDOFF 갱신 강제를 회수 방식으로 재설계 — Stop 훅 매 응답 block 폐기→더러움 플래그(.claude/tmp/dirty-*.flag), 다음 SessionStart가 project 스코프서 감지해 git log/diff로 회수 유도(초안→확인). CONVENTIONS §5에 summary=현재상태 스냅샷 규칙(KO/EN) 추가. Stop 훅 CI fixture 테스트도 회수 방식에 맞춰 green 복구(07-26).
repo: bestcow/dear-agent
---

# dear-agent — HANDOFF

> 작업 세션 끝낼 때마다 갱신. 위 frontmatter가 상태의 단일 원본. (CONVENTIONS §4·§5)

## 마지막 작업
_2026-07-26: CI fixture 테스트를 회수 방식에 맞춰 갱신 — green 복구._

- `enforcement-assets`의 "hooks behave on fixture"가 옛 `스테일→"decision":"block"`을 검증해, 회수 재설계(`470ed7f`) 이후 **07-16부터 CI red**였다. 훅은 이미 block을 폐기했는데 테스트만 낡음.
- 교체(`ci.yml` `a004ff1`): 스테일 → **무출력 + `dirty-<slug>.flag` 생성**, 다음 SessionStart(project 스코프) → **`회수 필요` 주입**, clean stop → 플래그 해제·회수 안 함까지 검증.
- 검증: `WORKSPACE_HOOKS_ROOT` 오버라이드로 로컬 9/9 → push 후 GitHub CI 두 잡 green(run 30052731394).
- 직전 07-16 재설계 엔트리는 LOG로 내림(위생 규칙).

## 다음 할 일
- 업데이트 트윗 게시(초안 준비됨 — "종료 막는다"를 맨 위로 둔 버전).
- 백로그: Claude Code 플러그인 패키징, 데모 GIF, `_templates/`에 AGENTS.md 동봉.

## 막힌 것
_해당 없음_
