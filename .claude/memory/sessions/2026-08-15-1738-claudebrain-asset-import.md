# 2026-08-15 17:38 — claudeBrain asset import

**Goal:** Review `RorySullivan1/claudeBrain` for skills, workflows and agents this project
could use or update.

## What claudeBrain is, relative to this repo

A factory for `.claude/` assets, with two halves: `.claude/` (meta-skills for *authoring*
assets) and `example-project/` (a mock consumer showing a produced asset set). This repo was
clearly seeded from it — `build-hooks.py`, `catalog.py`, `context.py`, `memory.py` and every
shared hook fragment are **byte-identical**.

## The drift runs OUTWARD — do not import the domain skills

Ten skills overlap. Four are identical (`power-fx-review`, `sharepoint-column-formatting`,
`knowledge-router`, `session-memory`). The other six differ, and in **every** case this repo is
the strict superset, because it carries corrections paid for here:

- `sharepoint-list-architecture` — this repo has the **8-join hard ceiling**; claudeBrain still
  says 12. Its copy is *wrong*, not merely older.
- `power-fx-development/delegation.md` — +49 lines here: the Live Monitor `getRows` procedure
  and the Person/Lookup/Choice blank-check trap. claudeBrain says flatly "`= Blank()`
  delegates".
- `graph-api-integration`, `power-apps-components`, `power-bi-dax`, `power-query-m` — smaller
  local additions.

claudeBrain's copies last moved 2026-07-24. **Anyone tempted to "sync from upstream" would
regress this repo.** The flow is repo → claudeBrain.

## Imported (adapted, not copied verbatim)

- **`/reindex`** — `CLAUDE.md` and `CATALOG.md` both told you to run it and
  `.claude/commands/` did not exist. Dead reference, now real.
- **Authoring layer** — `skill-authoring`, `agent-authoring`, `workflow-authoring`,
  `context-vs-skill`; the six `/add-*` commands; the `author-asset` workflow; layer READMEs.
- **Context economy** — `pre_read_guard`, `post_bash_filter`, `skill-distiller` (+ its
  ExitPlanMode nudge), `token-optimizer`, `agent-finder`, the `token-manager` agent.
- **GitHub** — `github-pull-requests` / `-issues` / `-comments` / `-releases` + `github-operator`.

Every file was rewritten to reference *this* repo's assets. The factory/consumer placement
questions, the `.meta/version` roadmap machinery and all the VBA/VSTO/Python examples are gone.

## Deliberately NOT imported

The stack-specific families (VSTO, VBA, Python, quant, the branding→deck/brochure pipeline and
their agents), and the whole roadmap/version system (`development-mapping`, `/roadmap-*`,
`/version-*`, `goal-auditor`, three guard hooks). The app is BUILT and in a paste-out phase;
`INDEX.md` tracks the paste queue better than a version card would.

## Two things the import had to change to be safe here

1. **`pre_read_guard.py` exempts `src/` and `schema/`.** The only files in the repo over its
   60KB threshold are the three biggest authored screens. Unmodified, the hook would have fired
   almost exclusively on the golden source — and a screen read at 1500 of 3000 lines is how a
   truncated read becomes a wrong paste that returns as "it didn't work". Both branches tested.
2. **No `README.md` in `.claude/commands/` or `.claude/agents/`.** The harness registers every
   `.md` in those flat layers as an asset — the imported `commands/README.md` showed up as a
   live `/README` command. `catalog.py` skips READMEs; the harness does not.

## Branch note

`claude/powerapp-repo-init-xymvlm` was 119 commits behind `main` and 0 ahead — its work had
already merged. Restarted it from `origin/main` per the merged-branch rule and re-applied the
`CLAUDE.md` edits against main's copy.

## Verification

`build-hooks.py --check` green (12 fragments), `catalog.py` regenerated, all imported scripts
compile, both guard hooks smoke-tested (including fail-open on garbage input), validator
22/22.
