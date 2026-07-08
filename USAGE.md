# 워크스페이스 양식 — 사용법

> English: [USAGE.en.md](USAGE.en.md) _(KO 정본)_

이 폴더는 새 **워크스페이스**(문서 규약을 따르는 작업 루트)를 시작하기 위한 양식이다. 통째로 복사해 채우면 하나의 워크스페이스가 된다. (개별 *프로젝트* 양식은 `_templates/`에 따로 있다.)

## 새 워크스페이스 만들기

> GitHub이면 **Use this template**(또는 clone)로 새 repo를 만든 뒤, 아래 1~8을 그 폴더 안에서 수행한다.

1. **배포물 정리** — 데모 폴더 `_example/`를 삭제한다. 폴더를 직접 복사해 받았다면 세션 스크래치(`.remember/`·`.claude/worktrees/`·`__pycache__/`)도 삭제한다(git으로 받았으면 없음). ⚠ `.claude/`의 나머지(settings.json·skills/·hooks/·commands/)는 규약 강제 계층이니 지우지 않는다.
2. **README 교체** — 공개 소개용인 `README.md`를 지우고 아래 스니펫으로 새로 만들어 H1·한 줄 소개를 채운다:
   ```markdown
   # <워크스페이스>

   _한 줄 소개._ 분류 폴더 아래 프로젝트를 담는다. 규약과 지도는 아래.

   - **프로젝트 지도** → [OVERVIEW.md](OVERVIEW.md) _(생성물, 직접 편집 금지)_
   - **문서 규약** → [CONVENTIONS.md](CONVENTIONS.md) _(단일 기준)_
   - **빈 양식** → `_templates/`
   - **목차 생성** → `build-index.ps1` (Windows·PowerShell) / `python3 build-index.py` (동일 출력)
   ```
3. **이름·소개 채우기** — `CLAUDE.md`·`OVERVIEW.md` 맨 위 H1의 `<워크스페이스>`를 실제 이름으로, `OVERVIEW.md`의 한 줄 설명(`> ...` 자리)을 채운다.
4. **양식 안내 제거** — `CLAUDE.md` 맨 위 📋 양식 안내 줄을 지운다. 참고 자산 섹션은 쓰면 채우고, 안 쓰면 삭제. `CONVENTIONS.md` 맨 아래 "구조 변경 기록"의 `<YYYY-MM-DD>`를 생성일로. `LICENSE`·`.github/`는 자기 repo 정책에 맞게 두거나 삭제한다.
   - ⚠️ `CONVENTIONS.md`의 스키마 예시 `repo: <org>/<name>`과 `<!-- AUTO:* -->` 마커는 **예시·문법**이니 건드리지 않는다.
5. **분류 폴더 + 프로젝트 추가** — 분류 폴더(예: `apps/`)를 만들고 그 안에 `_templates/`의 `.md`를 복사해 잎(프로젝트)을 만든다. 분류는 미리 깔지 말고 생기는 대로(CONVENTIONS §2). 생성기는 컨테이너→잎 구조를 본다.
6. **목차 생성** — 환경에 맞는 한 줄을 실행하면 컨테이너를 자동 탐색해 `OVERVIEW.md`·`_INDEX.md`를 만든다.
   - Windows: `powershell -ExecutionPolicy Bypass -File ./build-index.ps1`
   - PowerShell 7 (어느 OS든): `pwsh -File ./build-index.ps1`
   - PowerShell 없음 (mac/linux 등): `python3 build-index.py` _(동일 출력)_
7. **훅 승인** — Claude Code로 이 폴더를 처음 열면 프로젝트 설정(`.claude/settings.json`의 SessionStart/Stop 훅) 승인을 묻는다. 승인해야 규약 강제(세션 브리핑·HANDOFF 게이트)가 작동한다. Python 3.7+가 없으면 훅만 비활성되고 스킬·CLAUDE.md는 그대로 작동한다.
8. **확인 후 정리** — 생성된 `OVERVIEW.md`가 정상이면 이 `USAGE.md`를 지운다(양식 안내 전용). 절차 요약은 루트 `CLAUDE.md`에도 있어 삭제 후에도 남는다.

## 구성

> 이 표가 루트 파일 **전체 목록**이다 — 파일을 추가/삭제하면 여기도 갱신한다.

| 파일 | 역할 |
|---|---|
| `CONVENTIONS.md` | 문서 체계 단일 기준 |
| `CONVENTIONS.en.md` | CONVENTIONS 영어 미러 (KO가 정본) |
| `USAGE.en.md` | USAGE 영어 미러 (KO가 정본) |
| `CLAUDE.md` | 루트 에이전트 운영 지침 (+ 신규 구축 진입점) |
| `README.md` | 공개 레포 소개 (구축 시 워크스페이스 소개로 교체 — 2단계) |
| `build-index.ps1` | `_INDEX`·`OVERVIEW` 생성기 (PowerShell, UTF-8 BOM) |
| `build-index.py` | 같은 생성기의 크로스플랫폼 쌍둥이 (PowerShell 없을 때, 동일 출력) |
| `_templates/` | 프로젝트(잎) 양식 — PLAN·HANDOFF·LOG·README·CLAUDE |
| `_example/` | 채워진 데모 워크스페이스 (구축 시 삭제 — 1단계) |
| `OVERVIEW.md` | 빈 씨앗 (첫 생성 때 채워짐) |
| `.claude/settings.json` | SessionStart/Stop 훅 배선 (규약 강제) |
| `.claude/hooks/` | 훅 스크립트 — session_brief.py(브리핑 주입)·handoff_guard.py(HANDOFF 게이트)·workspace_lib.py(스코프 판정 공통부) |
| `.claude/skills/dear-agent/` | 프로젝트 스킬 — 규약 실행 절차 |
| `.claude/commands/handoff.md` | `/handoff` — 세션 종료 절차 수동 호출 |
| `.gitignore` | 세션 스크래치 제외 + 루트 .claude 배포 자산 추적 |
| `.gitattributes` | 줄바꿈 LF 고정 — 생성기의 "바이트 동일 출력"이 OS별 CRLF 변환에 깨지지 않게 |
| `.github/workflows/ci.yml` | 두 생성기의 동일 출력·멱등성 검증 |
| `.github/banner.png` | README 상단 배너 (소셜 프리뷰용과 동일 이미지) |
| `LICENSE` | MIT |
| `USAGE.md` | 이 안내 (구축 후 삭제) |

> 두 생성기는 **동일 출력**을 보장한다 — 로직을 고치면 양쪽을 같이 고친다(CI가 검증).
> 루트 `.gitignore`가 세션 스크래치를 이미 제외한다. 분류 폴더를 만들면 `<분류>/*/` 한 줄을 추가한다 — 프로젝트는 각자 독립 repo.
