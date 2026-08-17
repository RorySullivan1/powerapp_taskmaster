# App structure — screens, components, and the reporting surface

Reference for the canvas app's shape: the screens, what each does, the components, and how the
native reporting surface fits. The *how-to* of building any of it — responsive containers,
custom-property contracts, HtmlText, galleries/forms — is the **`power-apps-components`** skill;
the query logic and delegation behind each screen is **`power-fx-development`**; charts are
**`power-apps-svg`**. This doc records *what* the app is, not *how* to build a control.

## Reporting surface — POWER BI IS OUT OF SCOPE (2026-08-17)

**Power BI has been dropped from this project entirely.** No embed, no licence gate, no
`gHasPowerBiLicence`, no DAX, no Power Query. `scrReports` is the analytics surface for
everyone, built natively.

**Charts are SVG by default** — an `Image` control fed a `data:image/svg+xml` URI built in
Power Fx, per the **`power-apps-svg`** skill, which is now the only charting layer this app
has. The reason is not cost avoidance: SVG is fully custom, needs no licence, no PCF and no
external asset, and it renders inside galleries where a chart control cannot go.

What survives from the old constraint, because it was never really about licensing:

- **Navigation is native and stands on its own.** Nothing about reaching a part of the app
  ever depends on a reporting surface.
- **Aggregates never delegate.** `CountRows`/`Sum`/`Average` compute locally over fetched
  rows, so every figure must be scoped to a set small enough to be exact, and a screen showing
  desk-wide numbers owes the user a truncation banner saying so.

What was reversed: the old rule said *do not rebuild the aggregate dashboard as native charts
to dodge the licence gap*. That rule is void — native charts are now the design, not a dodge.
See `docs/reports-screen-design.md`.

**Consequence with no owner:** the blended cross-currency notional. C5 sends
`transaction_notional` per-currency only and named Power BI as the thing that would convert
it. **Nothing owns that now** — it needs an FX dimension (currency, rate, as-of date) that
does not exist in the model. Either the app grows one, or the blended figure is permanently
out of scope. Open.

## Required screens

- **Personalised home.** My open tasks (owned **or** backed up, via the delegable `Or` on the
  three Person columns); due/overdue counts; my open issues; pinned projects; recent activity;
  quick-add.
- **Reports.** Native analytics for everyone, drawn as SVG. Not a navigation hub.
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
