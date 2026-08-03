# Data model — the SharePoint lists (canonical)

The concrete backend for the canvas app. **snake_case is canonical** (user-confirmed 2026-08-02);
this supersedes the earlier PascalCase `tm*` design entirely.

Transcribed from schema screenshots supplied by the user — the only channel, since the air gap is
**one-way** (`context/air-gap.md`). Provenance and the raw capture log live in
`schema/incoming-lists.md`. The *how-to* of list design (column types, thresholds, indexing, the
join budget) is the **`sharepoint-list-architecture`** skill; the delegation matrix is
`power-fx-development/delegation.md`. This brief records **what this model is** and **what it
costs**, not how SharePoint works in general.

> **Names are frozen at creation.** Everything below binds by **internal name**, exactly as
> written — including the casing anomalies `Issue_owner` and `product_UID`. Confirm those two
> before provisioning; a rename afterwards changes only the display label.

## The lists

| List | Role | Complex cols (join cost) |
|---|---|:-:|
| `taskmaster_projects` | The parent. Everything hangs off it. | 6 |
| `taskmaster_tasks` | Units of work. **The heaviest list — see J1.** | 11 |
| `taskmaster_transactions` | Trades, full transaction-level. | 4 |
| `taskmaster_issues` | Freeform issues. | 5 |
| `taskmaster_clients` | Client dimension. | 4 |
| `taskmaster_products` | Product reference. | 1 |
| `asset_approval` | Approval reference (tasks point at it). | 0 |
| `asset_library` | **Referenced by `task_output_asset` — schema not yet supplied.** | ? |

**Relationships** (all via SharePoint **Lookup** columns — records, not integers):

```
taskmaster_projects ──< taskmaster_tasks         (task_project_id)
                    ──< taskmaster_transactions  (transaction_project_id)
                    ──< taskmaster_issues        (issue_project_id, required)

taskmaster_clients  ──< taskmaster_tasks         (task_client_name)
                    ──< taskmaster_transactions  (transaction_client_name)
taskmaster_products ──< taskmaster_tasks         (task_product_id)
                    ──< taskmaster_transactions  (transaction_product_id)
asset_approval      ──< taskmaster_tasks         (task_output_approval)
asset_library       ──< taskmaster_tasks         (task_output_asset)
taskmaster_tasks    ──< taskmaster_issues        (issue_task_name, optional)
taskmaster_transactions ──< taskmaster_issues    (issue_transaction_name, optional)
```

---

## `taskmaster_projects`

| Column | Type | Req | Notes |
|---|---|:-:|---|
| `project_name` | Text | **Y** | User-facing title; "unique enough for identification" (not enforced). Delegable `=`/`StartsWith`/`Sort`. |
| `project_manager` | Person | **Y** | Accountable owner. Filter on `.Email`. |
| `project_coverage` | Managed Metadata | N | Coverage term set. |
| `project_description` | Multi-line text | N | Display only — never filter/sort/index. |
| `project_region` | Managed Metadata | **Y** | AMER, EMEA, APAC, JAPAN, GLOBAL. |
| `project_pathway` | Text | N | SharedDrive folder path. |
| `project_type` | Managed Metadata | **Y** | Production, Campaign, Platform, Event, Operational. |
| `project_requestor` | Person | N | Requesting user. |
| `project_phase` | Choice | **Y** | Planning, Active, Blocked, Complete, **Archived**. |
| `project_priority` | Choice | **Y** | Lowest, Low, Moderate, High, Critical. |
| `project_perc_completion` | Number | N | 0–100. "Calculated" by description — **nothing computes it (C3)**. |
| `project_date_start` | Date/Time | N | Default = Created. |
| `project_date_target` | Date/Time | N | Desired completion. |
| `project_date_complete` | Date/Time | N | Set when complete. |
| `project_other_resources` | **Person — MULTI** | N | Contributors. **No delegable filter (C1).** |
| `Created` `Modified` `Created By` `Modified By` | System | — | **Never patch.** |

## `taskmaster_tasks`  ⚠ heaviest list

| Column | Type | Req | Notes |
|---|---|:-:|---|
| `task_name` | Text | **Y** | Task title. |
| `task_project_id` | **Lookup → projects** | **Y** | Parent. Filter `task_project_id.Id = <n>`. |
| `task_description` | Multi-line text | N | Display only. |
| `task_category` | Managed Metadata | N | Marketing taxonomy. |
| `task_status` | **Managed Metadata** | N | Task Status term set. **The most-filtered column in the app — see C2.** |
| `task_priority` | Choice | **Y** | Low, Moderate, High, Critical. |
| `task_lead` | Person | **Y** | Primary owner. Delegable on `.Email`. |
| `task_other_resources` | **Person — MULTI** | N | Contributors. **No delegable filter (C1).** |
| `task_date_start` | **Calculated** | Sys | Derived. **Cannot be filtered, sorted or indexed delegably (C4).** |
| `task_date_target` | Date/Time | N | Due date. |
| `task_date_completion` | Date/Time | N | Set on completion. |
| `task_output_approval` | Lookup → `asset_approval` | N | Approval required for output. |
| `task_output_language` | Choice | N | EN, FR, DE, ES, IT, JP, … |
| `task_output_format` | Managed Metadata | N | Flyer, Email, PDF, Webpage, Deck, Video. |
| `task_output_branding` | Choice | N | Barclays, QIS, EXO, Custom. |
| `task_output_asset` | Lookup → `asset_library` | N | Linked asset. |
| `task_client_name` | Lookup → clients | N | Associated client. |
| `task_product_id` | Lookup → products | N | Associated product. |
| `task_client_stage` | Managed Metadata | N | Prospect, Active, Existing, Post-Trade. |
| `Created` `Modified` `Created By` `Modified By` | System | — | **Never patch.** |

## `taskmaster_transactions`

| Column | Type | Req | Notes |
|---|---|:-:|---|
| `transaction_name` | Text | **Y** | Label. |
| `transaction_project_id` | Lookup → projects | **Y** | Parent. |
| `transaction_client_name` | Lookup → clients | **Y** | Client. |
| `transaction_product_id` | Lookup → products | **Y** | Product. |
| `transaction_sales` | Person | **Y** | Sales owner. |
| `transaction_notional` | **Currency** | N | Positive. Numeric underneath → delegable comparisons, indexable. |
| `transaction_currency` | Choice | **Y** | USD, EUR, GBP, JPY, CHF, … **No normalised USD column (C5).** |
| `transaction_date` | Date/Time | **Y** | Actual trade date. |
| `Created` `Modified` `Created By` `Modified By` | System | — | **Never patch.** |

## `taskmaster_issues`

| Column | Type | Req | Notes |
|---|---|:-:|---|
| `issue_name` | Text | **Y** | Summary. |
| `issue_description` | Multi-line text | N | Display only. |
| `issue_project_id` | Lookup → projects | **Y** | Parent. |
| `issue_task_name` | Lookup → tasks | N | Related task. |
| `issue_transaction_name` | Lookup → transactions | N | Related transaction. |
| `issue_assignee` | Person | **Y** | Resolver. |
| `issue_status` | Choice | N | Open, Review, Waiting, Blocked, Closed. |
| `issue_type` | Choice | N | Approval, Process, Compliance, Branding, Technical. |
| `issue_impact` | Choice | N | Low, Moderate, High, Critical. |
| `issue_date_open` | Date/Time | N | Default = Created. |
| `issue_date_target` | Date/Time | N | Expected resolution. |
| `issue_date_close` | Date/Time | N | Set on closure. |
| `Issue_owner` *(capital I — sic)* | System | — | "Business Owner". Type ambiguous — Author, or a Person column? **Confirm.** |
| `Created` `Modified` `Modified By` | System | — | No `Created By` listed on this list. |

## `taskmaster_clients`

| Column | Type | Req | Notes |
|---|---|:-:|---|
| `client_name` | Text | **Y** | Display name. |
| `client_type` | Managed Metadata | **Y** | Internal taxonomy. |
| `client_coverage` | Managed Metadata | **Y** | Coverage taxonomy. |
| `client_sales` | Person | **Y** | Primary sales owner. |
| `client_region` | Managed Metadata | **Y** | AMER, EMEA, APAC, JAPAN — **no GLOBAL (C6)**. |
| `client_notes` | Multi-line text | N | Display only. |
| `Created` `Modified` `Created By` `Modified By` | System | — | **Never patch.** |

## `taskmaster_products`

| Column | Type | Req | Notes |
|---|---|:-:|---|
| `product_UID` *(capital UID — sic)* | Text | **Y** | Business key (ISIN / Ticker / Internal ID). Uniqueness not enforced. |
| `product_type` | Managed Metadata | **Y** | Product taxonomy. |
| `product_description` | Multi-line text | **Y** | Display only. |
| `Created` `Modified` `Created By` `Modified By` | System | — | **Never patch.** |

## `asset_approval`

| Column | Type | Req | Notes |
|---|---|:-:|---|
| `approval_id` | Text | **Y** | Business key (e.g. MAW, Legal, Compliance, Brand). |
| `approval_region` | **Choice** | **Y** | GLOBAL, AMER, EMEA, APAC, JAPAN — **Choice here, MM elsewhere (C6)**. |
| `approval_status` | Yes/No | N | True = Active. Delegable + indexable. |
| `approval_link` | Hyperlink | N | Display only — never a query key. |
| `Created` `Modified` `Created By` `Modified By` | System | — | **Never patch.** |

## `asset_library` — **not yet supplied**
Referenced by `task_output_asset`. Schema unknown; any binding to it is blocked.

---

# Consequences — what this model costs

Ordered by severity. ❗ = breaks or silently returns wrong results. ⚠ = needs a decision.

## J1 ❗ `taskmaster_tasks` is at 11 of the 12-join limit — and 13 with system fields

Lookup, Person/Group **and** Managed Metadata columns each cost a join, capped at **12 per
view/query**. On tasks:

- **5 Lookups** — `task_project_id`, `task_output_approval`, `task_output_asset`,
  `task_client_name`, `task_product_id`
- **2 Person** — `task_lead`, `task_other_resources`
- **4 Managed Metadata** — `task_category`, `task_status`, `task_output_format`, `task_client_stage`

**= 11.** Add the system Person fields `Created By` + `Modified By` and a view projecting
everything is at **13 — over the limit**, and SharePoint blocks it.

**Consequences:** no single view or query can surface every task column. Keep **Explicit Column
Selection** on (default) so the app fetches only bound columns; build SharePoint views that project
a *subset*; and never add another complex column to tasks without removing one. If tasks needs to
grow, convert fixed-vocabulary MM columns to **Choice** (Choice costs **no join**) — `task_status`,
`task_output_format` and `task_client_stage` are the obvious candidates and would drop the count to 8.

## C1 ❗ Multi-person columns have no delegable filter

`project_other_resources` and `task_other_resources` are **multi-person**. Multi-value columns are
**unsupported for delegation** by the SharePoint connector — any filter touching them evaluates
locally over the first 500/2,000 rows and **silently omits the rest**.

So **"tasks/projects I contribute to" cannot be a server-side query.** Options:
1. Treat them as **display-only**, and drive "mine" off `task_lead` / `project_manager`
   (single-Person, delegable on `.Email`). ← recommended, zero schema change
2. Fixed single-Person slots (`task_resource_1/2/3`) if server-side "am I on it?" is required.
3. A write-time text mirror — but `contains` on it still won't delegate; only exact `=` would.

**No contributor filter will be authored until this is chosen** — there is no correct one.

## C2 ⚠ `task_status` is Managed Metadata — the app's hottest column

Status drives the kanban, "my open tasks", and every count. As MM: **`=` via subfield delegates**
(so per-status kanban columns work), but **`Sort` never delegates**, it **costs a join**, and the
term set is hand-maintained (no CSOM/PnP route here → no sync automation).

**Recommendation: make `task_status` a Choice.** Identical filtering, no join, sortable, and
`tmLookups`-style governance isn't needed for a workflow status. Same argument for
`task_output_format` and `task_client_stage`.

## C3 ⚠ `project_perc_completion` has no writer

Typed **Number** — correct (a *Calculated* column can't be indexed and never delegates). But
nothing computes it: SharePoint won't, and Power Fx can't aggregate server-side. It needs a
**Power Automate rollup** on task change (**Q12**) or it stays blank/stale. Note tasks carry no
per-task completion %, so a rollup must derive from `task_status` values.

## C4 ❗ `task_date_start` is a Calculated column

Calculated columns **cannot be indexed** and **nothing about them delegates**. Any filter or sort
on `task_date_start` (a "my week" view, a timeline, "starting soon") will process only the first
500/2,000 rows and be silently wrong.

**Recommendation: make it a real Date/Time column** written at creation (default = Created, or
copied from the project's start), exactly as `project_date_start` already is.

## C5 ⚠ No normalised-USD column on transactions

`transaction_notional` (Currency) + `transaction_currency` (Choice) with **no `transaction_notional_usd`**.
Mixed-currency values **cannot be meaningfully summed or compared** — and FX-converting inside a
query is neither delegable nor reproducible. Since transactions are the full transaction-level
primary store and notional is the value column, any total is wrong unless every row shares a
currency.

**Recommendation:** add a **`transaction_notional_usd` (Currency/Number)** normalised at write
time, and aggregate on that (in Power BI, or locally over a delegably-filtered set).

## C6 ⚠ `region` is modelled three ways across two domains

| List | Column | Type | Values |
|---|---|---|---|
| `asset_approval` | `approval_region` | **Choice** | GLOBAL, AMER, EMEA, APAC, JAPAN |
| `taskmaster_projects` | `project_region` | **Managed Metadata** | AMER, EMEA, APAC, JAPAN, GLOBAL |
| `taskmaster_clients` | `client_region` | **Managed Metadata** | AMER, EMEA, APAC, JAPAN *(no GLOBAL)* |

One concept, two types, two value sets. A shared region slicer can't treat them uniformly and Power
BI will model them as unrelated dimensions. Recommend one type and one domain.

## C7 ⚠ "Not archived" / "open" have no delegable form

There is no boolean archive flag; `Archived` is a value of the **Choice** `project_phase`. A
`.Value <> "Archived"` predicate is a **Text `<>`** → **does not delegate**. Delegable rewrite:

```powerapps
Filter(taskmaster_projects,
    project_phase.Value = "Planning" || project_phase.Value = "Active"
 || project_phase.Value = "Blocked"  || project_phase.Value = "Complete")
```
Verbose but server-side. Same pattern for open issues on `issue_status`. (A Yes/No `is_archived`
column would be cheaper, indexable, and simpler.)

## C8 ⚠ Casing anomalies and unenforced keys
- **`Issue_owner`** (capital I) and **`product_UID`** (capital UID) break the lowercase convention.
  Formulas must match exactly. Fix before provisioning or accept them permanently.
- **No uniqueness is enforced** anywhere. `approval_id`, `product_UID` and `project_name` are
  business keys by convention only — **join on the built-in `ID`** (always indexed, fastest lookup).

---

# Delegation reference (this model)

| Column kind | Delegates | Does NOT delegate |
|---|---|---|
| Text (`*_name`, `approval_id`, `product_UID`, `project_pathway`) | `=`, `StartsWith`, `Sort` | `<` `>` `<>`, `Search`, `in` |
| Choice (`*_priority`, `project_phase`, `issue_*`, `approval_region`, `transaction_currency`, `task_output_language/branding`) | `=` via `.Value` | **`Sort`**, `StartsWith` on subfield, `<>` |
| Managed Metadata (11 across the model) | `=` via subfield | **`Sort`** · costs a join |
| Lookup (11 across the model) | `=` via `.Id` / `.Value` | **`Sort`** · costs a join |
| Person — single | `=` on `.Email` / `.DisplayName` | other subfields, **`Sort`** · costs a join |
| **Person — multi** (`*_other_resources`) | **nothing** | **unsupported — C1** |
| Date/Time (`*_date_*`) | `=` `<` `>` `<=` `>=`, `Sort` | arithmetic in the predicate |
| Number / Currency (`project_perc_completion`, `transaction_notional`) | `=` `<` `>` `<=` `>=`, `Sort` | — |
| Yes/No (`approval_status`) | `=`, `Sort` | — |
| **Calculated** (`task_date_start`) | **nothing** | **everything — C4** |
| Multi-line text (`*_description`, `client_notes`) | **nothing** | not filterable/indexable |
| Hyperlink (`approval_link`) | **nothing** | display only |
| System (`Created`, `Modified`, `Created By`, `Modified By`) | — | **never patch** |

**Aggregates never delegate to SharePoint** (`Sum`, `Average`, `CountRows`, `CountIf`, `Max`,
`Min`). Filter delegably to a bounded set, then aggregate locally — or aggregate in Power BI.

**Writing Lookup and Person columns** — records, never scalars:
```powerapps
// Lookup
task_project_id: { '@odata.type': "#Microsoft.Azure.Connectors.SharePoint.SPListExpandedReference",
                   Id: gSelProject.ID, Value: gSelProject.project_name }
// Person
task_lead: { '@odata.type': "#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser",
             Claims: "i:0#.f|membership|" & Lower(gUserEmail),
             DisplayName: …, Email: … }
```

**Index early** (mandatory >5,000 items; can't be added past 20,000):
`task_project_id`, `task_status`, `task_lead`, `task_date_target` ·
`project_phase`, `project_manager`, `project_name`, `project_date_target` ·
`transaction_project_id`, `transaction_date`, `transaction_client_name` ·
`issue_project_id`, `issue_status`, `issue_assignee` ·
`client_name`, `client_region` · `product_UID` · `approval_id`, `approval_status`.
