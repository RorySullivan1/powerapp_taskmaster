# 2026-09-04 · scrProjects assessment → two epics (#45, #50)

Assessment only. **Nothing in `src/` was touched and nothing is queued for paste.**

## What was asked

Two problems on `scrProjects`: (1) users cannot see their own projects after turning on
"Only show my projects"; (2) `galProjects.Items` may be reducible.

## Filed

- **#45 [BUG]** — the "only mine" defect, five ranked candidates. Sub-issues #46 (probe),
  #47 (verify live indexes), #48 (widen "mine" to manager-or-supporter), #49 (casing convention).
- **#50 [SIMPLIFY]** — `Items` is 155 lines / 16 branches. Sub-issues #51 (probe the two claims),
  #52 (hoist phase groups into named formulas), #53 (collapse the search axis 16 → 8).

`#45` is sequenced **before** `#50`: both rewrite the same eight person predicates, and each
paste across the gap returns one bit.

## The finding worth keeping

**MS Learn note 20 settles the half of the #17 post-mortem the ledger recorded as unsettleable.**
The 2026-08-19 entry says of `StartsWith(person.Email, "")` returning nothing: *"which half fails
(the empty argument, or `StartsWith` over a Person subfield) cannot be settled from this side of
the gap"*. The SharePoint delegation table's note 20 says plainly:

> SharePoint does not support delegation of `StartsWith` on subfields of Choice or Lookup complex types.

A Person column is a lookup complex type, so that construct was **never delegable with any
argument**. The empty string was incidental. This does not license the halving in #53 — the
empty-argument half is still untested, and `project_name` is a different column type entirely —
but it means the ban was correctly applied to a Person subfield and has been over-generalised
to Text, at a cost of eight branches.

## The suspicion worth keeping

**The two claims holding `Items` at 16 branches were never isolated from each other.** The
"every branch needs its own phase predicate" rule rests on one observation — a bare
`Filter(ActiveProjects, StartsWith(...))` wrapped in `Sort` returning "the query is not valid".
At the time, the same formula also carried the non-delegable Person-subfield `StartsWith` above.
A non-delegable clause anywhere in a filter is a sufficient explanation for a rejected query;
the phase group may simply have been the variable that changed. #51 separates them.

## Ranked candidates for the defect (detail in #45)

A. "Mine" tests `project_manager` only; `project_supporter` (indexed, and named by decision C2
   as part of "mine") is ignored — the only candidate that explains *some* users, not all.
B. `gUserEmail` is `Lower()`ed while the column it is compared against is not. `scrReports`
   normalises both sides; `scrProjects` and `scrHome` normalise one.
C. `gUserEmail` blank at first paint (self-heal should cover it; cheap to rule out).
D. `project_manager` is `indexed: true` in the golden source but unverified on the live list —
   the #39 gap, now urgent because of the 2000+ backfill and the 5,000 threshold.
E. Query shape: nested `Filter` over `ActiveProjects` restating the same OR-group.

## Blast radius noted

`project_manager.Email = gUserEmail` is also `scrHome.pa.yaml:80`, behind the "projects I lead"
KPIs. If the cause is B/C/D/E the dashboard has been reading zero for the same users unnoticed —
a number tile does not announce that it is wrong. Any fix moves both screens in one paste.
