#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""워크스페이스 훅·도구 공통 라이브러리 — 스코프 판정·frontmatter 파서·세션 스탬프.

디스패처형 강제 계층(CONVENTIONS §9)의 공통부. stdlib만 사용.
WS_ROOT: 이 파일 위치(.claude/hooks/) 기준 실제 워크스페이스 루트.
루트 repo 워크트리 안의 사본으로 실행돼도 본 루트로 해석한다.
환경변수 WORKSPACE_HOOKS_ROOT 는 테스트 전용 오버라이드."""
import json
import os
import re
import sys
import time
from pathlib import Path

META_DIRS = {'docs', 'notes', 'tests'}   # 루트 직속 meta — 스캔·가드 제외 (build-index와 동일 유지)
SKIP_DIRS = {'.git', '.claude', '.remember', 'node_modules', '__pycache__',
             '.venv', 'venv', 'dist', 'build', '.next', 'out', 'target',
             '.pytest_cache', '.mypy_cache', '.ruff_cache', 'htmlcov',
             'coverage', '.gradle', '.godot', '.import'}
# 문서 체계 5종 + 생성 목차는 '작업 산출물'이 아니다 — 가드는 코드 변경에만 반응한다(문서만 고친 세션은 안 막힘).
SKIP_FILES = {'HANDOFF.md', '_INDEX.md', 'PLAN.md', 'LOG.md', 'README.md', 'CLAUDE.md'}
GRACE = 2  # 초 — 같은 응답에서 코드→HANDOFF 순서로 저장한 경우의 허용 오차


def _main_repo_root(checkout: Path) -> Path:
    """checkout(.git 보유 폴더)의 본 repo 루트. 워크트리(.git 파일)면 gitdir을 풀어낸다."""
    git = checkout / '.git'
    if git.is_dir():
        return checkout
    try:
        text = git.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return checkout
    m = re.search(r'^gitdir:\s*(.+)$', text, re.M)
    if not m:
        return checkout
    gitdir = Path(m.group(1).strip())
    if not gitdir.is_absolute():
        gitdir = (checkout / gitdir).resolve()
    parts_lower = [p.lower() for p in gitdir.parts]
    if '.git' in parts_lower:                      # ...\<main>\.git\worktrees\<n> → <main>
        i = parts_lower.index('.git')
        return Path(*gitdir.parts[:i])
    return checkout


def _detect_ws_root() -> Path:
    env = os.environ.get('WORKSPACE_HOOKS_ROOT')
    if env:
        return Path(env).resolve()
    cand = Path(__file__).resolve().parents[2]     # <root>\.claude\hooks\ → <root>
    if (cand / '.git').is_file():                  # 인덱스 repo 워크트리 안의 사본
        return _main_repo_root(cand)
    return cand


WS_ROOT = _detect_ws_root()
STAMP_DIR = WS_ROOT / '.claude' / 'tmp'


def force_utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def read_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def session_cwd(payload: dict) -> Path:
    cwd = payload.get('cwd') or os.getcwd()
    try:
        return Path(cwd).resolve()
    except Exception:
        return Path(os.getcwd()).resolve()


def resolve_scope(cwd: Path):
    """(kind, checkout, project_rel).
    kind='out'|'root'|'project'. checkout=브리핑·가드가 볼 체크아웃 루트(root면 WS_ROOT).
    project_rel='apps/blog' 표시명(project일 때만)."""
    try:
        cwd.relative_to(WS_ROOT)
    except ValueError:
        return ('out', None, None)
    cur = cwd
    while True:
        if (cur / '.git').exists():
            main_root = _main_repo_root(cur)
            if main_root == WS_ROOT:
                return ('root', WS_ROOT, None)
            try:
                rel = main_root.relative_to(WS_ROOT).as_posix()
            except ValueError:
                rel = main_root.name
            return ('project', cur, rel)
        if cur == WS_ROOT:
            return ('root', WS_ROOT, None)
        if cur.parent == cur:                      # 드라이브 루트 안전망
            return ('out', None, None)
        cur = cur.parent


def parse_frontmatter(path: Path) -> dict:
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


def iter_projects():
    """분류→프로젝트(HANDOFF.md 보유) 순회 → (분류명, 프로젝트 Path)."""
    try:
        cats = sorted(WS_ROOT.iterdir())
    except OSError:
        return
    for cat in cats:
        if not cat.is_dir() or re.match(r'^[._]', cat.name) or cat.name in META_DIRS:
            continue
        try:
            projs = sorted(cat.iterdir())
        except OSError:
            continue
        for proj in projs:
            if proj.is_dir() and (proj / 'HANDOFF.md').exists():
                yield cat.name, proj


def newest_file(checkout: Path, since=None):
    """HANDOFF·생성물·스크래치 제외 최신 파일 (mtime, Path). since 지정 시 그 이후 것만."""
    newest, newest_path = 0.0, None
    for dirpath, dirnames, filenames in os.walk(checkout):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name in SKIP_FILES:
                continue
            p = Path(dirpath) / name
            try:
                m = p.stat().st_mtime
            except OSError:
                continue
            if since is not None and m <= since:
                continue
            if m > newest:
                newest, newest_path = m, p
    return newest, newest_path


def stamp_path(session_id: str) -> Path:
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', str(session_id))
    return STAMP_DIR / f'session-{safe}.start'


def write_stamp(session_id: str) -> bool:
    """스탬프가 없으면 생성하고 True. 이미 있으면 False. 7일 지난 스탬프 GC."""
    try:
        STAMP_DIR.mkdir(parents=True, exist_ok=True)
        now = time.time()
        for old in STAMP_DIR.glob('session-*.start'):
            try:
                if now - old.stat().st_mtime > 7 * 86400:
                    old.unlink()
            except OSError:
                pass
        p = stamp_path(session_id)
        if p.exists():
            return False
        p.write_text(str(now), encoding='utf-8')
        return True
    except Exception:
        return True                                # 스탬프 실패가 브리핑을 막으면 안 됨


def read_stamp(session_id: str):
    try:
        return float(stamp_path(session_id).read_text(encoding='utf-8').strip())
    except Exception:
        return None
