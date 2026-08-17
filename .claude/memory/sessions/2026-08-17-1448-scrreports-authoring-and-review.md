# 2026-08-17 14:48 · scrreports-authoring-and-review

**Goal:** Author scrReports end to end, build the person overlay, and remediate two code-review passes

## What happened
- **`scrReports` authored from scratch — ~2,560 lines, the largest screen in the repo.** Three
  commits of construction (`4016997` tranche 1 = data layer + bands 0–2, `48c1c65` tranche 2 =
  bands 3–5, `d3feb3e` the person overlay), then two review-remediation commits (`b45fc06`
  + `3749553`, and `7b4a06a`). All on `main`; 22/22 validator; globals audit clean.
- **Architecture: ONE load routine, fold once, render from folds.** The whole fetch/enrich/fold
  chain lives in a hidden `btnRptLoad.OnSelect`, reached by `Select(btnRptLoad)` from three
  callers — `OnVisible`, the period strip, and the refresh icon. No band re-queries.
- **Layout:** control bar absolute at `Y = HeaderH`; `bodyRoot` below it, vertical auto-layout,
  `LayoutOverflowY: Scroll`. Bands 0–5 stack inside it. The person overlay is a scrim plus a
  centred card, both gated on `gRptSelPerson`.
- Everything namespaced `colRpt*` / `gRpt*` — closes the latent `colMyTasks`/`colMyProjects`
  collision with `scrHome` that the pre-rebuild screen carried.
- Two `/code-review` passes at high effort: 8 findings on `4016997`, then 9 on `4016997..d3feb3e`.
  **All 17 were legitimate.** 16 fixed; 1 documented as an accepted cost.
- Also this session (pre-`scrReports`): Power BI dropped from scope entirely, `transaction_sales`
  excluded from person productivity, cross-currency settled as permanently out of scope, and
  `main` fast-forwarded to the feature branch. Those are already in INDEX Decisions.

## Gotchas & dead ends
- **`Select()` QUEUES the target's `OnSelect` — it does not run it inline and does not wait**
  (MS Learn). That is exactly why one load routine can serve three callers. The constraint that
  comes with it: **nothing may read a fold in the same formula that `Select`s the button which
  builds it.** The period strip sets `gRptPeriod` and then Selects; it must not then read
  `colRptPerson`.
- **A calendar quarter can make a doubled window collapse to zero.** Fixing "Quarter == 90 days"
  into a real calendar quarter meant that on **1 April `gRptFrom = Today()`**, so `gRptFrom2x`
  — the prior-window span — was zero and **every transaction fetch came back empty**. Blank
  trend, blank tiles, blank grid, one day in ninety, and only on that day. The old fixed 90
  days could not degenerate. Now floored at 14 days each side. **A fix that makes a boundary
  more correct can also make it degenerate; check the window at its own edges.**
- **`fill-opacity='1%'` — the `"%"` was appended OUTSIDE the `If`,** so empty heatmap cells got
  one percent opacity instead of opaque. Zero cells are the whole point of a gap grid, and they
  would have rendered as smudges. String-built SVG puts unit suffixes inside every branch.
- **Rounding a stacked bar: round the RUNNING BOUNDARY, never each segment.** `Gc=3 Ac=5` gave
  `Round(112.5)=113` and `Round(187.5)=188` → the last rect came out `width='-1'`, an SVG error
  that kills the whole drawing. Cumulative rounding is monotonic, so widths are non-negative by
  construction.
- **A filtered chart needs its ORDINAL collapsed, not just its rows.** The heatmap honouring the
  coverage combo was not enough — the surviving row still drew at its index in the full grid, so
  the chart looked empty. `If(all, Ci - 1, 0)`.
- **Two windows in one collection.** The monthly bars read `colRptTx`, which spans current AND
  prior; since `gRptFrom` rarely lands on the 1st, a transaction earlier in the same calendar
  month as the window start shared its month key and inflated the first bar — putting the trend
  at odds with the desk-pulse tile above it. Bars now read `colRptTxCur`.
- **`WrapCount: 5` fitting exactly today's five currency values is the bug, not the fit.** A
  sixth value added in SharePoint would have been silently unreachable. Made scrollable.
- **YAML broke on an inline `DefaultSelectedItems: =Table( { Value: "..." } )`** — YAML reads the
  inner `Value:` as a mapping key. Block scalar required. This landed as a committed-but-invalid
  file (`b45fc06`) because the command used `;` instead of `&&` between validate and commit.
  **Gate every commit with `&&`.**
- **My own header comment was FALSE** — it claimed bands 3–5 render from folds built in the same
  load, when those folds did not exist yet. Corrected in `bb0c62e`. A comment that reads as
  further along than the file is, is worse than no comment.
- **Accepted, not fixed:** the transaction enrichment does two linear `LookUp`s per row. Power Fx
  has no hash join and no index on a collection, so there is no cheaper shape; it is bounded by
  the same 2,000-row cap the truncation banner reports. The real fix is a denormalised coverage
  column on the transaction, not a cleverer join.
- **The overlay is a PANEL, not a screen.** A `Navigate` would cost a fresh `OnVisible` and
  discard every fold — the whole reason the folds exist. Its bars are plain `Rectangle`s whose
  `Width` is the datum: no string to build, so no decimal separator to get wrong.
- **A person who both leads and supports one task was counted twice** in the unpivot. Fixed.
- Unmapped transactions (client with no coverage, or product with no type path) land on fallback
  labels matching no axis, so they sit in no cell while still counting in the KPI tile above.
  `gRptUnmapped` now states that count under the grid — a total that does not reconcile is worse
  than one that explains itself.

## State at end
- `main` = `7b4a06a`, clean, pushed, no divergence. Verified against `git ls-remote` AND the
  GitHub API after the user reported a GitHub UI error — **the error was GitHub's front end;
  the repo is intact.** The stale branch `claude/powerapp-repo-init-xymvlm` sits at `3fb2215`
  on the remote, fully contained in `main`.
- **`scrReports` HAS NOT CROSSED THE AIR GAP.** 2,560 lines authored, validated and twice
  reviewed, never pasted. Nothing about it is confirmed in Studio.
- Bands built: 0 controls, 1 KPI tiles, 2 people table (sortable, click → overlay), 3 family /
  format / cycle-time, 4 started-completed-net-open from dated events, 5 monthly trend +
  per-currency tiles + coverage×product heatmap + ranked gap list. Person overlay complete.

## Open threads
- **Paste queue, in order:** `scrProductEdit` BEFORE `scrTaskEdit` (the return path feeds
  `colTkProducts`); delete `cmpAppBar.HasLicence` by hand before re-pasting that component;
  delete the six superseded components; then `scrReports`, `scrHome`, `scrProjects`,
  `scrProject`, `scrIssueEdit`, `scrTransactionEdit` and the remaining components.
- **Owed in SharePoint:** real values for the four PLACEHOLDER Choice columns (`client_coverage`,
  `client_type`, `project_coverage`, `product_assetclass` — asset class **in provisioned order**,
  since order decides a new product's default); `project_phase` column default → `Not Started`;
  index `task_date_completion`.
- `scrHome`'s three SVG charts remain on their second correction with the actual root cause still
  unconfirmed — no return signal has come back on them.
- INDEX is ~380 lines against its own ≤80 budget and has not been pruned since 2026-08-13.
