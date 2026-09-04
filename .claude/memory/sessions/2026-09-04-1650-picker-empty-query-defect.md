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
- **NOTHING AUTHORED.** The fix was offered and not yet commissioned — no `src/` file
  was edited this session. The six sites are still broken as described.
- Memory INDEX previously said #51's probes "await a paste". They do NOT — the results
  are recorded in `tests/README.md` (run by the user in Studio, 2026-09-04). State
  updated accordingly.

## Open threads
- Author the empty-query branch fix across the three screens (six branches). Small,
  mechanical, one paste per screen.
- Row 5b's delegation warning was never recorded, so whether `StartsWith` over a Person
  subfield DELEGATES remains open. Nothing shipping depends on it.
