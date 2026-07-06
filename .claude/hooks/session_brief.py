#!/usr/bin/env python3
"""SessionStart 훅: 문서 규약 브리핑 + 프로젝트 현황을 세션 컨텍스트에 주입.
stdout이 컨텍스트로 들어간다. 세션을 막지 않도록 어떤 경우에도 exit 0."""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]


def frontmatter(path):
    try:
        text = path.read_text(encoding='utf-8-sig')
    except Exception:
        return {}
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.S)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip()
    return fm


def main():
    lines = []
    for cat in sorted(ROOT.iterdir()):
        if not cat.is_dir() or cat.name.startswith(('.', '_')) or cat.name == 'docs':
            continue
        for proj in sorted(cat.iterdir()):
            handoff = proj / 'HANDOFF.md'
            if proj.is_dir() and handoff.exists():
                fm = frontmatter(handoff)
                lines.append(
                    f"- {cat.name}/{proj.name}: {fm.get('status', '?')}"
                    f" / {fm.get('updated', '?')} — {fm.get('summary', '')}"
                )

    print("[dear-agent] 이 워크스페이스는 문서 규약(CONVENTIONS.md)을 따른다.")
    print(
        "규칙: (1) 프로젝트 작업 전 그 프로젝트의 HANDOFF.md를 읽는다. "
        "(2) 코드를 수정한 세션은 끝내기 전 HANDOFF.md(frontmatter 포함)를 갱신한다 — "
        "Stop 훅이 검사한다. (3) 폴더 구조가 바뀌면 build-index를 재실행한다. "
        "절차 상세는 dear-agent 스킬 사용."
    )
    if lines:
        print("프로젝트 현황(HANDOFF frontmatter):")
        print('\n'.join(lines))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"[dear-agent] session_brief 훅 오류(무시 가능): {e}")
    sys.exit(0)
