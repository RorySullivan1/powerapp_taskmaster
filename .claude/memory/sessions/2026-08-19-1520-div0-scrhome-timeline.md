# 2026-08-19 15:20 · div0-scrhome-timeline

**Goal:** Diagnose the intermittent 'Division by 0' error at app start
(user: "when the app starts sometimes an error states Division by 0")

## What happened
- **DIAGNOSIS ONLY — NOTHING EDITED.** The user asked for a review and the
  sources highlighted; the fix is written out below but not applied.
- Enumerated EVERY division in `src/` with a script (strip `#` and `//` comments,
  strip `Classic/Icon@2.5.0`-style control tokens, strip `data:image/svg+xml`
  and single-quoted SVG attributes, then take the token after each surviving `/`).
  That reduced ~200 grep hits to a short list of real divisors. Worth re-running
  rather than re-deriving — SVG string concatenation makes a naive `grep '/'`
  useless on this repo.
- **THE ANSWER: `scrHome.pa.yaml:1069, 1073, 1090, 1092` — `/ gTlSpan` in
  `imgTimeline.Image`, unguarded at the point of division.** See the Decisions
  entry in INDEX.md for the full mechanism and the fix.
- Grounded the semantics on MS Learn (public sources, per the air-gap rule):
  - *Error handling → Getting started*: "Mathematical operations with *blank*,
    such as division, coerce the blank value to a zero. That value causes a
    division by zero error." — verbatim.
  - *Power Fx overview → No undefined value*: "all uninitialized variables start
    with a blank value."
  - *Error handling → Observing errors*: `If( false, 1/0, 3 )` reports NO error —
    the untaken branch is never observed. This is what makes the `If(x = 0, …)`
    guards genuinely safe.
  - *Error handling → Error propagation*: "the system observes errors on the
    input to all control properties" — so a Div0 inside `Image` raises the
    app-level banner rather than just blanking the control.

## Gotchas & dead ends
- **RULED OUT — do not re-audit these.** Every one was checked against the
  schema of the formula, not eyeballed:
  - `scrHome:343, 402` (`/ gPrjLed`, `/ gTaskLed`) — wrapped in
    `If(gPrjLed = 0, "none open", …)`. `If` short-circuits AND blank `= 0` is
    true, so the guard also covers the pre-`OnVisible` blank state. Safe.
  - `scrHome:1188/1190, 1288/1290` — donut divisor is `tot: Max(1, Sum(cats, n))`.
  - **All of `scrReports`.** Every divisor in a DECLARATIVE property is
    `Max(1, …)` at the point of division (`1117, 1175, 1630, 1826, 2018, 2179,
    2185–2200, 2338, 2398, 2404–2416`). `gRptAudTot`/`gRptRgnTot`/`gRptPrdTot`/
    `gRptPr2Tot` are `Max(1, …)` at the `Set` and only read later inside the same
    behaviour formula. `gRptBucketDays` is `If(gRptPeriod = "1W", 1, 7)`.
  - **Every `Average()`** (`scrHome:93/217`, `scrProject:103`,
    `scrProjectEdit:1393`, `scrTaskEdit:1608`) — all guarded by
    `CountRows(…) = 0`, and every `wgt` is `Coalesce(LookUp(…), 0)`. That second
    half matters and is easy to miss: **`Average()` drops blanks from the
    denominator**, so a non-empty table of all-blank values would also be a Div0.
    The `Coalesce(…, 0)` is what makes that unreachable — do not "simplify" it away.
  - Every `Mod()` — constant divisor or `Max(1, …)`.
  - `cmpKpiRing` — no division at all; the arc is `pct` / `100 - pct` on a
    circumference-100 circle.
- `gTlStart` is blank in the same window. `DateDiff(Blank(), d0)` reads blank as
  1899-12-30 and returns ~46000, so it produces an absurd x offset, NOT an error.
  Cosmetic, self-corrects — it is not a second bug.

## State at end
- Unchanged. Working tree clean, nothing authored, nothing to paste.

## Open threads
- **The fix is not applied.** Offered to the user; awaiting a go-ahead. Landing
  it means a full-file `scrHome` paste across the gap.
