# 2026-08-19 01:11 · issue11-scrreports-rework

**Goal:** Implement #11: the scrReports rework, all five steps

## What happened
- Plan posted to GitHub #11 first (comment 5336083698) and approved with "Okay implement".
  All four open questions were resolved on the recommendation given in the plan.
- Five commits, one per step, `bdf1e04` → `8faa865`, plus `728fb56` for the design note.
  `scrReports.pa.yaml` 2783 → 2833 lines. Validator 22/22 after every step.
- **Step 1 (subtract).** `pnlRptCyc` + its three folds; the coverage × product grid, the ranked
  gap list and their folds. **The Coverage combo went with them** — `gRptCoverage` was read in
  five places, all inside the dropped block. `colRptClients`, `colRptCoverage`, `colRptCovOpts`
  and `colRptProdL1` had no other consumer either, so `taskmaster_clients` and
  `mapping_producttype` are no longer fetched or refreshed by this screen at all.
- **Step 2 (data layer).** `colRptOpen` + `task_date_start`; `colRptPrj` + `project_region_path`
  and `project_requestor`; `colRptPrjMap` splits region L1 and resolves a requestor label;
  `colRptOpenTag` gains Rgn/Req off ONE hoisted LookUp; `colRptTxEnriched` gains product-type L2,
  the transaction date, and loses Cov. New folds: requestor bars, region pie, product L1/L2 pies,
  per-bucket-per-currency segments.
- **Step 3 (people).** Tx column removed from the fold, the header, the sort switch and the body.
  Subtitle now states the completed-tasks-with-no-date count. The 29-control overlay became a
  task gallery reading `colRptPersonSrc`.
- **Step 4 (band 3).** Two columns became four; output format became a pie; requestor bars and a
  region pie added; panel `LayoutMinWidth` 320 → 260.
- **Step 5 (band 5).** Trend bars stacked by currency; product-type pies added as a second column.

## Gotchas & dead ends
- **THE REAL #11 PEOPLE BUG WAS IN THE FETCH, not the fold.** `colRptPersonSrc` already ingested
  completed work and Owns/Sups already counted it. `colRptDone` required
  `task_date_completion >= gRptFrom`, and **that comparison is FALSE for a blank date**, so a task
  at stage Completed with no completion date never entered the collection: Done read 0, median and
  on-time read "—", and nothing said why. Now fetched on stage alone (still delegable) and
  windowed locally, with `Days`/`OnT` guarded on `nod` so neither measures against a blank.
  The cost — completed work accumulates where open work does not — is carried by the truncation
  banner, which now watches `colRptDoneAll`.
- **PIE PERCENTAGES COME FROM A RUNNING CUMULATIVE**, `Pct = Cum(i) - Cum(i-1)`, never rounded one
  slice at a time. Rounding per slice drifts and the wedges stop closing the circle.
- **`Li`, not `Idx`, positions a legend row.** `Idx` comes from the pre-filter sequence, so
  dropping zero-count slices leaves holes in the legend. Bit the format pie specifically, whose
  vocabulary deliberately includes zero-count values.
- **A nested `Concat` would have had to reach an outer record scope** for the currency stack.
  Avoided entirely: `colRptTxSeg` carries its own bucket index `Bi`, so the segments are a
  SEPARATE `Concat` and no formula reaches outward.
- **`Variant: ManualLayout` is NOT a grounded GroupContainer variant** — only `AutoLayout` and
  `GridLayout` are (validator caught it). The overlay caption row became an AutoLayout whose
  PaddingLeft 8 + LayoutGap 8 over widths 280/90/70/84 reproduce the gallery template's absolute
  X grid exactly. Change one, change both.
- **`ColorValue()`, `Char()` and 2-arg `Mid()` are not grounded anywhere else in this repo.**
  All three replaced with constructs the file already uses — `RGBA()`, plain text, and
  `Right(sp, Len(sp) - i - 2)`. Air-gap rule: prefer the grounded construct over the nicer one.
- Deleting the `Cov:` field from `colRptTxEnriched` by line range removed the record literal's
  opening `{`. Caught by the validator's bracket check, not by YAML parsing.
- `gRptFmtMax` became dead when the format chart turned into a pie; a reference sweep for
  set-but-never-read caught it.

## State at end
- **#11 IS BUILT AND UNPASTED.** `scrReports.pa.yaml` is the whole paste. Nothing else changed
  in `src/`. 22/22 valid. Pushed to `main`.
- Four checks to run in Studio after the paste are listed in the GitHub comment on #11.

## Open threads
- Nothing on this screen fetches `task_output_audience`. "Open tasks by output" was read as the
  existing `task_output_format` chart converted to a pie, per the numbering in the issue.
- `task_supporter` was deleted and recreated on 2026-08-17, so the supports column may still be
  largely empty — a correct report over an empty column looks identical to a broken one.

## Follow-up (same day, user-directed)
- **The output pie now groups by `task_output_audience`, not `task_output_format`.** The deciding
  fact is enforcement, not recency: `scrTaskEdit`'s `lblTkMissing` blocks the save until an
  audience is picked whenever the Output toggle is on, and there is NO equivalent rule for format.
  So audience stays complete and format accumulates blanks indefinitely. **`task_output_format` is
  now reported nowhere in the app.**
- The audience column is younger than the open backlog, so Unspecified will dominate at first.
  Stated in the subtitle deliberately — on a pie, "the column is new" and "the report is broken"
  look identical. Other outranks Unspecified in that subtitle: rarer, and a real data question.
  The bucket drains as tasks are touched, because an existing task with output data cannot be
  saved at all until an audience is picked.
- **`Fam` and `Fmt` dropped from `colRptPersonSrc`.** They fed the overlay mini-charts that step 3
  replaced, and nothing read them after. Removing `Fam` removed the per-task
  `LookUp(colRptPrjMap, ...)` behind it, so `colRptOpenTag` is now the ONLY place that join runs.
  `colRptDoneAll` stopped fetching `task_output_format` for the same reason.

## Paste defect 1 (user, 2026-08-19) — FIXED, unverified
- Studio rejected the `colRptPersonSrc` Collect: **"the TNm column expects a text type and you're
  using an error type"**.
- `TNm: t.task_name` is the ONLY field in that record read RAW. Every other one is wrapped in
  `Coalesce` or reached through `.Value` / `.Email`, which forces a type and masks the fault —
  that is why TNm alone surfaced, and why `task_name` sat in the fetch UNREAD for weeks without
  anyone noticing. `TId: t.ID` sits immediately before it and resolves fine, so the collection is
  not wholly broken; it is the plain Text column that goes missing.
- Root cause: `colRptOpen` / `colRptDoneAll` were `ShowColumns` over `Filter(LiveTasks, ...)`.
  **LiveTasks is a NAMED FORMULA, and wrapping one in a Filter does NOT restore the schema.** The
  file's own comment claimed it did — that claim is now disproved and deleted.
- Same symptom, same fix as `p.project_name` off `ActiveProjects` on 2026-08-17: an explicit
  `ForAll(... As x, { col: x.col, ... })` projection. Two independent instances now.
- `colRptTx` deliberately KEEPS ShowColumns — it filters `taskmaster_transactions` directly, and
  its raw `transaction_date` / `transaction_notional` reads have been working, which is what
  isolates the fault to the named-formula root rather than to ShowColumns itself.
- Commit `3818e40`. **NOT yet confirmed in Studio.**

## Band 5 extension (user, 2026-08-19)
- **Third column added, LEFT of the trend: "Project leads by transaction count".** Top 6 + Other,
  counting transactions on projects the person MANAGES. This is the same measure dropped from the
  people table in step 3 — it was wrong there (project attribution among task measures) and is
  right here, in the transactions band, with the basis stated on the panel.
- `colRptTxEnriched` gains `Ld` from a second `LookUp`, hoisted into the SAME pass as the product
  lookup so the display name and its email fallback come off one join rather than two. Cost note
  updated to O(tx x products) + O(tx x projects).
- **The two product-type pies are side by side, not stacked.** They are children of a HORIZONTAL
  container now, so the flexible dimension is WIDTH: `LayoutMinWidth`, not `LayoutMinHeight`, and
  `Height: =Parent.Height` with the row set to `LayoutAlignItems.Stretch`. Getting that backwards
  is the easy mistake — the container notes say the minimum is "along the parent's Direction".
- Row is `FillPortions` 1 : 2 : 2 and 360 high (was 420, two columns). Minimums ~1120px, matching
  band 3's ~1100.

## Paste defect 1 — CONFIRMED FIXED
- User, 2026-08-19: **"It pastes clean now, all charts render."** The explicit ForAll projection
  over `Filter(LiveTasks, ...)` was the right fix, and it also confirms the pie renderer, the
  currency stack and the `With({pm: LookUp(...)}, pm.Field)` record form all work.

## Paste defect 2 (user, 2026-08-19) — FIXED, unpasted
- The person overlay's task rows **overlapped**.
- The cells were absolute on a hand-computed X grid with a declared `Width` each. **The
  arithmetic was right — no two boxes overlapped on paper** (8..288, 296..386, 394..404,
  410..464, 472..556, 564..714 inside 720). It overlapped anyway, so the premise was wrong:
  a modern `Label@2.5.1` does not hold a declared Width the way that grid assumed.
- Fixed by switching to the idiom `galRptPeople` already proves: ONE horizontal auto-layout
  container inside the template, cells with `FillPortions` + `LayoutMinWidth` and NO `X`/`Width`,
  captions above carrying the identical portions pair for pair.
- The health dot is its own zero-portion column with a BLANK caption above it. That keeps one
  caption to one cell without nesting a second container inside a gallery template — nesting is
  proven container-in-container (band 5) but NOT container-in-template.
- Commit `dc463a7`.
