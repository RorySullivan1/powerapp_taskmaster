# 2026-08-18 11:18 · issue14-multiproduct-diagnosis

**Goal:** Diagnose issue #14: multi-product task links never reach taskmaster_taskproduct

## What happened
- **Read-only session. NOTHING WAS CHANGED and nothing was pushed** — the plan was posted
  to the issue and the fixes are still unwritten. Comment:
  https://github.com/RorySullivan1/powerapp_taskmaster/issues/14#issuecomment-5327408716
- Issue #14: task↔product links "not properly saving", dropped after the cache clears, and
  `taskmaster_taskproduct` never written to. Traced the whole path in `scrTaskEdit` — the
  junction's ONLY consumer, so all of it is in one file.
- **The reported symptom is three defects stacked, not one.** All confirmed by reading, none
  of them the SharePoint fault the title implies.

## Gotchas & dead ends
- **THE JUNCTION WRITES HAVE NO ERROR HANDLING AND THE SUCCESS TOAST DOES NOT DEPEND ON
  THEM.** `IfError` wraps only the `Patch(taskmaster_tasks, …)` (`scrTaskEdit.pa.yaml`
  `:1347`→`:1412`); the `RemoveIf` / re-read / `ForAll`+`Collect` at `:1435-1454` are bare.
  The rollup immediately below them DOES get one (`:1488`), so the omission is specific.
  `:1505` then notifies "Task saved" and `:1507` calls `Back()`. **A rejected junction write
  is indistinguishable from success** — which is why the fault has no diagnostic signal at
  all across the gap.
- **IT HALF-SAVES, AND THAT IS WHY IT READS AS "SAVED THEN GONE".**
  `task_product_summary` is written INSIDE the task Patch (`:1402`), from `colTkProducts`,
  BEFORE the junction is touched and regardless of whether the junction write succeeded.
  The task row claims products with no links behind it; the OnVisible seed (`:86-89`) reads
  the JUNCTION, not the summary, so a reopen shows nothing.
- **LIVE DATA-LOSS PATH, independent of issue #14.** The whole product set is gated on
  `tglTkOutput.Value`: `:967` hides the block, `:1426` leaves `colTkWanted` empty, `:1435`
  then deletes every link. Open a task with products, switch the Output section off for any
  reason, save → **all links deleted, silently**. The toggle's own `Default` already
  special-cases `!IsEmpty(colTkProducts)` (`:884`) to stop hiding them — the design saying
  products are not an output attribute.
- **The `RemoveIf` predicate does not delegate.** `in` against a local collection (`:1435`),
  so it only ever sees the first page of the WHOLE junction list. Invisible while the list
  is small; silently stops removing links as it grows.
- **WHY THE `Collect` IS REJECTED IS STILL UNKNOWN, AND I DID NOT GUESS.** It COMPILES — the
  task saves, and a property in compile error runs nothing at all (last session's lesson) —
  so it is a RUNTIME rejection, the one class the repo has no instrument for. Deliberately
  not diagnosed from inference: `Title` was called wrong on a different list on 2026-08-17
  the same way.
- **Nothing in `src/` reads `task_product_summary`**, despite `schema.yaml` describing it as
  what galleries render. Noticed in passing; not acted on.

## State at end
- `main` unchanged, working tree clean, no commits, no branch pushed.
- Issue #14 carries the plan: **probe first**, then four fixes.
  0. A `tests/` probe — one button, bare `Collect(taskmaster_taskproduct, {…})` wrapped in
     `IfError` → `Notify(FirstError.Message)`, plus a positive control. Returns SharePoint's
     ACTUAL error in one paste. Knowingly breaks `tests/README.md` rule 1 (names a data
     source) because the data source IS the claim.
  1. `IfError` around the reconcile → `gTkWarn`, AND verify by re-reading the junction
     (row count for `gTkSaved.ID` vs `CountRows(colTkWanted)`). **The re-read matters more
     than the IfError** — it catches a silent no-op as well as a throw.
  2. Write `task_product_summary` AFTER the reconcile, from what the junction actually
     holds. Two writes, but the summary can no longer claim links that do not exist.
  3. Take products out of the output gate (design call flagged to the user: narrower fix is
     to keep the toggle controlling visibility but not deletion).
  4. Replace the non-delegable `RemoveIf` with a delegable `Filter` on the indexed FK +
     `Remove` of the scope record. **Do NOT project `ID` out of the `ForAll` row** — that is
     the construct that failed three ways on 2026-08-14 and is why `RemoveIf` was chosen;
     passing `lk` itself is a different shape. Unproven — if Studio refuses it, keep
     `RemoveIf` and record the limit instead.
- SharePoint checks handed to the user, all framed as CHECKS not diagnoses: is `Title` still
  required on `taskmaster_taskproduct` (list created 2026-08-14, nothing has ever
  successfully written to it); the display field on both lookup columns (three other lookups
  in this tenant diverged to the target's ID, `schema.yaml:188-195`); write permission.

## Open threads
- **Everything above is unwritten.** Next session writes the probe and the four fixes on
  `claude/powerapp-repo-init-xymvlm`.
- The probe result decides nothing about fixes 1-4 — they stand either way — but it decides
  whether a SharePoint change is also needed before `scrTaskEdit` is worth re-pasting.
- Still to land from the previous wave: `scrHome`, `scrProjects`, `scrProject`,
  `scrIssueEdit`, `scrTransactionEdit`, `scrProductEdit`, and the remaining components.
  Fixes 1-4 land in the SAME `scrTaskEdit` paste, so they cost no extra crossing.
