# Bulk import of outputs from an Excel file (#102)

**Status: designed, deliberately NOT BUILT.** #94 decided that "bulk" means in-app multi-row entry,
which scrTaskEdit, scrTransactionEdit and scrProject now provide. Build this flow only if in-app
entry proves too slow, or a large back-catalogue of outputs prepared outside the app has to be
loaded. Nothing in the app depends on it.

## The template

An Excel workbook in SharePoint or OneDrive with one **table** named `Outputs`, one row per output:

| Column | Required | Notes |
|---|---|---|
| `RowKey` | yes | Any value unique in the sheet (1, 2, 3 …). *Update a row* needs a key column. |
| `ProjectId` | yes | The project's SharePoint ID. |
| `TaskId` | no | Leave blank unless the output came from a task. |
| `TransactionId` | no | Leave blank unless the output came from a transaction. **Fill at most one of TaskId and TransactionId.** |
| `Name` | yes | |
| `Date` | yes | Date only. |
| `Format` | yes | Must be exactly one of the `output_format` values in `schema/schema.yaml`. |
| `Audience` | yes | Exact `output_audience` value. |
| `Language` | yes | Exact `output_language` value. |
| `Branding` | yes | Exact `output_branding` value. |
| `ApprovalFlag` | no | `Yes` / blank. |
| `ApprovalId` | no | |
| `OutputId` | — | **Written by the flow.** The new row's ID. A row with this filled in is skipped on a re-run. |
| `Result` | — | **Written by the flow.** `OK`, or why the row was rejected. |

## The flow (instant / manually triggered)

1. **Initialize variables**, one array per Choice column, copied **exactly** from `schema/schema.yaml`
   (`Formats`, `Audiences`, `Languages`, `Brandings`). If someone changes a column's choices in
   SharePoint, change them in the schema first and then here.
2. **Excel Online (Business) → List rows present in a table** on `Outputs`. In Settings, turn
   **Pagination** on with **Threshold** 5000.
3. **Apply to each** row, with **Concurrency control off** (one at a time, so the sheet's results
   line up). Inside it:
   1. **Condition:** `OutputId` is not empty → do nothing. This is what makes a re-run safe.
   2. **Validate, building a `Problems` string** (start empty, append each failure):
      - **Project exists:** *Get items* on `taskmaster_projects`, Filter `ID eq <ProjectId>`,
        Top 1. No rows means "project not found".
      - **At most one parent:** TaskId and TransactionId are not both filled in.
      - **The parent belongs to the project:**
        - If TaskId is set: *Get items* on `taskmaster_tasks`, Filter `ID eq <TaskId>`, Top 1. Its
          `task_project_id` → `Id` must equal ProjectId.
        - If TransactionId is set: the same on `taskmaster_transactions` and `transaction_project_id`.
      - **Required fields:** Name and Date are not empty.
      - **Choices:** `contains(variables('Formats'), <Format>)` and so on for each Choice column. A
        value not in the list is reported, not guessed.
   3. **If `Problems` is empty:**
      - **SharePoint → Create item** on `taskmaster_output`:
        - `output_name`, `output_project_id`, `output_date`, and the four Choices.
        - `output_task_id` or `output_transaction_id`: only the one that's filled in.
        - `output_approval_flag`, `output_approval_id`.
        - `output_project_archived`: **true if the project's `project_phase` is `Archived`, otherwise
          false.** Always write it. A blank is invisible to `LiveOutputs`.
      - **Excel → Update a row** (key column `RowKey`): `OutputId` = the new item's ID,
        `Result` = `OK`.
      - On the *Create item* failure path (Configure run after → has failed): **Update a row** with
        `Result` = the error message.
   4. **Else:** **Update a row** with `Result` = `Problems`.

*Create item* is right here, unlike the MERGE in the other runbooks, because the import supplies
every required column anyway.

## Check it worked

1. **A small test sheet:** one good row, one row with a bad Format, one with both TaskId and
   TransactionId. Expect `OK`, then two clear rejections.
2. **Re-run the flow.** Nothing new is created, because the good row now has an `OutputId`.
3. **The good output** shows on the project's Outputs panel, and on its task or transaction if it
   has one.
