---
description: Scaffold a new skill bundle (.claude/skills/<name>/SKILL.md) with correct frontmatter and structure.
argument-hint: <skill-name> [— one-line purpose]
---

You are scaffolding a new **skill** named `$1` in `.claude/skills/`.

## 1. Load the authoring conventions

Use the **skill-authoring** skill — it owns the rules for the triggering `description`,
the naming, and the body structure. Model the shape on a built skill such as
`.claude/skills/studio-transfer/SKILL.md` (YAML frontmatter + a sectioned markdown body).

That skill plus a built bundle is the format spec — do **not** spawn Explore/research
agents to re-derive conventions or re-read example bundles. For a request that needs
several assets, follow the `author-asset` workflow and batch them.

## 2. Scaffold (folder name MUST equal `name:`)

Create `.claude/skills/$1/SKILL.md` with:

- **frontmatter** — `name: $1` and a `description:` that leads with the use case and
  lists concrete trigger phrases. This field drives auto-invocation, so make it
  specific; a vague description means the skill never triggers. State the boundaries
  against neighbouring skills — this repo's set is dense and overlaps easily.
- **body** — a title, then the sections the task warrants: core principles, the
  workflow / how-to, a checklist, anti-patterns, and an out-of-scope section.

## 3. Verify

Confirm the folder name equals the `name:` value and the description names real
triggers. Rebuild the catalog (`/reindex`) so the new skill is listed, then report the
path created and offer to fill in the body.
