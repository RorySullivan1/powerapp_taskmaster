# skills/

**Domain-expertise bundles.** Each skill teaches Claude *how to think and behave* for a
recurring task type. Skills auto-load by their `description:` — the harness picks the
right one, so they are not invoked by hand.

## Format

- One folder per skill containing `SKILL.md`; **the folder name equals the skill's
  `name:` frontmatter.** Renaming means renaming both.
- Frontmatter: `name` and a `description` that leads with the use case, names concrete
  trigger phrases, and states the boundaries against neighbouring skills.
- A skill may ship supporting files beside `SKILL.md` — a reference doc it deep-reads on
  demand (`power-fx-development/delegation.md`, `graph-api-integration/endpoints.md`) or
  a `scripts/` engine (`session-memory`, `knowledge-router`, `agent-finder`,
  `token-optimizer`, `skill-distiller`).

Author with the **skill-authoring** skill and scaffold with `/add-skill`. Use
**context-vs-skill** to confirm the knowledge is a skill and not a context brief, and
**skill-distiller** to decide whether it should exist at all — folding into an existing
skill usually beats a new one.

## The categories here

Boundaries matter more than count, because these overlap. In rough dependency order:

- **Canvas app, generic** — the four `powerapp-canvas-*` skills: `controls` (what a
  control is called and what it returns), `development` (the `.pa.yaml` file and its
  Power Fx), `design` (geometry and whether a user can touch it), `project-management`
  (state and paper trail).
- **Canvas app, formulas** — `power-fx-development` (writes), `power-fx-review`
  (audits), `power-apps-components`, `power-apps-editable-table`, `power-apps-svg`.
- **SharePoint backend** — `sharepoint-list-architecture` (the store),
  `sharepoint-column-formatting` (declarative formatter JSON).
- **Integration & reporting** — `graph-api-integration`, `power-bi-dax`, `power-query-m`.
- **The air gap** — `studio-transfer` owns the transfer channel and its discipline.
- **Authoring** — `skill-authoring`, `agent-authoring`, `workflow-authoring`,
  `context-vs-skill`, `skill-distiller`: how to build more of this.
- **Operational** — `session-memory`, `knowledge-router`, `token-optimizer`,
  `agent-finder`: how a session keeps state and stays cheap.
- **GitHub** — `github-pull-requests`, `github-issues`, `github-comments`,
  `github-releases`, orchestrated by the `github-operator` agent.

For the current inventory with one-line purposes, read `../CATALOG.md` (regenerate with
`/reindex`) — this README describes the layer; the catalog enumerates it.
