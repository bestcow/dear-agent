# Documentation Convention (CONVENTIONS)

> **Translation.** The Korean original ([CONVENTIONS.md](CONVENTIONS.md)) is canonical; if this file and the original disagree, the original wins. Please update both when changing the rules.

This document is the **single source of authority** for this workspace's documentation system. `CLAUDE.md` points to it.

---

## 1. Scope — work vs meta

Every top-level folder in the workspace is one of two kinds.

- **work** — the things you work on (category folders and the projects inside them). The convention applies **only here**.
- **meta** — the system itself. `CONVENTIONS.md` · `OVERVIEW.md` · `CLAUDE.md` · `README.md` · `USAGE.md` (deleted after setup) · `_templates/` · `_example/` (demo, deleted at setup) · `build-index.ps1`·`build-index.py` (index generators) · `.claude/` (skill·hooks·settings — the enforcement layers) · `docs/` (workspace-shared assets, if present) · `.gitignore` · `LICENSE` · `.github/`. These are **not** subject to the convention or the scan.

> Folders outside this workspace (separate tools, knowledge bases, etc.) are not governed by the convention — each carries its own docs.

## 2. Folder classification — decided by content (not name)

- **Project (leaf)** = a folder that is itself a work target → **all five** of `PLAN.md` · `HANDOFF.md` · `LOG.md` · `README.md` · `CLAUDE.md`.
- **Container** = a folder that holds projects inside it → `_INDEX.md` (generated).

A category folder holds projects, so it is a container; each folder inside it is a leaf. When a leaf gains sub-projects it conceptually becomes a container at that point — but the **index generator currently scans only two levels (category → project)**, and warns about deeper nesting and excludes it from the index (extend the generator when you actually need it).

> **Don't lay out structure ahead of time.** The folder hierarchy forms according to the content of the projects that appear. With no special requirement, follow an ordinary hierarchy; when a project demands a particular architecture, build the folder hierarchy that fits it.

## 3. Per-document update triggers

| Document | Location | What | When to update |
|---|---|---|---|
| `PLAN.md` | project | goals·scope, tech decisions, milestones | when goals·scope·tech decisions **change** |
| `HANDOFF.md` | project | last work / next steps / blockers + **status (frontmatter)** | **at every work session's end** |
| `LOG.md` | project | notable changes by date | one line per feature done·bug fixed·version bump |
| `README.md` | project | intro·how to run·env vars | when run steps·dependencies change |
| `CLAUDE.md` | project | agent ops guide — commands·code map·pitfalls | when build·run·structure·pitfalls change |
| `_INDEX.md` | container | project list in the category + one-line status | **generated** — do not edit by hand (§4) |
| `OVERVIEW.md` | root | map of all projects | **generated** — do not edit by hand (§4) |

## 4. Single source — write state only once

The **only original of state is each project's `HANDOFF.md` frontmatter**. `_INDEX.md`·`OVERVIEW.md` are **derivatives** scraped from it and are never written by hand.

```
HANDOFF.md (frontmatter = original)
   └─(scan→generate)→ _INDEX.md (container)
        └─(scan→generate)→ OVERVIEW.md (root)
```

Do not hand-edit `_INDEX.md`·`OVERVIEW.md`. When the folder structure or state changes, **fix HANDOFF and then regenerate the index** (deterministic, since the scan reads only frontmatter). Regeneration is done by the root's `build-index.ps1` (or `python3 build-index.py` when PowerShell is absent — identical output) — it auto-discovers containers, and only this generator writes the tables·counts (inside `<!-- AUTO:START -->`…`<!-- AUTO:END -->`). Curation notes outside the markers (`> Note:` etc.) are written by humans and preserved by the generator.

## 5. HANDOFF frontmatter schema

```yaml
---
status: 개발            # 기획 | 개발 | 운영 | 보류 (planning | building | live | paused)
updated: <YYYY-MM-DD>   # update at session end
summary: one-line status   # basis for the _INDEX/OVERVIEW one-liner
repo: <org>/<name>      # delete this line if no remote
---
```

- **기획 (planning)** = before code, conception · **개발 (building)** = under construction · **운영 (live)** = live/in use (in use counts as live even if finished — regardless of maintenance frequency) · **보류 (paused)** = stopped (unfinished·halted·superseded·abandoned).
- English aliases allowed: `planning`→기획 · `building`→개발 · `live`→운영 · `paused`→보류 (the generator normalizes them). Put only the value in the frontmatter — the parser does not strip inline `#` comments, so don't add them.

## 6. Document boundaries (no overlap)

- **README** = how to run·env vars·dependencies (how a human runs it).
- **PLAN** = goals·scope·decisions (why·what).
- **HANDOFF** = current state (where things stand now·next·blockers).
- **CLAUDE** = agent ops (commands·code map·pitfalls — what Claude needs to know).

## 7. New project

**Copy the five `.md` files** from `_templates/` and fill them in. Fill at least `PLAN`·`HANDOFF`·`CLAUDE` first (the rest once there's content). Leave empty sections as `_해당 없음_` ("N/A") to distinguish from "not yet written".

> **Only the `.md` files in `_templates/` are copy targets.** `.remember/` (remember-tool scratch)·`.claude/` (worktree·local settings) are not templates — do not copy them.

## 8. Scan exclusions

The index-generation scan looks only at work (category folders). `_templates/`·`docs/` and root meta files are excluded (the generator does not treat a root-level `docs/` as a container).

## 9. Enforcement layers

The convention is enforced in three layers. All three are included in the repo, so they work identically for anyone who receives the template.

| Layer | File | Role |
|---|---|---|
| context | root `CLAUDE.md` | keeps the convention's existence and triggers always visible |
| skill | `.claude/skills/dear-agent/SKILL.md` | procedures for start·end·new project·structure change (includes the `/handoff` command) |
| hooks | `.claude/settings.json` + `.claude/hooks/*.py` | SessionStart: inject convention + status into context · Stop: block session end when HANDOFF is older than the project's files |

- The hooks run on Python 3.7+ (standard library only). With no Python, only the hooks silently disable — the skill·CLAUDE.md layers still work.
- A first-time user must accept Claude Code's project-settings (hooks) approval prompt for the hooks to run.

---

## Change log

- _<YYYY-MM-DD>_ — workspace created, this convention adopted.
