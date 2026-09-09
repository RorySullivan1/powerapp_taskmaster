# 2026-09-08 17:24 · epic66-probes-authored

**Goal:** Author the three #67 probes that unblock epic #66

## What happened
- Epic #66 was filed 2026-09-04 with nothing authored. #67 blocks the build, so #67 is what
  "move forward with #66" means. Four files written, all validated, nothing in `src/` touched
  (probes live in `tests/`, which the validator does not scan — still 22/22).
- `tests/cmpProbeTable.pa.yaml` — ONE throwaway component definition serving BOTH component
  probes. Three Table Inputs (`RowsFlat`, `RowsRich`, `RowsCtl`), because a component input's
  TYPE IS ITS DEFAULT LITERAL and the three candidate contracts have three different shapes.
  Separate properties rather than one retyped property, so a partial result stays readable.
- `tests/scrProbe-component-table-input.pa.yaml` (`scrProbeCT`) — claim 1. The instance is pasted
  with NO inputs set; each candidate is hand-typed into the formula bar. Adds row **1d**,
  `ShowColumns(...)`, which is not in #67: it is the only candidate that could give both an exact
  schema and a live query.
- `tests/scrProbe-component-gallery-paging.pa.yaml` (`scrProbeCG`) — claim 2. G1 direct-bound
  (positive control), G2 inside the component (verdict), G3 `ForAll` projection (negative
  control), each with a `CountRows(gal.AllItems)` readout.
- `tests/scrProbe-sortbycolumns-dynamic.pa.yaml` (`scrProbeSBC`) — claim 3. L0 literal/literal,
  L1–L3 literal column with variable order, V fully variable, NC the same formula over a `ForAll`
  projection. Column and order are set by on-screen buttons; a probe screen's `OnVisible` cannot
  be pasted.
- `tests/README.md` gains a combined `#67` section: the shared instrument, one block per probe,
  the protocol, and the how-to-read ladders. All three marked NOT YET RUN.

## Gotchas & dead ends
- **THE DEPARTURE THAT MATTERS: lower the data row limit to 10 instead of bounding the subset.**
  #67 asked for a bounded phase subset read against a screen gallery. No phase's size is knowable
  from this side of the gap, and — worse — at the normal 2,000 limit a cap and a small result set
  are indistinguishable, which is why this question has never been settled. With the limit at 10,
  a capped gallery reads exactly 10 and nothing else does, and a delegated descending sort can be
  told from a local one by two printed names. It also serves claims 2 and 3 at once, so the
  setting changes once per sitting.
  **IT IS APP-WIDE. It must be put back, and the original value written down first.**
- **Geometry: the component's sizes had to become formulas off `Parent`.** One definition serves
  two screens at different instance heights; fixed heights would put the galleries' own bottom
  edge outside the shorter instance, and the last row — the row claim 2 is read from — would land
  in the clipped strip and be unreadable while looking fine.
- **Dropped `RowsCtl` from the claim-2 paste.** It was set alongside `RowsFlat` at first, but the
  component has no gallery bound to it, so it produced no count — it only added a second way for
  the paste to fail. G3 on the screen already is the projection control.
- Considered switching one in-component gallery between the two schemas by formula. `If()` over
  two tables of DIFFERENT shapes is a type error, so the component carries two galleries instead.
- The prefix box must never be left empty on any of the three: `StartsWith(project_name, "")` is
  rejected outright (`scrProbe-startswith-empty`, 2026-09-04) and would take every row down.

## State at end
- Four files added under `tests/`, validator 22/22 (unchanged — `tests/` is not scanned).
- Committed and pushed to `claude/powerapp-repo-init-xymvlm`.
- **NOTHING HAS BEEN RUN.** #67 is authored, not answered. #68 and #69 stay blocked until the
  three results are recorded in `tests/README.md` and a Decision names which of #66's three
  contract outcomes applies.

## Open threads
- The run itself, which only the user can do: build `cmpProbeTable` in Studio (three custom
  properties hand-typed), paste its Children, then the three screens, then the protocol.
- Everything already open before this session is untouched: the 2026-09-04 paste queue (six edit
  screens + `scrReports`, `transaction_comment` needing provisioning first, the `scrProjects`
  banner on its own branch), and Item-level Permissions on `taskmaster_projectcomments`.

## Run notes — 2026-09-08, claim 1 first attempt

- **The first `scrProbeCT` run produced nothing to read: the seeded literal `"a"` is not the first
  letter of any open project.** Same shape as #51 row 6's `"ab"`.
- **I called that "the instrument being blind" and floated blank `project_phase` as the cause.
  Both were wrong, and the user corrected it.** The sheet read correctly; the letter was wrong.
  Raw list matching where `OpenProjects` does not is the phase filter doing its job — exactly
  what #51 row 6 vs 6r already showed — not a defect.
- **The cost is real even though nothing was broken:** a true no-match prints `-- no rows --` on
  every panel, which is precisely what a rejection prints, so a wrong letter burns a whole run
  across the gap.
- **Fix, and the general rule it establishes:** no project name is visible from the repo side, so
  a probe must never hard-code a data literal. All three prefix boxes now seed from
  `Left( First(taskmaster_projects).project_name, 1 )` and `scrProbeCT` prints five real names
  (row N) to widen from. Row EO keeps `OpenProjects` beside the raw list and is labelled NOT
  CLAIM 1 so the phase filter's ordinary behaviour is never read as a result.

## RESCOPED AND BUILT — 2026-09-08

**The user stopped the probe programme, and was right to.** Verbatim: "This is literally the most
confusing probe ever… This doesn't even look like what i envisioned for the projects table. It
needs to be a single table with filterable/sortable columns… i am not convinced these probes are
even moving toward that outcome."

- **The root error: I treated "the gallery becomes a new component" as a requirement when it was a
  means.** The goal was always the table. Building the epic around the component generated a
  research programme — three probe screens, a throwaway component, ten hand-typed properties, an
  app-wide setting to change and restore — and four trips across the gap that returned NO readings,
  because each was spent repairing the instrument.
- **Keeping `galProjects` on the screen deletes the risk instead of measuring it.** Claims 1 and 2
  only existed because the gallery was going to move. It pages past 2,000 today; leaving it alone
  is strictly safer than proving a component could match it.
- **Claim 3 did not need a probe either.** Whether a variable column name folds is settled by one
  gesture on the real screen (sort by name descending, check the top row), and the fallback is
  mechanical. A probe earns its cost when a wrong guess is catastrophic or invisible.
- **Built in one pass:** `rowTableHead` mirroring `rowBody`'s budget, three sort headings, coverage
  filter moved into its heading, `rowCoverage` column, `SortByColumns` across all sixteen branches
  (equivalence machine-verified by whitespace-normalised comparison), search box pinned, gallery
  moved to Y=272. `project_coverage` flipped to indexed. 22/22.
- **Grounded before use:** `Align` and `PaddingLeft` on `Classic/Button@2.2.0` — the repo had never
  landed either, and MS Learn's control-button page plus properties-text "Text placement" both name
  Button explicitly.
- #67 and #68 closed not-planned with the reasoning in their bodies; #66 rewritten; #69 is now the
  whole epic and carries the proof list.

## First paste — `SortByColumns` rejected, and why it matters beyond this screen

- **`project_name` is not a SharePoint internal name. That column is the built-in `Title`,
  renamed** (user, on the paste). `schema/schema.yaml` recorded `project_name` as though it were
  the internal name, and the golden source was wrong about it from the beginning.
- **It has been invisible for the whole life of the app** because every other formula names
  columns as Power Fx IDENTIFIERS, which resolve by DISPLAY name. The only construct that cares
  is a column name travelling as a STRING — which nothing in this app did until `SortByColumns`.
- **Fixed by removing the dependency, not by supplying internal names.** Internal names would
  work, but they would put a second naming scheme into the one formula `pre_write_column_guard.py`
  and `schema.yaml` cannot check — and only `Title` is confirmed; `project_date_target` and
  `project_perc_completion` are unverified from this side of the gap.
- `gPrjSortCol` is now a **KEY**, compared with `=` in a Switch; each arm sorts on a **literal
  identifier**, the same delegable shape the screen already shipped sixteen times. 48 branches.
  `Sort(If(...))` and an expression sort key do not fold, so the Switch has to be outside the
  filters — the duplication is the mechanism.
- **Each of the three arms was machine-verified** equivalent to the landed sixteen branches by
  whitespace-normalised comparison, so the filter logic is provably untouched by the rewrite.
- This retired the last live question from the withdrawn #67: there is no variable column name
  left, so whether one would delegate no longer matters to anything being built.

## Table landed — two corrections from the user

**"Table lands and looks good. The header does not match the width of the columns. Also why is
priority not filterable or sortable?"**

- **Header width was GUESSED and the guess was wrong.** It computed its own width and paid for the
  gallery scrollbar with `PaddingRight: =32` against the row's 16, on the assumption the scrollbar
  costs exactly 16px off `TemplateWidth`. Now `Width: =galProjects.TemplateWidth` with padding
  identical to the row, so the two containers are the same width BY CONSTRUCTION. **General rule:
  when a second container has to match a gallery row, read TemplateWidth — never re-derive it.**
  The forward reference to a later-declared control is the case scrProbe-layout-freeze P3 tested.
- **Priority was not filterable for a reason I had put in an issue instead of on the sheet** — each
  server-side predicate doubles the query, and it was a v1 non-goal. That is a cost decision, not a
  limitation, and the user could not see it from the code. Now filtered.
- **Priority sorting is refused on TWO grounds and only one is delegation.** SharePoint does not
  fold a Sort on Complex; and even if it did, the order would be ALPHABETICAL — Critical, High,
  Low, Lowest, Moderate — which is not severity order. **So this is not a delegation gap waiting to
  be closed.** It needs an indexed Number rank column, written by all six edit screens and
  back-filled across 2,000+ rows. Recorded in schema.yaml on the column itself.
- **The Items formula is now GENERATED (96 branches).** The generator was first proved to reproduce
  the landed 48-branch formula character for character, so enabling the priority dimension was a
  controlled extension rather than a rewrite. Regenerate; never hand-edit one branch.

## Internal names confirmed — 96 branches collapse to 32

- **User confirmed:** `project_priority` indexed in SharePoint; `project_date_target` and
  `project_perc_completion` internal names EQUAL their display names. With `project_name` = `Title`
  already known, all three sort columns are pinned down.
- **So the sort column can travel as a string again.** One `SortByColumns` per branch instead of a
  Switch over three literal-identifier arms: 32 branches, 443 fewer lines.
- **`gPrjSortCol` flipped meaning between two commits** — an opaque key one commit, a SharePoint
  internal column name the next. Every comment asserting the old meaning was rewritten rather than
  left standing. A stale comment that confidently states the opposite of the code is worse than no
  comment, and this file now has three places that would have said it.
- **`tools/gen_projects_items.py` added.** The formula is hundreds of near-identical delegable
  branches; hand-editing one is how the arms drift and how a filter quietly stops folding. The tool
  owns the shape AND the reasoning, `--check` fails on drift, and it was verified to reproduce the
  landed 96-branch formula character for character before emitting the 32.
- **`--mode switch` is a real fallback, not decoration.** Whether `SortByColumns` delegates with the
  column name in a VARIABLE is undocumented against SharePoint and unproven here. If the
  descending-name check fails, one flag rewrites the 96-branch literal-identifier version.
- **`project_coverage`'s SharePoint index is still unconfirmed** — the user indexed priority and
  said nothing about coverage. Do not assume.

## Confirmed working — and the probe question answered by using the app

**"Sorting works - looks good."** (user, 2026-09-08)

- **This settles the last open question on the screen, and it is the one the withdrawn probes
  existed for.** `SortByColumns` DOES delegate with the column name in a variable. MS Learn is
  silent on it, so `scrProjects` is the only evidence that exists anywhere in this project.
- **It is also the whole argument for the rescope, demonstrated.** #67 claim 3 would have cost a
  probe screen, a paste and a reading. Using the shipped screen answered it for free, because the
  fallback was cheap and mechanical (`--mode switch`) rather than catastrophic.
- **Recorded as evidence, not as a guarantee.** The failure mode if it ever stops holding is
  silent — one page sorted, the rest of a 2,000+ row list left in its old order, looking fine. The
  source and the generator both say so, and both name the check and the one-flag fallback.
- Epic #66 delivered end to end: sortable headings on the delegable set, Coverage and Priority
  filtering from their own headings, a Coverage column, 32 generated branches, both filter columns
  indexed in SharePoint. PR opened onto `main`.

## #71 — identity is three values, not one

**User report: someone with multiple addresses sees no projects of his own and a blank dashboard.**

- **Root cause is structural and was provable from the source without a repro.** The pickers write
  every Person column from `Office365Users.SearchUserV2(...).Mail` (`scrProjectEdit.pa.yaml:1998`,
  and the Patch at `:1184-1186` puts it in both Claims and Email). Every "mine" predicate read
  `User().Email`. Different Azure AD attributes.
- **Why it hid for the life of the app:** the two coincide for most people. It only appears for a
  user whose UPN differs from their primary SMTP — and then it is TOTAL rather than partial,
  because every equality in the app fails on the same mismatch at once.
- **Why it is silent:** an empty filter result is indistinguishable from "you own nothing". There
  is no error to notice. This is the same class as the delegation failures recorded elsewhere here.
- **Fix:** three identities OR'd in every predicate — `User().Email`, `MyProfile().Mail`,
  `MyProfile().UserPrincipalName`. Covers the mismatch in EITHER direction, so it does not depend
  on diagnosing which way round this particular user is.
- **The trap inside the fix:** a blank identity global would make `supporter.Email = ""` match every
  row with no supporter — optional Person columns turn a blank into a wildcard. Each global falls
  back to gUserEmail, and the generator comment says so where the predicate is built.
- **`Office365Users.MyProfile()` grounded on MS Learn before use** (no inputs; Mail and
  UserPrincipalName both outputs). The repo had only ever used `SearchUserV2`.
- **scrProject's comment gate was affected too and nobody had reported it** — `'Created By'` is
  stamped by SharePoint, a third attribute again, so the same user could not edit his own comments.
- **The regression check is half the acceptance:** a user for whom this already worked must see the
  same projects and the same KPI numbers.

## #71 pasted — 2026-09-09

All four pastes landed cleanly: `App.OnStart` via the formula bar, then `scrProjects`, `scrHome`
and `scrProject`. The three identity globals and the widened Person predicates are live.

**Landed is not fixed.** Nothing yet says the affected user can see his projects, and nothing says
a previously-working user still sees the same ones. #71 stays open on both.

## #71 confirmed fixed — 2026-09-09

**"It has landed and worked for both."** The affected user sees his projects; a previously-working
user is unchanged. Both halves reported, which is what the acceptance asked for — the regression
half was never a formality, since a blank identity global would have turned `supporter.Email = ""`
into a wildcard matching every project without a supporter.

Not separately read back: the comment author gate on `scrProject`. Same mechanism, so it should
follow, but nobody reported it.

**The standing rule this leaves behind:** any NEW predicate on a Person column ORs over all three
of `gUserEmail` / `gUserMail` / `gUserUpn`. Matching one attribute is the defect, not the baseline.
