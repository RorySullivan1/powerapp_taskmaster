# `.claude/` — project infrastructure

This directory holds the typed building blocks Claude Code uses for a project.
Each subdirectory is a distinct *layer* with a distinct job. The layers compose.

> This describes the **layers**. For the current inventory of what's in them, read
> `CATALOG.md`; for the project itself, `../CLAUDE.md`. The layer taxonomy originates
> in the [claudeBrain](https://github.com/RorySullivan1/claudeBrain) factory — assets
> lifted from there are adapted to this repo, never carried over verbatim.

## The composability stack

```
hooks      ← enforcement, underneath everything (Claude cannot skip these)
─────────────────────────────────────────────────────────────────────────
workflows  ▸  commands  ▸  agents  ▸  skills
(orchestrate)  (one-shot)   (isolated)  (expertise)
```

- **hooks/** — Deterministic shell scripts run by the harness on lifecycle events
  (`PreToolUse`, `PostToolUse`, `SessionStart`, …). They are the enforcement layer
  *underneath* the prompt stack — the model cannot choose to skip them. Use for
  anything that must *always* happen: formatting, branch guards, write protection,
  cache warming. Configured in `settings.json`.
- **workflows/** — Multi-step autonomous orchestrations. Claude executes a scripted
  sequence that can loop, branch, and spawn agents. Each is a markdown file.
- **commands/** — Single-shot, stateless prompt templates — saved prompts you'd
  otherwise retype. One file per command (`/<name>`).
- **agents/** — Isolated subagents spawned with clean context. They do focused work
  and return only a summary, so they don't bleed context into the main session.
- **skills/** — Domain-expertise bundles that tell Claude *how to think and behave*
  for a task type. Applied within a session or an agent's context. One folder per
  skill containing `SKILL.md`; the folder name equals the skill's `name:` frontmatter.

## Supporting files

- **context/** — Reference docs (architecture notes, schemas, stack instructions).
  `CLAUDE.md` points here; Claude deep-reads only what's relevant to the task. See
  `context/README.md` for the manifest.
- **settings.json** — Permissions, model, and hook configuration.
- **memory/** — Cross-session state via the `session-memory` skill: an auto-loaded
  `INDEX.md` plus append-only `sessions/*.md` logs (loaded/persisted by the lifecycle
  hooks in `settings.json`). Replaces a static `DECISIONS.md` log.
- **CATALOG.md** — A generated, **on-demand** inventory of every skill, agent, command, and
  workflow with a one-line purpose. `CLAUDE.md` references it by path instead of enumerating
  assets (skills/agents already auto-load by their `description:`). Produced by
  `hooks/catalog.py` (a mechanical generator), kept fresh by a `PostToolUse` auto-rebuild +
  a `SessionStart` staleness warning, and regenerated with the `/reindex` command.

## Status in this project

All seven layers are populated:

- **skills/** — the canvas-app families (`powerapp-canvas-*`, `power-fx-*`,
  `power-apps-*`), the SharePoint backend (`sharepoint-*`), integration and reporting
  (`graph-api-integration`, `power-bi-dax`, `power-query-m`), `studio-transfer` for the
  air gap, the authoring meta-skills, the GitHub set, and the operational skills
  (`session-memory`, `knowledge-router`, `agent-finder`, `token-optimizer`,
  `skill-distiller`). See `skills/README.md` for the category map.
- **agents/** — `powerapp-canvas-developer` (writes app source end to end),
  `pre-paste-review` (read-only, the last gate before a paste), `github-operator`, and
  the context-economy `token-manager`.
- **commands/** — `/reindex` plus the `add-*` scaffolding family.
- **workflows/** — `change-end-to-end`, `screen-build`, `control-grounding`,
  `author-asset`.
- **hooks/** — memory + context lifecycle hooks, the context-economy guards
  (`pre_read_guard`, `post_bash_filter`), and the `build-hooks.py` / `catalog.py`
  generators, compiled into `settings.json` from the fragments here.
- **context/** — the briefs (`schema.md`, `app-structure.md`, `air-gap.md`,
  `open-questions.md`) plus the reference-notes tier, and **memory/** is active.

For the full, current list of any layer, read **`CATALOG.md`** (regenerate with `/reindex`)
— this README describes the layers; the catalog enumerates them.

## What this repo is *not*

`.claude/` maintains the app's source; it does not run it. There is no CI, no linter and
no test run on this machine, and no connection to Power Apps Studio — the only path from
here to the running app is a human with a clipboard, one way. Hooks are therefore the
only enforcement that exists. See `../CLAUDE.md`.
