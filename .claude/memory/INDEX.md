# MEMORY INDEX  ·  keep ≤ ~80 lines

> Everything before 2026-08-13 lives verbatim in `sessions/ARCHIVE-2026.md` — the
> full 236-entry Decisions ledger, 46 Threads and 45 Log pointers, unedited.
> Below is only what a session still needs in context. Search the archive for
> anything older; do not reconstruct it from here.

## State            (rewrite in place — current truth only, ≤ ~10 lines)
- **BUILT — editing and refining, not creating.** 11 screens, 10 components, the App object.
  22/22 valid. **The published app renders properly** (user, 2026-08-12).
- **App object is two formula-bar properties:** `OnStart` holds the constants (`gTheme`,
  `gNavMenu`, `gStageWeights`, `gClaimPrefix`, `gUserEmail`, `gHasPowerBiLicence`); `Formulas`
  holds only the three data-source filters, which **must stay named formulas**.
- **Paste in progress.** Landed: `App.OnStart`, `cmpAppBar`. Remaining: `cmpPicker`,
  `cmpLookupField`, `cmpNestedSelect`, `cmpToast`, then EVERY screen — `scrHome` was the
  last one not on the queue and it is now a full rework. `scrProjects` is a full rework;
  `scrProject` / `scrIssueEdit` / `scrTransactionEdit` / the picker screens carry LOGIC
  fixes, so none of it is cosmetic.
- **`project_phase` is DERIVED BY THE APP, not picked** (2026-08-13): open issue -> Stalled;
  started task or any transaction -> Active; any child -> Planning; nothing -> Not Started.
  Vocabulary is exactly Not Started · Planning · Active · Stalled · Complete · Archived.
  Complete comes ONLY from scrProject's Mark-complete button; Archived ONLY from an external
  flow, which now also owns the three `*_project_archived` child flags. Complete and Archived
  are terminal. PENDING IN SHAREPOINT: set the column default to `Not Started`. **No orphaned controls: the user DELETES a screen before pasting it back.**
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
- [2026-08-13] **THE APP NO LONGER ARCHIVES ANYTHING, AND THAT MOVED A LOAD-BEARING JOB OUT OF IT.** Removing scrProjectEdit's phase picker also removed the only place the app wrote `project_phase`, and therefore the cascade that mirrored it onto `task_/transaction_/issue_project_archived`. **Those three flags are what let every cross-project query exclude archived work with a delegable `= false` instead of a join — the external cleanup flow now owns BOTH halves, and a flow that sets the phase without the child flags leaves the children in every query.** The column's whole vocabulary is **Not Started · Planning · Active · Stalled · Complete · Archived** (user-confirmed); `Under Review` and `Blocked` are gone from it and from every enumeration. **`ActiveProjects` is now that list minus Archived, so it must be kept in step with the column — an allow-list fails CLOSED, and a value added in SharePoint and not added there vanishes from the app rather than erroring** — INDEX Decisions
- [2026-08-13] **ROOT CAUSE, CONFIRMED FIXED — `Selected` was never declared as an OUTPUT property in Studio.** A custom property of any other kind cannot reference the component's own controls, so the formula was rejected and every consumer read BLANK: issue type and impact silently not writing, status coming back empty so the form said "needs status". **A component crosses the gap in TWO parts and only the CONTROLS paste — every custom property is declared and typed by hand, so this repo can be correct while Studio is not, silently.** Check the property KIND before touching a screen. The two entries below were both wrong about the cause: neither the control type nor the vocabulary was at fault. Checklist now lives at the top of `cmpSelection.pa.yaml` — INDEX Decisions
- [2026-08-13] **PARTLY WRONG (see above) — the cmpSelection conversion below was a fix for the wrong problem.** `issue_type` was not landing because the strip's LITERAL option list did not match the live column, so the app wrote a label the Choice would not accept. The controls are back to `cmpSelection`, now fed from `Choices()`. **`Choices()` returns only `Value`, and cmpSelection needs `{Id, Label}` — synthesise the Id POSITIONALLY with `Sequence(CountRows(ch))` + `Index(ch, n)`, and look the default up BY LABEL, because those Ids depend on the order SharePoint returns.** The lesson is about diagnosis, not controls: **the user's own follow-up ("use Choices") named the cause, and I kept acting on my earlier timing hypothesis instead of re-reading it** — INDEX Decisions
- [2026-08-13] **SUPERSEDED BY THE LINE ABOVE — plausible but never evidenced.** `cmpSelection` RAISES OnChange BEFORE ITS OWN OUTPUT SETTLES. `optBtn.OnSelect` is `Select(Parent); cmpSelection.OnChange()`, so a consumer's `Set(gX, sel.Selected.Label)` reads `Selected` in the same behaviour chain that just changed it — and can get the PREVIOUS pick. **It fails SILENTLY: the strip highlights correctly while the global, and therefore the write, holds something else.** `issue_status` was moved to a `ModernCombobox` on 2026-08-12 and has been right since; `issue_type` (user-reported not landing) and `issue_impact` followed on 2026-08-13. **`selTxCurrency` on scrTransactionEdit is the last consumer left on the strip** — same defect, on a REQUIRED column. Prefer `ModernCombobox@1.1.1` for any single-select bound to a global — INDEX Decisions
- [2026-08-13] **A CHOICE VALUE THE APP DOES NOT ENUMERATE IS INVISIBLE, NOT BROKEN.** `project_phase` had `Under Review` and `Not Started` live in SharePoint while `schema.yaml` listed neither, so `ActiveProjects` — which enumerates phases because `<> "Archived"` will not delegate — silently dropped every Under Review project from every screen in the app. **An Or-of-equals allow-list fails CLOSED and says nothing.** Any value added to that column must be added to the named formula, to scrProjects' four branches, to scrProjectEdit's picker and to the status-glyph Switch in the same pass. The glyph is the only one of those that fails loudly — an unlisted phase renders "?" — INDEX Decisions
- [2026-08-13] **MIXING PROPORTIONAL AND EDGE-PINNED ANCHORING IS THE COLLISION BUG.** `scrProjects` had `rowDue` at `X = TW*0.54, Width = TW*0.26` beside `rowPercent` pinned to the right edge with a FIXED 160px. Both are individually reasonable; together they converge as the container narrows — clear at 1318, overlapping below ~850. **Collision arithmetic run at ONE width proves nothing; the question is always "at which width does this first collide".** Fixed by making the row an auto-layout container: children carry no X, so overlap is structurally impossible. Every column is `FillPortions` + `LayoutMinWidth`, because a child of an auto-layout container is flexible by default and a declared `Width` alone is advisory — INDEX Decisions
- [2026-08-13] `StartsWith(col, "")` is TRUE for every row, so a default page and a search are ONE branch — `FirstN` picks the cap. This is what let cmpPicker open with rows in it without a second query path — INDEX Decisions
- [2026-08-13] **THERE IS NO DELEGABLE SINGLE QUERY FOR "CHILDREN OF THE PROJECTS I MANAGE".** No `issue_project_manager` column exists, and `issue_project_id.Id in colMyProjects.ID` does NOT delegate — it caps at the data row limit and UNDERCOUNTS SILENTLY. The shape that works is one delegable round trip PER PARENT: `Sum( ForAll(colMyProjects As p, CountRows(Filter(OpenIssues, issue_project_id.Id = p.ID))), Value )`. MS Learn: "if the result of the formula is a single value, the resulting table is a single-column table" — the column is `Value`. **Cost scales with how many projects one person manages, not with the size of the child list** — the trade to check before reusing this — INDEX Decisions
- [2026-08-13] **SVG CHARTING IS THE NATIVE, LICENCE-FREE CHART LAYER, AND `Concat` IS THE WHOLE UNLOCK.** `Concat(Table, Formula, Separator)` emits ONE SVG ELEMENT PER ROW, which is the difference between a KPI ring and a chart. Three things come with it: a row gets a POSITION only via `Sequence(CountRows(src))` + `Index(src, Value)` (**Index ERRORS out of range, it does not return blank** — take the count from the table Index reads); a part-to-whole chart needs a RUNNING TOTAL, which Power Fx has no primitive for, so each row does `Sum(Filter(cats, i < r.i), n)` with the outer scope named `As r` or the inner Filter shadows it, `Coalesce`d because Sum of an empty table is blank; and categories must be a WRITTEN-OUT literal table, never `GroupBy` — a group only exists where a row exists, so GroupBy drops empty categories and can RECOLOUR one between two refreshes. **NEVER INTERPOLATE A FRACTION — scale the viewBox instead.** A bare fraction takes the VIEWER'S decimal separator; `Text(v, "[$-en-US]0.#", "en-US")` is the documented cure and is the WRONG TRADE, because **an attribute Power Fx cannot render comes out EMPTY, and empty attributes delete geometry rather than degrade it** — `width=''` draws no rect, and `stroke-dasharray=''` draws a SOLID RING in the last slice's colour. Scale the viewBox until integers are precise enough (x10 gives a donut a tenth of a percent) and keep `Text` for label text only. **Also keep `stroke-dashoffset` POSITIVE with `Mod(1250 - cum, 1000)`** — negative is an SVG 1.1 error and a renderer that clamps it to 0 stacks every later slice at the same angle. **And give every category allow-list an "Other" bucket**: without it a live vocabulary that has drifted from `schema.yaml` makes `tot = Max(1, 0)`, and then ONE matching row renders as 100% of the ring. Hard ceiling: an Image is ONE control — **no hover, no per-slice click, no animation, and no way to measure text**, so labels are budgeted by character count. Full technique in `.claude/skills/power-apps-svg/SKILL.md` — INDEX Decisions
- [2026-08-12] A gallery bound to a DATA SOURCE pages as the user scrolls, so `.AllItems` is what is on screen, not the total. Count from the query — INDEX Decisions
- [2026-08-12] A global's type unifies across every `Set`; one name holding differently-shaped records is a type conflict — INDEX Decisions
- [2026-08-06] Modern controls are ON in this tenant — ARCHIVE
- [2026-08-13] **A COMPONENT CANNOT BE INSERTED INTO A GALLERY OR A FORM** (MS Learn, canvas component known limitations #4 — user hit it landing `cmpProjectStatus`). Per-row visuals must be plain controls inlined in the template; the status glyph is now an `Image` + SVG data URI inside `scrProjects`. **The validator now FAILS on it** — a documented, unambiguous rule is worth a hard check, unlike the geometry NOTE removed the same day — INDEX Decisions
- [2026-08-05] A component is a CONTRACT: custom properties are hand-typed in the editor, and `AccessAppScope: false` means it cannot read `gTheme` or any data source — colours are literals — ARCHIVE
- [2026-08-12] Layout formulas FREEZE at paste, so cross-control geometry references can land as a constant that was never correct — ARCHIVE
- [2026-08-13] **SUPERSEDES THE LINE ABOVE — it was FALSE.** A probe in Studio (`tests/README.md`) showed layout formulas cross a paste LIVE, forward references included: changing an input MOVED the controls, which a constant cannot do. What replaces a formula with a number is **DIRECT MANIPULATION** — drag, resize handle, or the position/size boxes in the properties pane; the formula bar keeps what you type. The old rule was an inference written in the voice of its citation, so every later reader checked the quote, saw a real Microsoft sentence, and moved on. **A false claim with a true quote attached is more durable than one with no evidence at all** — INDEX Decisions
- [2026-08-12] COMMENTS ARE NOT A CHANGELOG (now enforced in CLAUDE.md): git holds history, `.claude/memory/` holds reasoning, comments hold constraints — ARCHIVE

## Threads          (open items; remove when closed)
- **`cmpStatusCard` and `cmpConfirmDialog` now have NO consumer in `src/`** — scrHome's
  rebuild dropped both (inert cards are plain containers; the archive button and its
  confirm modal are gone). Files kept; Studio housekeeping candidates.
- **ASSUMED, not confirmed: "issues I own" = `issue_assignee`**, not `issue_owner`.
  issue_owner is the un-indexed who-raised-it stamp and an Or-arm on it kills delegation.
- **scrHome's three SVG charts are on their SECOND correction.** Reported: the donut showed a
  phantom category and then turned entirely one colour when a task was added; the timeline drew
  only its grey tracks. All three symptoms are what EMPTY attributes look like, so every
  fractional coordinate is gone. **Still unconfirmed which of the three causes was actually at
  work** — the empty-attribute theory, the negative dashoffset, or a live `task_stage`
  vocabulary that does not match `schema.yaml`. The new "Other" slice answers the third on
  sight, and `colTimeline` is now inspectable in Studio's Collections pane.
- **The records track "IN STUDIO", never "PUBLISHED" — different apps.** Studio runs the latest
  SAVED version, end users the last PUBLISHED one. Record both, separately.
- **Six superseded COMPONENTS to delete in Studio** — `cmpPeoplePicker`, `cmpRecordPicker`,
  `cmpUiKit`, `cmpEditableGrid`, `cmpStatusPill`, `cmpChoicePill`. Instance-free but still
  shipping inside the `.msapp`.
- **UNTESTED follow-up to the freeze probe:** a reference to a name that is NOT in the paste at
  all. The probe only covered references that resolve. If an unresolvable one is what gets
  replaced by a constant, the 2026-08-04 `Y=193` report is fully explained and the rule becomes
  "relative geometry is fine as long as the name survives the paste".
- **`galProjects.Y` reads 193 in Studio, not the authored 210.** Nothing in the current source
  can evaluate to 193 and the literal appears nowhere in `src/`; 193 is exactly the PRE-REWORK
  `SearchBox.Y + Height + Gap`. Working theory: a NAME COLLISION — control names are unique
  app-wide, so a surviving `galProjects` forces the pasted one to `galProjects_1` and the panel
  keeps reading the old control. Awaiting a Studio tree search for the name. A rename in source
  (`galProjects` → e.g. `galPrjList`, plus four `=galProjects.*` refs in `ProjectsEmptyLabel`)
  is the permanent fix if confirmed.
- **OWED IN SHAREPOINT:** set the `project_phase` column default to `Not Started` (the value
  itself already exists).
- **`cmpSelection` is IN USE and WORKING** — issue status/type/impact, transaction currency,
  and now task stage/health/priority, all fed from `Choices()`. Fixed 2026-08-13 by declaring
  `Selected` as an Output property in Studio. Do not convert these to comboboxes; the control
  was never the fault. **The strips carry no colour input**, so scrTaskEdit's stage/health/
  priority lost the value-coloured text the comboboxes had.
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
- 2026-08-13 | scrProjects rebuilt on auto-layout after the columns were found to collide below ~850px TemplateWidth; vertical stack now relative; status SVG inlined (a component cannot go in a gallery) | INDEX Decisions 2026-08-13
- 2026-08-13 | scrProjects reworked: coverage filter + show-completed toggle + six-column rows; new SVG cmpProjectStatus; project_phase gains "Not Started" as default | INDEX Decisions 2026-08-13
- 2026-08-13 | layout formulas SURVIVE a paste (probe run in Studio); design + transfer skills, validator check, build-history row and src comments all corrected | tests/README.md
- 2026-08-13 | cmpPicker opens on the first 10 records (current user for person fields); record branches un-gated from query length | INDEX Decisions 2026-08-13
- 2026-08-13 | INDEX pruned 620 lines/231KB to ~80; full prior contents archived verbatim | sessions/ARCHIVE-2026.md
- 2026-08-13 | project_phase derived in-app + Mark-complete button; cmpSelection root cause (Selected not an Output property); scrProject galleries rebuilt; scrProjects reworked | sessions/2026-08-13-1724-project-phase-derivation-and-selection-fix.md
- 2026-08-13 | scrHome rebuilt as a dashboard: four inert cards, my-tasks/my-issues galleries routing to the parent project, chart placeholders + the KPI ring; archive button and confirm modal removed | sessions/2026-08-13-1739-scrhome-dashboard.md
- 2026-08-13 | scrHome chart placeholders replaced with real SVG charts; power-apps-svg skill gains the data-driven section (Concat, Sequence+Index, running totals, literal category tables, the locale decimal trap) | .claude/skills/power-apps-svg/SKILL.md
- 2026-08-13 | scrTaskEdit stage/health/priority converted from ModernCombobox to cmpSelection strips fed from Choices(); stage hoisted to its own full-width row | INDEX Threads
