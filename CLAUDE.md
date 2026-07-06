# <워크스페이스> 작업 지침

> 📋 **이 파일은 '워크스페이스 양식'의 일부다.** 이 폴더를 새 워크스페이스로 만들라는 요청을 받거나 `<...>` placeholder가 남아 있으면, 다른 작업을 시작하기 전에 **먼저 [USAGE.md](USAGE.md)의 1~8단계를 순서대로 수행**한다. (요약: `_example/`·스크래치 정리 → README 교체 → 이름·소개 placeholder 채우기 → 이 📋 안내 줄 삭제 → 분류 폴더 만들고 `_templates/` 복사로 잎 생성 → 생성기 실행 → 확인 후 `USAGE.md` 삭제.) 구축이 끝나면 이 안내 줄을 지운다.

> 에이전트 운영 가이드. 문서 체계의 단일 기준은 [CONVENTIONS.md](CONVENTIONS.md).

## 문서 규약 (항상 적용)

프로젝트 작업은 [CONVENTIONS.md](CONVENTIONS.md)를 따른다. 핵심 트리거-동작:

- **코드 수정·기능 추가 작업은, 응답을 끝내기 전에 해당 프로젝트의 `HANDOFF.md`(frontmatter 포함)를 갱신하고 마친다.**
- **폴더 구조가 바뀌면** 누락 MD를 만들고(`_templates/` 복사), 상위 `_INDEX.md`와 루트 `OVERVIEW.md`를 `build-index.ps1`(PowerShell 없으면 `python3 build-index.py`) 실행으로 재생성한다(HANDOFF frontmatter 스캔, 컨테이너 자동 탐색).
- **새 프로젝트 폴더**엔 `_templates/`에서 PLAN·HANDOFF·CLAUDE를 먼저 만든다.
- `_INDEX.md`·`OVERVIEW.md`는 **생성물** — 직접 편집 금지.
- 이 규약은 3중으로 강제된다: 이 CLAUDE.md(상시 컨텍스트) · `dear-agent` 스킬(작업 시작·종료·구조 변경 절차) · `.claude/settings.json` 훅(SessionStart 브리핑 주입 + Stop의 HANDOFF 미갱신 차단). 세션 종료 절차는 `/handoff`로도 호출할 수 있다.

## 참고 자산 (선택)
_워크스페이스 공유 스킬·프롬프트·가이드가 있으면 `docs/`에 두고 여기 기술. 없으면 이 섹션 삭제._
