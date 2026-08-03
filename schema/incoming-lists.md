# Schema provenance — capture log

The **canonical** data model lives in **`.claude/context/schema.md`**. This file records only
*where it came from*, so the transcription can be audited later. Do not duplicate column tables
here — single-source them in the context brief.

The air gap is **one-way**: schema screenshots supplied by the user are the only channel, and
nothing can be pulled back to verify a transcription.

## Capture log

| Received | Screenshot(s) | List(s) transcribed |
|---|---|---|
| 2026-08-02 | IMG_8566 | `asset_approval` |
| 2026-08-02 | IMG_8568 | `taskmaster_clients` |
| 2026-08-02 | IMG_8569, IMG_8570 | `taskmaster_issues` |
| 2026-08-02 | IMG_8571 | `taskmaster_products` |
| 2026-08-02 | IMG_8571, IMG_8572, IMG_8573 | `taskmaster_projects` |
| 2026-08-02 | IMG_8574, IMG_8575 | `taskmaster_tasks` |
| 2026-08-02 | IMG_8576 | `taskmaster_transactions` |

## Not yet supplied
- **`asset_library`** — referenced by `taskmaster_tasks.task_output_asset` (Lookup). No schema
  received; any binding to it is blocked.

## User clarifications on the record
- **snake_case is canonical** and supersedes the earlier PascalCase `tm*` design (2026-08-02).
- `approval_id` / `product_UID` are **genuine identifiers**; the "Values / Rules" cells list
  *example identifier forms* (MAW/Legal/…, ISIN/Ticker/Internal ID), **not** enumerated domains.

## Transcription caveats
Two columns carry casing that breaks the otherwise-lowercase convention and must be confirmed
before provisioning freezes internal names: **`Issue_owner`** (capital I) and **`product_UID`**
(capital UID). `taskmaster_issues` also lists no `Created By`, and its `Issue_owner` is typed
"System" with a rule of "Business Owner" — ambiguous between the SharePoint `Author` field and a
Person column.
