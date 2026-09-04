# 2026-09-04 16:50 · picker-empty-query-defect

**Goal:** Answer whether the 2000-row ceiling breaks the people/product lookup pickers

## What happened
- Question asked: will the 2000-item ceiling stop the lookup components retrieving
  people and products? Answer researched across `cmpPicker`, `cmpLookupField` and the
  five screen-side `Results:` bindings. **No** — for two different reasons per branch:
  - **People** — `Office365Users.SearchUserV2({searchTerm, top: 25}).value` is a
    CONNECTOR ACTION, not a tabular data source. The 500/2000 data-row limit governs
    Power Fx queries over tabular sources only; it does not apply to a `.value` array.
    Search runs server-side in the directory, capped by `top`. Real constraints there
    are different ones: prefix matching over displayName/mail/UPN (mid-string terms
    miss) and tenant scope.
  - **Products / clients** — SharePoint, so the limit is in play, but the query FOLDS.
    `client_name` / `product_uid` are indexed Text; `StartsWith` and `Sort` both
    delegate on Text (schema.yaml:29). Sort is delegated, so SharePoint returns rows
    ALREADY ORDERED and the non-delegable `FirstN` takes the top of a correctly-ordered
    server result. Top-50 is genuinely the top 50 at any list size.
  - The ceiling that would actually matter on those two lists is the **5000-item view
    threshold, not 2000** — and both filter columns being indexed is exactly what keeps
    a delegable query working past it.

## Gotchas & dead ends
- **DEFECT FOUND, NOT A CEILING PROBLEM — SIX SITES.** Every client/product picker
  branch runs `StartsWith(col, "")` as its "first 10 with nothing typed" default page.
  The 2026-09-04 probe (`tests/README.md:770`, `scrProbe-startswith-empty`) proved that
  construct is REJECTED OUTRIGHT — *"the query is not valid"*, a visible data-retrieval
  error, not truncation and not zero rows. Every picker sets its query global to `""`
  on open (`scrTaskEdit:96`, `scrProjectEdit:115`, `scrTransactionEdit:64`), so the
  default page errors. Type two characters and it is fine at any list size.
  Affected: `scrProjectEdit:1974` (NxClient, NxProduct), `scrTaskEdit:1666`
  (Client, Product), `scrTransactionEdit:604` (Client, Product).
- The PERSON branches are already gated on `Len(gQuery) >= 2`, which is why only
  client/product are exposed — and why `cmpPicker`'s header comment "THE DIALOG OPENS
  WITH ROWS ALREADY IN IT" is currently true for the person fields ONLY.
- Fix shape is the conclusion the probe already drew for #53: an off state is a BRANCH,
  not an empty argument. Split the `Len(q) >= 2` case from the default page and give the
  default `FirstN( Sort( taskmaster_products, product_uid ), 10 )` with no Filter at all.

## State at end
- **FIX AUTHORED, AWAITING PASTE** — all six branches, three screens, validator 22/22.
  Each record kind is now TWO branches: typed (`Len(q) > 0`, Filter + Sort + FirstN,
  keeping `If(Len >= 2, 50, 10)`) and off-state (`FirstN( Sort( <list>, <col> ), 10 )`
  with no Filter). Person branches untouched.
- **The typed branch is gated on `Len(q) > 0`, NOT `>= 2`, and that is deliberate:** the
  only forbidden input is the EMPTY string, so a one-character query must still narrow.
  Gating at >= 2 would have silently changed one-char behaviour from "10 matches" to
  "10 arbitrary rows" — a second defect introduced while fixing the first.
- **The projection is REPEATED, not lifted into `ForAll( If(a, t1, t2) As x, … )`.**
  The compact form is unproven in this dialect and #52 had already shipped one unprobed
  shape; two guesses in one paste cycle is not affordable when the only return signal is
  "it didn't work". Cost is ~12 duplicated lines per screen, accepted knowingly.
- Memory INDEX previously said #51's probes "await a paste". They do NOT — the results
  are in `tests/README.md`, #53 is closed won't-fix and #52 is built. State corrected.

## Open threads
- **Paste all three screens.** Proof is opening a client or product picker and NOT typing:
  ten rows by name, no error banner. Then type one character and confirm it narrows.
- `pkHint`'s ladder still says "Type at least two characters" when a ONE-character query
  matches nothing — the query did run, it just found nothing. Pre-existing, untouched by
  this fix, cosmetic.
- Row 5b's delegation warning was never recorded, so whether `StartsWith` over a Person
  subfield DELEGATES remains open. Nothing shipping depends on it.
