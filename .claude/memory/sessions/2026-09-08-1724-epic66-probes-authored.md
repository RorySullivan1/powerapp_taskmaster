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
