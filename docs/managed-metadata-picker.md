# Managed Metadata: cascading term picker — research & validation

**Verdict: the proposed approach works.** Detect nesting as the user selects, generate another
dropdown per level until the leaf, then write the selected term's **GUID** into the SharePoint
managed-metadata column. Both halves are supported. One architectural choice and one dependency
remain, both called out below.

Context: `project_region`, `project_type` (required) and `project_coverage` on
`taskmaster_projects`, plus `client_type`/`client_coverage`/`client_region` and `product_type`,
are **Managed Metadata and staying that way** (decision 2026-08-03). Without a working picker,
creating a project from the app is impossible, because two of those are required.

---

## 1. Reading the hierarchy — **confirmed, first-party**

The Microsoft **Graph termStore API** is generally available (since August 2021) and exposes
exactly the parent/child walk the design needs:

```http
GET /sites/{site-id}/termStore/sets/{set-id}/children              # top-level terms of a set
GET /sites/{site-id}/termStore/sets/{set-id}/terms/{term-id}/children   # one level down
```

- A `term` carries `id` (**the GUID we need**), `labels`, and a `children` relationship.
- **Nesting detection falls out of the API**: call `children` on the selected term — a non-empty
  collection means another level exists, so render another dropdown; empty means leaf, stop. That
  is precisely "until the depth required is met", and it needs no hard-coded depth.
- **Permissions:** `TermStore.Read.All` (least privileged), `TermStore.ReadWrite.All` higher.
  ⚠ **Delegated only — application (app-only) permission is *not supported*** for these endpoints.
  Whatever calls Graph must run **as the signed-in user**, not as a daemon.

### The "Graph doesn't support managed metadata" caveat — resolved

Our own `schema.md` says Graph doesn't fully support managed metadata, and that's still true — but
it refers to **the list column's value**, not the term store. Microsoft's own guidance now says the
**Graph taxonomy API is the recommended approach** for term-store work, over CSOM. Both statements
hold at once:

| Surface | Graph support |
|---|---|
| Term **store** (groups, sets, terms, children) | ✅ GA, and the recommended route |
| Managed-metadata **column values on list items** | ❌ still not fully supported |

So we read terms with Graph and write the column with the **SharePoint connector**, not Graph.

## 2. Writing the value — **community-confirmed, not first-party**

A single-value MM column is patched as an expanded-taxonomy record:

```powerapps
Patch( taskmaster_projects, Defaults(taskmaster_projects),
    { project_region:
        { '@odata.type': "#Microsoft.Azure.Connectors.SharePoint.SPListExpandedTaxonomy",
          TermGuid: gRegionTermGuid,      // the leaf term's Graph `id`
          Label:    gRegionLabel,
          WssId:    -1,                   // -1 = "not cached in this site yet; resolve by GUID"
          Path:     gRegionPath,          // full hierarchical path, e.g. "EMEA;UK"
          Value:    gRegionLabel } } )
```

- `WssId: -1` is the important part — it tells SharePoint to resolve the term by GUID rather than
  by a site-collection cache id that a new value won't have.
- **This shape is not in Microsoft's first-party docs.** It is consistently reported across
  independent community sources, but under a one-way gap that makes it the **single riskiest
  construct in the whole app**. Treat the first paste of a project-create as a test of this shape
  specifically, and see §5.

## 3. Architecture — two options, and a recommendation

The canvas app **cannot call Graph directly**; there's no generic HTTP action in Power Apps. So
something has to sit between:

| | **A. Live Graph call per level** | **B. Cached term list** *(recommended)* |
|---|---|---|
| How | App → Power Automate flow (or custom connector) → Graph `children` on each selection | A scheduled flow walks the term store and writes a flat SharePoint list; the app reads that list natively |
| Freshness | Always current | Stale between refreshes (terms change rarely) |
| Runtime cost | A flow call **per dropdown level, per user, per form** | None — it's just another list |
| Delegation | N/A (flow returns a small payload) | **Delegable** `Filter` on `parent_guid`; indexable |
| Offline / latency | Round-trip on every pick | Instant |
| Dependency at runtime | **Hard** — Power Automate/custom connector must be up | None; only the nightly refresh needs it |
| Failure mode | Form unusable if the flow fails | Form keeps working on last-known terms |

**Recommend B.** The term store is a slow-moving vocabulary; paying a network round-trip per
dropdown level to re-derive a hierarchy that changes monthly is a poor trade, and it makes the
create form depend on a flow being healthy. Option B also keeps the app's *runtime* dependency
surface at zero, which matters more than usual here — we can't debug it interactively.

### The cache list (proposed — needs a decision before provisioning)

`taskmaster_terms`, one row per term, flat with a parent pointer:

| Column | Type | Notes |
|---|---|---|
| `term_guid` | Text, indexed | The Graph term `id` — what gets written to the MM column |
| `term_label` | Text, indexed | Display label |
| `term_set` | Choice, indexed | Which vocabulary: `Region`, `ProjectType`, `Coverage`, `ClientType`, `ProductType` |
| `term_parent_guid` | Text, indexed | Empty for top level — **this is what drives the cascade** |
| `term_path` | Text | Full path, for the `Path` field of the patch |
| `term_depth` | Number | 1-based; convenience for the UI |
| `term_is_leaf` | Yes/No | Precomputed — avoids a count to decide whether to show another level |

The cascade then becomes ordinary delegable Power Fx, with no flow in the loop:

```powerapps
// Level 1
Filter( taskmaster_terms, term_set.Value = "Region" && IsBlank(term_parent_guid) )
// Level N+1 — driven by the level-N pick
Filter( taskmaster_terms, term_set.Value = "Region" && term_parent_guid = gRegionPick1.term_guid )
```

Each is a delegable `=` on indexed Text. Depth is discovered from the data (`term_is_leaf`), so
the UI generates levels until the leaf — exactly the proposed behaviour, with no Graph at runtime.

## 4. Dependency

Either option needs **Power Automate or a custom connector** — that is still **open question Q12**,
and it is now blocking, because two required MM columns mean *no project can be created from the
app* until a term source exists. Option B needs it only for a scheduled refresh; option A needs it
on every keystroke.

## 5. What is proven vs what must be tested

| Claim | Status |
|---|---|
| Graph termStore `children` walks the hierarchy and yields term GUIDs | **Confirmed** — MS Learn, GA Aug 2021 |
| Delegated `TermStore.Read.All`; app-only **not supported** | **Confirmed** — MS Learn |
| Graph is the recommended term-store route over CSOM | **Confirmed** — MS Learn |
| Graph still can't set an MM **column value** on a list item | **Confirmed** — MS Q&A |
| `SPListExpandedTaxonomy` + `WssId: -1` writes an MM column from Power Apps | **Community-confirmed only** — highest-risk construct in the app |
| Our specific tenant/connector version accepts that shape | **Untested** |

**Cheapest possible test, before any of this is built:** provision `taskmaster_projects`, then
paste a one-button screen whose `OnSelect` patches a single project with one hard-coded
`TermGuid`/`Label`/`Path`. If it writes, the whole design is unblocked. If it errors, we learn the
exact message and adapt — and we've spent one paste instead of an entire create-flow.

## Sources

- [List children — Graph termStore](https://learn.microsoft.com/graph/api/termstore-term-list-children?view=graph-rest-1.0)
- [set resource type — Graph termStore](https://learn.microsoft.com/graph/api/resources/termstore-set?view=graph-rest-1.0)
- [Microsoft Graph what's new — termStore GA, Aug 2021](https://learn.microsoft.com/graph/whats-new-earlier#august-2021-new-and-generally-available)
- [Add-In / ACS retirement FAQ — Graph taxonomy API recommended](https://learn.microsoft.com/sharepoint/dev/sp-add-ins/add-ins-and-azure-acs-retirements-faq#can-i-still-perform-taxonomy-updates)
- [Graph API managed metadata support — Microsoft Q&A](https://learn.microsoft.com/answers/a/1862317)
- [Saving to SharePoint Managed Metadata columns using Patch — Power Platform Community](https://community.powerplatform.com/blogs/post/?postid=acb09ed6-bda5-4c3a-b70d-ccda63a6ba2e)
- [Power Apps Patch for SharePoint's complex column types — sympmarc](https://sympmarc.com/2020/12/23/powerapps-patch-function-for-sharepoints-complex-column-types/)
- [PowerApps, Flow and Managed Metadata fields — cleverworkarounds](https://www.cleverworkarounds.com/2017/10/23/powerapps-flow-and-managed-metadata-fields-part-4/)
