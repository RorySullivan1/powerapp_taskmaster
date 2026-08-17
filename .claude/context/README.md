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
| `air-gap.md` | The **one-way** transfer model (repo → Studio; only binary confirmation returns; repo is the authoritative source). Governs every authoring/hand-off decision. | `studio-transfer` |
| `schema.md` | Model shape, delegation/join costs, and open consequences. **Columns live in `schema/schema.yaml` (golden source)** — this brief points there, never repeats it. | `sharepoint-list-architecture` |
| `app-structure.md` | Screens, components, and the native reporting surface (SVG charted). | `power-apps-components` |
| `open-questions.md` | Unresolved decisions still shaping schema/app/provisioning. Answered ones live in `.claude/memory/`. | — |
| `powerapps-docs-source.md` | The authoritative control & layout **docs source** (`MicrosoftDocs/powerapps-docs`) — paths + fetch methods. Grounds SEMANTICS/property meaning, not pa-yaml tokens. | `powerapp-canvas-controls` / `-design` |

**Decisions with reasoning** are **not** a brief here — they live in the `session-memory`
Decisions ledger (`.claude/memory/INDEX.md`), append-only and decay-proof, so a later session
can't relitigate a settled call. See the `knowledge-router` routing rule (state/decisions →
memory; stable facts → context).

Reference notes are catalogued automatically in `INDEX.md` — not listed here.
