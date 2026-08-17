# 2026-08-17 00:19 · scrreports-analytics-design

**Goal:** Design scrReports as native person-level analytics

Design only — nothing authored in `src/`. Plan lives in `docs/reports-screen-design.md`.
User's ask: person-level productivity, impact, transaction trends, offering gaps; primary
purpose "where people spend their time and how projects are trending", secondary
"transactions by coverage area broken down by product type (level 1 only)", optimised for speed.

## What happened

Three decisions taken with the user, all three the recommended option:

1. **Coverage axis = `client_coverage`**, reached through `transaction_client_name`, not
   `project_coverage` through the parent project. A transaction carries both, so this was a real
   fork. The grid now reads "this coverage team has never traded that product type". Both are
   client-side joins off small dimension lists, so neither option cost delegation — the choice was
   purely semantic and is cheap to reverse.
2. **The Power BI licence gate comes off** — `scrReports` becomes the analytics surface for
   everyone. See the Decisions entry; this reverses part of `app-structure.md`.
3. **Effort is proxied and labelled as such.** No hours/effort column exists anywhere in the model.
   Volume by activity family + output format, plus median cycle time
   (`task_date_start` → `task_date_completion`) as the one real duration signal. A `task_effort`
   column was offered and declined for now — worthless until populated, and internal names freeze.

Architecture settled as **fetch bounded → fold once → render from folds**: refetch only on a period
change; scope, coverage and person selection are local filters over collections of tens of rows;
person detail is an overlay rather than a `Navigate` so the folds survive.

## Gotchas & dead ends

- **`Distinct()` returns its column as `Result`** — the product-L1 vocabulary is
  `Distinct(mapping_producttype, level1).Result`, not `.level1`. Easy to typo into a silently empty
  axis.
- **Level-1 extraction uses `Find`/`Left`, not `Split`.** The `" | "` separator is stored data and
  `Split` on a multi-char separator was not worth betting a paste on when `Find`/`Left` is
  unambiguous. Blanks bucket to "Unclassified" explicitly.
- **Month bucketing is an integer key** — `Year(d)*12 + Month(d)` — not date comparison. Sidesteps
  timezone and month-length edges.
- **The nested-`ForAll` cross product was a dead end.** Nesting `ForAll` over coverage and product
  returns a table of tables. Reused the repo's existing `Sequence` + `Index` idiom with
  `RoundDown((s-1)/nProd,0)+1` / `Mod(s-1,nProd)+1`, which also hands the heatmap its coordinates.
- **`transaction_sales` is assumed sales-side, not a desk person**, so it does not feed person
  productivity. Unconfirmed — listed as a schema ask.

## State at end

Design committed and pushed (`3294ee3`) on `claude/powerapp-repo-init-xymvlm`. `src/` untouched,
still 22/22 valid. Next step is authoring `scrReports.pa.yaml` as a **full screen replacement** —
the user deletes the screen in Studio before pasting it back.

## Open threads

- Decisions ledger entries appended to INDEX (see below). Design doc and ledger now both carry the
  three calls; the ledger is authoritative for the reasoning.
- Schema asks raised, none blocking: index `task_date_completion`; real `client_coverage` values;
  confirm `transaction_sales` is sales-side.
