# MEMORY INDEX  ·  keep ≤ ~80 lines

> Everything before 2026-08-13 lives verbatim in `sessions/ARCHIVE-2026.md` — the
> full 236-entry Decisions ledger, 46 Threads and 45 Log pointers, unedited.
> Below is only what a session still needs in context. Search the archive for
> anything older; do not reconstruct it from here.

## State            (rewrite in place — current truth only, ≤ ~10 lines)
- **BUILT — editing and refining, not creating.** 11 screens, 11 components, the App object.
  23/23 valid. **The published app renders properly** (user, 2026-08-12).
- **App object is two formula-bar properties:** `OnStart` holds the constants (`gTheme`,
  `gNavMenu`, `gStageWeights`, `gClaimPrefix`, `gUserEmail`, `gHasPowerBiLicence`); `Formulas`
  holds only the three data-source filters, which **must stay named formulas**.
- **Paste in progress.** Landed: `App.OnStart`, `cmpAppBar`. Remaining: `cmpPicker`,
  `cmpLookupField`, `cmpNestedSelect`, `cmpToast`, the NEW `cmpProjectStatus`, then every
  screen but `scrHome`. `scrProjects` is a full rework; `scrProject` / `scrIssueEdit` /
  `scrTransactionEdit` / the picker screens carry LOGIC fixes, so none of it is cosmetic.
- **SharePoint matches `schema/schema.yaml`** — archived columns and the Choice-value edits
  are applied. **No orphaned controls: the user DELETES a screen before pasting it back.**
- Six superseded components still ship inside the `.msapp` — see Threads.

## Decisions        (append-only; supersede, never delete)
Pre-2026-08-13 entries: `sessions/ARCHIVE-2026.md`. Kept here because a session that does
not know them will author something broken:
- [2026-08-12] `gTheme`, never `Theme` — `Theme` collides with modern theming (`App.Theme`, theme objects loaded by instance name). Studio TOLERATES it silently; the player does not — ARCHIVE
- [2026-08-12] Constants live in `App.OnStart`, not `App.Formulas` — named formulas did not resolve in the published app. But `Set(x, Filter(...))` captures a TABLE VALUE and filtering a variable does not delegate, so `ActiveProjects`/`OpenIssues`/`LiveTasks` must NOT move — ARCHIVE
- [2026-08-12] Archiving happens at the PROJECT level. `*_project_archived` on each child list is a denormalised mirror, indexed, so the exclusion delegates — a join would not. Aim: keep rows in scope under 2000 — ARCHIVE
- [2026-08-12] `'Created By'` / `Created` DO NOT RESOLVE in the canvas app. On `taskmaster_issues`, `issue_owner` IS the created-by. **The columns the list has and the columns the app can see are not the same set** — INDEX Decisions
- [2026-08-12] A field NAMED in a `Patch` is written. To leave a column alone on edit, OMIT it — hence provenance goes in a second, insert-only Patch — INDEX Decisions
- [2026-08-12] `gStageWeights` survivors keep their ORIGINAL numbers. Re-spacing would move every stored `project_perc_completion` without a task changing — ARCHIVE
- [2026-08-12] Hover states have no safe defaults on a transparent or layered control: Button derives `HoverFill` from `Fill` (dim 20%), Icon derives `HoverColor` from `Color`. Write them explicitly — INDEX Decisions
- [2026-08-12] `Classic/Icon` DOES accept `HoverFill`/`HoverColor`/`HoverBorderColor` (user-confirmed). **MS Learn's per-property "Applies to" lists are incomplete — an omission means UNCONFIRMED, not unsupported** — INDEX Decisions
- [2026-08-12] `AccessibleLabel` is modern-only (classic takes `Tooltip`); `SetFocus` cannot target a control inside a Gallery, form, Component or Container. Both rejected by Studio — ARCHIVE
- [2026-08-12] Only `=` delegates on `ID`; `<>` does not. A non-delegable clause added to make a check STRICTER makes it weaker, because the query it poisons IS the check — INDEX Decisions
- [2026-08-09] The three `*_project_id` lookups DISPLAY the numeric ID, not the name. Screens resolve it app-side with `LookUp(taskmaster_projects, ...)`. **Two reviewers have flagged that as waste by trusting the schema comment** — ARCHIVE
- [2026-08-03] `Sort(If(...))` does NOT fold — the Sort must sit INSIDE each branch — ARCHIVE
- [2026-08-03] Person writes use the expanded-user shape with `gClaimPrefix & Lower(mail)` and the `'@odata.type'` tag — ARCHIVE
- [2026-08-13] `StartsWith(col, "")` is TRUE for every row, so a default page and a search are ONE branch — `FirstN` picks the cap. This is what let cmpPicker open with rows in it without a second query path — INDEX Decisions
- [2026-08-12] A gallery bound to a DATA SOURCE pages as the user scrolls, so `.AllItems` is what is on screen, not the total. Count from the query — INDEX Decisions
- [2026-08-12] A global's type unifies across every `Set`; one name holding differently-shaped records is a type conflict — INDEX Decisions
- [2026-08-06] Modern controls are ON in this tenant — ARCHIVE
- [2026-08-05] A component is a CONTRACT: custom properties are hand-typed in the editor, and `AccessAppScope: false` means it cannot read `gTheme` or any data source — colours are literals — ARCHIVE
- [2026-08-12] Layout formulas FREEZE at paste, so cross-control geometry references can land as a constant that was never correct — ARCHIVE
- [2026-08-13] **SUPERSEDES THE LINE ABOVE — it was FALSE.** A probe in Studio (`tests/README.md`) showed layout formulas cross a paste LIVE, forward references included: changing an input MOVED the controls, which a constant cannot do. What replaces a formula with a number is **DIRECT MANIPULATION** — drag, resize handle, or the position/size boxes in the properties pane; the formula bar keeps what you type. The old rule was an inference written in the voice of its citation, so every later reader checked the quote, saw a real Microsoft sentence, and moved on. **A false claim with a true quote attached is more durable than one with no evidence at all** — INDEX Decisions
- [2026-08-12] COMMENTS ARE NOT A CHANGELOG (now enforced in CLAUDE.md): git holds history, `.claude/memory/` holds reasoning, comments hold constraints — ARCHIVE

## Threads          (open items; remove when closed)
- **The records track "IN STUDIO", never "PUBLISHED" — different apps.** Studio runs the latest
  SAVED version, end users the last PUBLISHED one. Record both, separately.
- **Six superseded COMPONENTS to delete in Studio** — `cmpPeoplePicker`, `cmpRecordPicker`,
  `cmpUiKit`, `cmpEditableGrid`, `cmpStatusPill`, `cmpChoicePill`. Instance-free but still
  shipping inside the `.msapp`.
- **UNTESTED follow-up to the freeze probe:** a reference to a name that is NOT in the paste at
  all. The probe only covered references that resolve. If an unresolvable one is what gets
  replaced by a constant, the 2026-08-04 `Y=193` report is fully explained and the rule becomes
  "relative geometry is fine as long as the name survives the paste".
- **Three auto-layout containers have BOTH children unpinned** (`colIssType` among them) —
  unpinned children split space evenly and ignore declared heights.
- **The Choice columns that replaced Managed Metadata (2026-08-10) have no recorded internal
  names** — verify against SharePoint before any formula binds them.
- **Column-token validator write-time hook** — proposed in CLAUDE.md, not built. "Never invent a
  column name" is prose a model can drift past; a hook would make it enforced.
- **App and Power BI disagree on blank vs zero**: the app shows `Coalesce(project_perc_completion, 0)`
  so a project with no tasks reads 0%, while Power BI sees blank and excludes it from averages.
- **Power BI owes the blended notional** (an FX dimension: currency, rate, as-of date).
- **One Power Automate flow to author:** the list-provisioning flow.
- **Known edge, accepted:** an issue whose linked task/transaction belongs to a DIFFERENT project.
- Open questions Q3–Q10, Q13, Q2b (PBI workspace/refresh/embed) — see `.claude/context/open-questions.md`.

## Log              (append-only pointers)
Pre-2026-08-13 pointers: `sessions/ARCHIVE-2026.md`.
- 2026-08-13 | layout formulas SURVIVE a paste (probe run in Studio); design + transfer skills, validator check, build-history row and src comments all corrected | tests/README.md
- 2026-08-13 | cmpPicker opens on the first 10 records (current user for person fields); record branches un-gated from query length | INDEX Decisions 2026-08-13
- 2026-08-13 | INDEX pruned 620 lines/231KB to ~80; full prior contents archived verbatim | sessions/ARCHIVE-2026.md
