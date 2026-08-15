---
description: Scaffold a new subagent (.claude/agents/<name>.md) following the agent-authoring conventions.
argument-hint: <agent-name> [— one-line purpose]
---

You are scaffolding a new **subagent** named `$1` in `.claude/agents/`.

## 1. Load the authoring expertise

Invoke the **agent-authoring** skill — it owns the rules for the triggering
`description`, the least-privilege `tools` allowlist, `permissionMode`, `model`, and
the system-prompt mandate.

That skill plus a built agent (`.claude/agents/powerapp-canvas-developer.md` writes,
`.claude/agents/pre-paste-review.md` is read-only) is the format spec — do **not** spawn
Explore/research agents to re-derive conventions. For a request that needs several
assets, follow the `author-asset` workflow and batch them.

## 2. Decide before writing

Settle the six questions from agent-authoring — mandate, trigger, tools, permissions,
model, return value. Ask the user only for what you can't infer from `$ARGUMENTS`.

## 3. Scaffold

Create `.claude/agents/$1.md` with:

- **frontmatter** — `name: $1`, a triggering `description`, a least-privilege `tools`
  allowlist, the weakest workable `permissionMode`, and a fitting `model`.
- **body** — the agent's complete system prompt: a role line, a numbered workflow, and
  an explicit *concise-summary* output format (the agent starts fresh, so restate any
  constraint it must know — including the air gap, if it touches app source).

## 4. Verify

Run the agent-authoring checklist. Rebuild the catalog (`/reindex`), then report the
path created and how to invoke it (`@agent-$1`).
