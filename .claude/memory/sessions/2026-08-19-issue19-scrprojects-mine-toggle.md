# 2026-08-19 · Issue #19 — REWORK scrProjects: the lead filter becomes "Only Show my Tasks"

## What was asked
> "Currently the filtering system does not work — when selecting all leads the filter yields
> nothing. Lets move forward with another solution." The people filter must be (1) on the same
> line as coverage and search, and (2) reduced to a checkbox saying "Only Show my Tasks",
> like the completed toggle, replacing the people filter entirely.

## The defect being removed
The #17 lead filter (2026-08-18) rested on ONE claim: `StartsWith(person.Email, "")` is a no-op
that matches every row, so an unset filter needs no branch of its own. That claim is what kept
`galProjects.Items` at four branches instead of eight, and it is what failed — the user reports
NOTHING comes back, "All leads" included, which is exactly the state where the predicate is the
empty-string form. The prefix-vs-equality trade recorded in that session is therefore moot: the
prefix form does not return rows at all.

**Not diagnosed further, and deliberately.** MS Learn's delegable-operations table says
`StartsWith` defers to the Person subfield and that `Email` is delegable — the #17 research was
sound as far as it went. Whether the failure is the empty argument, the Person subfield, or
something the query returns unlogged cannot be settled from this side of the gap, and the issue
asks for the filter to be replaced rather than repaired. So the session removed the construct
instead of theorising about it, and moved to the form this repo has already proven in
production: `project_manager.Email = gUserEmail`, which is what scrHome's three KPI Filters
have always run against Person columns.

## What changed in `src/Screens/scrProjects.pa.yaml`
1. **`rowFilters2` deleted whole** — caption, `btnPrjLead`, `btnPrjLeadAll` — and with it
   `cmpPrjPick`, the screen's `cmpPicker` instance. `gPrjLead` / `gPrjLeadInit` / `gPrjPicker` /
   `gPrjQuery` were set and read ONLY on this screen (grepped), so nothing else moves.
2. **`tglOnlyMine` + `lblOnlyMine` added to `rowFilters`**, a `Classic/Toggle@2.1.0` and a
   `Label@2.5.1` mirroring `tglShowComplete` / `lblShowComplete` exactly — the same reason
   applies, a check-box token is not grounded for this dialect and an unverified control fails
   the WHOLE screen paste.
3. **`galProjects.Items` is now eight branches**, three binary filters (show completed ×
   coverage × only mine), each independently delegable with its `Sort` inside it. Eight is the
   real cost of an equality with no neutral value; the four-branch version was cheap because
   its off state was a no-op that did not work.
4. **`galProjects.Y` 266 → 220 and `Height` subtracts the same 220** — the band the deleted row
   occupied is given back to the gallery, 46px. The file header's band table was updated with
   it; those two numbers are coupled and the header says so.
5. **`OnVisible`** dropped the picker state and the once-only lead seed, and gained scrHome's
   `If( IsBlank(gUserEmail), Set(...) )` self-heal — the new branches read `gUserEmail`, and
   `App.OnStart` is non-blocking.
6. **The empty-state label** lost its "No projects led by X" branch and gained an
   only-mine one.

## The width claim that was wrong
#17's session recorded "718px against 720 usable at the tablet-768 target" and concluded a
second filter row was **forced**. That reads the 768 DESIGN HEIGHT as the width. The screen is
768 TALL — `docs/build-history.md` says so directly ("numbers that only coincide on a screen
exactly 768 tall") and the bands run 0..744 + gutter — and 1318 wide, which INDEX's own
2026-08-13 collision entry states outright ("clear at 1318, overlapping below ~850"), and which
scrReports' 1200-wide overlay could not otherwise fit. Six children at their floors plus five
16px gaps come to 980 against 1318. The one-line row the issue asks for was always available;
it was arithmetic on the wrong axis that ruled it out. The corrected budget is now written into
the file so the next session does not redo the mistake.

## Default behaviour changed on purpose
The lead filter SEEDED itself to the current user, so the screen opened showing only your
projects. The toggle defaults OFF, so it now opens showing everything and "mine" is opt-in —
which is what "similar to the completed toggle" means, and it is the behaviour to check first
after the paste.

## State
Authored, validated 22/22, **NOT landed**. `scrProjects` is the whole paste queue.

## The label — RESOLVED
Shipped first as the issue's own wording, "Only Show my Tasks", unedited, with the mismatch
flagged rather than silently corrected: the toggle filters `project_manager`, so what it means
is "only projects I lead". **The user chose "Only show my projects" (2026-08-19)** and that is
what `lblOnlyMine.Text` now carries, along with the empty-state sentence that names the toggle.
Nothing else moved — no predicate reads the string.
