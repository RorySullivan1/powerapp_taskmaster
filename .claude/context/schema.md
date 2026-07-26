# Data model — the eight `tm*` SharePoint lists

Reference for the SharePoint-list backend behind the EQD desk-work Power App. This brief is
the **concrete instance**: which lists and columns exist, their types, and the decisions
behind them. The *how-to* of list design — column-type trade-offs, the 5,000-item threshold,
indexing playbook, the 12-join wall — is the **`sharepoint-list-architecture`** skill; the
delegation rules the column types serve are **`power-fx-development`** (matrix in its
`delegation.md`). This doc does not re-teach those; it records what *this* model is and why.

> **Provisioning is manual (SharePoint UI).** Internal names are therefore **not yet known**
> and are at risk of `_x0020_` mangling. Every "internal name" below is marked **⟨capture⟩**
> until the column is actually created; the **schema snapshot** (`schema/` + this doc) must
> then record the **true** internal name, not the intended one. See `open-questions.md` and
> the `pull-reconcile` command's internal-name cross-check. Set clean internal names at
> creation (create the column named simply, then rename the display label) — the internal
> name is frozen at creation and every formula, view, and Graph/Power Query call binds to it.

## Shape of the model

A **Project is the parent.** Three *different kinds* of record hang off it — they are **not**
variants of one thing (see `decisions` in `.claude/memory/`):

| | What it is | Status | Assigned | Drives progress |
|---|---|:-:|:-:|:-:|
| **Task** | a unit of work | ✓ | ✓ | ✓ (the only roll-up) |
| **Ticket** | a trade — numerical | lifecycle only | ✗ | ✗ |
| **Issue** | freeform information | light | optional | ✗ |

Three lists, not one discriminated list. Only **Tasks** roll up into completion; Tickets and
Issues surface *alongside*, never inside. There is **no snapshot/metrics list** — Power BI
imports the lists whole, so the reason one would exist is gone; do not reintroduce it.

## Cross-cutting policies (apply to every list)

- **Keys derive from the built-in `ID`.** e.g. `TaskKey = ProjectKey & "-T-" & ID`, patched in
  a **second write** (SharePoint has no atomic increment; a per-project counter races).
- **Column-type policy** (follows from delegation): **Text** for anything sorted, plus a
  **Number rank** column where ordered sort matters (Text sorts delegably but Choice/Person do
  not); **Choice** only where filtered and never sorted; **Person** for people, filtered on
  `.Email`; **no Lookup columns at all** — integer FKs to the built-in `ID`, joined
  client-side. **No Managed Metadata** columns (see below).
- **Person columns** are patched as a full record with lowercase **`Claims`**
  (`"i:0#.f|membership|" & Lower(email)`), never an email string (silent failure otherwise).
  Bind pickers to **Office365Users**. `Author` and `Created` are **system fields — never
  patch them.** (Patching *mechanics* live in `power-fx-development`.)
- **Index every column used in a filter or sort.** Mandatory above 5,000 items. Set the app's
  **Data row limit to 2,000** — a ceiling to stay under, not a budget to spend.
- **Denormalisation is deliberate and minimal.** `OwnerEmailTxt` exists only because Person
  can't sort. `BusinessUnit` lives on **projects alone** (the in-app-aggregation
  denormalisations were removed with the snapshot list).

> **Decision in force — full ticket-level rows as the primary store** (approved 2026-07-26).
> `tmTickets` holds every trade row and drives figures directly. Consequence: it is the list
> most exposed to the 5,000-threshold and to delegation — **indexing is mandatory** on its
> filter/sort columns, and every query against it must be delegable. See `open-questions.md`
> Q9 (scale) — sizing at 12/36 months is still open and directly governs the index plan.

---

## `tmProjects` — the parent (small; reference/parent list)

| Column (display) | Internal | Type | Indexed | Notes / decision |
|---|---|---|:-:|---|
| Title | `Title` | Text | yes | Project name (built-in Title, repurposed). |
| ProjectKey | ⟨capture⟩ | Text | yes | Human key; unique by convention. |
| Status | ⟨capture⟩ | Choice | – | Filtered, not sorted. |
| Health | ⟨capture⟩ | Choice | – | |
| Priority | ⟨capture⟩ | Choice | – | Paired with a rank for ordered sort. |
| PriorityRank | ⟨capture⟩ | Number | – | Sortable rank behind Priority. |
| Workstream | ⟨capture⟩ | Choice | – | |
| **BusinessUnit** | ⟨capture⟩ | Text (from lookups, not free text) | yes | **Primary reporting dimension.** Sourced from a controlled list (see Q3 — can a project span two? if so this needs its own list + junction). Lives on projects only. |
| Owner | ⟨capture⟩ | Person | – | Filter on `.Email`. |
| StartDate | ⟨capture⟩ | Date | – | |
| TargetDate | ⟨capture⟩ | Date | – | |
| Description | ⟨capture⟩ | Multi-line text | – | Display only; never filtered. |
| IsArchived | ⟨capture⟩ | Yes/No | yes | Delegable boolean for "not archived" filters (Text `<>` doesn't delegate). |
| SortOrder | ⟨capture⟩ | Number | – | Manual ordering. |
| *(optional)* rollup counters | ⟨capture⟩ | Number | – | Write-time counters for in-app progress bars, **if** Power Automate is available (Q12). Not a substitute for Power BI. |

## `tmTasks` — the only work items (large; child)

Always set `ProjectId`. Two fixed backup columns (not one multi-person column): multi-select
Person is unsupported, and a delimited email column needs a `contains` match, which doesn't
delegate — but **`Or` does**, so *owner-or-backup* stays one server-side query.

| Column (display) | Internal | Type | Indexed | Notes / decision |
|---|---|---|:-:|---|
| Title | `Title` | Text | – | Task summary. |
| TaskKey | ⟨capture⟩ | Text | yes | `ProjectKey & "-T-" & ID`, second write. |
| **ProjectId** | ⟨capture⟩ | Number (FK→`ID`) | **yes** | Always set; the parent link (client-side join). |
| **TicketId** | ⟨capture⟩ | Number (FK→`ID`) | yes | Optional — the transaction this work services; **`0` = project level.** (Q6: can a task serve >1 ticket? this assumes one.) |
| ParentTaskId | ⟨capture⟩ | Number (FK→`ID`) | – | One level of same-type nesting **only**. |
| Status | ⟨capture⟩ | Choice | **yes** | Primary filter. |
| StatusRank | ⟨capture⟩ | Number | – | Ordered sort behind Status. |
| Priority / PriorityRank | ⟨capture⟩ | Choice / Number | – | |
| **Owner / BackupPrimary / BackupSecondary** | ⟨capture⟩ | Person ×3 | Owner: yes | All Person. "My open tasks" = `Owner.Email = me OR BackupPrimary.Email = me OR BackupSecondary.Email = me` (delegable `Or`). |
| OwnerEmailTxt | ⟨capture⟩ | Text | yes | **Denormalised** — only because Person can't sort. |
| DueDate / StartDate / CompletedDate | ⟨capture⟩ | Date ×3 | DueDate: **yes** | Date range filters delegate; index DueDate. |
| EstimateHours / ActualHours / PercentComplete | ⟨capture⟩ | Number ×3 | – | PercentComplete drives the Task roll-up. |
| Description | ⟨capture⟩ | Multi-line text | – | Display only. |
| Tags | ⟨capture⟩ | Text | – | |
| IsArchived | ⟨capture⟩ | Yes/No | yes | |
| SortOrder | ⟨capture⟩ | Number | – | |

## `tmTickets` — trades (**large, primary transactional store**)

The only value columns are Notional/Currency/NotionalUSD. **Normalise USD at write time** —
FX-converting in a query is neither delegable nor reproducible. `SalesRep` (commercial
attribution) is distinct from `Author` (who keyed it in).

| Column (display) | Internal | Type | Indexed | Notes / decision |
|---|---|---|:-:|---|
| Title | `Title` | Text | – | |
| TicketRef | ⟨capture⟩ | Text | yes | Points at the real booking system. |
| ProjectId | ⟨capture⟩ | Number (FK) | **yes** | |
| ClientId | ⟨capture⟩ | Number (FK→`tmClients.ID`) | yes | |
| **SalesRep** | ⟨capture⟩ | Person | – | Commercial attribution; ≠ `Author`. |
| InstrumentType | ⟨capture⟩ | Choice (Product/Index) | yes | |
| InstrumentId | ⟨capture⟩ | Number (FK→Product/Index `ID`) | yes | Resolves via ISIN/ticker join key. |
| TicketStatus | ⟨capture⟩ | Choice | **yes** | Lifecycle only. |
| TradeDate / SettleDate | ⟨capture⟩ | Date ×2 | TradeDate: **yes** | |
| Direction | ⟨capture⟩ | Choice | – | |
| **Notional / Currency / NotionalUSD** | ⟨capture⟩ | Number / Choice / Number | – | The only value columns. `NotionalUSD` normalised at write. **Known bias:** Notional favours large low-margin trades — correct if the measure is issuance volume (decision, `.claude/memory/`). |
| Notes | ⟨capture⟩ | Multi-line text | – | |
| IsArchived | ⟨capture⟩ | Yes/No | yes | |

## `tmProducts` — deliberately a stub (not a product master)

Economics live in the existing ISIN-keyed structured-product database; sync is one-directional
**in**; **ISIN is the egress contract**.

| Column | Internal | Type | Notes |
|---|---|---|---|
| Title | `Title` | Text | |
| **ISIN** | ⟨capture⟩ | Text (indexed) | **The join key.** |
| Issuer | ⟨capture⟩ | Text | |
| ProductType | ⟨capture⟩ | Choice | Coarse. |
| Currency | ⟨capture⟩ | Choice | |
| MaturityDate | ⟨capture⟩ | Date | |
| IsActive | ⟨capture⟩ | Yes/No | Deprecate with `false`, don't delete. |

## `tmIndices` — same principle, keyed on ticker

| Column | Internal | Type | Notes |
|---|---|---|---|
| Title | `Title` | Text | |
| **IndexTicker** | ⟨capture⟩ | Text (indexed) | Join key. |
| Sponsor | ⟨capture⟩ | Text | |
| AssetClass | ⟨capture⟩ | Choice | **Taxonomy source unresolved** — the desk's strategy vocabulary is *not* in claudeBrain (see `open-questions.md` Q5). Do not invent terms; values TBD. |
| RiskPremium | ⟨capture⟩ | Choice | Same — taxonomy TBD. |
| IsActive | ⟨capture⟩ | Yes/No | |

> Q5 is open: **is there an index master?** If not, `tmIndices` is a *real* list rather than a
> stub, which changes the seeding route (Q4).

## `tmClients` — minimal (a slicing dimension, not a CRM)

| Column | Internal | Type | Notes |
|---|---|---|---|
| Title | `Title` | Text | |
| ClientCode | ⟨capture⟩ | Text (indexed) | |
| ClientType | ⟨capture⟩ | Choice | |
| Region | ⟨capture⟩ | Choice | |
| Coverage | ⟨capture⟩ | Person | |
| IsActive | ⟨capture⟩ | Yes/No | |

## `tmIssues` — freeform, deliberately loose

| Column | Internal | Type | Indexed | Notes |
|---|---|---|:-:|---|
| Title | `Title` | Text | – | |
| IssueKey | ⟨capture⟩ | Text | yes | |
| ProjectId | ⟨capture⟩ | Number (FK) | yes | |
| IssueType | ⟨capture⟩ | Choice | – | (Q8: which types need a lifecycle — drives `NA`/triage.) |
| IssueStatus | ⟨capture⟩ | Choice | yes | Includes **`NA`** — a plain note has no lifecycle. |
| Impact / ImpactRank | ⟨capture⟩ | Choice / Number | – | |
| Body | ⟨capture⟩ | Multi-line text | – | |
| RaisedBy / Owner | ⟨capture⟩ | Person ×2 | – | |
| RaisedDate / ResolvedDate | ⟨capture⟩ | Date ×2 | – | |
| AttributesJson | ⟨capture⟩ | Multi-line text | – | JSON blob for read-only, never-sliced fields (see "adding depth"). |
| Tags | ⟨capture⟩ | Text | – | |
| IsArchived | ⟨capture⟩ | Yes/No | yes | |

## `tmComments` — polymorphic

`EntityType` + `EntityId` across Project/Task/Ticket/Issue; `ProjectId` denormalised; `Body`;
`Author` (Person); `CommentType`.

## `tmLinks` — relationships

`FromType`/`FromId`, `ToType`/`ToId`, `LinkType` (Blocks/RelatesTo/Duplicates/Affects). Cycle
detection on **Blocks** is app logic.

## `tmUserPrefs` — one row per user

`PinnedProjectIds`, `HomeWidgetOrder`, `DefaultView`, `Theme`.

## `tmLookups` — vocabularies so nothing is hardcoded

`LookupType`, `Value`, `DisplayName`, `ColorHex`, `SortOrder`, `IsActive`. Includes a
**FieldVisibility** row set driving conditional form fields. **Cached whole at startup.**

---

## Adding depth — the rule to encode

Separate two decisions that get conflated. Conditional visibility is always the right
*presentation* answer but says nothing about *storage*.

1. **Does this field already have a home?** If it's analysed outside the app and lives in
   another system, store the **join key** and nothing else. Two copies diverge, and SharePoint
   is the copy that loses.
2. Then: **will you ever filter, sort, group, or aggregate on it in the app?**
   - **Yes** → a **real column**, revealed conditionally. Sparse columns are cheap.
   - **No, a human just reads it** → a **JSON blob** (`AttributesJson`).
   - **"Maybe later"** → a **real column** — promoting JSON later means backfilling by hand.
- **Never build a generic attribute table** (`EntityId`/`AttrKey`/`AttrValue`): it delegates,
  but every value is a string (no typed comparison, no aggregation) and every read grows a join.
- **Reporting test:** anything you'd slice a Power BI visual by must be a real column. Power BI
  reads JSON only via Power Query parsing, which breaks silently on a missing key.

## No managed-metadata columns

Term-store vocabularies sync **down into `tmLookups` as plain Text** instead. Managed metadata
is Complex (never sorts), multi-value is unsupported, Graph doesn't fully support the columns,
and it's excluded from Dataverse virtual tables. **Sync via CSOM or PnP — not Graph** — keyed
on `TermGuid` so upstream renames reconcile; deprecate with `IsActive = false` rather than
deleting, or historical rows lose their labels.

> **Gap:** claudeBrain has **no PnP/CSOM skill** and provisioning here is **manual UI**, so
> there is currently no automated term-store sync route. Until one is chosen (Q11/Q12),
> `tmLookups` (and the `tmIndices` taxonomy) are seeded and maintained **by hand**.
