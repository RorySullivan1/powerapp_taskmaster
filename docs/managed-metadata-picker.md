# Managed Metadata: cascading term picker — research & design

**Verdict: the approach works, and it needs no second copy of the taxonomy.** Detect nesting as
the user selects, reveal another level per step until the leaf, and write the leaf back. The term
store stays the single source of truth; the app reads it directly.

Context: `project_region`, `project_type` (required) and `project_coverage` on
`taskmaster_projects`, plus `client_type` / `client_coverage` / `client_region`, `product_type` and
`task_category`, are **Managed Metadata and staying that way** (decision 2026-08-03). Without a
working picker, creating a project from the app is impossible, because two of those are required.

> **Revised 2026-08-03, the same day it was written.** The first version recommended caching the
> term store into a flat `taskmaster_terms` list. That was wrong, and §2 explains why. The list has
> been removed from the schema.

---

## 1. The app can read the term store directly — `Choices()`

`Choices([@taskmaster_projects].project_region)` returns the column's term set, straight from the
term store, with no Graph call and nothing stored in between. Each record carries:

| Field | What it is |
|---|---|
| `Label` | the term's own label |
| **`Path`** | **the term's FULL hierarchical path** — e.g. `EMEA;UK;London` |
| `Guid` | the term GUID |
| `WssId` | the site-collection cache id |

**`Path` is the finding that decides the design.** The hierarchy is already in the data. There is
nothing to precompute, no parent-pointer column to maintain, and no recursive walk to perform — a
cascade is prefix matching on a string:

```powerapps
// Level 1 — paths with exactly one segment
Filter( Terms, CountRows(Split(Path, ";")) = 1 )

// Level 2 — one segment deeper, sitting under the level-1 pick
Filter( Terms, CountRows(Split(Path, ";")) = 2
            && StartsWith(Path, pick1 & ";") )
```

Depth is discovered from the data — a level appears only if terms exist beneath the pick above — so
nothing hard-codes how deep a vocabulary goes.

### The one real limit: 20 terms

**`Choices()` on a managed-metadata column is capped at 20 terms by the SharePoint connector's
backend query.** It is not configurable, and there is a standing Microsoft Ideas request to lift
it. This is the *only* reason a term source other than `Choices()` would ever be needed.

If a term set outgrows 20, the screen swaps one binding — `Choices(...)` for a collection filled by
a single Power Automate call returning the same `{Label, Path}` shape (Graph termStore; a canvas
app has no HTTP action of its own, and `TermStore.Read.All` is **delegated only**, so the flow runs
as the signed-in user). **The component does not change**, and there is still no second *store*:
that collection lives in memory for the session, not in a list that can drift.

Whether any of these term sets actually exceeds 20 terms is answerable at first paste, not now.

## 2. Why the cache list was wrong

The first version of this document recommended mirroring the term store into a flat
`taskmaster_terms` list (`term_guid`, `term_label`, `term_set`, `term_parent_guid`, `term_path`,
`term_depth`, `term_is_leaf`), refreshed by a scheduled flow, so the cascade could run as delegable
`Filter`s on `term_parent_guid`.

That was a second copy of a vocabulary that already exists — carrying a refresh schedule, a seeding
step and a drift risk — to reconstruct a hierarchy that `Path` hands over for free. The delegation
argument used to justify it doesn't survive contact either: a term set small enough to be usable is
small enough to hold in memory, so there is nothing to delegate.

The honest comparison, now that both are on the table:

| | **Read `Choices()` directly** | **Cache list** |
|---|---|---|
| Copies of the taxonomy | **1** (the term store) | 2 |
| Can drift | **No** | Yes, between refreshes |
| Provisioning | **Nothing** | 1 list, 7 columns, indexes |
| Seeding / refresh | **None** | A flow, plus a first seed |
| Hierarchy source | **`Path`, already present** | `term_parent_guid`, reconstructed |
| Works past 20 terms | Needs a flow-fed collection | Yes |
| Survives a flow outage | N/A — no flow | Yes, on stale terms |

The cache buys exactly one thing: tolerance of a flow outage in the >20-term case. That is not
worth a permanent second store for the ≤20 case, and in the >20 case an in-memory collection gets
most of the same benefit without persisting anything.

## 3. Writing the value — hand the connector its own record back

```powerapps
Patch( taskmaster_projects, Defaults(taskmaster_projects),
    { project_region: LookUp( Choices([@taskmaster_projects].project_region),
                              Path = gPrRegionPath ) } )
```

The picker resolves a **path**; the screen turns that back into the connector's **own record** with
a direct `Choices()` lookup. That replaces the hand-built literal the first version used:

```powerapps
// SUPERSEDED — no longer authored anywhere in this repo
{ '@odata.type': "#Microsoft.Azure.Connectors.SharePoint.SPListExpandedTaxonomy",
  TermGuid: …, Label: …, WssId: -1, Path: …, Value: … }
```

That literal was the least-proven construct in the app — community-reported, never first-party
documented, and dependent on getting `WssId: -1` and the exact field names right. Passing back a
record the connector itself produced removes the whole class of risk. It also sidesteps a live
ambiguity in the sources over whether the GUID field is called `Guid` or `TermGuid`, since nothing
we author ever names it.

The hand-built shape survives only as a documented fallback — see §5.

## 4. What the component does with all this

`src/Components/cmpTermPicker.pa.yaml`. Four progressively-revealed vertical galleries.
Two details are load-bearing, and are commented as such in the file:

- **A `"— select —"` sentinel row per level.** A gallery's `Selected` returns its first row until
  the user touches it, so without the sentinel the picker would auto-select a whole path nobody
  chose — into a *required* column. `Coalesce` treats `""` as blank, which is why the sentinel's
  `Path` is an empty string rather than a marker value.
- **Chain validation, which `Path` makes almost free.** A level's value counts only if its path
  sits under the level above (`StartsWith(childPath, parentPath & delimiter)`). If the user changes
  level 1 after picking level 2, the stale deeper pick fails that test and is discarded rather than
  written. Under the parent-GUID design this needed a `LookUp` per level; here it is one
  `StartsWith`.

`IsComplete` — the leaf test — counts terms sitting below the pick, using the same data the cascade
walks, so it cannot disagree with what is on screen.

## 5. Proven vs. untested

| Claim | Status |
|---|---|
| `Choices()` works on an MM column and returns `Label` / `Path` / `Guid` / `WssId` | **Community-confirmed, multiple independent sources** |
| `Choices()` on an MM column is capped at **20 terms** | **Community-confirmed, multiple sources + an open MS Ideas request** |
| `Path` carries the full hierarchy | **Community-confirmed** |
| The `Path` segment delimiter is `;` | **Not first-party documented** — see below |
| Graph termStore walks the hierarchy (the >20 route) | **Confirmed** — MS Learn, GA Aug 2021 |
| `TermStore.Read.All` is delegated-only; app-only unsupported | **Confirmed** — MS Learn |
| Graph cannot set an MM **column value** on a list item | **Confirmed** — MS Q&A |
| Patching an MM column with a `Choices()` record | **Untested here** — but it hands the connector its own shape back, which is strictly better odds than a hand-built literal |

**The delimiter is the one genuinely unverifiable detail**, so it isn't guessed at: the component
takes it as a `PathDelimiter` input (default `";"`) and prints a raw `Path` on screen beneath the
picker. The first paste shows what the separator actually is, and the fix is one input. That is the
right shape for a one-way gap — a single "here's what it says" report settles it.

**Fallback if the `Choices()` record won't patch:** revert that one binding to the hand-built
`SPListExpandedTaxonomy` literal, taking the GUID from the same `LookUp` result. Check the field
name in Studio's intellisense first — the sources disagree between `Guid` and `TermGuid`.

**Cheapest first test:** create one project and set only a region. If the MM write lands, the whole
design is proven for the price of one paste — and unlike the previous plan, nothing has to be
provisioned or seeded first.

## Sources

- [Choices function — Power Fx reference](https://learn.microsoft.com/power-platform/power-fx/reference/function-choices)
- [Display more than 20 items for Managed Metadata fields — Xylos](https://xylos.com/powerapps-display-more-than-20-items-for-managed-metadata-fields/)
- [Display more than 20 items for Managed Metadata fields in Power Apps — Ward Wilmsen](https://wardwilmsen.com/2021/08/09/display-more-than-20-items-for-managed-metadata-fields-in-power-apps/)
- [Allow more than 20 entries from the managed metadata — Power Apps Ideas](https://ideas.powerapps.com/d365community/idea/fd814fe7-8dbf-4443-8ccf-8aaad24f4e6c)
- [PowerApps and managed metadata — Albert Hoitingh](https://alberthoitingh.com/2019/07/09/powerapps-and-managed-metadata/)
- [PowerApps, Flow and Managed Metadata fields — cleverworkarounds](https://www.cleverworkarounds.com/2017/10/23/powerapps-flow-and-managed-metadata-fields-part-4/)
- [List children — Graph termStore](https://learn.microsoft.com/graph/api/termstore-term-list-children?view=graph-rest-1.0)
- [Microsoft Graph what's new — termStore GA, Aug 2021](https://learn.microsoft.com/graph/whats-new-earlier#august-2021-new-and-generally-available)
- [Graph API managed metadata support — Microsoft Q&A](https://learn.microsoft.com/answers/a/1862317)
- [ParseJSON function — Power Fx reference](https://learn.microsoft.com/power-platform/power-fx/reference/function-parsejson) *(for the >20-term flow route)*
