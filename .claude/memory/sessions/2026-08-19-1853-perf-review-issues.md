# 2026-08-19 18:53 · perf-review-issues

**Goal:** Codebase-wide performance review; file GitHub issues for every meaningful enhancement

## What happened
- /code-review (perf focus: screen-transition data latency + save/upload time) reviewed all of
  `src/` and filed **#27–#35**. Seven finder-agent angles (load paths, gallery N+1, repeated
  queries, save paths, render waste, delegation ceilings, architecture) were then reconciled
  against those nine; every extra candidate was verified against source before filing.
- Verification killed two agent findings as false positives (below), confirmed the rest, and
  filed **#36–#40**: #36 taskproduct reconcile unconditional on every save, #37 scrProductEdit
  whole-list Concat per open, #38 delete-path stage serialization, #39 missing index on
  `transaction_product_id`, #40 hard-coded 2000 sentinels → `gDataRowLimit` constant.
- Corrected three filed bodies: **#27** gained the two header-label reads (lblTxTitle :1146,
  lblIssuesTitle :1418 — reads 7-8, repointed at the proposed collections); **#31** gained the
  first-visit `Concurrent()` addendum; **#34**'s claim that txtProjSearch lacked delayed output
  was wrong and was fixed.

## Gotchas & dead ends
- **"Health recompute is an N+1 over the project's tasks" is FALSE.** Every seeding site puts
  1–2 ids in `colHlTasks` (scrIssueEdit :793-796, :905; scrProject :1770) — never a whole
  project. Real cost ≈ 2-4 calls per recompute. Do not refile; the finder agents' 60-90-call
  scenario assumed a seeding that doesn't exist.
- **"The hidden picker keeps querying while closed" is FALSE.** `gTkPicker` is cleared on
  OnCancel (scrTaskEdit :1664), on confirm, and in OnVisible; with it empty the Results If-chain
  yields blank and no branch queries.
- Deliberately NOT filed: the scrHome donut Image formulas recompute their aggregation inline
  (client-side only, small row counts — wouldn't move perceived perf, and refactoring adds
  paste risk); a staleness guard on scrProject's repair-on-read recompute (the self-heal is
  deliberate, and #27 already collapses its cost to 3 concurrent reads).

## State at end
- **14 open perf issues, #27–#40, none built.** Biggest wins by hot path: #31+#27 (screen
  transitions), #29+#36 (task-save round trips), #30+#28+#32 (dashboard), #33 (heaviest upload).
  #39/#40 are guards; #34/#35 are scale cliffs; #37/#38 smaller.

## Open threads
- #30, if built, AMENDS the 2026-08-13 gIssLed decision (single truncation-guarded fetch, old
  per-project shape kept as the ≥2000 fallback) — record as amendment, not reversal, on landing.
- #35 and #34-option-1 each need a probe per tests/README.md before authoring.
