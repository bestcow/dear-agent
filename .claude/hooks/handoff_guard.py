#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stop 훅(디스패처형): 이번 세션에서 수정된 파일이 HANDOFF.md보다 새로우면
'더러움 플래그'(.claude/tmp/dirty-<slug>.flag)만 조용히 남긴다 — block하지 않는다.
깨끗이 끝났으면(변경 없음/HANDOFF 갱신됨) 기존 플래그를 지운다. 회수는 다음
SessionStart(session_brief)가 그 플래그를 감지해 git 기록과 함께 프롬프트로 띄운다.
세션 스탬프가 없으면 레거시 판정(전체 이력 기준)으로 폴백. stop_hook_active=true면 통과.

가드는 **현재 작업 중인 프로젝트(project 스코프)에만** 동작한다. 루트 스코프에선
하위 프로젝트를 훑지 않는다(각각 독립 repo). 어떤 경우에도 exit 0; stdout 무출력."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import workspace_lib as ws

def check_checkout(checkout: Path, label: str, since):
    """더러움 사유 문자열 or None."""
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
    if kind != 'project':
        return  # out/root 스코프는 침묵 (하위 프로젝트는 각자 세션에서 걸린다)
    since = ws.read_stamp(payload.get('session_id', 'unknown'))  # None → 레거시 판정
    r = check_checkout(checkout, rel, since)
    if r:
        ws.mark_dirty(rel, r)      # block 대신 조용히 회수 대상으로 표시
    else:
        ws.clear_dirty(rel)        # 깨끗이 끝났으면 회수 대상 해제


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"[dear-agent] handoff_guard 훅 오류(무시 가능): {e}", file=sys.stderr)
    sys.exit(0)
