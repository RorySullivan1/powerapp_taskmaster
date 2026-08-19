# 2026-08-19 00:19 · backlog-ordering

**Goal:** Review open issues, order the development, and build #9

## What happened
Read the remote backlog and ordered it. **Only #9 and #11 are open** — #10, #12–#17 are all
closed. No code was written; this session produced the sequencing and the findings below.

**Agreed order: #9 first, then #11 in five steps.**

#9 (scrIssueEdit) leads because it is the only WRITE-PATH change on the board and #11 is
entirely read-path. Every day `issue_date_close` is hand-entered or forgotten poisons the data
any future issue-cycle report reads. Fix the writer before reworking the readers.

#11 (scrReports) in five steps, **subtract before adding**:
1. **Drop** median cycle time by activity family (band 3 col 3, ~`:1814`–1886) and the coverage
   gap x product type grid (inside `pnlRptTx`), INCLUDING their folds in `btnRptLoad` (~`:562`–598).
   The median drop frees the band-3 column slot the requestor and region charts move into, so the
   grid geometry is computed once, not twice.
2. **Extend the data layer** — one paste of `btnRptLoad.OnSelect`. Invisible by design: no pixel
   changes, so the only signal is "nothing regressed", which is what you want from the riskiest region.
3. **People (band 2)** — flagged as WRONG, not merely missing. A misleading number beats an absent
   one. Also deletes ~430 lines of person overlay (`:2333`–2760).
4. **Task grouping (band 3)** — output pie, requestor column, region-L1 pie. 3 columns become 4.
5. **Transactions (band 5)** — product-type pies (L1+L2), currency-coloured bars. Last so the pie
   renderer is proven in step 4's simpler section (single-level path, no join) before step 5 asks
   it to carry a two-level path AND a `transaction_product_id` join.

**#9 IS BUILT, LANDED AND EXERCISED** (`b46a17a`; landed 2026-08-19, all four checks clear). Plan posted on the issue first and confirmed by the
user ("remove the opened by box outright"). Removed `lblIssCloseCap`/`dtpIssClose`, the
`Reset(dtpIssClose)`, and `colIssOpened` with its provenance comment; `colIssAssignee` took the
whole of `rowIss6`; `gridIss5` KEPT its two columns so Related transaction holds its width and
stays aligned under Related task. 22/22 valid.

**The late hardening that matters:** the derived date reads the stored value with
`LookUp(taskmaster_issues, ID = gEditIssue.ID, issue_date_close)`, NOT `gEditIssue.issue_date_close`.
`gEditIssue` is set once, on scrProject (`:1761`), and carried across the screen boundary in a
global — and now that NO CONTROL reads `issue_date_close`, that is precisely the record shape
Explicit Column Selection trims. Off the snapshot the Coalesce would have seen blank and restamped
`Now()` on every save, defeating the preserve branch IN SILENCE. The LookUp also fixes
close-reopen-close inside one session, which off the snapshot restored the original date.

## Gotchas & dead ends
- **THE PIE PROBLEM IS ALREADY SOLVED — DO NOT WRITE ARC PATHS.** `scrReports.pa.yaml:1645`
  requires every SVG coordinate to be a whole number: a fraction goes through `Text()`, which drags
  the locale decimal separator into an attribute, and an attribute Power Fx cannot render comes out
  EMPTY (`width=''` is not a thin rect, it is no rect). `Cos`/`Sin` arc endpoints are exactly that
  hazard, hit four times over. **`cmpKpiRing.pa.yaml:65` already dodges it**: `stroke-dasharray` on a
  circumference-100 circle (`r=15.9155`), integer percentages only. A pie is N stacked circles with a
  running `stroke-dashoffset` — no arcs, no fractions, and the technique is already landed in Studio.
- **#9 is NOT a pure deletion.** Removing `dtpIssClose` means `issue_date_close` (`:799`) needs a
  derived write: stamp `Now()` when `gIssStatus` crosses into a `Closed - *` value and is not already
  stamped, clear on reopen. Follow the insert-only provenance Patch at `:822`. Also: `lblIssCloseCap`
  /`dtpIssClose` and the `lblIssOpenedCap` block both sit in `gridIss5` column 2, so removal leaves an
  empty grid column that needs re-flowing, and `Reset(dtpIssClose)` at `:112` must go too.
- **"Supports looks wrong" may be DATA, not code.** `task_supporter` was deleted and recreated
  2026-08-17, discarding every stored value (#10). If it was not back-filled, a correct report over an
  empty column looks identical to a broken one. CHECK THE COLUMN BEFORE REWRITING THE MEASURE —
  otherwise step 3 chases a phantom.
- **`colRptPrj` is the hand-written `ForAll` projection**, the exact spot that already bit us with the
  ShowColumns-over-a-bare-named-formula bug (`:141`–152). Adding `project_requestor` and
  `project_region_path` there is the fragile part of step 2 — do it once, deliberately.

## State at end
- **Memory was stale and is now corrected: #14 is CLOSED (completed, by user, 2026-08-18 13:35).**
  The State block said it was open with the cause unknown. It is not.
- Nothing authored, nothing pasted. The paste queue is still empty. Working tree clean at `43c2155`.
- Columns #11 needs but the load does NOT currently fetch: `project_requestor`, `project_region_path`
  (both absent from `colRptPrj`), `task_date_start` (absent from `colRptOpen`, needed for "date opened"
  in the new person task gallery). Everything else — `transaction_currency`, `product_type_path`,
  `transaction_product_id` — is already fetched; those need folds, not fetches.
- The `Find`/`Left` path-splitting helper at `:203` already generalises to region L1 and product L2.

## Open threads
- **BLOCKS STEP 2 — "Open tasks by output": format or audience?** The existing chart is "Open tasks
  by output format" (`:1754`), but `task_output_audience` went live with #13 and NOTHING on this
  screen fetches it. The answer changes step 2's projection. Does not block step 1.
- **Decide whether to drop the per-person `Tx` column entirely** rather than fix it. It attributes
  through PROJECT management, not task work (`Filter(colRptPrjMap, Mgr = ... || Sup = ...)`, `:373`),
  which is probably why the user says it "does not make sense". Note the schema is explicit that
  `transaction_sales` is sales-side and must never become a desk-workload attribution path.
- **Completion measures may be silently dropping rows.** `Owns`/`Sups` already count completed tasks
  (2026-08-18 change), but `Dn`/`Med`/`OnTp` come from `colRptDone`, bounded by
  `task_date_completion >= gRptFrom` — so a task completed with a BLANK completion date is invisible
  to every completion measure. Cheap to check; a plausible direct cause of "done, median days,
  on-time do not make sense".
- Chart type for "Open tasks by requestor" is unspecified in #11. Recommended a ranked BAR, not a pie:
  requestor cardinality is open-ended and a pie needs few slices.

## Outcome
#9 landed first try and all four checks cleared — new issue saves with no resolution field, the
close stamps, **the re-save does NOT move the date**, and the reopen clears it. That third check
is the one worth remembering: it is the direct evidence that reading the stored value through
`LookUp(taskmaster_issues, ID = gEditIssue.ID, issue_date_close)` was necessary. Had the formula
been left on `gEditIssue.issue_date_close` as first planned, ECS would have trimmed the column off
a record no control reads any more, the Coalesce would have seen blank, and the date would have
crept forward on every save — passing every OTHER check while failing silently on that one.

`main` was fast-forwarded to `b7aa4ca` at the user's explicit request and the paste came from there.
