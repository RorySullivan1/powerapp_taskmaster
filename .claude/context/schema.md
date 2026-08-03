# Data model — shape, costs and consequences

**The column-by-column truth is `schema/schema.yaml` — the golden source.** That file *defines*
the SharePoint lists; SharePoint is the downstream apply-target. Never restate its columns here,
and never bind a formula to a column that isn't in it.

This brief carries what the YAML can't: the model's **shape**, what its type choices **cost** in
delegation and joins, and the **open consequences** that still need decisions. The *how-to* of
list design is the **`sharepoint-list-architecture`** skill; the full delegation matrix is
`power-fx-development/delegation.md`.

**Naming: snake_case** (user-confirmed 2026-08-02), superseding the earlier PascalCase `tm*`
design. **Internal names freeze at creation** — the YAML's `name:` key *is* the internal name.

## The lists

| List | Role | Join cost |
|---|---|:-:|
| `taskmaster_projects` | The parent — everything hangs off it | 6 |
| `taskmaster_tasks` | Units of work; the busiest list | 8 |
| `taskmaster_transactions` | Trades, full transaction level | 4 |
| `taskmaster_issues` | Freeform issues | 5 |
| `taskmaster_clients` | Client dimension | 4 |
| `taskmaster_products` | Product reference | 1 |
| `asset_approval` | Approval reference | 0 |
| `asset_library` | **Schema never supplied — bindings blocked** | ? |

**Relationships** — all via SharePoint **Lookup** columns, which Power Fx sees as *records*
(`.Id` / `.Value`), never integers:

```
taskmaster_projects ──< taskmaster_tasks         (task_project_id, required)
                    ──< taskmaster_transactions  (transaction_project_id, required)
                    ──< taskmaster_issues        (issue_project_id, required)

taskmaster_clients  ──< taskmaster_tasks         (task_client_name)
                    ──< taskmaster_transactions  (transaction_client_name, required)
taskmaster_products ──< taskmaster_tasks         (task_product_id)
                    ──< taskmaster_transactions  (transaction_product_id, required)
asset_approval      ──< taskmaster_tasks         (task_output_approval)
asset_library       ──< taskmaster_tasks         (task_output_asset)   ← blocked
taskmaster_tasks    ──< taskmaster_issues        (issue_task_name)
taskmaster_transactions ──< taskmaster_issues    (issue_transaction_name)
```

**Task health vs stage** — two orthogonal Choice columns, decided 2026-08-02:

| Column | Axis | Values |
|---|---|---|
| `task_status` | **Health** — how it's going | `Green`, `Amber`, `Red` |
| `task_stage` | **Lifecycle** — where it is | `Not Started`, `Planning`, `Drafting`, `Under Review`, `Finalizing`, `Complete`, `Archived` |

Health drives the RAG pill; stage drives the kanban columns. Both are Choice → **no join cost,
delegable `=`, and sortable** (Managed Metadata was neither).

---

# The two hard limits this model lives under

## Joins — 12 per view, and three types spend them

**Lookup, Person/Group and Managed Metadata each cost one join.** Choice, Text, Number, Date and
Yes/No cost **nothing**. `taskmaster_tasks` is the list to watch:

- 5 Lookup + 2 Person + 1 Managed Metadata = **8**, or **10** once the system `Created By` /
  `Modified By` Person fields are projected. Cap is 12 → two columns of headroom.

*(Before the 2026-08-02 Choice conversion it was 11, reaching 13 with system fields — over the cap,
which would have blocked any view projecting every task column.)*

**Rule:** prefer **Choice** for any fixed vocabulary. Reserve Lookup for genuine cross-list
references, and Managed Metadata only for taxonomies actually governed centrally across sites.

## Delegation — by column kind

| Kind | Delegates | Does **not** |
|---|---|---|
| Text | `=`, `StartsWith`, `Sort` | `<` `>` `<>`, `Search`, `in` |
| Choice | `=` via `.Value`, `Sort` on `.Value` | `StartsWith` on subfield, `<>` |
| Managed Metadata | `=` via subfield | **`Sort`** · costs a join |
| Lookup | `=` via `.Id` / `.Value` | **`Sort`** · costs a join |
| Person (single) | `=` on `.Email` / `.DisplayName` | other subfields, `Sort` · costs a join |
| Person (multi) | **nothing** | **everything** — no column uses this type any more (C1 resolved) |
| DateTime · Number · Currency | `=` `<` `>` `<=` `>=`, `Sort` | arithmetic inside the predicate |
| Yes/No | `=`, `Sort` | — |
| Calculated | **nothing** | **everything** — no column uses this type any more (C4 resolved) |
| Note (multi-line) · Hyperlink | **nothing** | not filterable, sortable or indexable |

**Aggregates never delegate to SharePoint** (`Sum`, `Average`, `CountRows`, `CountIf`, `Max`,
`Min`). The pattern: filter delegably down to a bounded set, *then* aggregate locally — or
aggregate in Power BI.

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

## The `Or`-of-equals pattern (needed constantly here)

Nothing in this model has a boolean "is archived" flag — terminal states are *values* of a Choice.
A `<>` against a Choice's `.Value` is a **Text `<>`**, which does **not** delegate. So enumerate
the wanted values instead:

```powerapps
// Open tasks — delegable
Filter(taskmaster_tasks,
    task_stage.Value = "Not Started"  || task_stage.Value = "Planning"
 || task_stage.Value = "Drafting"     || task_stage.Value = "Under Review"
 || task_stage.Value = "Finalizing")

// Open issues — delegable
Filter(taskmaster_issues,
    issue_status.Value = "Open"    || issue_status.Value = "Review"
 || issue_status.Value = "Waiting" || issue_status.Value = "Blocked")
```

Verbose, but it runs server-side. (A Yes/No `is_archived` column would be cheaper and indexable —
worth considering now that the schema is ours to edit.)

---

# Open consequences

Each is tracked in `schema/schema.yaml` → `open_recommendations`, and flagged inline on the
affected column via a `review:` key. Now that the repo is the golden source, these are **editable
decisions**, not fixed constraints.

**C1 ✅ Resolved 2026-08-03.** The multi-person columns became **single** Person columns —
`task_supporter` and `project_supporter` (one extra person beside `task_lead` / `project_manager`).
Both are indexed. **"Mine" is now fully delegable**, because single Person `=` on `.Email` and `Or`
both delegate:

```powerapps
Filter(taskmaster_tasks, task_lead.Email = gUserEmail || task_supporter.Email = gUserEmail)
```

No join cost changed (multi and single Person each cost 1), so tasks stays at 8. The trade is a
hard cap of two people per task — accepted as sufficient.

**C3 ✅ Resolved 2026-08-03 — weighted stage rollup, written app-side.**
`project_perc_completion` is the **mean stage-weight across a project's tasks**, not a done/total
count. Weights (`schema.yaml` → `rollups:`, mirrored as the `StageWeights` named formula in
`src/patches/App.Formulas.pa.fx`): `Not Started` 0 · `Planning` 10 · `Drafting` 35 ·
`Under Review` 60 · `Finalizing` 85 · `Complete` 100 · **`Archived` excluded** from numerator *and*
denominator.

**The app is the writer** — it recomputes and patches the parent whenever a task's stage changes
(task form `OnSuccess`, kanban drop, grid save). The canonical snippet lives beside `StageWeights`.
Two properties of that snippet are load-bearing:

- **Archived is excluded server-side by enumeration**, not by `<>`. The filter lists the six
  non-archived stages as an `Or` of `=`; `task_stage.Value <> "Archived"` is a Text `<>` and would
  **not** delegate. Tasks with a blank stage match nothing and are omitted.
- **`Average`/`CountRows` run locally** over the already-narrowed page — correct because the
  `Filter` reduces to one project first (indexed FK). Exact so long as a project holds fewer tasks
  than the data row limit (set it to 2,000).

**Known cost of app-side:** a stage edited directly in SharePoint, or bulk-imported, leaves the
value stale until the next in-app change to that project. Accepted.

**C4 ✅ Resolved 2026-08-03.** `task_date_start` is now a real **DateTime**, indexed, written at
creation — so "my week", timelines and "starting soon" filters delegate and sort correctly. No
column in the model is Calculated any more.

**C5 ✅ Resolved 2026-08-03.** `transaction_notional_usd` (Currency, indexed) is now in the model,
normalised **at write time**. It is the **only** column safe to aggregate across currencies —
`transaction_notional` is denominated in `transaction_currency` and must never be summed across
rows. Never FX-convert inside a query: it neither delegates nor reproduces.

**C6 ✅ By design 2026-08-03 — not a defect.** The three region columns serve **different
purposes** and are **never used in the same setting**: `approval_region` is deliberately
**broad-stroke**, while `project_region` and `client_region` carry the granularity their consumers
need. So the divergence in type and value set is intentional, and no conformed dimension is
required.

**Operational consequence** (not a problem, just a rule): don't build a single cross-model region
slicer, and read each with its own idiom — `approval_region.Value` (Choice) versus the Managed
Metadata subfield on projects/clients. In Power BI, model them as **separate dimensions**; don't
try to relate them.

**C10 ◐ Managed Metadata stays — cascading term picker validated 2026-08-03.**
`project_region` and `project_type` are **required** MM, so no project can be created from the app
without a way to write MM. Decision: **keep MM**, and build a cascading picker that walks the term
hierarchy and writes the leaf term's **GUID**.

Validated (full write-up + sources: `docs/managed-metadata-picker.md`):
- **Reading the hierarchy is first-party supported.** Graph's **termStore** API (GA Aug 2021)
  exposes `…/termStore/sets/{set}/children` and `…/terms/{term}/children`, so nesting detection
  falls out of the API — non-empty children means render another level. Permission is
  `TermStore.Read.All`, **delegated only; app-only is not supported.**
- **The earlier "Graph doesn't support managed metadata" note still stands but is narrower than it
  read:** it applies to the *list column value*, not the term store. Read terms with Graph, write
  the column with the SharePoint connector.
- **Writing** uses `'@odata.type': "#Microsoft.Azure.Connectors.SharePoint.SPListExpandedTaxonomy"`
  with `TermGuid`, `Label`, `Path` and **`WssId: -1`** (resolve by GUID, not site cache). This shape
  is **community-confirmed, not first-party** — the single riskiest construct in the app.

Recommended architecture: **cache the term store into a flat `taskmaster_terms` list** (a scheduled
flow walks Graph), and drive the cascade from delegable `Filter`s on `term_parent_guid`. That keeps
the create form's runtime dependency at zero, versus a flow round-trip per dropdown level.

**Blocked on:** a term source — Power Automate or a custom connector (**Q12**), now blocking rather
than optional. **Cheapest first test:** one button that patches a single hard-coded `TermGuid` — if
it writes, the design is unblocked for one paste instead of a whole create flow.

**C8 ✅ Resolved 2026-08-03 (casing).** Renamed to **`issue_owner`** (a real Person column,
distinct from `Created By`) and **`product_uid`**. The whole model is now consistently lowercase
snake_case.
**Still true:** no uniqueness is enforced anywhere — `approval_id`, `product_uid` and
`project_name` are business keys **by convention only**. Join on the built-in `ID`, which is always
indexed and the fastest possible lookup.

---

## Indexing

Create indexes **early** — mandatory above 5,000 items, and they cannot be added once a list passes
20,000. The `indexed: true` flags in `schema/schema.yaml` are authoritative; the shortlist:

- **tasks** — `task_project_id`, `task_stage`, `task_status`, `task_lead`, `task_date_start`, `task_date_target`, `task_name`
- **projects** — `project_phase`, `project_manager`, `project_name`, `project_region`, `project_date_target`
- **transactions** — `transaction_project_id`, `transaction_client_name`, `transaction_date`, `transaction_notional_usd`, `transaction_name`
- **issues** — `issue_project_id`, `issue_status`, `issue_assignee`, `issue_date_target`, `issue_name`
- **clients** — `client_name`, `client_region` · **products** — `product_uid` ·
  **approval** — `approval_id`, `approval_status`
