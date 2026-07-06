#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_INDEX/OVERVIEW 목차 생성기 — build-index.ps1의 크로스플랫폼 쌍둥이 (동일 출력).

PowerShell이 없는 환경(mac/linux 등)에서 쓴다. build-index.ps1과 바이트 동일한
_INDEX.md·OVERVIEW.md를 만든다 — 한쪽 로직을 고치면 다른 쪽도 같이 고친다.

  - 컨테이너 자동 탐색: 루트 직속 하위폴더(., _ 로 시작하는 meta·스크래치 제외)를 분류로 본다.
  - 생성 영역은 <!-- AUTO:START --> ~ <!-- AUTO:END --> 사이뿐. 마커 밖 텍스트는 보존.
  - 출력은 UTF-8 BOM + LF. 멱등(같은 입력이면 두 번 돌려도 바이트 동일).

사용:
  python3 build-index.py            # 생성/갱신
  python3 build-index.py --check    # 파일은 안 쓰고 변경 필요 여부만 (필요하면 exit 1)
  python3 build-index.py --root DIR # 루트 지정 (기본 = 이 스크립트 위치)
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

# Windows 기본 콘솔(cp949 등)에서 print()가 한글·em-dash로 UnicodeEncodeError를 내지 않도록.
# 파일 출력은 utf-8-sig라 무관하지만, 콘솔 print가 죽으면 파일 쓰기 전에 중단되므로 stdout/stderr를 UTF-8로 고정.
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

STATUS_ORDER = ['운영', '개발', '기획', '보류']
STATUS_ALIASES = {'planning': '기획', 'building': '개발', 'live': '운영', 'paused': '보류'}
PROJECT_DOCS = ['PLAN.md', 'HANDOFF.md', 'LOG.md', 'README.md', 'CLAUDE.md']
GEN_NOTE = '> **생성물** (CONVENTIONS §4). 직접 편집 금지 — `build-index` 재생성. 최종 생성: {0}'
START = '<!-- AUTO:START -->'
END = '<!-- AUTO:END -->'

warnings = []


def read_text(path: Path) -> str:
    # utf-8-sig: BOM이 있으면 제거. CRLF→LF 정규화.
    return path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def write_text_bom(path: Path, text: str) -> None:
    text = text.replace('\r\n', '\n')
    # utf-8-sig가 BOM을 붙이고, newline=''로 LF를 그대로 쓴다.
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(text)


def parse_frontmatter(handoff: Path):
    lines = read_text(handoff).split('\n')
    if len(lines) < 2 or lines[0].strip() != '---':
        return None
    fm = {}
    for line in lines[1:]:
        if line.strip() == '---':
            break
        m = re.match(r'^\s*([A-Za-z_]+)\s*:\s*(.*?)\s*$', line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def subdirs(path: Path):
    try:
        ds = [d for d in path.iterdir() if d.is_dir() and not re.match(r'^[._]', d.name)]
    except OSError:
        return []
    ds.sort(key=lambda d: d.name)  # 코드포인트(=ordinal) 정렬
    return ds


def get_leaves(container: Path):
    leaves = []
    for d in subdirs(container):
        handoff = d / 'HANDOFF.md'
        if handoff.exists():
            fm = parse_frontmatter(handoff)
            if not fm:
                warnings.append(f"{d}: HANDOFF frontmatter 파싱 실패 — 제외")
                continue
            status = fm['status'] if fm.get('status') else '?'
            status = STATUS_ALIASES.get(status.lower(), status)
            summary = fm.get('summary', '')
            repo = fm['repo'] if fm.get('repo') else ''
            if repo and ('<org>' in repo or '<name>' in repo):
                warnings.append(f"{d}: HANDOFF repo가 미충전 placeholder('{repo}') — 실제 repo로 바꾸거나 줄 삭제")
            if status not in STATUS_ORDER:
                warnings.append(f"{d}: HANDOFF status '{status}'가 규약 값(기획·개발·운영·보류 / planning·building·live·paused) 밖 — 오타/placeholder 확인")
            updated = fm.get('updated', '')
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', updated):
                warnings.append(f"{d}: HANDOFF updated '{updated}'가 YYYY-MM-DD 형식 아님(미충전 placeholder?) — 세션 종료 시 갱신")
            leaves.append({'Name': d.name, 'Status': status, 'Summary': summary, 'Repo': repo})
        else:
            has_doc = any((d / doc).exists() for doc in PROJECT_DOCS)
            nested = any((sub / 'HANDOFF.md').exists() for sub in d.rglob('*') if sub.is_dir())
            if nested:
                warnings.append(f"{d}: 중첩 컨테이너로 보임(하위에 HANDOFF) — 스크립트 미지원, 확장 필요")
            elif has_doc:
                warnings.append(f"{d}: 프로젝트 문서는 있으나 HANDOFF.md 없음 — 카탈로그 제외(HANDOFF 생성 필요)")
            else:
                warnings.append(f"{d}: 프로젝트 문서 없음(빈/비-프로젝트) — 제외(정체 확인 필요)")
    return leaves


def format_count(leaves) -> str:
    parts = []
    for s in STATUS_ORDER:
        c = sum(1 for l in leaves if l['Status'] == s)
        if c > 0:
            parts.append(f"{s} {c}")
    others = {}
    for l in leaves:
        if l['Status'] not in STATUS_ORDER:
            others[l['Status']] = others.get(l['Status'], 0) + 1
    for name, count in others.items():  # 첫 등장 순서 보존(py3.7+ dict)
        parts.append(f"{name} {count}")
    return ' · '.join(parts)


def count_or(leaves) -> str:
    return format_count(leaves) or '아직 없음'


def repo_cell(repo: str) -> str:
    return repo if repo else '_(로컬)_'


def build_table(leaves, prefix: str) -> str:
    rows = ['| 프로젝트 | 상태 | repo | 한 줄 |', '|---|---|---|---|']
    for l in leaves:
        rows.append(f"| [{l['Name']}]({prefix}{l['Name']}/) | {l['Status']} | {repo_cell(l['Repo'])} | {l['Summary']} |")
    return '\n'.join(rows)


def splice_auto(path: Path, fallback_title: str, auto_content: str) -> str:
    block = f"{START}\n{auto_content}\n{END}"
    if path.exists():
        existing = read_text(path)
        i_s = existing.find(START)
        i_e = existing.find(END)
        if i_s >= 0 and i_e > i_s:
            return existing[:i_s] + block + existing[i_e + len(END):]
        if existing.strip():
            warnings.append(f"{path}: AUTO 마커 없음 — 기존 내용 보존하고 끝에 AUTO 블록 추가. 원하는 위치에 마커를 넣고 재실행.")
            return existing.rstrip() + "\n\n" + block + "\n"
    return f"{fallback_title}\n\n{block}\n"


def commit(path: Path, new_content: str, check: bool) -> bool:
    old = read_text(path) if path.exists() else ''
    new = new_content.replace('\r\n', '\n')
    if old == new:
        print(f"  =  {path}")
        return False
    if check:
        print(f"  ~  {path}  (변경 필요)")
        return True
    write_text_bom(path, new)
    print(f"  +  {path}  (갱신)")
    return True


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--root', default=str(Path(__file__).resolve().parent))
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    today = datetime.date.today().strftime('%Y-%m-%d')
    print(f"build-index — Root: {root}  ({today})")

    containers = [d.name for d in subdirs(root)]
    if not containers:
        warnings.append("분류 폴더가 없음 — 빈 워크스페이스로 OVERVIEW만 생성. (프로젝트는 분류 폴더 안에 _templates/ 복사로 만든다)")

    all_leaves = []
    ov_sections = []
    changed = False

    for c in containers:
        cpath = root / c
        leaves = get_leaves(cpath)
        all_leaves += leaves

        idx_auto = GEN_NOTE.format(today) + "\n\n" + build_table(leaves, '') + f"\n\n_상태: {count_or(leaves)}_"
        idx_content = splice_auto(cpath / '_INDEX.md', f"# {c} — 프로젝트 목차", idx_auto)
        if commit(cpath / '_INDEX.md', idx_content, args.check):
            changed = True

        head = f"## {c} ({len(leaves)})"
        if c in LABELS:
            head += f" — {LABELS[c]}"
        head += f" · [목차]({c}/_INDEX.md)"
        ov_sections.append(head + "\n\n" + build_table(leaves, f"{c}/"))

    ov_auto = (GEN_NOTE.format(today) + "\n\n" +
               f"전체 {len(all_leaves)}개 — **{count_or(all_leaves)}**. 규약: [CONVENTIONS.md](CONVENTIONS.md)\n\n" +
               "\n\n".join(ov_sections))
    ov_content = splice_auto(root / 'OVERVIEW.md', f"# {root.name} — 프로젝트 지도 (OVERVIEW)", ov_auto)
    if commit(root / 'OVERVIEW.md', ov_content, args.check):
        changed = True

    if warnings:
        print(f"\n경고 ({len(warnings)}):")
        for w in warnings:
            print(f"  ! {w}")
    print(f"\n잎 {len(all_leaves)}개 — {count_or(all_leaves)}")

    raise SystemExit(1 if (args.check and changed) else 0)


# 분류 폴더별 한 줄 설명(선택 — 없으면 라벨 생략). build-index.ps1의 $Labels와 동일하게 유지.
LABELS = {}

if __name__ == '__main__':
    main()
