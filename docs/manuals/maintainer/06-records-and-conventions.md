# 6 · Records and conventions

## The three records

| Record | What it is | Rule |
|---|---|---|
| `docs/build-history.md` | The paste log — every crossing of the gap, newest first | A row exists **only once a human has pasted and confirmed**. Nothing is "in the app" without one. |
| `schema/schema.yaml` → `provisioned:` | Which lists are live | Flipped on reality, never on intent |
| `.claude/memory/` | Decisions with their reasoning, plus state and threads | Append-only ledger; **committed**, because the environment is ephemeral |

The three answer different questions: *what is in the app*, *what is in SharePoint*, *why it is
that way*. None of them is derivable from the others, which is why all three exist.

## Comments are not a changelog

Do not write history into `src/`. No dates, no "was X", no "moved/superseded/reversed on
<date>", no narration of what a previous session got wrong. **Git has the history and
`.claude/memory/` has the decisions** — a comment that duplicates either rots the moment that
one changes, and it is dead weight in a file a human has to read.

A comment earns its place only if it stops someone breaking the code: a non-obvious constraint,
a delegation trap, a token that looks wrong but is right, a "do not optimise this away". Present
tense, about the code as it is now, and short. If the reasoning is long it belongs in
`.claude/memory/` with a one-line pointer in the file.

## Naming and structure

- One unit per file. A component is a **whole definition** — its custom properties and its
  controls live in the same file.
- A skill's folder name always equals its `name:` frontmatter.
- `.claude/settings.json` and `.claude/CATALOG.md` are **generated**. Edit the hook fragments and
  run `build-hooks.py`; regenerate the catalog with `/reindex`.

## Adding to `.claude/`

Use the assets built for it rather than ad-hoc judgement: the `/add-skill`, `/add-agent`,
`/add-command`, `/add-context`, `/add-hook` and `/add-workflow` commands scaffold, and the
`skill-authoring`, `agent-authoring`, `workflow-authoring`, `context-vs-skill` and
`knowledge-router` skills decide whether the thing should exist and where it belongs. The
routing rule in one line: **state and decisions → memory; stable facts → context; how-to →
a skill.**

## Where these manuals sit in that

They are the narrative layer, and they define nothing — see
[`docs/manuals/README.md`](../README.md). A manual that has to change because a column was
renamed was quoting something it should have linked.
