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

**C5 ⟲ Reversed 2026-08-03 (Q14) — conversion moved to the REPORT layer.**
`transaction_notional_usd` was briefly added and normalised at write time. It is now **dropped**:
the app stores only `transaction_notional` + `transaction_currency`, and Power BI converts against
an FX dimension keyed on currency and trade date.

Why the reversal: a write-time rate **freezes** whatever number the app happened to hold on the day
of the trade, and nothing downstream can ever correct it — a wrong rate becomes permanent history.
Report-time conversion can be restated, back-dated and audited. The app also had no FX source, so
the rates were a static table that would silently go stale.

**Consequence, and it is real: no cross-currency figure can be shown anywhere in the app.**
`transaction_notional` is denominated in `transaction_currency` and must never be summed across
rows. `scrProject`'s transactions tab therefore totals **per currency** and labels itself as such.
Never FX-convert inside a query either: it neither delegates nor reproduces.

**Power BI now owes this figure.** It needs an FX dimension (currency, rate, effective date) and a
measure converting at the trade date. Until that exists there is no blended notional anywhere —
that is the accepted cost of the decision, not an oversight.

**C6 ✅ By design 2026-08-03 — not a defect.** The three region columns serve **different
purposes** and are **never used in the same setting**: `approval_region` is deliberately
**broad-stroke**, while `project_region` and `client_region` carry the granularity their consumers
need. So the divergence in type and value set is intentional, and no conformed dimension is
required.

**Operational consequence** (not a problem, just a rule): don't build a single cross-model region
slicer, and read each with its own idiom — `approval_region.Value` (Choice) versus the Managed
Metadata subfield on projects/clients. In Power BI, model them as **separate dimensions**; don't
try to relate them.

**C10 ✅ Resolved 2026-08-03 — MM stays, and the app reads the term store directly.**
`project_region` and `project_type` are **required** MM, so without an MM write path no project can
be created from the app at all. Full write-up and sources: `docs/managed-metadata-picker.md`.

**`Choices([@list].mmColumn)` returns the term set from the term store**, each record carrying
`Label`, **`Path`**, `Guid`, `WssId` — and `Path` is the term's **full hierarchical path**
(`EMEA;UK;London`). The hierarchy is therefore already in the data: the cascade is prefix matching
on a string (`StartsWith(childPath, parentPath & ";")`), depth is discovered rather than declared,
and nothing needs to be precomputed or mirrored.

**The value written is the connector's OWN record**, found by the path the picker resolved:

```powerapps
project_region: LookUp( Choices([@taskmaster_projects].project_region), Path = gPrRegionPath )
```

That retires the hand-built `SPListExpandedTaxonomy` literal (community-reported, never first-party,
`WssId: -1`) that had been the least-proven construct in the app. Nothing we author names a GUID
field any more, which also sidesteps a live `Guid` vs `TermGuid` ambiguity in the sources.

**A `taskmaster_terms` cache list was briefly added and has been removed.** It was a second copy of
a vocabulary that already exists — refresh schedule, seeding step, drift risk — to reconstruct a
hierarchy `Path` provides for free. The delegation argument for it doesn't hold either: a term set
small enough to use is small enough to hold in memory.

**The one real limit: `Choices()` on an MM column is capped at 20 terms** by the connector, not
configurable. If a set outgrows that, the screen swaps one binding for a collection filled by a
single Power Automate call in the same `{Label, Path}` shape — the component is unchanged, and the
collection is in memory, not a list that can drift.

**Open detail:** the `Path` delimiter is reported as `;` but isn't first-party documented, so it is
a `PathDelimiter` input on the component, which prints a raw path on screen. First paste settles it.

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
- **transactions** — `transaction_project_id`, `transaction_client_name`, `transaction_date`, `transaction_name`
- **issues** — `issue_project_id`, `issue_status`, `issue_assignee`, `issue_date_target`, `issue_name`
- **clients** — `client_name`, `client_region` · **products** — `product_uid` ·
  **approval** — `approval_id`, `approval_status`
