# 2026-08-02 17:02 · external-repo-review

**Goal:** Review aprildunnam/PowerApps + PM-tracker template; distill reusable patterns into skill/agent candidates

## What happened
- Cloned two public repos directly (add_repo is pinned to the `rorysullivan1` owner — cross-tier
  adds unsupported, so plain public clones over the proxy).
- **aprildunnam/PowerApps** — ~25 samples, ~90% packaged binary. A subagent distilled **20
  reusable techniques (T1–T20)** from the readable source (DeskReservation `.pa.yaml`,
  weekly-timesheet `.fx.yaml`, + 3 unzipped `.msapp`). Wrote `docs/powerapp-patterns-distillation.md`.
- **Mohd-Abbas-Rizvi/PowerApp…Project-Manager-and-Tracker** — assessed as a "core template."

## Decisions / findings
- **PM-tracker = blueprint, not plumbing.** It's **SQL-backed** (`ProjectTrackerDB`;
  `[dbo].[User]/[ProjectTask]/[Projects]/[Account]`; a `vw_TaskStatusSummary` SQL view; `FlowPT`
  email flow). Reuse its **screen inventory + native-nav flow + task-assign→email + FK-by-ID
  client-side join** (all match our decisions). **Do NOT port** its data layer: SQL delegates
  aggregates/contains/Sum that SharePoint doesn't; its dashboard aggregates via a **SQL view = the
  snapshot list we rejected**; auto-increment PKs (we derive keys from `ID`); dropdowns vs
  `tmLookups`; UserID/UserName vs Person columns. It lacks Tickets/Issues — our model is a superset.
  Use it as the UX skeleton to **rebuild against our SharePoint schema** via code-view paste.
- **Distillation placement (fold-first):** most techniques already covered by our adopted skills
  (validation only). Net-new **gaps → candidate skills, dual-use for our app:**
  - **C1 SVG-in-PowerApps** (`"data:image/svg+xml,"&EncodeUrl(<svg>)`, `stroke-dasharray` progress
    ring) — no skill covers in-app vector rendering. **Directly useful:** native KPI visuals as the
    fallback for unlicensed Power BI users (our Q2).
  - **C2 editable-table (grid-in-gallery)** — `ForAll(gallery.AllItems, Patch(src, Defaults(src),…))`;
    `Defaults` (new) vs `ThisRecord` (update) trap. **Useful:** our tickets "dense numeric table" tab.
  - **C3 Teams deep-linking** — reference-note fact (URL scheme + `Param("subEntityId")`).
  - Plus §B recipe extensions to `power-apps-components` (nav-as-data-table, key/value Styles
    theming, timer-init-for-components, calendar) and `sharepoint-list-architecture` (sortable
    `yyyymmddhmm` companion column).

## Gotchas & dead ends
- Everything read was **export dialect** (`.pa.yaml`/`.fx.yaml`) or legacy `.msapp` JSON — NOT the
  code-view paste dialect; nothing paste-tested. Re-author through pulled→authored→landed; re-resolve
  column tokens to our `schema.md`.
- `.msapp` (both repos) is a zip → `unzip` to read `Src/*.pa.yaml` (modern) or `.fx.yaml` (legacy).
  PM-tracker's is modern `.pa.yaml` (read-only, GA source format).

## State at end
- `docs/powerapp-patterns-distillation.md` written (T1–T20 catalog + placement + PM-tracker §E).
  No new skills authored yet — these are candidates awaiting a go. Not committed yet.

## Open threads
- **Author C1 (SVG) + C2 (editable-table)?** Dual-use (our app + upstream). Awaiting user go.
- **Propose §B/§C upstream to claudeBrain** (can't push there from here — different owner scope).
- **Reconsider Q11 (provisioning):** the **flow-as-list-provisioner** pattern (T18) sets clean
  internal names repeatably — a real middle path vs the manual-UI route we chose. May revisit.
- Produce a **screen map** porting PM-tracker's 6-screen blueprint onto our schema (+ Ticket/Issue
  surfaces it lacks) — offered, awaiting go.
