---
description: Scaffold a new lifecycle hook script and its settings.json fragment.
argument-hint: <hook-name> [PreToolUse|PostToolUse|SessionStart|Stop|…]
---

You are scaffolding a new **hook** named `$1` in `.claude/hooks/`.

## 1. Conventions

Follow `.claude/hooks/README.md`. Two rules matter most here:

- **Never hand-edit `.claude/settings.json`.** Its `hooks` block is *generated* from the
  `*.json` fragments in `.claude/hooks/` by `build-hooks.py`. You add a fragment; the
  generator wires it.
- A `PreToolUse` hook that exits non-zero **vetoes** the tool call. Hooks run
  deterministically — the model cannot skip them — so keep the script safe, fast, and
  fail-open on unexpected input. `pre_read_guard.py` and `post_bash_filter.py` are the
  worked examples of that discipline.

With no CI on this machine, a write-time hook is the only enforcement this repo has —
which is exactly why the open **column-token validator** candidate in `CLAUDE.md` is
worth building here rather than writing more prose.

## 2. Confirm the event

Determine the lifecycle event and matcher from `$ARGUMENTS`; ask if not provided.

## 3. Scaffold

- Create the script `.claude/hooks/$1.py` with a shebang and a module docstring saying
  what it does and how it fails. Read hook input as JSON from stdin; exit `0` to allow
  and (for `PreToolUse`) non-zero to block, printing a reason to stderr.
- Create the fragment `.claude/hooks/<event-kebab-name>.json` — a partial hooks object
  keyed by event name, in exec-form (`command` + `args`), using
  `${CLAUDE_PROJECT_DIR}` for the script path.

## 4. Verify

Run `python .claude/hooks/build-hooks.py` and show the resulting `settings.json` entry.
Confirm the event and matcher are right, then report both paths created.
