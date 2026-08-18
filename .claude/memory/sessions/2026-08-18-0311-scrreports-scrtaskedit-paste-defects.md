# 2026-08-17 · scrreports-scrtaskedit-paste-defects

**Goal:** Land scrReports and scrTaskEdit across the gap; diagnose the paste-time defects each surfaced

## What happened
- **`scrReports` LANDED.** First crossing of the 2,560-line screen. Took four fix rounds:
  blank denominators, the `colRptPrj` schema loss, then feature work on top.
- **`scrTaskEdit` LANDED and the save runs.** Four defects, none of them the one first
  suspected.
- Feature work that went with it: period narrowed to **1W / 1M / 1QTR** (rolling, adaptive
  bar buckets), **scope became a project-manager combobox** replacing Me/My projects/Desk,
  and **five literal Choice arrays bound to `Choices()`** across scrTaskEdit and
  scrProjectEdit.
- SharePoint side: `task_supporter` and `project_perc_completion` both deleted and
  recreated by the user after their internal names turned out wrong;
  `taskmaster_taskproduct` added to the app as a data source.

## Gotchas & dead ends
- **THE ERROR LIST IS NOT THE FAULT LIST — three separate times this session.** One
  unresolvable name produced a scatter of unrelated-looking errors, and each time the
  named symptoms were innocent. `ShowColumns` naming one bad column reported four errors
  across two controls; an unconnected data source reported a missing *built-in* `ID`; a
  projected built-in reported three. **Count the errors against the number of places the
  suspect is used** — that is what cleared `gTkSaved.ID` (read in four places, only two
  errors) and what should have cleared `project_name` sooner.
- **A PROPERTY IN COMPILE ERROR DOES NOT RUN AND SAYS NOTHING.** The Create task button
  was inert: no toast, no label change, identical on a full and a minimal form. Cause was
  an unresolvable data-source name inside `OnSelect`. **A fresh probe formula in the same
  property fires perfectly**, which is what proves the event path is fine and the handler
  is the problem — that one-property `Notify` was the highest-value diagnostic of the
  session and should be reached for far sooner.
- **`provisioned:` ONLY EVER MEANT SHAREPOINT.** A screen paste never adds a data source,
  so a list can be live, correct in `schema.yaml`, and an unknown name in every formula.
  `taskmaster_taskproduct` had exactly one consumer, so nothing before `scrTaskEdit` could
  reveal it. Recorded at the junction in `schema.yaml`.
- **A BUILT-IN COLUMN DOES NOT SURVIVE PROJECTION OUT OF A `ForAll` ROW.**
  `{ LinkId: lk.ID }` then `LookUp(..., ID = gone.LinkId)` failed three ways. A real column
  projects fine. `RemoveIf` needs no ID at all and removed the whole construct.
- **`ShowColumns` OVER A BARE NAMED FORMULA ACCEPTS THE NAMES AND LOSES THE SCHEMA.**
  `ClearCollect` reported nothing while every `p.project_name` read as unrecognized. The
  siblings were immune because their first argument is a `Filter` EXPRESSION.
  **`colRptIss` has the same risky shape and survives only because nothing reads a field
  off it** — add one and it breaks the same way.
- **I WAS WRONG ABOUT `Title`** and sent the user at their SharePoint columns on an
  inference. The user's pushback — "it is correctly referenced elsewhere" — was the
  correct signal and I should have taken it as evidence rather than re-explaining. The
  retraction is in `schema.yaml`; the conversion pattern is kept only for a list that
  genuinely needs it.
- **NAME COLLISIONS, TWICE IN ONE CHANGE.** `colTkFormat` is a CONTAINER on scrTaskEdit
  (the screen uses `col*` for both), and `colTkStageOpts` already existed for `task_stage`
  with an `{Id, Label}` shape. Both surfaced as "Incompatible type" one hop from the cause.
  Scan for control names reused as collections AND collections seeded twice.
- **A DIVISION GUARD THAT TESTS `= 0` DOES NOT PROTECT A PROPERTY FORMULA** — the editor
  runs it with every global blank. `Max(1, x)` at the POINT OF USE, not at the `Set`.

## State at end
- `main` clean and pushed. 22/22 valid, globals audit clean.
- **`scrReports` and `scrTaskEdit` are BOTH LANDED.** First two screens of this wave.
- Still to land: `scrHome`, `scrProjects`, `scrProject`, `scrIssueEdit`,
  `scrTransactionEdit`, `scrProductEdit`, and the remaining components.

## Open threads
- **`scrProjectEdit` carries the two newly-bound Choice combos and is UNPASTED** —
  `colNtPrioOpts` / `colNxCcyOpts`. Same class of change as the ones that just cost four
  rounds on scrTaskEdit.
- **`scrProjects`' `colPrjCoverage`** uses the seed-then-Collect idiom; no collision, but
  unproven.
- **A names audit is worth building** — `tools/audit_names.py` alongside `audit_globals.py`.
  It found two real bugs in one sitting. The column-token hook already proposed in
  CLAUDE.md would NOT have caught either SharePoint name fault, and that should be said
  when it is built, so it is scoped to authoring typos rather than schema drift.
- Owed in SharePoint: re-index `task_supporter`; real values for the four PLACEHOLDER
  Choice columns; `project_phase` default to `Not Started`; index `task_date_completion`.
