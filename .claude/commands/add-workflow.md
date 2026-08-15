---
description: Scaffold a new multi-step workflow (.claude/workflows/<name>.md).
argument-hint: <workflow-name> [— what it orchestrates]
---

You are scaffolding a new **workflow** named `$1` in `.claude/workflows/`.

## 1. Conventions

Use the **workflow-authoring** skill, and follow `.claude/workflows/README.md`: one
markdown file per workflow; the body lays out the ordered steps, the agents/commands
each step invokes, the inputs and outputs, and the success/stop conditions. Reference
`../agents/` and `../commands/` rather than re-describing them. Model it on
`.claude/workflows/change-end-to-end.md`.

## 2. Scaffold

Create `.claude/workflows/$1.md` describing:

- **purpose and inputs** — what it produces and what it needs to start.
- **ordered steps** — each naming the agent or command it invokes and the output it
  passes on.
- **control flow** — any branch/loop logic, and explicit **stop / success conditions**.

If the workflow ends at the air gap, its terminal step is a hand-off note for the
human, not a paste — nothing crosses the gap without them.

## 3. Verify

Confirm every referenced agent and command exists (or is flagged as still to be
created). Rebuild the catalog (`/reindex`), then report the path created.
