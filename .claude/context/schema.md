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
| ~~`asset_approval`~~ | **RETIRED 2026-08-09** — approvals moved to an external portal; tasks now hold a free-text `task_output_approval_id`. Deprovision in SharePoint. | — |
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
asset_library       ──< taskmaster_tasks         (task_output_asset)   ← blocked
(asset_approval retired 2026-08-09 — task_output_approval_id is now a free-text id, not a lookup)
taskmaster_tasks    ──< taskmaster_issues        (issue_task_name)
taskmaster_transactions ──< taskmaster_issues    (issue_transaction_name)
```

**Task health vs stage** — two orthogonal Choice columns, decided 2026-08-02:

| Column | Axis | Values |
|---|---|---|
| `task_status` | **Health** — how it's going. **DERIVED, never picked** | `Green`, `Amber`, `Red` |
| `task_stage` | **Lifecycle** — where it is | `Not Started`, `Planning`, `Drafting`, `Finalizing`, `Complete` |
| `issue_status` | **Lifecycle + outcome** | `Open`, `Closed - Resolved`, `Closed - Unresolved`, `Closed - No Change` |

> **Changed 2026-08-12.** `task_stage` lost `Under Review` (review is signalled by raising an
> **issue**) and `Archived` (archiving is a **project** state — `project_phase`). That removed the
> task-level archiving axis altogether. `issue_status` lost its three intermediate states and
> split `Closed` into an outcome.

Health drives the RAG pill; stage drives the kanban columns. Both are Choice → **no join cost,
delegable `=`, and sortable** (Managed Metadata was neither).

> **Health became derived (#22).** `scrTaskEdit` has no health control. It is computed in two
> halves that are deliberately **not stored together** — see `rollups.task_health` in
> `schema/schema.yaml` for the rules:
> - **Stored** in `task_status`: from the task's **open issues**. An open issue typed
>   `Blockage`/`Exception`/`Limitation`, or of `Critical` impact → `Red`; any other open issue →
>   `Amber`; none → `Green`. Recomputed wherever a task's open-issue set can change.
> - **Live, never stored**: *not Completed AND past `task_date_target`* → `Red`. It changes with
>   no write — a task turns red at midnight — so a stored copy could only be as fresh as the last
>   save. `task_date_target` is on the task row, so folding it in at read time costs no join.
>
> **Consequence: a reader that shows `task_status` raw will under-report `Red`.** Today only
> `scrReports` reads it, and it folds overdue in.

## Constraints SharePoint cannot hold

Some rules are conditional on *another* field, and a SharePoint column can only be required or
not. Those rules live in the app, which means **the list will happily accept a row that violates
them** — anything writing outside `scrTaskEdit` bypasses them entirely.

- **`task_output_approval_flag` → `task_output_approval_id`.** A task whose Output section is on
  must carry an audience. Separately, a task whose approval flag is on must carry an approval id
  **before it can reach stage `Completed`**. The flag is set per task; the audience VALUE gates
  nothing. The id is deliberately *not* demanded earlier — the external approval portal issues it
  late in the lifecycle, so requiring it at draft time would block ordinary work. All three
  columns stay `required: false` in the golden source; `scrTaskEdit`'s `lblTkMissing` is the only
  enforcement.

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
aggregate outside the app.

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
// Open issues — delegable, and a SINGLE equality since 2026-08-12
Filter(taskmaster_issues, issue_status.Value = "Open")

// Not-yet-complete tasks — enumerate the wanted stages rather than `<> "Complete"`
Filter(taskmaster_tasks,
    task_stage.Value = "Not Started" || task_stage.Value = "Planning"
 || task_stage.Value = "Drafting"    || task_stage.Value = "Finalizing")
```

**Archived work is excluded AT THE SOURCE (2026-08-12).** Each child list carries a denormalised
`*_project_archived` Boolean mirroring its parent's `project_phase`, indexed, maintained by
scrProjectEdit's save. That is what makes "belongs to a live project" a delegable `= false` instead
of a join — and a join is the only alternative, since a child row does not carry its parent's phase.
The aim is a threshold one: **keep the rows in scope under 2000 so no query can silently truncate.**
A local `RemoveIf` cannot serve that, because the rows are fetched before they are dropped.

**The archived-exclusion chains are GONE, and not because they were verbose.** `task_stage` has no
`Archived` value any more, so a chain enumerating the "live" stages selects everything — and would
silently drop any row with a blank stage. Archiving is a **project** state, and a task/transaction/
issue does **not** carry its parent's phase, so it cannot be excluded server-side at all without a
join. The three cross-project child loads collect `ArchivedProjects` and `RemoveIf` locally; every
other child query is already scoped to one project. See `App.Formulas`.

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
count. Weights (`schema.yaml` → `rollups:`, mirrored as the `gStageWeights` named formula in
`src/App.pa.yaml`): `Not Started` 0 · `Planning` 10 · `Drafting` 35 ·
`Finalizing` 85 · `Complete` 100. `Under Review` (60) and `Archived` (excluded) went with the
stages themselves on 2026-08-12; **the survivors keep their original numbers on purpose**, so stored
percentages stay comparable — at the cost of a 35 → 85 jump. **Nothing is excluded any more**, so
every task under a project counts in both numerator and denominator.

**The app is the writer** — it recomputes and patches the parent whenever a task's stage changes
(task form `OnSuccess`, kanban drop, grid save). The canonical snippet lives beside `gStageWeights`.
Two properties of that snippet are load-bearing:

- **There is no stage filter at all any more.** It listed the six non-archived stages as an `Or`
  of `=` (because `task_stage.Value <> "Archived"` is a Text `<>` and would **not** delegate) — but
  `task_stage` lost its `Archived` value on 2026-08-12, so every task under the project counts.
  The rollup filter is now just the indexed FK. Archiving is a **project** state; see above.
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
the app stores only `transaction_notional` + `transaction_currency`, and something downstream converts against
an FX dimension keyed on currency and trade date.

Why the reversal: a write-time rate **freezes** whatever number the app happened to hold on the day
of the trade, and nothing downstream can ever correct it — a wrong rate becomes permanent history.
Report-time conversion can be restated, back-dated and audited. The app also had no FX source, so
the rates were a static table that would silently go stale.

**Consequence, and it is real: no cross-currency figure can be shown anywhere in the app.**
`transaction_notional` is denominated in `transaction_currency` and must never be summed across
rows. `scrProject`'s transactions tab therefore totals **per currency** and labels itself as such.
Never FX-convert inside a query either: it neither delegates nor reproduces.

**CROSS-CURRENCY CONVERSION IS OUT OF SCOPE (user, 2026-08-17) and is handled by other tools outside this project. No blended figure is owed anywhere.** It needs an FX dimension (currency, rate, effective date) and a
measure converting at the trade date. Until that exists there is no blended notional anywhere —
that is the accepted cost of the decision, not an oversight.

**C6 ✅ By design 2026-08-03; narrowed 2026-08-09.** Region was modelled three ways; the broad-stroke
`approval_region` was **retired with the `asset_approval` list on 2026-08-09**. The remaining two —
`project_region` and `client_region` — serve **different purposes** and are **never used in the same
setting**, so the divergence in type and value set is intentional and no conformed dimension is required.

**Operational consequence** (not a problem, just a rule): don't build a single cross-model region
slicer. `project_region` and `client_region` are Managed Metadata subfields; downstream model them
as **separate dimensions** and don't try to relate them.

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
**Still true:** no uniqueness is enforced anywhere — `product_uid` and `project_name` are business
keys **by convention only**. Join on the built-in `ID`, which is always indexed and the fastest
possible lookup.

---

## Indexing

Create indexes **early** — mandatory above 5,000 items, and they cannot be added once a list passes
20,000. The `indexed: true` flags in `schema/schema.yaml` are authoritative; the shortlist:

- **tasks** — `task_project_id`, `task_stage`, `task_status`, `task_lead`, `task_date_start`, `task_date_target`, `task_name`
- **projects** — `project_phase`, `project_manager`, `project_name`, `project_region`, `project_date_target`
- **transactions** — `transaction_project_id`, `transaction_client_name`, `transaction_date`, `transaction_name`
- **issues** — `issue_project_id`, `issue_status`, `issue_assignee`, `issue_date_target`, `issue_name`
- **clients** — `client_name`, `client_region` · **products** — `product_uid`
  <!-- asset_approval retired 2026-08-09 — approval_id/approval_status indexes no longer apply -->
