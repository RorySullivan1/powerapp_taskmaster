# 2026-08-13 17:24 · project-phase-derivation-and-selection-fix

**Goal:** Derive project_phase in-app, fix cmpSelection Selected output property, rework scrProjects/scrProject galleries

## What happened
- **Finished the `/code-review`** — committed the fixes, reported findings.
- **`Created By` removed from `scrIssueEdit`.** The canvas connector does not surface it;
  on `taskmaster_issues`, `issue_owner` IS the created-by. `issue_owner` / `issue_date_open`
  were un-retired in `schema.yaml`.
- **Hover states softened app-wide** — 11 buttons, 16 icons across `scrProjects`, `scrProject`,
  the nav menu and `scrReference`. `gTheme.Color.Hover` = `RGBA(0,90,158,0.05)`,
  `.Press` = `RGBA(0,90,158,0.1)`. Extended to `Classic/Icon` after the user confirmed
  `HoverFill`/`HoverColor`/`HoverBorderColor` exist there.
- **`.claude/memory/INDEX.md` pruned** 620 lines / 231KB → ~92 lines. Prior contents kept
  verbatim in `sessions/ARCHIVE-2026.md`.
- **`cmpPicker` opens with its first 10 rows** — `StartsWith(col, "")` is true for every row,
  so the default page and the search are ONE branch and `FirstN` supplies the cap.
- **The layout-freeze claim was re-tested and falsified.** New `tests/` directory,
  `tests/scrProbe-layout-freeze.pa.yaml` + `tests/README.md`. All four probe steps passed:
  formulas — forward references included — cross a paste live and keep recomputing.
  Corrected the docs everywhere the old rule was cited.
- **`scrProjects` fully reworked** — `rowFilters` auto-layout (coverage combobox / search /
  Show-completed toggle) over a four-branch delegable `Items` and an auto-layout gallery row
  with an inline status SVG, colour-coded priority, name, lead, due date + days-til-due and
  % complete.
- **`scrProject`'s three galleries rebuilt** as auto-layout rows with SVG glyphs and composite
  sort keys (`priority*100000 + days-til-due`, blanks pushed to 99999). Fixed the overlapping
  rows.
- **`cmpSelection` root cause found and fixed** (see Gotchas).
- **`project_phase` is now derived by the app.** `scrProject.OnVisible` computes it and Patches
  on change; a **Mark as Complete** button is the only route to Complete; the phase picker is
  gone from `scrProjectEdit`; the archive cascade moved out to an external flow.
- **Three layout edits landed** — name at `FillPortions: =2` in `rowPrD1`, priority and coverage
  as `cmpSelection` strips fed from `Choices()`, and `btnPrjComplete` spanning both columns
  below the KPI ring and the edit/delete icons.
- **`galProjects.Y` set to an absolute `210`** with `Height: =Parent.Height - 210 - Gutter`.

## Gotchas & dead ends
- **`Selected` was never declared as an OUTPUT property in Studio** — the real cause of issue
  `type`/`impact`/`status` not writing. Before finding it I guessed twice (a timing hypothesis,
  then a vocabulary one), converted controls that did not need converting, and invented a
  circular-reference explanation for a Studio error. The user named the cause. All the wrong
  diagnoses are left in the ledger, superseded rather than deleted.
- **A component cannot be inserted into a Gallery or a Form** (MS Learn known limitation #4).
  `cmpProjectStatus` would not land; the glyph is now a plain `Image` + SVG data URI inlined in
  the template. The validator now FAILS on it.
- **`Under Review` projects were invisible** — an Or-of-equals allow-list fails CLOSED and says
  nothing. Any value added to `project_phase` in SharePoint must be added to `ActiveProjects`,
  to scrProjects' four branches and to the glyph `Switch` in the same pass.
- **Column collisions on scrProjects** came from mixing proportional and edge-pinned anchoring —
  clear at 1318px, overlapping below ~850. Collision arithmetic run at ONE width proves nothing.
- **`Choices(col)` returns only `Value`** — no Id column. `cmpSelection` needs `{Id, Label}`, so
  the Id is synthesised positionally with `Sequence(CountRows(ch))` + `Index(ch, n)` and the
  default is looked up BY LABEL.
- **`GridLayout` span did not render full width** — dropped the grid and hoisted `colIssType`
  out rather than guess again.
- The validator caught `FillPortions`/`LayoutMinHeight` on a `cmpSelection` INSTANCE — invalid
  instance properties that would have failed the paste.
- **The old freeze rule was an inference written in the voice of its citation.** A false claim
  with a true quote attached survives review longer than one with no evidence at all.

## State at end
- 22/22 files valid. All work committed on `main`; HEAD `ba260fc`.
- Paste in progress — `scrProjects`, `scrProject`, `scrProjectEdit`, `scrIssueEdit` and
  `cmpSelection` all carry logic changes, none of it cosmetic.
- The user reports `galProjects.Y` "always goes to 193" in Studio. Nothing in the source can
  evaluate to 193 and `193` appears nowhere in `src/`; 193 is exactly the pre-rework
  `SearchBox.Y + Height + Gap`. Most likely a name collision — the pasted gallery landed as
  `galProjects_1` and the panel is reading a surviving old control. Diagnostic handed to the
  user: search the Studio tree for `galProjects`, read `Y` in the FORMULA BAR not the position
  box, and set it from the formula bar. A rename in source is offered but not done.

## Open threads
- **`galProjects.Y` = 193** — awaiting the Studio tree check above.
- **Owed in SharePoint:** set the `project_phase` column default to `Not Started`.
- **Unverified:** whether the live `issue_status` / `issue_type` / `issue_impact` values match
  `schema.yaml`. The pickers read from the columns now, but `OpenIssues`, the status glyph and
  the impact sort still carry literals that fail closed.
- **Studio housekeeping:** delete the six superseded components. `cmpSelection`'s file stays
  until the converted screens land.
- **Untested follow-up** from the freeze probe: whether a reference to a name *not in the paste*
  is what gets replaced by a constant.
