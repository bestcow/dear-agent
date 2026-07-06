---
description: 이 세션에서 작업한 프로젝트의 HANDOFF.md를 갱신하고 목차를 재생성한다
---

dear-agent 스킬의 "세션 종료" 절차를 지금 실행한다. 이 세션에서 수정한 각 프로젝트에 대해:

1. `HANDOFF.md` 본문(마지막 작업 / 다음 할 일 / 막힌 것)을 이 세션 내용으로 갱신한다.
2. frontmatter의 `status` · `updated`(오늘) · `summary`를 갱신한다.
3. 굵직한 변경은 `LOG.md`에 한 줄 추가한다.
4. 폴더 구조나 상태가 바뀌었으면 build-index(`build-index.ps1` 또는 `python3 build-index.py`)를 실행해 `_INDEX.md`·`OVERVIEW.md`를 재생성한다.
5. 생성기 경고가 있으면 해결하고 결과를 보고한다.
