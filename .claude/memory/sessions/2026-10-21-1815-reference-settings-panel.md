# 2026-10-21 18:15 · reference-settings-panel

**Goal:** Epic #145: rebuild scrReference as a settings panel for activities, products, clients and regions

## What happened
- User asked for a new epic: the Reference page as a settings panel where users add/edit choices in
  activities, products, clients and regions. Filed epic #145 with sub-issues #146 (shell), #147 (term
  editor), #148 (rename cascade + delete guard), #149 (Products/Clients sections), #150 (decision:
  client type/coverage Choice values).
- Rewrote `src/Screens/scrReference.pa.yaml` whole (it is re-pasted as one screen; no other file
  references its old control names). Validator 23/23.
- Pointed schema.yaml's "maintained via scrAdmin" comments and docs/notes/shell-screens.md at it.

## Design (the calls a later session should not re-derive)
- **Sections → lists.** Activities = `mapping_activitytype`; Regions = `mapping_region`; Products has
  two tabs: Products (`taskmaster_products`, opens scrProductEdit) and Product types
  (`mapping_producttype`); Clients = `taskmaster_clients` (opens scrClientEdit).
- **One editor for three lists.** `gRfView` ("activity" | "region" | "producttype" | "products" |
  "clients") picks the list; every write is a Switch with one arm per list, because a data source
  cannot be held in a variable. Terms are read into `colRfTerms` {Id, L1, L2, L3, Path}.
- **btnRfLoad refreshes the PICKER CACHES first** (`colMapActivity`, `colMapRegion`, `colMapRegionCl`,
  `colMapProdType`) and builds colRfTerms from them — those caches are otherwise fetched once per
  session, so without this an edit would not reach the pickers until restart.
- **Rename cascade is by ID** (`*_id = term ID`, indexed Number `=`, delegates), rewriting `*_path`.
  Records that picked a branch store id 0 and keep their old path — accepted, stated in the editor.
- **Delete is refused while any record stores the ID.** Counts come from hidden worker btnRfUsage;
  -1 = still counting, because Select() QUEUES. Rename refuses at gDataRowLimit (count may be capped).
- **Client type/coverage are Choice columns** — the app can read them (Choices()) but not edit them.
  Shown read-only in the Clients caption; #150 holds the decision whether to migrate to mapping lists.

## Pre-paste review
- First pass DO-NOT-PASTE on ONE blocker, carried over from the OLD screen: `StartsWith(col, txtSearch.Text)`
  with an empty box is `StartsWith(col, "")`, which SharePoint rejects ("the query is not valid",
  tests/README.md scrProbe-startswith-empty). The old scrReference had the same construct and was recorded
  landed, so its client/product lists probably never showed rows with an empty box. Fixed: two branches,
  Sort inside each. Also took W2 (cascade not gated on the open-time count), W3 (Coalesce(gDataRowLimit,
  2000)), W5 (dialog labels while counting), W6 (Save re-entry guard), explicit icon hover colours, and
  replaced `x in ["a","b"]` (no precedent in src/) with `=`/`||`.
- Left for the user: W1 (renaming a level-1 row does NOT rename the descendant rows that share that level,
  each row is its own term), W4 (confirm Title is not required on mapping_activitytype).

## Paste notes
- Code view, whole screen. Paste the new screen FIRST, then delete the old one (this screen types
  gEditClient / gEditProduct), then rename the suffixed screen and appBar back and log the suffixes.
- Run OnStart before testing. Check the two row icons sit at the right edge (Parent.TemplateWidth X).

## State at end
- Authored, validated 23/23, review blocker fixed, NOT PASTED.

## Open threads
- #150 decision (recommendation: keep Choice columns, read-only).
- Paste scrReference (code view, whole screen) and confirm add / rename / delete in each vocabulary.
