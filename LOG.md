# dear-agent — LOG

> 날짜별 굵직한 변경 한 줄. 세세한 커밋은 git log. (CONVENTIONS §3)
> _EN: One line per notable change, by date. Fine-grained commits live in git log. (CONVENTIONS §3)_

## 2026-07-09 — `handoff_guard`/`session_brief` 오탐 근본수정 — `newest_file`이 `.gitignore` 존중 (HANDOFF에서 이동)
_2026-07-09: `handoff_guard`/`session_brief` 오탐 근본수정 — `newest_file`이 `.gitignore` 존중._

- `workspace_lib.newest_file`을 **git-aware**로 교체 — `git ls-files --cached --others --exclude-standard`로 추적+미추적 파일만 보고 **git 무시 파일(로그·빌드 산출물·대용량 원본)은 제외**. 백그라운드 프로세스가 갱신하는 gitignore된 파일(예: 어떤 프로젝트의 `logs/*.jsonl`)이 Stop 훅을 계속 트리거하던 오탐 해소. git 불가 환경은 기존 `os.walk`(SKIP_DIRS/SKIP_FILES) 폴백 유지 → 무회귀.
- 검증: 로그를 쏟는 프로젝트에서 OLD os.walk = `logs/*.jsonl`(오탐) vs NEW git-aware = `NONE`(통과). 정당한 코드 변경(추적/미추적 소스)은 여전히 감지.
- 배포: 원본 `tools/dear-agent/.claude/hooks/` + 실행 사본 2곳(`C:/workspace/.claude/hooks/`, sharp-edison 워크트리) 동일 반영(md5 일치).
- **root 게이트 완화 배포 확정(A)**: `handoff_guard`가 root 스코프에서 하위 프로젝트를 훑지 않는 코드는 원본엔 이미 있었으나 **실행 배포본(워크트리)이 옛 버전**이라 여전히 전 프로젝트를 게이트 → 인덱스 워크트리 cwd 세션서 외부편집(다른 세션/에디터가 건드린 다른 프로젝트 등)까지 잡히는 오탐. handoff_guard 배포로 해결 — root/out=게이트 안 함, project=그 프로젝트만 게이트(각 프로젝트는 자기 폴더 cwd 세션서). 검증: root payload=무출력(통과)·project payload=해당 HANDOFF 검사 유지.

## 2026-07-08 — 훅에 스코프 디스패처 이식(workspace_lib.py 신규) (HANDOFF에서 이동)
_2026-07-08: 훅에 스코프 디스패처 이식(workspace_lib.py 신규)._

- `session_brief`·`handoff_guard`를 스코프 판정형으로 교체 — 프로젝트 스코프면 그 프로젝트 HANDOFF만 주입/게이트, 루트 스코프면 전 프로젝트 표. 루트에서 하위 프로젝트를 mtime으로 훑던 걸 없애 동시작업·외부편집 오탐 해소.
- `workspace_lib.py`(스코프 판정·frontmatter 파서·세션 스탬프 공통부) 신규. 브랜딩 `[dear-agent]` 유지, doctor.py 미참조.
- KO/EN `CONVENTIONS`·`USAGE`에 스코프 동작 + 디스패처(사용자 레벨) 등록 옵션 문서화.

## 2026-07-07 — 규약을 3중 강제 계층으로 격상, main 푸시·CI 통과 (HANDOFF에서 이동)
_2026-07-07: 규약을 3중 강제 계층으로 격상, main 푸시·CI 통과._

- `.gitignore` 수정 — 루트 `.claude/`의 배포 자산(skills/hooks/commands/settings.json) 추적(구 `**/.claude/`가 다 가리던 버그).
- SessionStart 훅(`session_brief.py`) 규약+현황 주입 · Stop 훅(`handoff_guard.py`) HANDOFF 미갱신 시 종료 차단.
- `dear-agent` 스킬 + `/handoff` 커맨드. CI에 `enforcement-assets` 잡 추가.
- status 영어 별칭(planning/building/live/paused) 두 생성기 동시 지원(바이트 동일 유지).
- 영어 미러 `CONVENTIONS.en.md`·`USAGE.en.md`(KO 정본), 템플릿 이중언어 줄, README CI 배지+FAQ.
- 부수: 두 생성기가 루트 `docs/`를 컨테이너로 오인하던 것 제외(META_DIRS).
- `git push origin main`(9132324..9375434), GitHub CI 두 잡(generator-parity·enforcement-assets) 통과.
- 개인 `enabledPlugins`는 gitignore되는 `settings.local.json`으로 분리(배포 제외).
