# hooks/

**Lifecycle enforcement layer.** Deterministic shell scripts the harness runs on
events — the model cannot skip them. This is the floor underneath the whole prompt
stack. Use hooks for anything that must *always* execute.

## Storage — one fragment file per hook (the source of truth)

Claude Code can't load hook definitions from external files; the `hooks` block must be
inline in `settings.json`. To keep that file from becoming a large hand-edited blob,
each hook is stored as its own small `*.json` **fragment** here, and `../settings.json`
is **generated** from them by `build-hooks.py`. Edit the fragments, then rebuild — never
hand-edit the generated `hooks` block.

A fragment is a partial hooks object keyed by event name. Use **exec-form**
(`command` + `args`) for cross-platform reliability:

```json
{ "SessionStart": [ { "matcher": "...", "hooks": [ { "type": "command", "command": "python", "args": [ "..." ] } ] } ] }
```

Every `*.json` here is a fragment (README and `build-hooks.py` are ignored); fragments
merge in filename order, same-event arrays concatenate.

### Rebuild after editing a fragment

```bash
python .claude/hooks/build-hooks.py          # regenerate ../settings.json
python .claude/hooks/build-hooks.py --check   # exit 1 if settings.json is stale
```

(`python3` on macOS/Linux.)

## Fragments in this project

**Memory + context lifecycle** — these drive `session-memory` (load / persist / recall)
and `knowledge-router`'s notes catalog:

| Fragment | Event | Subcommand |
|---|---|---|
| `session-start.json` | `SessionStart` | `memory.py index` — load `INDEX.md` into context |
| `context-start.json` | `SessionStart` | `context.py index` — load the notes catalog |
| `pre-compact.json` | `PreCompact` | `precompact-hook` — persist reminder before compaction |
| `stop.json` | `Stop` | `stop-hook` — once-guarded end-of-session write reminder |
| `user-prompt-submit.json` | `UserPromptSubmit` | `prompt-hook` — recall on "continue"-style prompts |

**Context economy** — these trim volume automatically, underneath the `token-optimizer`
skill's judgment layer:

| Fragment | Event | Calls | Effect |
|---|---|---|---|
| `pre-tool-use-column-guard.json` | `PreToolUse` (Write/Edit) | `pre_write_column_guard.py` | **Blocks a write under `src/` that names a SharePoint column not in `schema/schema.yaml`**, naming the offender and the nearest real column. Judges only snake_case tokens already in the columns' prefix namespace, so camelCase globals and collections are never considered; strips comments first, because screens legitimately discuss retired columns. The only hook here that VETOES — everything else nudges — because an invented column is not a test failure but a failed paste on a work machine. Fails open on anything it cannot parse. |
| `pre-tool-use-read-guard.json` | `PreToolUse` (Read) | `pre_read_guard.py` | Caps an un-paged Read of a very large file to its first 1500 lines and says so. Respects explicit `offset`/`limit`. **Exempts `src/` and `schema/`** — a partial view of the golden source is how a truncated read becomes a wrong paste. Fails open. |
| `post-tool-use-bash-filter.json` | `PostToolUse` (Bash) | `post_bash_filter.py` | Strips ANSI codes and head/tail-elides long output before the model sees it. The command still ran in full. |
| `post-tool-use-plan-nudge.json` | `PostToolUse` (ExitPlanMode) | `skill-distiller/scripts/plan_nudge.py` | On plan approval, asks whether the plan encoded reusable know-how worth distilling into a skill. |

To add a hook: drop a `<event>.json` fragment here and run `build-hooks.py` — or use
`/add-hook`, which does both. A `PreToolUse` fragment that exits non-zero **vetoes** the
tool call.

### Fail open

Every guard here must no-op on unexpected input rather than block work: with no CI and
no way to test against the running app, a hook that misfires is a hook that silently
costs a paste. `pre_read_guard.py` and `post_bash_filter.py` both swallow every error
and let the original call through — copy that shape.

## Self-maintaining (the drift guard)

Two fragments keep `settings.json` in sync automatically, so you rarely run the
generator by hand:

| Fragment | Event | Calls | Effect |
|---|---|---|---|
| `post-tool-use-build.json` | `PostToolUse` (Edit/Write/MultiEdit) | `build-hooks.py --on-edit` | Auto-rebuilds `settings.json` when Claude edits a fragment here. |
| `session-start-hooks-check.json` | `SessionStart` | `build-hooks.py --warn-if-stale` | Warns in-context at session start if `settings.json` is stale (catches manual/IDE edits). |

`--check` (exit 1 when stale) remains for CI / a pre-commit guard.

## Other generators living here

`catalog.py` is a second mechanical generator (like `build-hooks.py` — a plain script, not a
hook). It regenerates `../CATALOG.md`, the on-demand inventory of this project's skills, agents,
commands, and workflows. It is kept fresh by two fragments and the `/reindex` command:

| Fragment | Event | Calls | Effect |
|---|---|---|---|
| `post-tool-use-catalog.json` | `PostToolUse` (Edit/Write/MultiEdit) | `catalog.py --on-edit` | Rebuilds `CATALOG.md` when an asset file (`SKILL.md`, an agent/command/workflow `.md`) is edited. |
| `session-start-catalog-check.json` | `SessionStart` | `catalog.py --warn-if-stale` | Warns at session start if `CATALOG.md` is stale (catches git/IDE changes). It only *warns* — the catalog is on-demand, never printed into every session. |

`CATALOG.md` is per-tree and **not** symlinked (its content differs per tree, like
`settings.json`); regenerate it in each tree with `python .claude/hooks/catalog.py` or `/reindex`.
