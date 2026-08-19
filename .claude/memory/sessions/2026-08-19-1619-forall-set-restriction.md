# 2026-08-19 · forall-set-restriction

**Goal:** Fix the ForAll Set() rejection on btnIssHealth / btnPrjHealth

## What happened
- User: "the function calls in forall are failing in btnIssHealth.OnSelect, btnPrjHealth.OnSelect".
- Grounded the rule on MS Learn rather than guessing: the ForAll page sanctions **Patch** and
  **Collect** as the actions a body may take, and rules out `UpdateContext` / `Clear` /
  `ClearCollect` because ForAll may run records in any order and in parallel. `Set` is the
  global twin of `UpdateContext`.
- Fixed both bodies identically (they are duplicated by design and their own comment says so).
- Commit `4511d3c`. NOT yet pasted.

## Gotchas & dead ends
- **The `Set(scrap, Patch(...))` wrapper was doing the opposite of what it looked like.** It was
  there to absorb Patch's return value, but the same docs page says an UNCAPTURED ForAll result
  is never built — so capturing it was the only thing creating a per-record data-source copy.
- `gHlScrapI`, `gHlScrapP` and `gHlErr` were **all write-only** across the whole repo. The error
  capture had never surfaced anything, so discarding the error with `IfError(..., Blank())`
  preserves the actual behaviour exactly while matching the comment's stated intent.
- **Two independent scans of all 91 ForAll sites** (paren-depth and indentation) agree there is
  no other occurrence in `src/`.
- **NOT the same thing, left alone:** `btnPrjRecompute.OnSelect` has the identical
  `IfError(Set(gPrjPhaseScrap, Patch(...)), Set(gPrjPhaseErr, ...))` idiom, but it is NOT inside
  a ForAll, so it is legal and the user did not report it failing. Both globals are write-only
  dead weight and could be tidied — deliberately not touched in a paste meant to fix errors.

## State at end
- Authored and unpasted: `scrIssueEdit` and `scrProject`, both carrying only this change.

## Open threads
- Offer to tidy `gPrjPhaseScrap` / `gPrjPhaseErr` in `btnPrjRecompute.OnSelect` — same dead-weight
  idiom, legal where it sits.
