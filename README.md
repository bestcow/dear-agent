# Dear Agent,

**English** | [한국어](#한국어)

*…here is everything you need to pick up where we left off.*

A tiny, opinionated documentation system for projects built with AI coding agents (Claude Code and friends) — the letter your project leaves for the next session's agent.

**The problem:** agents forget everything between sessions. Every new session starts with you re-explaining what the project is, where it stopped, and what to do next.

**The fix:** five small markdown files per project — each with exactly one job, zero overlap — plus a generator that turns them into a workspace-wide project map once you have many projects.

## Tier 1 — one project (30 seconds)

Copy the five files from [`_templates/`](_templates/) into your repo and fill them in:

| File | Job | Update when |
|---|---|---|
| `PLAN.md` | goals, scope, tech decisions | decisions change |
| `HANDOFF.md` | current state: last work / next steps / blockers, + status frontmatter | **every session end** |
| `LOG.md` | one line per notable change | features/fixes land |
| `README.md` | how to run it | run steps change |
| `CLAUDE.md` | agent ops guide: commands, code map, pitfalls | build/structure changes |

The heart is `HANDOFF.md`. Its YAML frontmatter is the **single source of truth** for project state:

```yaml
---
status: 개발            # 기획(planning) | 개발(building) | 운영(live) | 보류(paused)
updated: 2026-07-05
summary: one-line status
repo: org/name          # delete this line if no remote
---
```

An agent reads it at session start and knows exactly where to pick up — no re-explaining.

> Using an agent other than Claude Code? Copy or symlink `CLAUDE.md` to `AGENTS.md`.

## Tier 2 — many projects (a workspace)

When projects multiply, this repo doubles as a **workspace template**: category folders hold projects, and a generator scans every `HANDOFF.md` frontmatter to build tables of contents.

```
workspace/
├─ OVERVIEW.md          ← generated: map of ALL projects
├─ CONVENTIONS.md       ← the single rulebook
├─ apps/                ← a category folder (any name)
│  ├─ _INDEX.md         ← generated: projects in this category
│  ├─ todo-api/         ← a project (the 5 files + code)
│  └─ web-dashboard/
└─ build-index.ps1 / build-index.py
```

Run either generator — they produce **byte-identical output** (CI-enforced), no dependencies:

```
powershell -File ./build-index.ps1    # Windows PowerShell 5.1+
python3 build-index.py                # anywhere with Python 3.7+
```

It auto-discovers categories, regenerates `_INDEX.md` / `OVERVIEW.md` between `<!-- AUTO -->` markers (hand-written notes outside the markers are preserved), and warns about unfilled placeholders, invalid status values, and stale dates.

See [`_example/`](_example/) for a filled-in demo, and the generated tables it produces.

**Get started:** click **Use this template**, then follow [USAGE.md](USAGE.md) (7 steps). Full rules live in [CONVENTIONS.md](CONVENTIONS.md).

> **Note:** the detailed convention docs (CONVENTIONS.md, USAGE.md, templates) are currently in Korean. This README covers the essentials in English; translations are welcome.

License: [MIT](LICENSE)

---

## 한국어

**Dear Agent** — 다음 세션의 에이전트에게 남기는 편지입니다. AI 코딩 에이전트(Claude Code 등)와 함께 만드는 프로젝트를 위한 초소형 문서 체계입니다.

**문제:** 에이전트는 세션이 끝나면 전부 잊습니다. 새 세션마다 "이 프로젝트가 뭐고, 어디까지 했고, 다음이 뭔지"를 다시 설명하게 됩니다.

**해법:** 프로젝트당 md 파일 5개 — 각자 역할이 하나씩이고, 중복이 없습니다. 프로젝트가 여러 개가 되면 생성기가 `HANDOFF.md` frontmatter를 읽어 전체 지도를 자동으로 만들어 줍니다.

### 시작하기

- **프로젝트 하나만** → [`_templates/`](_templates/)의 md 5개를 내 레포에 복사해 채우면 끝입니다.
  핵심은 `HANDOFF.md`입니다 — frontmatter(status·updated·summary·repo)가 프로젝트 상태의 **단일 원본**이고, 에이전트가 세션 시작 때 이걸 읽고 바로 이어서 작업합니다. 세션을 끝낼 때마다 갱신하는 것이 규칙의 전부입니다.
- **워크스페이스(여러 프로젝트)** → **Use this template**으로 레포를 만들고 [USAGE.md](USAGE.md)의 7단계를 따라 주세요. 분류 폴더 안에 프로젝트를 두면 `build-index.ps1`(또는 `python3 build-index.py`, **바이트 동일 출력**)가 `_INDEX.md`·`OVERVIEW.md` 목차를 자동 생성합니다.

전체 규약(문서별 갱신 시점, 상태 값 정의, 단일 출처 원칙)은 [CONVENTIONS.md](CONVENTIONS.md)가 단일 기준입니다. 채워진 예시는 [`_example/`](_example/)를 참고하세요.

Claude Code 외의 에이전트를 쓰신다면 `CLAUDE.md`를 `AGENTS.md`로 복사하거나 링크하면 됩니다.
