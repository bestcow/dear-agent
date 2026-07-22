---
status: 운영
updated: 2026-07-16
summary: 규약 3중 강제(스킬+훅+CI)·스코프 디스패처·영어 미러. HANDOFF 갱신 강제를 회수 방식으로 재설계 — Stop 훅 매 응답 block 폐기→더러움 플래그(.claude/tmp/dirty-*.flag), 다음 SessionStart가 project 스코프서 감지해 git log/diff로 회수 유도(초안→확인). CONVENTIONS §5에 summary=현재상태 스냅샷 규칙(KO/EN) 추가.
repo: bestcow/dear-agent
---

# dear-agent — HANDOFF

> 작업 세션 끝낼 때마다 갱신. 위 frontmatter가 상태의 단일 원본. (CONVENTIONS §4·§5)

## 마지막 작업
_2026-07-16: HANDOFF 갱신 강제를 회수 방식으로 재설계 (block→회수)._

- Stop 훅(`handoff_guard`): 매 응답 종료 `block` 폐기 → `.claude/tmp/dirty-<slug>.flag` 마킹, HANDOFF 갱신하면 클리어. block이 AI를 매번 재소환하던 병목 제거.
- SessionStart(`session_brief`): project 스코프서 지난 세션 dirty 감지 시 회수 프롬프트 + `git log`/`status`/`diff --stat` 주입(초안→사용자 확인). `_git`·`recovery_block` 신규.
- `workspace_lib`: `dirty_path`/`mark_dirty`/`read_dirty`/`clear_dirty` 추가.
- CONVENTIONS §5(KO/EN)·`_templates/HANDOFF.md`: `summary`=현재상태 스냅샷·상한 ≈800자·이력 금지(그건 LOG)·갱신은 덮어쓰기 규칙 명문화.
- 알려진 한계(설계상 의도): 회수 알림 single-shot — clean 세션이 stale 플래그를 클리어. git이 backstop이라 알림 유실이지 데이터 유실 아님.
- 검증은 downstream(workspace 사본)에서 41 tests green(실제 git repo 픽스처로 회수 주입 경로까지). push `853c883`.

## 다음 할 일
- 업데이트 트윗 게시(초안 준비됨 — "종료 막는다"를 맨 위로 둔 버전).
- 백로그: Claude Code 플러그인 패키징, 데모 GIF, `_templates/`에 AGENTS.md 동봉.

## 막힌 것
_해당 없음_
