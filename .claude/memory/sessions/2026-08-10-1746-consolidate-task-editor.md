# 2026-08-10 17:46 — Delete scrTask, make scrTaskEdit the sole task writer

## Goal
User reported that BOTH `scrTask` and `scrTaskEdit` let you edit a task and "actually
fails on changes", and proposed consolidating them since people only open a task in
order to edit it. Diagnose, then consolidate.

## What happened / decisions

**The failure was `scrTask`, and it was a staleness bug, not a data bug.** Confirmed by
the user: the failures produced NO red banner. That rules out the retired Managed
Metadata `Required` columns (`schema.yaml -> blocking_now:`), which fail loudly with a
named column — those are still an open SharePoint-side issue, just not this one.

`scrTask` contained **zero `Reset()` calls** (the only match in the file was a comment
*about* Reset). Every control was seeded from `Default` / `DefaultId` off `gSelTask`,
and those are read once at control load, not per visit:

- `txtTaskName.Default = gSelTask.task_name` → on the second task opened, the input
  still held task A's name, and `btnSave` writes `txtTaskName.Text` → **saving B renamed
  B to A.**
- `selStage` / `selHealth` / `selPriority` are `cmpSelection` instances seeded by
  `DefaultId` → still displayed A's picks.

The write path had been hardened (seed `gTaskStage`/`gTaskHealth`/`gTaskPriority` in
`OnVisible`, Patch from the globals, not the strips — the 2026-08-03 audit fix). **That
defence has a hole:** those globals only move when the strip raises `OnChange`. When the
strip displays a stale value and the user clicks the value they actually wanted, the
component believes nothing changed, `OnChange` never fires, `gTaskDirty` stays false —
the Save button stays disabled and the edit silently does nothing. That is exactly the
reported symptom, and it is why the write-side fix in August didn't cure it: **the
correct fix for a stale DISPLAY is `Reset()`, not a defensive write.**

**Two writers for one row is the deeper defect.** `scrTaskEdit` derives
`task_date_completion` from stage (Complete stamps, Archived preserves, anything else
clears). `scrTask` wrote `task_stage` and *not* the completion date — so completing a
task from the quick screen left the completion date blank. `scrTask` also still carried
`CountRows(scored) >= 2000` as its rollup guard where `scrTaskEdit` uses `500`; under a
500-row limit that guard can never fire, so it would write a truncated average into
`project_perc_completion`, which Power BI reads.

**Consolidation was cheap and obviously right.** `scrTask` was not in `NavMenu`; its only
inbound reference was one `OnSelect` in `scrProject`. Transactions and issues *already*
go straight from the project row to their editor — tasks were the only child type with
an extra hop, and the hop was a second, weaker editor. `scrTaskEdit` is a strict superset
of every field `scrTask` showed, and it resets all 16 of its inputs in `OnVisible`.

User was asked whether to preserve `scrTask`'s one advantage (one-tap stage change via
horizontal strips vs two taps on a combo box) and said **it doesn't matter** — so no
inline quick-flip was added to the project row.

**Switched `ThisItem` → `LookUp` on the way into the editor.** `colProjectTasks` is a
snapshot taken in `scrProject.OnVisible` and the editor Patches against whatever record
it is handed. Re-reading the live row costs one delegable ID lookup and removes a class
of write-stale-data bug. That made a miss possible (row deleted by someone else since
the snapshot), so the `OnSelect` now guards `IsBlank(gEditTask.ID)` and refuses with a
Notify rather than opening an empty "Edit task" form that would Patch against nothing.

## Gotchas & dead ends

- **`Default` is not re-read on revisit; `Reset()` is the only lever.** `scrTaskEdit`
  already knew this and says so in its `OnVisible` comments. `scrTask` never got the
  memo. When a screen is reused for a different record, EVERY seeded input needs a
  `Reset()` — text inputs, combo boxes (`DefaultSelectedItems`), date pickers
  (`DefaultDate`), toggles.
- **`Reset()` cannot reach inside a component instance.** So a `cmpSelection` strip
  reused across records is unfixable from outside. Seeding a global and writing from it
  makes the WRITE correct but leaves the DISPLAY lying — and a lying display produces a
  no-op `OnChange`, which is its own failure. **Don't reuse `cmpSelection` for
  per-record seeded state.**
- Don't read "the save is defended" as "the screen is correct". The August audit fixed
  `IsError(Errors(...))`, unconditional success Notify, and the write-from-globals
  problem on `scrTask` — and the screen was still broken, because nothing had addressed
  what the user was looking at.

## State at end
- Branch `claude/powerapp-repo-init-xymvlm`. Validator: **23/23 valid** (was 24/24 —
  one screen deleted). Remaining NOTEs are pre-existing and on unrelated screens.
- `src/Screens/scrTask.pa.yaml` **deleted**. No live `gSelTask` reference remains.
- `scrProject.pa.yaml` `galTasksHit.OnSelect` rewritten: `LookUp` + blank guard +
  `Set(gEditMode,"Edit")` + `Navigate(scrTaskEdit)`.
- Comment pointers fixed: `App.pa.yaml` C3 reference block, `scrProject` KPI ring
  comment, `docs/notes/edit-screens.md`, `docs/notes/shell-screens.md`.

## Open threads / next
- **NOT YET IN STUDIO.** Hand-off is two steps and the ORDER matters: (1) edit
  `galTasksHit.OnSelect` in the formula bar, (2) *then* delete the `scrTask` screen.
  Reversing it leaves a `Navigate` pointing at a deleted screen.
- `scrTransactionEdit` and `scrIssueEdit` are still reached with `Set(gEdit*, ThisItem)`
  straight off a collection snapshot — the same stale-base-record exposure that tasks
  just had fixed. Not changed here; worth the same `LookUp` treatment.
- The retired Managed Metadata `Required` columns remain unfixed in SharePoint
  (`schema.yaml -> blocking_now:`). Separate issue, fails loudly, still blocks project
  inserts.
