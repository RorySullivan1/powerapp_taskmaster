# App structure — screens, components, and the reporting surface

Reference for the canvas app's shape: the screens, what each does, the components, and how the
Power BI reporting surface fits. The *how-to* of building any of it — responsive containers,
custom-property contracts, HtmlText, galleries/forms — is the **`power-apps-components`** skill;
the query logic and delegation behind each screen is **`power-fx-development`**; the embedded
report's measures are **`power-bi-dax`** and its data load **`power-query-m`**. This doc records
*what* the app is, not *how* to build a control.

## Reporting surface — decided constraint (2026-07-26)

**Not everyone who opens the app has a Power BI licence.** Consequences, in force:

- **The embedded Power BI report is not the primary dashboard and cannot carry core
  navigation.** A user without a licence must still be able to reach every part of the app.
- **Navigation is native and licence-independent.** The home screen and menu stand on their own.
- The embedded report appears as a **reporting panel for licensed users**, with a **real empty
  state** (a clear "reporting needs a Power BI licence — here's who to ask" card, not a broken
  frame) for everyone else.
- Where the app shows figures natively, it uses delegable in-app queries; Power BI remains the
  place for aggregate analytics (it imports the lists whole — see the "no snapshot list"
  decision). Do **not** rebuild the aggregate dashboard as native charts to dodge the licence
  gap; provide the empty state instead. (Q2 sub-items — workspace, refresh cadence, embedded vs
  linked — remain open; see `open-questions.md`.)

## Required screens

- **Personalised home.** My open tasks (owned **or** backed up, via the delegable `Or` on the
  three Person columns); due/overdue counts; my open issues; pinned projects; recent activity;
  quick-add. This is the licence-independent landing surface.
- **Dashboard (reporting panel).** The **embedded Power BI report** for licensed users, with the
  empty state above for the rest. Not a navigation hub.
- **Projects menu.** Browse/select projects.
- **Project detail — three genuinely different tabs**, served by **three separate
  `ProjectId`-filtered queries** (not one shared query):
  - **Tasks → kanban** (status columns).
  - **Tickets → dense numeric table** (the value columns; primary transactional store).
  - **Issues → card feed** (freeform).
- **Separate detail screens** for a single **task**, **ticket**, and **issue**.

## Recommended screens (propose with rationale)

- **Blotter across all projects** that also **produces the extract** for external product
  analysis — carrying **ISIN / IndexTicker** as the join key (the egress contract). Prefer a
  **Power Automate flow** over an in-app `Download()`: app-side export only sees what's in
  memory and truncates at 2,000 rows, precisely when the extract matters. (Depends on Q12
  Power Automate availability; Q7 extract contents/route.)
- **Triage** — open issues needing attention (drives the `NA` status split, Q8).
- **My week** — a personal planning view.
- **Global search** — `StartsWith` only (substring can't delegate against SharePoint).
- **Reference** — maintain clients; browse product/index stubs.
- **Admin** — lookups, bulk archive, orphan detection (FK integrity is app logic; no real joins).

## Components

Navigation, task card, issue card, ticket row, **status badge** (colour from `tmLookups`),
person chip, empty state, confirm dialog, toast. Build repeating row templates from plain
controls or HtmlText — a canvas **component can't sit inside a gallery or form**; reserve
components for screen-level building blocks (header, nav, side panels). Centralise colours and
type in **named formulas** (`App.Formulas`), fed from `tmLookups` where the palette is
data-driven. (All mechanics → `power-apps-components`.)

## Data-flow notes that shape the UI

- **Three peers under a project.** Tasks/Tickets/Issues never nest into one another in the UI;
  they surface alongside. Only Tasks roll up into completion.
- **Client-side joins.** No Lookup columns — the app resolves FKs (`ProjectId`, `TicketId`,
  `ClientId`, `InstrumentId`) against `ID` in memory. Resolve once at screen load, not per
  gallery row (avoid the N+1 — see `power-fx-review`).
- **`tmLookups` cached whole at startup** drives conditional field visibility (the
  `FieldVisibility` rows) and badge colours.
