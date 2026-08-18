# 2026-08-18 · Issue #17 — filter scrProjects by project lead

## What was asked
Let users filter the projects browser by the person who leads the project. The issue
suggested "a dropdown or a people picker that defaults as the current user". Plan was
posted on the issue first and approved before building.

## The real constraint — branch explosion, not filtering
`galProjects.Items` was ALREADY four branches: two binary filters (show-completed x
coverage), each with its own `Sort` inside it because `Sort(If(...))` does not fold. A third
binary filter naively means EIGHT branches of near-identical Power Fx.

**It collapses back to four because `StartsWith(Text, "")` returns true.** The unset filter
state is the empty string, so the predicate is a no-op rather than a separate branch. The
screen's own name search already depended on this; the lead filter just reuses it.

## Delegation, resolved from public sources (no round trip exists)
From the SharePoint connector's delegable-operations table on MS Learn:
- `StartsWith` is delegable on complex types, deferring to the subfield involved.
- **Only `Email` and `DisplayName` are delegable in the Person data type.**
- The exclusion note covers **only Choice and Lookup** subfields. Person is not excluded.

`project_manager` is `Person, multi:false, required:true, indexed:true`, so
`StartsWith(project_manager.Email, ...)` is delegable AND indexed.

**Accepted cost: prefix semantics, not equality.** `a@b.com` also matches `a@b.com.au`.
Requires two directory users with prefix-related full addresses. The alternative is the
eight-branch explosion, so this was taken deliberately.

## Layout — the second row was forced, not chosen
`rowFilters`' children at their `LayoutMinWidth` floors plus three 16px gaps come to
**718px against 720 usable** at the tablet-768 target. Two pixels of slack — nothing more
fits on that line at any width the app supports. So:
- New `rowFilters2` anchored off `rowFilters` the same relative way.
- **`galProjects.Y` 210 -> 266 and `Height` subtracts the same 266.** The file header warns
  these are coupled; the band comment was updated with them.
- Row 1 left completely untouched: on a landed screen, minimal churn beats a prettier
  rebalance. Moving the show-completed toggle down to balance the rows was offered and
  declined in the plan.

## Controls (user chose the cmpPicker option over a Distinct() dropdown)
A dropdown of leads actually present in the data was rejected because `Distinct` does not
delegate on SharePoint — it would read up to 2000 project rows per visit and silently omit
any lead past the limit. That is the exact silent-truncation class this repo keeps hitting.

Built instead: `lblPrjLeadCap` + `btnPrjLead` (opens the modal, labelled with the current
lead or "All leads") + `btnPrjLeadAll` (clears, disabled when already clear), and a
`cmpPrjPick` full-screen `cmpPicker` instance wired exactly like `cmpPrPick` on
`scrProjectEdit`. `Office365Users` was already app-wide, so **no new data source**.

## Why the default seed is guarded
`OnVisible` runs on every visit. The coverage combo and the search box both SURVIVE a round
trip into a project and back, because nothing `Reset`s them. An unguarded `Set` would have
made the lead the one filter that silently reverts to "mine" whenever the user returns. It
is therefore behind a `gPrjLeadInit` guard. Seeding in `App.OnStart` would be cleaner state
but costs a SECOND formula-bar crossing, which is not worth it.

## Empty state
`ProjectsEmptyLabel` gained a lead branch FIRST — with the default being "mine", the lead is
now the most likely reason the list is empty, and the old text would have blamed coverage or
the completed toggle instead.

## Consequence, stated in the plan and accepted
Opening Projects now shows only your own projects by default. That is what the issue asked
for, but it changes what the screen shows on arrival for every user.

## Hand-off
`scrProjects` is landed, so this is a RE-paste. No new data source and no schema change, so
it can cross independently of #13's SharePoint column work. The paste queue is now two
screens: `scrTaskEdit` (#13 + #14) and `scrProjects` (#17).

## Noticed, not fixed
`docs/notes/shell-screens.md` still describes scrProjects as "cmpSectionHeader + a
cmpSelection filter strip". That has been wrong since the 2026-08-13 rework — it is a
combobox + search box + toggle, and now a second row. Left alone rather than half-updating a
doc that is stale in several places.
