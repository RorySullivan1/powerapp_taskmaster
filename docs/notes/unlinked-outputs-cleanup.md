# One-off clean-up: unlinked outputs

**Why:** an output belongs to a task or a transaction (`schema/schema.yaml`, taskmaster_output
link rules). For a short while, outputs could also be saved against just a project. Those rows
have **neither** `output_task_id` nor `output_transaction_id`. scrProject's Outputs dialog is
read-only, so the app can't edit or delete them. It shows them as **"Unlinked"** and counts them
on the project card as "· N unlinked".

Nothing in the app writes an unlinked output any more. scrTaskEdit always sets `output_task_id`,
and scrTransactionEdit and scrQuickTx always set `output_transaction_id`. So the set is fixed and
small, and a clean-up in SharePoint is cheaper than putting a delete path back into the app (#112).

## Steps (SharePoint, in the browser; no flow needed)

1. Open the **taskmaster_output** list.
2. Create a personal view (or filter the default one) with two conditions, joined by **And**:
   - `output_task_id` **is equal to** *(leave the value empty)*
   - `output_transaction_id` **is equal to** *(leave the value empty)*

   Show `ID`, `output_name`, `output_project_id`, `output_date` and both FK columns.
3. For each row, decide:
   - **It came from a task or a transaction.** Open that task or transaction in SharePoint,
     note its **ID**, and type that ID into the output's `output_task_id` **or**
     `output_transaction_id`. Fill in **one** of them, never both. Leave `output_project_id`
     as it is. It has to be the parent's project, so check that it is.
   - **It shouldn't exist.** Delete the row.
4. The view should now be empty.

## Check in the app

Open each affected project in the app. The Outputs line on the info card should no longer end
in "· N unlinked". A newly linked output now opens its task or transaction when tapped in the
Outputs dialog.

## If unlinked rows come back

Then something is writing them, and this runbook is the wrong fix. Look for the writer first.
Only then consider option (a) from #112: a delete icon on unlinked rows in `mdOl`, going through
`cmpPrjConfirmDel`.
