# Workspace Template — Usage

> **Translation.** The Korean original ([USAGE.md](USAGE.md)) is canonical; if this file and the original disagree, the original wins. Please update both when changing the steps.

This folder is a template for starting a new **workspace** (a work root that follows the documentation convention). Copy the whole thing and fill it in, and you have one workspace. (The per-*project* template lives separately in `_templates/`.)

## Creating a new workspace

> On GitHub, create a new repo via **Use this template** (or clone), then do steps 1–8 below inside that folder.

1. **Clean the distribution** — delete the demo folder `_example/`. If you received the folder by direct copy, also delete session scratch (`.remember/`·`.claude/worktrees/`·`__pycache__/`) (absent if you got it via git). ⚠ Do not delete the rest of `.claude/` (settings.json·skills/·hooks/·commands/) — those are the enforcement layers.
2. **Replace the README** — delete the public-facing `README.md` and create a new one from the snippet below, filling in the H1 and one-line intro:
   ```markdown
   # <workspace>

   _One-line intro._ Holds projects under category folders. Convention and map below.

   - **Project map** → [OVERVIEW.md](OVERVIEW.md) _(generated, do not edit)_
   - **Documentation convention** → [CONVENTIONS.md](CONVENTIONS.md) _(single source of authority)_
   - **Blank templates** → `_templates/`
   - **Index generation** → `build-index.ps1` (Windows·PowerShell) / `python3 build-index.py` (identical output)
   ```
3. **Fill in name·intro** — set the `<workspace>` in the top H1 of `CLAUDE.md`·`OVERVIEW.md` to the real name, and fill in the one-line description of `OVERVIEW.md` (the `> ...` slot).
4. **Remove template guidance** — delete the 📋 template-guidance line at the top of `CLAUDE.md`. Fill in the reference-assets section if you use it, delete it if not. Set the `<YYYY-MM-DD>` in the "Change log" at the bottom of `CONVENTIONS.md` to the creation date. Keep or delete `LICENSE`·`.github/` per your repo policy.
   - ⚠️ The schema example `repo: <org>/<name>` and the `<!-- AUTO:* -->` markers in `CONVENTIONS.md` are **examples·syntax** — don't touch them.
5. **Add category folders + projects** — create a category folder (e.g. `apps/`) and inside it make a leaf (project) by copying the `.md` files from `_templates/`. Don't lay out categories ahead of time — add them as they arise (CONVENTIONS §2). The generator looks at the container→leaf structure.
6. **Generate the index** — run the one line that fits your environment; it auto-discovers containers and builds `OVERVIEW.md`·`_INDEX.md`.
   - Windows: `powershell -ExecutionPolicy Bypass -File ./build-index.ps1`
   - PowerShell 7 (any OS): `pwsh -File ./build-index.ps1`
   - No PowerShell (mac/linux, etc.): `python3 build-index.py` _(identical output)_
7. **Approve the hooks** — the first time you open this folder in Claude Code, it asks you to approve the project settings (the SessionStart/Stop hooks in `.claude/settings.json`). Approval is required for enforcement (session brief·HANDOFF gate) to work. Without Python 3.7+, only the hooks disable; the skill·CLAUDE.md still work.
8. **Verify then tidy** — once the generated `OVERVIEW.md` looks right, delete this `USAGE.md` (it's template guidance only). A procedure summary also lives in the root `CLAUDE.md`, so it remains after deletion.

## Layout

> This table is the **complete list** of root files — update it here too when you add/remove a file.

| File | Role |
|---|---|
| `CONVENTIONS.md` | single source of authority for the doc system |
| `CONVENTIONS.en.md` | English mirror of CONVENTIONS (KO is canonical) |
| `USAGE.en.md` | English mirror of USAGE (KO is canonical) |
| `CLAUDE.md` | root agent-ops guide (+ entry point for new setup) |
| `README.md` | public repo intro (replaced with the workspace intro at setup — step 2) |
| `build-index.ps1` | `_INDEX`·`OVERVIEW` generator (PowerShell, UTF-8 BOM) |
| `build-index.py` | cross-platform twin of the same generator (when no PowerShell, identical output) |
| `_templates/` | project (leaf) template — PLAN·HANDOFF·LOG·README·CLAUDE |
| `_example/` | filled-in demo workspace (deleted at setup — step 1) |
| `OVERVIEW.md` | empty seed (filled on first generation) |
| `.claude/settings.json` | SessionStart/Stop hook wiring (enforcement) |
| `.claude/hooks/` | hook scripts — session_brief.py (brief injection)·handoff_guard.py (HANDOFF gate)·workspace_lib.py (shared scope resolution) |
| `.claude/skills/dear-agent/` | project skill — the convention's procedures |
| `.claude/commands/handoff.md` | `/handoff` — manually invoke the session-end procedure |
| `.gitignore` | excludes session scratch + tracks the root `.claude` distribution assets |
| `.gitattributes` | pins line endings to LF — so the generator's "byte-identical output" isn't broken by per-OS CRLF conversion |
| `.github/workflows/ci.yml` | verifies the two generators' identical output·idempotence |
| `.github/banner.png` | README top banner (same image as the social preview) |
| `LICENSE` | MIT |
| `USAGE.md` | this guide (deleted after setup) |

> The two generators guarantee **identical output** — when you change the logic, change both (CI verifies).
> The root `.gitignore` already excludes session scratch. When you create a category folder, add one line `<category>/*/` — projects are each their own repo.
