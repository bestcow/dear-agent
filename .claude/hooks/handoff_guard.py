#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stop 훅(디스패처형): 이번 세션에서 수정된 파일이 HANDOFF.md보다 새로우면
종료를 차단하고 HANDOFF 갱신을 요구한다. 세션 스탬프가 없으면 레거시 판정
(전체 이력 기준, dear-agent 원본 동작)으로 폴백. stop_hook_active=true면 통과.

가드는 **현재 작업 중인 프로젝트(project 스코프)에만** 동작한다. 루트 스코프
(워크스페이스 루트 repo 자기 자신)에선 하위 프로젝트를 훑지 않는다 — 하위 프로젝트는
각각 독립 repo이고, 그 HANDOFF 규율은 해당 프로젝트 안에서 세션을 열 때 걸린다.
(루트에서 전 프로젝트를 mtime으로 훑으면 동시 작업·외부 편집이 오탐으로 걸렸다.)

항상 exit 0; 차단은 stdout JSON {"decision":"block"}."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import workspace_lib as ws

REASON_HEAD = "아래 프로젝트의 파일이 HANDOFF.md보다 나중에 변경됐다. 종료 전에 "
REASON_TAIL = ("각 HANDOFF.md를 갱신하라 — 마지막 작업/다음 할 일/막힌 것 + frontmatter"
               "(status·updated=오늘·summary). 굵직한 변경은 LOG.md 한 줄. "
               "폴더 구조·상태가 바뀌었으면 build-index도 재실행: ")


def check_checkout(checkout: Path, label: str, since):
    """차단 사유 문자열 or None."""
    handoff = checkout / 'HANDOFF.md'
    newest, newest_path = ws.newest_file(checkout, since=since)
    if not handoff.exists():
        if newest:
            return (f"{label}: HANDOFF.md 없음 — _templates/의 5종(PLAN·HANDOFF·LOG·README·CLAUDE)을 "
                    f"복사해 채운 뒤 build-index를 실행하라 (CONVENTIONS §7)")
        return None
    if newest and newest > handoff.stat().st_mtime + ws.GRACE:
        try:
            rel = newest_path.relative_to(checkout).as_posix()
        except Exception:
            rel = str(newest_path)
        return f"{label} (최근 변경 예: {rel})"
    return None


def main():
    ws.force_utf8_stdout()
    payload = ws.read_payload()
    if payload.get('stop_hook_active'):
        return
    cwd = ws.session_cwd(payload)
    kind, checkout, rel = ws.resolve_scope(cwd)
    if kind == 'out':
        return
    if kind != 'project':
        return  # 루트 스코프(워크스페이스 루트 repo)에선 하위 프로젝트를 훑지 않는다
    since = ws.read_stamp(payload.get('session_id', 'unknown'))  # None → 레거시 판정

    r = check_checkout(checkout, rel, since)
    if r:
        reason = REASON_HEAD + REASON_TAIL + r
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"[dear-agent] handoff_guard 훅 오류(무시 가능): {e}", file=sys.stderr)
    sys.exit(0)
