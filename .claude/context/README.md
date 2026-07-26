# context/

Reference docs Claude deep-reads when a task needs them. `CLAUDE.md` points here so the main
session stays lean — only what's relevant gets opened.

Two tiers:

1. **Project briefs** (flat `*.md` below) — longer reference docs for this project, listed in
   the **Manifest**. Plain markdown, no frontmatter, kebab-case. Each records *what is true*
   for this app; the *how-to* lives in the matching skill (they stay DRY — a brief points to
   its skill for behavior rather than re-teaching it).
2. **Reference notes** (`notes/*.md` + auto-generated `INDEX.md`) — small declarative cards,
   read on demand, catalogued in the always-loaded `INDEX.md`. The **`knowledge-router`** skill
   decides what earns a note and its `context.py` engine creates them and regenerates the
   catalog so it can't drift. `python .claude/skills/knowledge-router/scripts/context.py list`.

## Manifest (project briefs)

| File | What it's for | Paired skill (how-to) |
|---|---|---|
| `schema.md` | The eight `tm*` SharePoint lists — columns, types, indexing, and the decisions behind them (the concrete data model). | `sharepoint-list-architecture` |
| `app-structure.md` | Screens, components, and the Power BI reporting surface (licence-gated). | `power-apps-components` |
| `open-questions.md` | Unresolved decisions still shaping schema/app/provisioning. Answered ones live in `.claude/memory/`. | — |

**Decisions with reasoning** are **not** a brief here — they live in the `session-memory`
Decisions ledger (`.claude/memory/INDEX.md`), append-only and decay-proof, so a later session
can't relitigate a settled call. See the `knowledge-router` routing rule (state/decisions →
memory; stable facts → context).

Reference notes are catalogued automatically in `INDEX.md` — not listed here.
