# Incoming schema — staging capture (NOT yet canonical)

Transcribed verbatim from schema screenshots supplied by the user (one-way gap: these photos are
the only channel — nothing can be pulled back to verify). **Staging only.** Nothing here is
promoted into `.claude/context/schema.md` until the full set has arrived and the naming-convention
question below is settled.

> ⚠️ **Unreconciled with the documented `tm*` model.** `.claude/context/schema.md` documents
> `tmProjects`/`tmTasks`/`tmClients`… with PascalCase columns. These incoming lists use
> **snake_case** list *and* column names (`asset_approval`, `approval_id`, `taskmaster_clients`).
> The two are incompatible. Do not author data-bound Power Fx against either until the user
> confirms which convention is real — a wrong column token is a failed paste we learn about only
> as "it didn't work."

## Source log
| Received | Screenshot | Lists captured |
|---|---|---|
| 2026-08-02 | IMG_8566 (dated 7/23/26) | `asset_approval` (complete); `taskmaster_clients` (heading only — cut off) |

---

## List: `asset_approval`

| Column | Type | Required | Description | Values / Rules |
|---|---|---|---|---|
| `approval_id` | Single line of text | **Yes** | Approval identifier | `MAW`, `Legal`, `Compliance`, `Brand` |
| `approval_region` | Choice | **Yes** | Applicable region | `GLOBAL`, `AMER`, `EMEA`, `APAC`, `JAPAN` |
| `approval_status` | Yes/No | No | Approval availability / active state | `True` = Active |
| `approval_link` | Hyperlink | No | Link to approval guidance or documentation | URL |
| `Created` | System | System | Creation date | SharePoint managed |
| `Modified` | System | System | Update date | SharePoint managed |
| `Created By` | System | System | Creator | SharePoint managed |
| `Modified By` | System | System | Last editor | SharePoint managed |

### Delegation / typing notes (per `sharepoint-list-architecture` + `delegation.md`)
- `approval_id` — **Text**: `=` and `StartsWith` delegate; **indexable**; sorts delegably. Storing
  this enumeration as Text (not Choice) is consistent with our column-type policy (*Text for
  anything sorted; Choice only where filtered and never sorted*).
- `approval_region` — **Choice**: `=` delegates via the subfield; **never sorts delegably**. If
  region ever needs ordered sort, it needs a companion rank column.
- `approval_status` — **Yes/No**: delegable, cheap, indexable. Default it explicitly.
- `approval_link` — **Hyperlink**: display-only — **not filterable, not indexable, never a query
  key**. Stored as two subfields (URL + description).
- `Created`/`Modified`/`Created By`/`Modified By` — **system fields; never patch them.**

### Open questions on this list
1. **Is `approval_id` a unique row key or a category?** Its values (`MAW`/`Legal`/`Compliance`/
   `Brand`) are an enumeration, so it is *not* unique per row — the name implies a key but the
   data is a type. If a row is really *(approval type × region)*, the row identity is the built-in
   `ID`, and `approval_id` should be read as `approval_type`. Confirm before it is used as a
   lookup key anywhere.
2. **Relationship to the rest of the model** — what does an approval attach to (a product? an
   asset? a project?)? No FK column is present, so as captured this list is a standalone
   vocabulary/reference table, not a child of anything.
3. **Are these the TRUE internal names** (post-provisioning, `_x0020_`-safe) or design intent?
   Snake_case avoids the `_x0020_` mangling risk entirely, which is a point in its favour.

---

## List: `taskmaster_clients`
Heading visible only — **table cut off in the screenshot. Awaiting capture.**
(Presumed counterpart to the documented `tmClients`.)
