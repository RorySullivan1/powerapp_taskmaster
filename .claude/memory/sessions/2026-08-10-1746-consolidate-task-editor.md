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
- ~~`scrTransactionEdit` and `scrIssueEdit` are still reached with `Set(gEdit*, ThisItem)`
  straight off a collection snapshot — the same stale-base-record exposure that tasks
  just had fixed.~~ **DONE at 18:12, and the premise was wrong: those two galleries bind
  to a live `Filter`, not a snapshot. See the follow-up below.**
- ~~The retired Managed Metadata `Required` columns remain unfixed in SharePoint.~~
  **RESOLVED — the user retired them all on 2026-08-10. See the follow-up below.**

---

## Follow-up, same session (18:12)

**Managed Metadata is gone.** User: "I retired all managed metadata columns. Choice columns
replace them." `schema.yaml -> blocking_now:` rewritten to RESOLVED (kept, not deleted — it
records a fault whose shape is worth remembering: a save rejected by a column the app never
writes is SharePoint-side and unfixable in Power Fx). `migration.status` is now PARTIALLY
APPLIED: step 6 done, the rest not, and possibly superseded.

**What was deliberately NOT done: nothing in `src/` now targets a Choice column.** The
replacement columns' internal names and allowed values were not supplied, and `schema.yaml`
is the golden source — inventing a token there would put a name into the app that SharePoint
does not have, and an unknown column in a Filter yields an EMPTY result rather than an error,
so it would fail silently. Recorded the gap as `choice_replacement_UNRECORDED:` with the two
questions that block any code move: whether the Choice columns supersede the C11
`*_id`/`*_path` + `mapping_*` + `cmpNestedSelect` apparatus or sit beside it, and whether the
level1/level2/level3 hierarchy is being dropped on purpose (a Choice column is flat).

**Transaction and issue rows fixed — and a correction.** I had claimed these carried "the same
stale-base-record exposure" as tasks. Not so: `galTasks` bound to `colProjectTasks`, a
ClearCollect SNAPSHOT, while these two bind to a live `Filter` of the data source. `ThisItem`
there is a genuine data-source row, identity is correct, Patch always hit the right ID. The
real gap is freshness — a gallery's query result is cached between refreshes, so the editor
could seed from values another user had since changed and patch them back, or open on a
deleted row. Same `LookUp` + `IsBlank` guard applied to both, for the smaller reason, with the
comments saying which reason.

## State at end (updated)
- 23/23 valid. `scrProject` now re-reads the row for all three child editors.
- Studio hand-off owed: `galTasksHit`, `galTxHit`-equivalent and the issue row `OnSelect` are
  three formula-bar edits on `scrProject`; the `scrTask` screen deletion still stands, and the
  OnSelect edit must come FIRST.

---

## Follow-up 2 (19:05) — "I clicked Save task and nothing happened"

Reported after the consolidation: description added, stage changed, click on **Save task**,
no toast, no navigation, nothing.

**Cause: `btnTkSave.DisplayMode` was `If(Len(lblTkMissing.Text) = 0, Edit, Disabled)`.** A
disabled button cannot fire `OnSelect`, and every path through that `OnSelect` ends in a
`Notify` — so silence proves the handler never ran. The task was missing a required field.

**The gate was not wrong; the silence was.** `task_name`, `task_lead` and `task_project_id`
are all `required: true` in `schema.yaml`, so SharePoint would reject the write regardless.

**It can only ever trip on an EDIT**, which is why it survived New-task testing:

    Set( gTkLead, If( gEditMode = "Edit",
        { ... Mail: Coalesce(gEditTask.task_lead.Email, "") },   <- blank if none stored
        { ... Mail: Coalesce(User().Email, "") } ) );            <- New always fills it

Same for `gTkProject` (Edit reads the record, New falls back to `gSelProject`). So a task
stored without a lead makes the editor permanently, silently dead.

**Fix, applied to three screens.** `DisplayMode` removed so the button is always enabled;
the entire save body wrapped in a guard that names what is missing:

    =If( Len(lblTkMissing.Text) > 0,
         Notify( "Can't save yet — this task still needs: " & lblTkMissing.Text,
                 NotificationType.Error ),
         <the whole existing body> )

Wrapping rather than re-indenting: Power Fx ignores whitespace, so only the first and last
lines changed and the ~110-line body is untouched. Paren balance was checked mechanically on
all three (depth 0) because a nesting level was added to a large expression by hand.

- `scrTaskEdit` — 3 gated fields.
- `scrIssueEdit` — 3 gated fields (summary, project, assignee).
- `scrTransactionEdit` — **SIX** (label, project, client, product, sales owner, date). Worst
  of the three: editing any older transaction missing one of them was a dead click.

**`scrProjectEdit`'s three inline sub-form buttons were deliberately NOT changed.** They gate
on fields inside the same modal the user is filling in right now, so the empty field sits on
screen beside the dead button. That is a different situation from an editor seeded off a
stored record, and touching three more large formulas would add paste risk with no reported
symptom behind it.

## Gotchas (added)
- **Never gate a save with `DisplayMode.Disabled`.** The control that knows why the save is
  blocked is the one control that has been prevented from saying so. Put the requirement in
  `OnSelect` and `Notify`.
- **The `lbl*Missing` labels must stay a BARE LIST.** The guard now tests
  `Len(lbl*Missing.Text) > 0`; a static prefix would make it permanently non-empty and block
  every save on that screen. Recorded in each label's own comment.
