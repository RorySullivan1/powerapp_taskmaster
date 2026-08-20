# Manuals

Two manuals, two audiences. They are the **narrative** layer of this repo: they explain how the
app is used and how it is maintained. They are **not** a source of truth for anything the repo
already defines.

| Manual | Who it is for | Answers |
|---|---|---|
| [**User manual**](user/) | People on the desk who open EQD Taskmaster and do work in it | What each screen is for, what a field means, why a number looks the way it does |
| [**Maintainer manual**](maintainer/) | Whoever changes this repo and carries the change into Power Apps Studio | Where source lives, how a change reaches the running app, what must stay in step with what |

## The rule these manuals live by

**A manual describes; the golden source defines.** Where the two disagree, the golden source
wins and the manual is the thing to fix.

| Subject | Defined in | Never re-stated here |
|---|---|---|
| SharePoint lists and columns | `schema/schema.yaml` | Column names, types, choice values |
| App source (screens, components, App object) | `src/**.pa.yaml` | Formulas |
| Decisions and their reasoning | `.claude/memory/` | Why a settled call was made |
| Every crossing of the air gap | `docs/build-history.md` | Paste history |
| Repo assets (skills, agents, commands) | `.claude/CATALOG.md` | The asset inventory |

So a chapter that needs a column name links to the schema instead of copying it, and a chapter
that needs a formula points at the file and line rather than quoting it. Copies rot; links do not.

## Scope boundary against `docs/`

The rest of `docs/` is **design notes and history** — how something came to be built and what was
diagnosed along the way (`build-history.md`, `reports-screen-design.md`, `notes/`). Those are
written for the moment of building. The manuals are written for someone arriving now, who needs
the current shape of things and not the route that got here.

## Keeping them true

- A change to a **screen's behaviour** that a user would notice → update the matching user chapter
  in the same commit.
- A change to the **workflow, tooling or enforcement** → update the matching maintainer chapter.
- A change to **schema or formulas alone** → usually nothing here changes. If a manual has to
  change because a column was renamed, the manual was quoting something it should have linked.
