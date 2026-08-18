# 2026-08-18 · Issue #15 — delete tasks / transactions / issues

## What was asked
Enable deletion of transactions, tasks and issues from the project screen or the edit
screens. Planned and commented on the issue first; built after approval.

## Two forks settled with the user
1. **Detach, don't cascade.** Issues referencing a deleted task/transaction keep existing;
   only `issue_task_name` / `issue_transaction_name` is cleared. `issue_project_id` is
   `required: true` and untouched, so the issue stays valid. An issue raised against a task
   is usually worth more than the task.
2. **`cmpConfirmDialog`, not the two-press arm** used by `icoDeleteProject`. Only a dialog
   can say what ELSE the delete changes ("2 issues will be detached").

## The reference map that drove it
- **Task -> `taskmaster_taskproduct`**: SharePoint CASCADE is already configured and
  confirmed, so the junction rows go with the task. **The app must not delete them itself.**
- **Task/transaction -> `taskmaster_issues`**: optional lookups, detached app-side.
- **Issue**: nothing references it. Clean delete.

## The rollup repair — and the probe that decided it
Deleting a child invalidates `project_phase` and `project_perc_completion`, both derived in
`scrProject.OnVisible`, which does not re-run in place. Copying that ~45-line block into three
delete handlers would have created FOUR writers of the same two columns that can drift.

`tests/scrProbeRerun` settled the mechanism. **`Select()` fires on a control with
`Visible: =false`** — confirmed in Studio, positive control passing. So the derivation moved
into `btnPrjRecompute.OnSelect` (hidden, 1x1) with four callers: `OnVisible` plus the three
delete handlers. One copy.

**`Navigate()` to the current screen also works** (confirmed on a second pass). It was NOT
used: it repaints the screen on every delete, and it pushes `scrProject` onto its own history
on a screen that already carries a comment about a `Back()`-alternation bug. Reversible in
one line if the worker ever proves awkward.

The worker RE-READS `colProjectTasks` rather than having each caller patch the snapshot — one
delegable Filter on an indexed FK, and it cannot drift.

## Traps that shaped the code
- **`IfError( Remove(...), Notify(...) )` is REJECTED by Studio**, despite being MS Learn's own
  idiom: `Remove` and `ForAll`/`Patch` return a TABLE, `Notify`/`Set` return a boolean, and
  `IfError` requires type-compatible arguments. Every call site is
  `IfError( Set(<scrap>, <op>), Set(gDelErr, FirstError.Message) )` with a **different scrap
  name per site** — a global's type unifies across every `Set`.
- **Z-ORDER: the row delete icons are declared AFTER the transparent full-template hit
  buttons.** Those buttons cover the whole row and are what make rows clickable; anything
  declared before them is underneath and cannot be clicked. The icon still RENDERS, so getting
  this wrong looks like a dead control rather than a layering bug.
- **Count, then refuse.** The detach is a local `ForAll` over a delegable `Filter`, so past the
  data row limit it would clear SOME references, raise no error, and delete the parent anyway.
  Blocked at 500, same shape as the project cascade.
- **Detach BEFORE remove.** The reverse leaves issues pointing at a row that is already gone.
- **No transaction exists.** If the `Remove` fails after the detach committed, the error message
  says so rather than implying nothing changed.

## Hand-off
Four screens re-paste: `scrProject`, `scrTaskEdit`, `scrTransactionEdit`, `scrIssueEdit`.
No schema change and no new data source.

**BLOCKING, and easy to miss: `cmpConfirmDialog` had NO consumer in `src/` until now.** A
component crosses the gap in two parts and only the CONTROLS paste — every custom property is
declared and typed BY HAND in Studio. Its eight properties may never have been declared at all.
Verify `IsOpen` / `Title` / `Message` / `ConfirmLabel` / `CancelLabel` / `Destructive` are
INPUTS and `OnConfirm` / `OnCancel` are EVENTS before pasting any of the four screens —
otherwise every dialog reads blank and simply never opens, exactly as `cmpSelection` did.

## Not done
The delete path is untested in Studio. Nothing here is landed.
