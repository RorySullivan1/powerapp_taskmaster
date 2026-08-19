# 2026-08-19 · issue-40-datarowlimit

**Goal:** Build #40: name the data row limit once as gDataRowLimit

## What happened
- `d6e0b6e`. `App.OnStart` gains `Set( gDataRowLimit, 2000 )`; all SEVEN `>= 2000` sentinels now
  read it — six in `gRptTrunc` (scrReports) and one in `gIssLed` (scrHome).
- `CLAUDE.local.md` gained a **rebuild/import checklist** (Data row limit = 2000, formula bar on,
  App properties pasted via the bar). **That file is gitignored, so the checklist is NOT in the
  repo** — it lives only on this machine.

## Gotchas & dead ends
- **THE ISSUE'S PROPOSAL WOULD HAVE SHIPPED A COLD-START REGRESSION, and it is not mentioned in
  the issue.** `App.OnStart` is NON-BLOCKING (already recorded for `gUserEmail`, and both these
  screens already self-heal it). A blank global compares as ZERO in Power Fx, so an unseeded
  `gDataRowLimit` makes every `CountRows(x) >= gDataRowLimit` TRUE:
  - `gRptTrunc` would report **all six datasets truncated** — a visible false banner.
  - `gIssLed` would take the **expensive per-project query arm** on every cold start — exactly
    the cost #30 removed.
  Neither is data-wrong and both self-correct on the next refresh, but both are new failures the
  seven literals did not have.
- **FIX: seed it in the two OnVisible handlers that reach a sentinel**, beside the existing
  `gUserEmail` self-heal, which is there for the identical reason. So the number lives in THREE
  places (App.OnStart + two seeds), not one. **That is a deliberate trade, not a miss** — three
  is still down from seven, all three are `gDataRowLimit` sites that one grep finds, and a
  mismatch degrades gracefully instead of going silently dead.
- **REJECTED: a named formula in App.Formulas.** It would dodge the ordering problem entirely,
  but the repo has a recorded failure — named formulas did not resolve in the published app and
  blanked every colour and dimension, which is why `gTheme` is a `Set`. Unverifiable across the
  gap, so not used.
- **REJECTED: `Coalesce(gDataRowLimit, 2000)` at each sentinel.** That is seven literals again.
- **MY PAREN-BALANCE CHECKER WAS WRONG TWICE before it was right.** Stripping `//` comments
  before string literals eats `http://www.w3.org/2000/svg` inside every SVG `Image` property;
  stripping `'...'` first eats prose apostrophes ("the fold's") and the parens after them. Only a
  character state machine (code / "" / '') gives a true answer. Kept at
  `scratchpad/balance.py` — **rewrite it, do not trust a regex version.** Under it the WHOLE
  repo balances, all 22 files.
- `tools/formula_bar_body.py` picks the constant up with no change and reports 6 globals.

## State at end
- 22/22 valid; state-machine balance clean across all 22 files; column guard run manually over
  the three edited files (python edits bypass the Write/Edit hook).
- **LANDED AND CLOSED (user, 2026-08-19).** `App.OnStart` through the formula bar, `scrReports`
  and `scrHome` through code view — all clean, first try. The paste queue is empty.
- #33 and #37 **LANDED (user)** before this was started; #39 done on both sides.

## Open threads
- **A WRONG `gDataRowLimit` IS STILL UNDETECTABLE.** Power Fx cannot read the Studio setting, so
  this makes the assumption findable, not checkable. The checklist that guards it is in a
  gitignored file.
- Perf backlog after this: **#34** (blocked on the prefix-vs-substring call) and **#35** (blocked
  on a probe) and **#38** (deferred, own pass).
