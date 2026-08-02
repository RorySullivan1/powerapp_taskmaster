# Screen map — the buildable skeleton

The concrete, screen-by-screen build blueprint: the PM-tracker template's 6-screen structure
(`docs/powerapp-patterns-distillation.md` §E) **ported onto our SharePoint schema and decisions**,
with the **Ticket** and **Issue** surfaces the template lacks. This is the checklist we build to.

**Stays DRY:** columns resolve to `.claude/context/schema.md` (internal names ⟨capture⟩ until
provisioned — never invent one); the *why* of screens/reporting is `.claude/context/app-structure.md`;
delegation/Power-Fx *how* is the `power-fx-development` skill. This doc adds only the concrete
per-screen **data bindings + nav + template lineage + build order**.

**Air-gap note:** the bindings below are *authoring intent*, not paste payloads. Each screen is
authored in `src/authored/`, audited by `pre-paste-review`, then pasted via code view against a
confirmed dialect (`studio-transfer`). Nothing binds to a real column until provisioning + a pull
confirms the internal name.

**Named formulas assumed** (`App.Formulas`, data-independent — build first):
`gUserEmail = User().Email`; `Theme = {…}` colour/type tokens (fed from `tmLookups` later).

---

## Navigation model (native, licence-independent)

One reusable **nav component** driven by a `Table({Name, Icon, Screen, Visible})` (template
technique T6 — see distillation §B), placed on every screen. `OnSelect: Navigate(ThisItem.Screen)`.
**Not** dependent on the Power BI dashboard (our Q2 decision). The `Reports` entry is hidden/greyed
when the user has no Power BI licence.

---

## Screens

Lineage = which PM-tracker screen it derives from. "Delegable Items" = the server-side query;
every predicate below is delegation-safe on SharePoint (integer FK `=`, Person `.Email =`, `Or`,
boolean `=`, `StartsWith` on Text, `Sort` on Number/Date).

### 1. Home — personalised landing  *(new; template had no personalised home)*
- **Purpose:** my open tasks (owned *or* backed up), due/overdue counts, my open issues, pinned
  projects, recent activity, quick-add. The licence-independent entry point.
- **My-tasks (delegable):**
  `Filter(tmTasks, IsArchived = false && (Owner.Email = gUserEmail || BackupPrimary.Email = gUserEmail || BackupSecondary.Email = gUserEmail))`
  — Person `.Email =`, `Or`, boolean `=` all delegate.
- **Counts:** `CountRows`/`CountIf` **do not delegate** → compute due/overdue **locally** over the
  already-filtered (small, bounded) my-tasks collection. Filter delegably to a small set first,
  then aggregate in memory — the core SharePoint pattern.
- **My-issues:** `Filter(tmIssues, IsArchived = false && (RaisedBy.Email = gUserEmail || Owner.Email = gUserEmail))`.
- **Pinned:** read `tmUserPrefs.PinnedProjectIds` for this user, resolve client-side.
- **Nav out:** any tile → the relevant detail screen.

### 2. Reports — dashboard panel  *(template: Dashboard, re-architected)*
- **Purpose:** the embedded **Power BI** report for licensed users.
- **CHANGE from template:** the template aggregates via a **SQL view** (`vw_TaskStatusSummary`) —
  **we cannot** (no server-side aggregation on SharePoint; it's the "snapshot list" we rejected).
  Power BI imports the lists whole and does the aggregation.
- **Empty state:** unlicensed users get a real "reporting needs a Power BI licence" card — never a
  broken frame — **plus** optional **native SVG KPI rings** (distillation C1) computed from a
  delegable-filtered small collection, so they still see headline status without Power BI.

### 3. Projects menu  *(template: Screen5 Project Task Overview)*
- **Items (delegable):** `Sort(Filter(tmProjects, IsArchived = false), SortOrder)` (Sort on Number
  delegates). Search: `StartsWith(Title, txtSearch.Text)`.
- **Nav out:** select → Project detail (pass the record via `Navigate(scrProject, …, {gSelProject: ThisItem})`).

### 4. Project detail — three tabs, three queries  *(template: Screen5/6, extended)*
One screen, a tab strip, **three separate `ProjectId`-filtered queries** (never one shared):
- **Tasks → kanban:** `Filter(tmTasks, ProjectId = gSelProject.ID && IsArchived = false)` — integer
  FK `=` delegates. Group into status columns client-side.
- **Tickets → dense numeric table:** `Filter(tmTickets, ProjectId = gSelProject.ID)` — the value
  columns (Notional/Currency/NotionalUSD). Candidate for the **editable-table** pattern
  (distillation C2). Full ticket-level, so **index `ProjectId`** (mandatory).
- **Issues → card feed:** `Filter(tmIssues, ProjectId = gSelProject.ID && IsArchived = false)`.

### 5. Task detail / edit + assignment  *(template: Screen6 Task Details & Edit)*
- **Purpose:** view/edit one task; assign Owner/BackupPrimary/BackupSecondary; link `TicketId`
  (`0` = project-level).
- **Assignment:** Person columns patched with the lowercase **Claims** record (bind picker to
  Office365Users) — see `power-fx-development`; also maintain `OwnerEmailTxt` (denormalised, for sort).
- **Key:** `TaskKey = ProjectKey & "-T-" & ID` patched in a **second write** (no atomic increment).
- **Optional:** task-assignment **email** via a Power Automate flow (template's `FlowPT` pattern; our Q12).

### 6. Ticket detail  *(new — not in template)*
- **Purpose:** one trade; the value columns. **Normalise `NotionalUSD` at write** (FX in a query
  is neither delegable nor reproducible). `SalesRep` (Person) ≠ `Author`.

### 7. Issue detail  *(new — not in template)*
- **Purpose:** freeform; `IssueStatus` includes `NA` (a plain note). `AttributesJson` blob for
  read-only, never-sliced fields (schema.md "adding depth").

### 8. Reference — Clients + stubs  *(template: Screen3 Client Management / Screen4)*
- **Clients:** maintain `tmClients` — `Filter(tmClients, IsActive = true)`, form CRUD.
- **Products / Indices:** browse the ISIN / IndexTicker stubs (read-mostly; seeded externally).

### 9. Admin  *(new — not in template)*
- Lookups (`tmLookups`), bulk archive, orphan detection (FK integrity is app logic — no real joins).

**Recommended (from app-structure.md), build after the core:** Blotter + **extract** (Power
Automate flow, carries ISIN/IndexTicker), Triage, My Week, Global Search (`StartsWith` only).

---

## What we drop or change from the template

| Template | Our version | Why |
|---|---|---|
| **Screen1 User Management** (SQL User table CRUD) | **Dropped as a screen** | Users are directory-sourced — SharePoint **Person** columns bound to Office365Users, not an in-app user table. |
| **Dashboard via `vw_TaskStatusSummary` SQL view** | **Power BI** (+ native SVG fallback) | No server-side aggregation on SharePoint; the SQL view = the snapshot list we rejected. |
| **Auto-increment PKs** (`UserID`, `TaskID`) | Keys from built-in `ID` in a **2nd write** | SharePoint has no atomic increment; a per-project counter races. |
| **Role/status dropdowns** (SQL columns) | `tmLookups`-driven vocabularies | Nothing hardcoded; cached whole at startup. |
| **SQL-delegable ops** (`Search`/`contains`/`Sum`) | Delegable SharePoint equivalents | SharePoint delegates far less — `StartsWith` not `Search`; Power BI/local for aggregates. |
| *(none)* | **Ticket & Issue surfaces added** | Our three-peers-under-a-project model is a superset of the template. |

---

## Build order (respects the air gap + schema dependency)

- **Phase 0 — work machine (unblocks everything):** create the blank canvas app; run the
  `studio-transfer` **round-trip test** (paste one control's code-view YAML into `studio/pulled/`);
  start provisioning the 8 lists and capture true internal names into `schema/`.
- **Phase 1 — author now, data-independent:** `App.Formulas` **theme**; the **nav component** (T6);
  screen **shells** + **empty states**; component **contracts** (status badge, task/issue card,
  ticket row, person chip, confirm dialog, toast); the **SVG gauge** component (C1) with a static
  input. All paste-ready without provisioning.
- **Phase 2 — after provisioning + a confirmed pull:** wire the **delegable data bindings** per
  screen above; Person patching; key second-writes; forms. Audit every unit with `pre-paste-review`
  (schema tokens + delegation) before hand-off.
- **Phase 3 — reporting & automation:** Power BI embed + SVG fallback; the extract/blotter (Power
  Automate); admin. Depends on Q2b (workspace/refresh/embed) and Q12 (Power Automate).
