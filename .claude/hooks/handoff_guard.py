#!/usr/bin/env python3
"""Stop 훅: 프로젝트 파일이 HANDOFF.md보다 새로우면 종료를 한 번 차단하고
HANDOFF 갱신을 요구한다. stop_hook_active=true면 통과(무한 루프 방지).
항상 exit 0; 차단은 stdout JSON {"decision": "block"}으로 전달."""
import json
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {'.git', '.claude', '.remember', 'node_modules', '__pycache__',
             '.venv', 'venv', 'dist', 'build', '.next', 'out', 'target'}
SKIP_FILES = {'HANDOFF.md', '_INDEX.md'}
GRACE = 2  # 초 — 같은 응답에서 코드→HANDOFF 순서로 저장한 경우의 허용 오차


def newest_file(proj):
    newest, newest_path = 0.0, None
    for dirpath, dirnames, filenames in os.walk(proj):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SKIP_FILES:
                continue
            p = Path(dirpath) / name
            try:
                m = p.stat().st_mtime
            except OSError:
                continue
            if m > newest:
                newest, newest_path = m, p
    return newest, newest_path


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    if payload.get('stop_hook_active'):
        return

    stale = []
    for cat in sorted(ROOT.iterdir()):
        if not cat.is_dir() or cat.name.startswith(('.', '_')) or cat.name == 'docs':
            continue
        for proj in sorted(cat.iterdir()):
            handoff = proj / 'HANDOFF.md'
            if not proj.is_dir() or not handoff.exists():
                continue
            newest, newest_path = newest_file(proj)
            if newest > handoff.stat().st_mtime + GRACE:
                rel = newest_path.relative_to(ROOT).as_posix()
                stale.append(f"{cat.name}/{proj.name} (최근 변경 예: {rel})")

    if stale:
        reason = (
            "아래 프로젝트의 파일이 HANDOFF.md보다 나중에 변경됐다. 종료 전에 각 "
            "HANDOFF.md를 갱신하라 — 마지막 작업/다음 할 일/막힌 것 + frontmatter"
            "(status·updated=오늘·summary). 구조가 바뀌었으면 build-index도 재실행: "
            + "; ".join(stale)
        )
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"[dear-agent] handoff_guard 훅 오류(무시 가능): {e}", file=sys.stderr)
    sys.exit(0)
