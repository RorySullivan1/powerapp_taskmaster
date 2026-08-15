---
description: Scaffold a new slash command (.claude/commands/<name>.md).
argument-hint: <command-name> [— what it does]
---

You are scaffolding a new **command** `/$1` in `.claude/commands/`.

## 1. Conventions

One markdown file per command, filename equals the command name; the body is the
prompt; use `$ARGUMENTS` (or `$1`, `$2`, …) for parameters. Keep each command focused on
one repeatable action. Model it on `.claude/commands/reindex.md` (no args) or
`.claude/commands/add-skill.md` (parameterised).

Do **not** put a `README.md` in this directory — the harness would register it as a
`/README` command.

## 2. Scaffold

Create `.claude/commands/$1.md` with:

- **frontmatter** — a `description` and an `argument-hint` so the command is
  self-documenting.
- **body** — a focused prompt for one repeatable action, parameterized with
  `$ARGUMENTS` / `$1`…. State the goal, the steps, and the expected output.

## 3. Verify

Confirm it does one thing well. Rebuild the catalog (`/reindex`), then report the path
created and how to invoke it (`/$1`).
