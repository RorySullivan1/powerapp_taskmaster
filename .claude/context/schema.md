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
| **Person (multi)** | **nothing** | **everything — C1** |
| DateTime · Number · Currency | `=` `<` `>` `<=` `>=`, `Sort` | arithmetic inside the predicate |
| Yes/No | `=`, `Sort` | — |
| **Calculated** | **nothing** | **everything — C4** |
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

**C1 ❗ Multi-person has no delegable filter.** `project_other_resources` and
`task_other_resources` are multi-person; multi-value columns are unsupported for delegation, so any
filter touching them silently processes only the first 500/2,000 rows. **"Tasks I contribute to"
cannot be a server-side query.** Options: display-only (drive "mine" off `task_lead` /
`project_manager` — recommended, no schema change); fixed single-Person slots; or a write-time text
mirror (exact `=` only). *No contributor filter will be authored until this is settled.*

**C3 ⚠ `project_perc_completion` has no writer.** Typed Number, which is correct — a *Calculated*
column can't be indexed and never delegates. But nothing computes it: SharePoint won't, and Power
Fx can't aggregate server-side. Needs a Power Automate rollup on task change (Q12), manual entry,
or removal. Note tasks carry no per-task %, so a rollup must derive from `task_stage`.

**C4 ❗ `task_date_start` is Calculated.** Cannot be indexed, and *nothing* about it delegates —
so any "my week", timeline, or "starting soon" filter/sort is silently wrong past the row limit.
**Recommend converting to a real DateTime** written at creation, exactly as `project_date_start`
already is.

**C5 ⚠ No USD-normalised notional.** `transaction_notional` + `transaction_currency` with no
`transaction_notional_usd`. Mixed-currency values can't meaningfully be summed or compared, and
FX-converting inside a query is neither delegable nor reproducible. **Recommend adding
`transaction_notional_usd`**, normalised at write time (a commented-out stub sits in the YAML).

**C6 ⚠ `region` is modelled three ways.** Choice on `asset_approval` (with `GLOBAL`), Managed
Metadata on `taskmaster_projects` (with `GLOBAL`) and on `taskmaster_clients` (**without**). One
concept, two types, two domains — a shared slicer can't treat them uniformly and Power BI will
model them as unrelated dimensions.

**C8 ⚠ Casing anomalies and unenforced keys.** `Issue_owner` (capital I) and `product_UID` (capital
UID) break the lowercase convention; formulas must match exactly, so **fix them before creation** —
names freeze then. `Issue_owner` is also typed "System" in the source doc: confirm whether it's a
real Person column or just `Created By`. No uniqueness is enforced anywhere, so `approval_id`,
`product_UID` and `project_name` are business keys **by convention only** — join on the built-in
`ID`, which is always indexed and the fastest possible lookup.

---

## Indexing

Create indexes **early** — mandatory above 5,000 items, and they cannot be added once a list passes
20,000. The `indexed: true` flags in `schema/schema.yaml` are authoritative; the shortlist:

- **tasks** — `task_project_id`, `task_stage`, `task_status`, `task_lead`, `task_date_target`, `task_name`
- **projects** — `project_phase`, `project_manager`, `project_name`, `project_region`, `project_date_target`
- **transactions** — `transaction_project_id`, `transaction_client_name`, `transaction_date`, `transaction_name`
- **issues** — `issue_project_id`, `issue_status`, `issue_assignee`, `issue_date_target`, `issue_name`
- **clients** — `client_name`, `client_region` · **products** — `product_UID` ·
  **approval** — `approval_id`, `approval_status`
