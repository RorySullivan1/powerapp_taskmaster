# 2026-08-20 23:46 · manuals-section

**Goal:** Organize a docs section for two manuals: users and maintainers

## What happened
- Built `docs/manuals/` — a section index plus two manuals, each with a README and seven
  chapters. Committed and pushed on `claude/powerapp-repo-init-xymvlm` (47cd07d).
  - **user/** — getting started (nav + form conventions), Home, Projects, the three work
    types, reference data, Reports, troubleshooting.
  - **maintainer/** — repo/authority, the air gap, the end-to-end change path, schema
    changes, validation + enforcement, records + conventions, failed-paste triage.
- Added `docs/README.md` separating the manuals (current shape, written for someone arriving
  now) from the build-time notes (`build-history.md`, `reports-screen-design.md`, `notes/`,
  `screen-map.md`), and a Documentation section in the root README.
- **The user manual was written from the SOURCE, not from intent** — real field labels and
  `*` markers, the `＋ New` entry points, the empty-state sentences, the output-toggle-clears
  behaviour, the derived ring and health, the Period/Scope controls and the exact truncation
  banner wording. Nothing in it was inferred from `screen-map.md`, which is stale.
- **The one piece of new synthesis** is the stay-in-step table in `maintainer/03-making-a-change.md`:
  `gDataRowLimit` ↔ the Studio setting, `gStageWeights` ↔ `rollups.stage_weights`, component
  colours ↔ `gTheme`, `gNavMenu` keys ↔ each screen's `Switch`, the `ActiveProjects` phase
  allow-list ↔ `project_phase`'s values. Each half was documented in its own file header;
  nothing had collected them, and every one of them fails silently when it drifts.
- Corrected two stale figures in the root README: component count 12 -> 10, and
  "App.pa.yaml — named formulas (Theme, NavMenu, …)", which contradicts the settled
  2026-08-12 decision that constants live in `OnStart` via `Set`.
- Verified every internal link and heading anchor across `docs/` with a script; validator
  still 22/22 (no `src/` change).

## Gotchas & dead ends
- **`docs/screen-map.md` is historical and reads as current.** It describes `tmTickets`, an
  Admin screen and a `tmLookups`-driven model the app did not end up with. Labelled as
  historical in `docs/README.md` rather than edited or deleted — that call is the user's.
- **`cmpAppBar`'s DEFAULT `Items` carries a fifth "Admin" entry (Key 5) and there is no
  `scrAdmin` in `src/Screens/`.** Every screen passes `Items: =gNavMenu` (four entries), so
  no user sees it — but an instance left on the default would render a nav row that
  navigates nowhere. Not changed; the manuals document four destinations.
- `docs/notes/components.md` says up front that it is partial and predates four components.
  Left alone — `.claude/CATALOG.md` is the current inventory and the manuals point there.

## State at end
- The manuals section exists, is committed and pushed, and nothing about it needs a paste —
  it is docs only, no `src/`, `schema/` or `.claude/` behaviour change.
- The paste queue is unchanged (empty as of 2026-08-19).

## Open threads
- Retire or keep `docs/screen-map.md`? It is provenance for the build, and it is also the
  most confidently wrong document in the repo about what the app currently is.
- The `cmpAppBar` Admin default: drop Key 5 from the component default, or keep it as the
  hook for a future admin screen?
- The manuals have no maintenance hook. If a screen's user-visible behaviour changes, nothing
  mechanical will notice the chapter went stale — the rule is written in
  `docs/manuals/README.md` and is prose, like "never invent a column name" was before the
  guard hook existed.
