#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SessionStart 훅(디스패처형): 이 워크스페이스 하위 세션에만 규약 브리핑+현황 주입.
프로젝트 스코프: 그 프로젝트 HANDOFF 전문만(다른 프로젝트 md는 읽지 않음).
루트 스코프: 전 프로젝트 표 + 신선도.
stdout이 세션 컨텍스트로 들어간다. 어떤 경우에도 exit 0."""
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import workspace_lib as ws

HANDOFF_MAX = 4000  # 자 — 초과분 절단
DEDUPE_SEC = 60     # 같은 세션의 중복 발화(유저+프로젝트 이중 등록) 침묵 창

RULES = (
    "[dear-agent] 이 워크스페이스는 문서 규약(CONVENTIONS.md)을 따른다. 규칙: "
    "(1) 프로젝트 작업 전 HANDOFF.md를 읽는다(아래 주입됨). "
    "(2) 코드를 수정한 세션은 끝내기 전 HANDOFF.md(frontmatter 포함)를 갱신한다 — Stop 훅이 검사한다. "
    "(3) 폴더 구조·상태가 바뀌면 build-index를 재실행한다. "
    "절차는 dear-agent 스킬, 수동 종료 절차는 /handoff."
)


def overview_freshness():
    ov = ws.WS_ROOT / 'OVERVIEW.md'
    try:
        text = ov.read_text(encoding='utf-8-sig')
    except Exception:
        return "OVERVIEW.md 없음/읽기 실패 — build-index 실행 필요"
    m = re.search(r'최종 생성: (\d{4}-\d{2}-\d{2})', text)
    gen = m.group(1) if m else ''
    latest = ''
    for _cat, proj in ws.iter_projects():
        u = ws.parse_frontmatter(proj / 'HANDOFF.md').get('updated', '')
        if re.match(r'^\d{4}-\d{2}-\d{2}$', u) and u > latest:
            latest = u
    if not gen:
        return "OVERVIEW에서 생성일을 못 읽음 — build-index 재실행 권장"
    if latest and latest > gen:
        return f"OVERVIEW가 낡음(생성 {gen} < 최신 HANDOFF {latest}) — build-index 재실행 권장"
    return None


def doc_code_drift(checkout: Path, handoff: Path):
    """HANDOFF updated < repo 마지막 커밋일이면 경고. git 실패 시 None(조용히 생략)."""
    try:
        out = subprocess.run(['git', '-C', str(checkout), 'log', '-1', '--format=%cs'],
                             capture_output=True, text=True, timeout=5)
        last = (out.stdout or '').strip()
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', last):
            return None
        updated = ws.parse_frontmatter(handoff).get('updated', '')
        if re.match(r'^\d{4}-\d{2}-\d{2}$', updated) and last > updated:
            return f"문서-코드 괴리 의심: 마지막 커밋 {last} > HANDOFF updated {updated} — HANDOFF 갱신 필요"
    except Exception:
        return None
    return None


def _git(checkout: Path, args, timeout=6):
    """git 서브커맨드 stdout(성공 시) 또는 빈 문자열. 실패·미설치·타임아웃 모두 ''."""
    try:
        out = subprocess.run(['git', '-C', str(checkout), *args],
                             capture_output=True, text=True, timeout=timeout,
                             encoding='utf-8', errors='replace')
        return out.stdout if out.returncode == 0 else ''
    except Exception:
        return ''


def recovery_block(checkout: Path, rel: str):
    """지난 세션이 코드 변경 뒤 HANDOFF 미갱신으로 끝났으면(dirty 플래그) 회수 프롬프트 주입.
    git log/status/diff로 '무엇을 했나'를 복원해 HANDOFF 초안을 만들 재료를 준다."""
    d = ws.read_dirty(rel)
    if not d:
        return
    print("\n[회수 필요] 지난 세션이 코드 변경 뒤 HANDOFF를 갱신하지 않고 끝났다. "
          "아래 git 기록으로 '마지막 작업/다음 할 일'을 복원해 HANDOFF 초안을 만들고 "
          "사용자에게 확인받아라. HANDOFF를 갱신하면(다음 종료 시) 이 알림은 사라진다.")
    log = _git(checkout, ['log', '-15', '--format=%h %cs %s']).strip()
    if log:
        print("--- git log (최근 15) ---")
        print(log)
    status = _git(checkout, ['status', '--porcelain']).strip()
    if status:
        print("--- 미커밋 변경 (git status --porcelain) ---")
        print(status)
    diffstat = _git(checkout, ['diff', '--stat']).strip()
    if diffstat:
        print("--- git diff --stat ---")
        print(diffstat)


def project_brief(checkout: Path, rel: str):
    print(RULES)
    print(f"\n[현재 프로젝트: {rel}]")
    handoff = checkout / 'HANDOFF.md'
    if handoff.exists():
        try:
            text = handoff.read_text(encoding='utf-8-sig').strip()
        except Exception:
            text = ''
        if len(text) > HANDOFF_MAX:
            text = text[:HANDOFF_MAX] + f"\n…(HANDOFF {HANDOFF_MAX}자 초과 — 이하 절단, 원문을 직접 읽을 것)"
        print("--- HANDOFF.md ---")
        print(text)
        print("--- /HANDOFF.md ---")
        drift = doc_code_drift(checkout, handoff)
        if drift:
            print(f"! {drift}")
    else:
        print("! HANDOFF.md 없음 — 새 프로젝트면 _templates/ 5종을 복사해 채울 것 (CONVENTIONS §7).")
    missing = [d for d in ['PLAN.md', 'HANDOFF.md', 'LOG.md', 'README.md', 'CLAUDE.md']
               if not (checkout / d).exists()]
    if missing:
        print(f"! 5종 문서 누락: {', '.join(missing)}")
    recovery_block(checkout, rel)


def root_brief():
    print(RULES)
    lines = []
    for cat, proj in ws.iter_projects():
        fm = ws.parse_frontmatter(proj / 'HANDOFF.md')
        lines.append(f"- {cat}/{proj.name}: {fm.get('status', '?')} / {fm.get('updated', '?')}"
                     f" — {fm.get('summary', '')}")
    if lines:
        print("\n프로젝트 현황(HANDOFF frontmatter):")
        print('\n'.join(lines))
    fresh = overview_freshness()
    if fresh:
        print(f"! {fresh}")


def main():
    ws.force_utf8_stdout()
    payload = ws.read_payload()
    cwd = ws.session_cwd(payload)
    kind, checkout, rel = ws.resolve_scope(cwd)
    if kind == 'out':
        return
    sid = payload.get('session_id', 'unknown')
    prior = ws.read_stamp(sid)
    created = ws.write_stamp(sid)
    if not created and prior is not None and (time.time() - prior) < DEDUPE_SEC:
        return  # 유저 레벨+프로젝트 레벨 이중 등록의 중복 발화 — 두 번째는 침묵
    if kind == 'project':
        project_brief(checkout, rel)
    else:
        root_brief()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"[dear-agent] session_brief 훅 오류(무시 가능): {e}", file=sys.stderr)
    sys.exit(0)
