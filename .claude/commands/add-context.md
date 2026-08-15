---
description: Scaffold a new context doc (.claude/context/<name>.md) — a whole-topic brief or a reference note.
argument-hint: <context-name|topic> [— what it documents]
---

You are scaffolding a new **context doc** for `$1`.

## 1. Confirm it belongs in context at all

Use the **context-vs-skill** skill first: context is reference Claude deep-reads on
demand (facts, schemas, system maps); a skill is how Claude should *think and behave*.
If the knowledge is a procedure, it is a skill, not a brief.

Then check it isn't better routed elsewhere — a **decision** goes to
`.claude/memory/`, never into a brief (see `CLAUDE.md`). Follow
`.claude/context/README.md` for the format: kebab-case plain markdown with **no YAML
frontmatter**, listed in the manifest.

That README plus an existing brief is the format spec — do **not** spawn
Explore/research agents to re-derive conventions.

## 2. Pick the tier

`context/` has two tiers — decide which `$1` is:

- a whole-topic **brief** — a longer operating doc (`context/<kebab-name>.md`, e.g.
  `schema.md`, `app-structure.md`, `air-gap.md`); continue here.
- a small **reference note** — a declarative card (a concept, an external-system fact,
  a schema, a system map) catalogued in `context/INDEX.md`. **Don't hand-write notes** —
  defer to the **knowledge-router** skill / its `context.py` engine, which creates the
  note and regenerates the catalog so it can't drift. Hand off and stop.

## 3. Scaffold (kebab-case, NO frontmatter)

Create `.claude/context/<kebab-name>.md` as plain markdown — **no YAML frontmatter**.
Give it a top `# <Title>` heading, then the sections the brief warrants (purpose/scope,
the model or architecture, constraints, key workflows, gotchas). Mirror an existing
brief like `.claude/context/schema.md` for depth and tone.

Every field token you name must resolve to a `name:` in `schema/schema.yaml` — the
golden source. Never invent a column name.

## 4. Register and verify

Add the new file to the **Manifest** table in `.claude/context/README.md` with a
one-line "what it's for" (a note instead goes to `context/INDEX.md` via the
knowledge-router flow). Confirm the filename is kebab-case and the doc carries no
frontmatter. Report the path created and that the manifest was updated.
