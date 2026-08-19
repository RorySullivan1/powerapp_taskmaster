# 2026-08-19 15:20 · div0-scrhome-timeline

**Goal:** Diagnose the intermittent 'Division by 0' error at app start
(user: "when the app starts sometimes an error states Division by 0")

## What happened
- **DIAGNOSED, THEN FIXED IN THE REPO (user said apply).** Not in Studio yet.
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
- `src/Screens/scrHome.pa.yaml` edited, 22/22 valid, committed and pushed to
  **main** (user asked for main explicitly; the branch was a clean fast-forward,
  0 behind / 1 ahead, so nothing unrelated rode along).
- The fix is two parts. **The guard is the fix; the reorder is defence in depth:**
  - `imgTimeline.Image` seeds `sp: Max(7, gTlSpan)` in its existing `With` and
    divides by `sp` at all four sites. `Max(7, Blank())` is 7, which is
    `gTlSpan`'s own floor, so nothing changes once the variable is populated.
  - The three `Set(gTlStart/gTlEnd/gTlSpan)` calls moved ABOVE
    `Clear/Collect(colTimeline)` in BOTH `OnVisible` and the `Refresh Stats`
    `OnAction`. This removes the wrong-scale frame the guard alone would still
    draw, but it is NOT what makes the error impossible — a render that beats
    `OnVisible` entirely is still covered only by the guard.
- **Watch the semicolons if this is ever re-ordered again.** `OnVisible` ends on
  the `Collect` (no trailing `;`) while the `OnAction` copy continues into the
  toast `Set`s (keeps its `;`). Moving statements across that boundary changes
  which one is last. Both blocks were re-diffed after the move with comments
  stripped: **49 code lines identical.** Keep them that way.

## Open threads
- **`scrHome` IS AUTHORED BUT NOT LANDED — the paste queue is no longer empty.**
  One full-file `scrHome` paste outstanding; DELETE the screen in Studio before
  pasting it back (the no-orphaned-controls rule). The only return signal will be
  whether the banner stops appearing on a cold start, and note it needs the
  triggering condition to be visible at all: the user must lead at least one
  non-complete project WITH a target date.
