# Incoming schema — staging capture (NOT yet canonical)

Transcribed verbatim from schema screenshots supplied by the user (one-way gap: these photos are
the only channel — nothing can be pulled back to verify). **Staging only** until the last two
lists arrive, then promoted into `.claude/context/schema.md`.

**Naming: snake_case is canonical** (user-confirmed 2026-08-02). It supersedes the old PascalCase
`tm*` model in `.claude/context/schema.md`. Bonus: snake_case sidesteps `_x0020_` mangling.

## Source log
| Received | Screenshot | Lists captured |
|---|---|---|
| 2026-08-02 | IMG_8566 | `asset_approval` |
| 2026-08-02 | IMG_8568 | `taskmaster_clients` |
| 2026-08-02 | IMG_8569 + IMG_8570 | `taskmaster_issues` |
| 2026-08-02 | IMG_8571 | `taskmaster_products` |
| 2026-08-02 | IMG_8571 + 8572 + 8573 | `taskmaster_projects` |

**Still awaiting:** `taskmaster_tasks`, `taskmaster_transactions` (both referenced by Lookups on
`taskmaster_issues`).

---

## List: `asset_approval`

| Column | Type | Req | Description | Values / Rules |
|---|---|:-:|---|---|
| `approval_id` | Single line text | **Y** | Approval identifier | e.g. MAW, Legal, Compliance, Brand |
| `approval_region` | **Choice** | **Y** | Applicable region | GLOBAL, AMER, EMEA, APAC, JAPAN |
| `approval_status` | Yes/No | N | Approval availability / active state | True = Active |
| `approval_link` | Hyperlink | N | Link to approval guidance/documentation | URL |
| `Created` · `Modified` · `Created By` · `Modified By` | System | — | — | SharePoint managed |

## List: `taskmaster_clients`

| Column | Type | Req | Description | Values / Rules |
|---|---|:-:|---|---|
| `client_name` | Single line text | **Y** | Client display name | User-facing |
| `client_type` | **Managed Metadata** | **Y** | Client classification | Internal taxonomy |
| `client_coverage` | **Managed Metadata** | **Y** | Coverage group | Coverage taxonomy |
| `client_sales` | Person | **Y** | Primary sales owner | Single person |
| `client_region` | **Managed Metadata** | **Y** | Client region | AMER, EMEA, APAC, JAPAN |
| `client_notes` | Multiple lines text | N | Client notes | Free text |
| `Created` · `Modified` · `Created By` · `Modified By` | System | — | — | SharePoint managed |

## List: `taskmaster_issues`

| Column | Type | Req | Description | Values / Rules |
|---|---|:-:|---|---|
| `issue_name` | Single line text | **Y** | Issue summary / title | User-entered |
| `issue_description` | Multiple lines text | N | Detailed issue description | Free text |
| `issue_project_id` | **Lookup → Projects** | **Y** | Parent project | Required |
| `issue_task_name` | **Lookup → Tasks** | N | Related task | Optional |
| `issue_transaction_name` | **Lookup → Transactions** | N | Related transaction | Optional |
| `issue_assignee` | Person | **Y** | Responsible resolver | Single person |
| `issue_status` | Choice | N | Current issue status | Open, Review, Waiting, Blocked, Closed |
| `issue_type` | Choice | N | Type of issue | Approval, Process, Compliance, Branding, Technical |
| `issue_impact` | Choice | N | Severity / impact level | Low, Moderate, High, Critical |
| `issue_date_open` | Date/Time | N | Date issue opened | Default = Created |
| `issue_date_target` | Date/Time | N | Expected resolution date | Future date |
| `issue_date_close` | Date/Time | N | Resolution date | Set on closure |
| `Issue_owner` *(sic — capital I)* | System | — | Issue owner / creator | "Business Owner" |
| `Created` · `Modified` · `Modified By` | System | — | — | SharePoint managed |

## List: `taskmaster_products`

| Column | Type | Req | Description | Values / Rules |
|---|---|:-:|---|---|
| `product_UID` *(sic — capital UID)* | Single line text | **Y** | Product identifier | e.g. ISIN, Ticker, Internal ID |
| `product_type` | **Managed Metadata** | **Y** | Product classification | Product taxonomy |
| `product_description` | Multiple lines text | **Y** | Product description | Free text |
| `Created` · `Modified` · `Created By` · `Modified By` | System | — | — | SharePoint managed |

## List: `taskmaster_projects`

| Column | Type | Req | Description | Values / Rules |
|---|---|:-:|---|---|
| `project_name` | Single line text | **Y** | User-facing project title | Unique enough for identification |
| `project_manager` | Person | **Y** | Accountable owner of project | Single person |
| `project_coverage` | **Managed Metadata** | N | Business/product coverage area | Coverage term set |
| `project_description` | Multiple lines text | N | Detailed project description | Free text |
| `project_region` | **Managed Metadata** | **Y** | Regional ownership | AMER, EMEA, APAC, JAPAN, GLOBAL |
| `project_pathway` | Single line text | N | SharedDrive folder location | Relative or full path |
| `project_type` | **Managed Metadata** | **Y** | Project classification | Production, Campaign, Platform, Event, Operational |
| `project_requestor` | Person | N | Requesting user | Single person |
| `project_phase` | Choice | **Y** | Current project lifecycle phase | Planning, Active, Blocked, Complete, Archived |
| `project_priority` | Choice | **Y** | Project priority level | Lowest, Low, Moderate, High, Critical |
| `project_perc_completion` | Number | N | Calculated project completion % | 0–100 |
| `project_date_start` | Date/Time | N | Actual project start date | Default = Created Date |
| `project_date_target` | Date/Time | N | Desired completion date | Future date |
| `project_date_complete` | Date/Time | N | Actual completion date | Set when complete |
| `project_other_resources` | **Person — MULTI** | N | Additional project contributors | **Multi-person allowed** |
| `Created` · `Modified` · `Created By` · `Modified By` | System | — | — | SharePoint managed |

---

# Consequences & flags

The schema is the user's to set; these are the **consequences to design around**, not objections.
Severity: ❗ = will break or silently return wrong results · ⚠ = needs a decision or a workaround.

## F1 ❗ `project_other_resources` is multi-person — this does not delegate *at all*

Multi-value columns are **unsupported by the SharePoint connector** for delegation (per
`delegation.md`: *Multi-value anything → nothing delegates*). Consequences:

- **"Projects I contribute to" cannot be a delegable server-side query.** Any filter touching this
  column processes only the first 500/2,000 rows and silently omits the rest.
- This is exactly the case the prior model avoided with *two fixed single-Person columns* rather
  than one multi-person column (`Or` of two `=` delegates; a multi-value match does not).

**Workarounds, in order of preference:**
1. Keep multi-person for *display only*, and drive "my projects" off the single-Person
   `project_manager` / `project_requestor` (both delegable on `.Email`).
2. Add a delegable companion — e.g. a text `project_resources_emails` maintained at write time —
   but note a `contains` match on it **still won't delegate**; only exact `=` would.
3. Split into fixed single-Person slots (`project_resource_1/2/3`) if server-side "am I on it?"
   filtering is genuinely required.

**Until resolved, I will not author a delegable contributor filter — there isn't one.**

## F2 ⚠ Managed Metadata on 6 columns — filter yes, sort no, and no sync route

`client_type`, `client_coverage`, `client_region`, `project_coverage`, `project_region`,
`project_type`, `product_type`.

- **Complex type → `=` via subfield delegates; `Sort`/`SortByColumns` NEVER does.** So galleries
  can *filter* by region/type server-side but cannot *sort* by them. Sorting must be by a Text,
  Number, Date or Yes/No column (e.g. `project_name`, `project_date_target`).
- Each MM column **costs a join** against the 12-join-per-view budget, alongside Person columns.
- **No term-store sync route exists here** (Graph doesn't fully support MM; sync needs CSOM/PnP,
  which this project has no path to, and provisioning is manual). The term sets are hand-maintained.
- `project_type` (5 fixed values) and `project_region` are enumerations — a **Choice** column would
  be cheaper (no join) and behave identically for filtering. MM is only worth it if the terms are
  genuinely governed centrally and reused across sites.

## F3 ⚠ Lookups on issues — bindings become records, not scalars

`issue_project_id` → Projects, `issue_task_name` → Tasks, `issue_transaction_name` → Transactions.

- Power Fx sees a Lookup as a **record**: filter with `issue_project_id.Id = gSelProject.ID`
  (delegates), and **patch** with the reference shape
  `{'@odata.type': "#Microsoft.Azure.Connectors.SharePoint.SPListExpandedReference", Id: …, Value: …}`
  — never a bare number.
- **Sorting by a Lookup never delegates**; each costs a join.
- Naming is inconsistent (`_id` vs `_name`) though all three are Lookups yielding a record —
  cosmetic, but formulas must use the exact internal name.

## F4 ❗ "Not archived" has no delegable form as modelled

There is no boolean archive flag; `Archived` is a value of the **Choice** `project_phase`. A
`.Value <> "Archived"` predicate resolves to a **Text `<>`**, which **does not delegate**.

**Delegable form** — enumerate the wanted values with `Or` of `=`:
```
Filter(taskmaster_projects,
    project_phase.Value = "Planning" || project_phase.Value = "Active"
 || project_phase.Value = "Blocked"  || project_phase.Value = "Complete")
```
Verbose but server-side. (A Yes/No `is_archived` column would be cheaper and indexable.) Same
pattern applies to "open issues" on `issue_status`.

## F5 ⚠ `region` is modelled three ways, with two different domains

| List | Column | Type | Values |
|---|---|---|---|
| `asset_approval` | `approval_region` | **Choice** | GLOBAL, AMER, EMEA, APAC, JAPAN |
| `taskmaster_projects` | `project_region` | **Managed Metadata** | AMER, EMEA, APAC, JAPAN, **GLOBAL** |
| `taskmaster_clients` | `client_region` | **Managed Metadata** | AMER, EMEA, APAC, JAPAN *(no GLOBAL)* |

One concept, two types, two domains. A shared region slicer can't treat them uniformly, and Power
BI will model them as unrelated dimensions. Recommend one type and one value set.

## F6 ⚠ `project_perc_completion` is described as "calculated" but typed Number

Typing it **Number is correct** (a SharePoint *Calculated* column can't be indexed and never
delegates). But nothing computes it: SharePoint won't, and Power Fx can't aggregate server-side.
It needs a **write-time rollup** — a Power Automate flow on task change (**Q12**) — or it stays
manually entered. Decide which; otherwise the field silently stays stale/blank.

## F7 ⚠ Casing anomalies must be matched exactly

`Issue_owner` (capital I) and `product_UID` (capital UID) break the otherwise-lowercase convention.
Internal names bind exactly as written — if these are the true internal names, formulas must match;
if they're typos in the design doc, fix them **before** provisioning (internal names freeze at
creation).

## F8 ⚠ No unique key columns; identity is the built-in `ID`

`approval_id` and `product_UID` are genuine identifiers (their "Values/Rules" cells list *example
identifier forms* — ISIN/Ticker/Internal ID — not an enumeration). But no list declares a
uniqueness constraint, and SharePoint won't enforce one. `project_name` is only "unique enough for
identification". Joins should use the built-in **`ID`** (always indexed, fastest possible lookup);
treat `approval_id`/`product_UID` as business keys enforced by convention only.

---

## Delegation quick-reference (all captured columns)

| Column kind | Delegates | Does NOT delegate |
|---|---|---|
| Single line text (`*_name`, `approval_id`, `product_UID`, `project_pathway`) | `=`, `StartsWith`, `Sort` | `<` `>` `<>`, `Search`, `in` |
| Choice (`*_status`, `*_type`, `*_impact`, `project_phase/priority`, `approval_region`) | `=` via `.Value` | **`Sort`**, `StartsWith` on subfield, `<>` (Text subfield) |
| Managed Metadata (6 cols) | `=` via subfield | **`Sort`** · costs a join |
| Lookup (3 on issues) | `=` via `.Id`/`.Value` | **`Sort`** · costs a join each |
| Person single (`project_manager`, `client_sales`, `issue_assignee`, `project_requestor`) | `=` on `.Email` / `.DisplayName` | other subfields, **`Sort`** · costs a join |
| **Person multi** (`project_other_resources`) | **nothing** | **unsupported — see F1** |
| Date/Time (`*_date_*`) | `=` `<` `>` `<=` `>=`, `Sort` | arithmetic inside the predicate |
| Number (`project_perc_completion`) | `=` `<` `>` `<=` `>=`, `Sort` | — |
| Yes/No (`approval_status`) | `=`, `Sort` | — |
| Multiple lines text (`*_description`, `client_notes`) | **nothing** | not filterable/indexable — display only |
| Hyperlink (`approval_link`) | **nothing** | display only; never a query key |
| System (`Created`, `Modified`, `Created By`, `Modified By`) | — | **never patch these** |

**Aggregates never delegate to SharePoint** (`Sum`, `Average`, `CountRows`, `CountIf`, `Max`,
`Min`) — filter delegably to a bounded set first, then aggregate locally, or use Power BI.

**Index early** (mandatory >5,000 items; can't be added past 20,000):
`project_phase`, `project_date_target`, `project_manager`, `project_name` ·
`issue_project_id`, `issue_status`, `issue_assignee`, `issue_date_target` ·
`client_name`, `client_region` · `product_UID` · `approval_id`, `approval_status`.
