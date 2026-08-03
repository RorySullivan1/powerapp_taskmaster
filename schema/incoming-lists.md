# Incoming schema — staging capture (NOT yet canonical)

Transcribed verbatim from schema screenshots supplied by the user (one-way gap: these photos are
the only channel — nothing can be pulled back to verify). **Staging only.** Nothing here is
promoted into `.claude/context/schema.md` until the full set has arrived and the conflicts in
§Reconciliation are settled.

## Source log
| Received | Screenshot | Lists captured |
|---|---|---|
| 2026-08-02 | IMG_8566 (dated 7/23/26) | `asset_approval` (complete) |
| 2026-08-02 | IMG_8568 | `taskmaster_clients` (complete) |
| 2026-08-02 | IMG_8569 + IMG_8570 | `taskmaster_issues` (complete, across two shots) |

**Still awaiting:** `taskmaster_projects`, `taskmaster_tasks`, `taskmaster_transactions` (all three
are referenced by Lookups in `taskmaster_issues` but not yet supplied), plus any lookups/comments/
links/user-prefs/products/indices equivalents.

---

## List: `asset_approval`

| Column | Type | Required | Description | Values / Rules |
|---|---|---|---|---|
| `approval_id` | Single line of text | **Yes** | Approval identifier | `MAW`, `Legal`, `Compliance`, `Brand` |
| `approval_region` | **Choice** | **Yes** | Applicable region | `GLOBAL`, `AMER`, `EMEA`, `APAC`, `JAPAN` |
| `approval_status` | Yes/No | No | Approval availability / active state | `True` = Active |
| `approval_link` | Hyperlink | No | Link to approval guidance or documentation | URL |
| `Created` · `Modified` · `Created By` · `Modified By` | System | System | — | SharePoint managed |

---

## List: `taskmaster_clients`

| Column | Type | Required | Description | Values / Rules |
|---|---|---|---|---|
| `client_name` | Single line of text | **Yes** | Client display name | User-facing |
| `client_type` | **Managed Metadata** | **Yes** | Client classification | Internal taxonomy |
| `client_coverage` | **Managed Metadata** | **Yes** | Coverage group | Coverage taxonomy |
| `client_sales` | Person | **Yes** | Primary sales owner | Single person |
| `client_region` | **Managed Metadata** | **Yes** | Client region | `AMER`, `EMEA`, `APAC`, `JAPAN` |
| `client_notes` | Multiple lines of text | No | Client notes | Free text |
| `Created` · `Modified` · `Created By` · `Modified By` | System | System | — | SharePoint managed |

---

## List: `taskmaster_issues`

| Column | Type | Required | Description | Values / Rules |
|---|---|---|---|---|
| `issue_name` | Single line of text | **Yes** | Issue summary / title | User-entered |
| `issue_description` | Multiple lines of text | No | Detailed issue description | Free text |
| `issue_project_id` | **Lookup → Projects** | **Yes** | Parent project | Required |
| `issue_task_name` | **Lookup → Tasks** | No | Related task | Optional |
| `issue_transaction_name` | **Lookup → Transactions** | No | Related transaction | Optional |
| `issue_assignee` | Person | **Yes** | Responsible resolver | Single person |
| `issue_status` | Choice | No | Current issue status | `Open`, `Review`, `Waiting`, `Blocked`, `Closed` |
| `issue_type` | Choice | No | Type of issue | `Approval`, `Process`, `Compliance`, `Branding`, `Technical` |
| `issue_impact` | Choice | No | Severity / impact level | `Low`, `Moderate`, `High`, `Critical` |
| `issue_date_open` | Date/Time | No | Date issue opened | Default = `Created` |
| `issue_date_target` | Date/Time | No | Expected resolution date | Future date |
| `issue_date_close` | Date/Time | No | Resolution date | Set on closure |
| `Issue_owner` *(sic — capital I)* | System | System | Issue owner / creator | "Business Owner" |
| `Created` · `Modified` · `Modified By` | System | System | — | SharePoint managed |

> Note: `Created By` is **not** listed on this list (unlike the other two); `Issue_owner` appears
> to take its place but is typed "System" with a rule of "Business Owner" — ambiguous whether it
> is the SharePoint `Author` field or a Person column. **Needs confirmation.**

---

# Reconciliation — conflicts with documented decisions

These are not style preferences; each has a **delegation or provisioning consequence** and each
contradicts a decision already recorded in `.claude/memory/INDEX.md`. Nothing data-bound should be
authored until they are resolved.

## C1 — Managed Metadata is used (3 columns), but our model forbids it ❗

`client_type`, `client_coverage`, `client_region` are **Managed Metadata**.
`.claude/context/schema.md` says **"No managed-metadata columns"**, with reasons that still apply:

- **Complex type → `Sort`/`SortByColumns` NEVER delegates.** A client list sorted by type, coverage,
  or region cannot sort server-side. `=` on the subfield does delegate, so *filtering* is fine.
- **Counts against the 12-join limit** per view (like Lookup and Person).
- **Multi-value is unsupported** by the SharePoint connector.
- **Graph does not fully support** managed-metadata columns, and they're excluded from Dataverse
  virtual tables.
- **Sync requires CSOM or PnP — not Graph.** We have **no PnP/CSOM route** (documented gap), and
  provisioning is manual (Q11), so there is currently **no way to sync the term store**.

**Options:** (a) keep Managed Metadata and accept no server-side sort on those three + no term-store
automation; (b) revert to the documented design — plain **Text** columns fed from a lookups list;
(c) hybrid — Managed Metadata for governance, plus a denormalised Text mirror for sort.

## C2 — Lookup columns are used (3 on issues), but our model forbids them ❗

`issue_project_id` → Projects, `issue_task_name` → Tasks, `issue_transaction_name` → Transactions.
Our decision was **"no Lookup columns at all — integer FKs to the built-in `ID`, joined
client-side."**

- Each Lookup is a **join** against the 12-join budget, and Lookup is a **Complex** type: `=` via
  subfield delegates, **`Sort` never does**, and `StartsWith` on a Lookup subfield doesn't delegate.
- Power Fx sees a Lookup as a **record** (`.Id` / `.Value`), not an integer — so every formula in
  `docs/screen-map.md` written as `Filter(child, FK = Gallery.Selected.ID)` must become
  `Filter(taskmaster_issues, issue_project_id.Id = gSelProject.ID)`, and patches must write the
  `{'@odata.type':"#…SPListExpandedReference", Id:…, Value:…}` record shape, not a number.

**This is workable** — the project-filtered issues feed still delegates — but it changes the
binding shape everywhere and forbids sorting issues by project/task/transaction server-side.

## C3 — `region` is modelled two different ways, with two different value sets ⚠

| List | Column | Type | Values |
|---|---|---|---|
| `asset_approval` | `approval_region` | **Choice** | GLOBAL, AMER, EMEA, APAC, JAPAN |
| `taskmaster_clients` | `client_region` | **Managed Metadata** | AMER, EMEA, APAC, JAPAN |

Same concept, different type *and* different domain (`GLOBAL` exists on one only). A shared region
filter/slicer can't treat them uniformly, and Power BI will see two unrelated dimensions. Recommend
one region vocabulary with one type.

## C4 — `approval_id` holds an enumeration, not an identifier ⚠

Values are `MAW / Legal / Compliance / Brand` — a category, so **not unique per row**. The row key
is the built-in `ID`. Read it as `approval_type`; do **not** use it as a join key as named.
(Storing it as **Text** rather than Choice is correct per our policy — Text sorts delegably.)

## C5 — Naming-convention drift, and one casing anomaly ⚠

- Incoming lists are **snake_case** (`taskmaster_clients`, `client_name`); the documented model is
  **PascalCase `tm*`** (`tmClients`, `ClientCode`). Confirm the snake_case set supersedes it.
  *(Upside: snake_case avoids the `_x0020_` mangling risk entirely.)*
- **`Issue_owner` has a capital `I`** while every sibling is lowercase. If that is the true internal
  name, formulas must match it exactly — SharePoint internal names are case-sensitive in binding.
- Lookup columns are named inconsistently: `issue_project_id` (`_id`) vs `issue_task_name` /
  `issue_transaction_name` (`_name`) — all three are Lookups and all yield a record, not a scalar.

## C6 — Design elements from the prior model that are absent ⚠

- **No archive/active flag** on `taskmaster_issues` (our design used `IsArchived`, and the delegable
  "not archived" filter depends on a boolean — Text `<>` does not delegate).
- **No `NA` status** on `issue_status` — the prior design's "a plain note has no lifecycle" concept
  (Q8) is gone. Fine if intentional.
- **No key column** (`IssueKey`) and no `AttributesJson`.
- `taskmaster_clients` has **no client code** and **no active flag** (prior design had both).

---

## Delegation quick-reference for what has arrived

| Column | Delegates for | Does NOT delegate |
|---|---|---|
| `client_name`, `issue_name`, `approval_id` (Text) | `=`, `StartsWith`, `Sort` | `<`/`>`/`<>`, `Search` |
| `issue_status/type/impact`, `approval_region` (Choice) | `=` via `.Value` | **`Sort`**, `StartsWith` on subfield |
| `client_type/coverage/region` (Managed Metadata) | `=` via subfield | **`Sort`** — and costs a join |
| `issue_project_id/task_name/transaction_name` (Lookup) | `=` via `.Id`/`.Value` | **`Sort`** — and costs a join each |
| `client_sales`, `issue_assignee` (Person) | `=` on `.Email` / `.DisplayName` | all other subfields, **`Sort`** |
| `issue_date_*` (Date/Time) | `=`, `<`, `>`, `<=`, `>=`, `Sort` | arithmetic in the predicate |
| `approval_status` (Yes/No) | `=`, `Sort` — index it | — |
| `client_notes`, `issue_description` (Multi-line) | **nothing** | not filterable/indexable — display only |
| `approval_link` (Hyperlink) | **nothing** | display only; never a query key |
| `Created`/`Modified`/`Created By`/`Modified By` | — | **system fields — never patch** |

**Indexing (mandatory above 5,000 items, and must be created while the list is small):**
`issue_project_id`, `issue_status`, `issue_date_target`, `issue_assignee` on issues;
`client_region`/`client_name` on clients.
