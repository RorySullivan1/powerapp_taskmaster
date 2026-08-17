# scrReports — design

The reporting screen, rebuilt as **native analytics for every user**. Primary purpose: understand
**where people spend their time and how their projects are trending**. Secondary: **transactions by
client coverage, broken down by product type level 1**, and the **offering gaps** that fall out of
that grid.

This is a design note, not source. The authored screen is `src/Screens/scrReports.pa.yaml`; every
field token below resolves to a `name:` in `schema/schema.yaml`.

---

## Decisions this design rests on

Three were settled with the user on 2026-08-17 and belong in the Decisions ledger:

1. **Coverage axis = `client_coverage`.** A transaction reaches coverage through its client
   (`transaction_client_name` → `taskmaster_clients.client_coverage`), not through its project. The
   gap grid therefore reads "this coverage team has never traded that product type".
2. **Power BI is OUT OF SCOPE entirely (2026-08-17).** Not demoted — dropped. `scrReports` is
   the analytics surface, full stop, and every chart on it is SVG. **This voids the
   `app-structure.md` rule** "do not rebuild the aggregate dashboard as native charts to dodge the
   licence gap": native charts are the design now, not a dodge. `gHasPowerBiLicence`,
   `NeedsLicence` and `cmpAppBar.HasLicence` are all deleted from the source.
3. **Effort is proxied, and labelled as such.** The model has no hours or effort column. "Where time
   goes" is measured as **task volume** by activity family and output format, plus **median cycle
   time** (`task_date_start` → `task_date_completion`) as a genuine elapsed-duration signal. The
   screen says "volume and elapsed time" on its face and never calls either "effort".

---

## What this screen cannot do

Stated here so a later session doesn't try to build it and find out the hard way.

- **No point-in-time history.** `project_perc_completion`, `task_stage` and `project_phase` are
  *current state* with no snapshot anywhere. "Completion over time" is therefore impossible natively.
  All trend on this screen is built from **dated events** (`transaction_date`,
  `task_date_completion`, `project_date_start`, `project_date_complete`) — never from stateful
  columns. A true snapshot needs a snapshot list written by a scheduled flow (blocked on Q12).
- **No blended notional.** C5 is emphatic: `transaction_notional` is denominated in
  `transaction_currency` and must never be summed across rows. Notional appears **per currency
  only**. **Nothing owes the FX-converted figure** now that Power BI is out of scope — it needs
  an FX dimension the model does not have. Open decision.
- **No org-wide certainty past the row cap.** Aggregates never delegate to SharePoint, so every
  number here is computed locally over fetched rows. The truncation banner (below) is what keeps
  that honest.

---

## Architecture: fetch bounded → fold once → render from folds

This is the whole speed story. Three rules, in priority order.

### 1. Bound the fetch at the source

The unbounded-growth part of the data is exactly the part that can be date-bounded, and the part
that can't be date-bounded is self-limiting. That is what makes this screen scale.

| # | Collection | Query | Delegable? |
|---|---|---|---|
| F1 | `colRptOpen` | `Filter(LiveTasks, task_stage.Value = "Not Started" \|\| … \|\| "Finalizing")` | Yes — Boolean `=` + indexed Choice `=` Or-chain. Unbounded but self-limiting: open work does not accumulate. |
| F2 | `colRptDone` | `Filter(LiveTasks, task_stage.Value = "Complete" && task_date_completion >= gRptFrom)` | Yes. **`task_date_completion` is not indexed** — see schema asks. |
| F3 | `colRptTx` | `Filter(taskmaster_transactions, transaction_project_archived = false && transaction_date >= gRptFrom2x)` | Yes — both indexed. **This is the load-bearing bound**; transactions grow fastest. |
| F4 | `colRptPrj` | `ActiveProjects` | Yes (named formula). Bounded in the hundreds. |
| F5 | `colRptIss` | `OpenIssues` | Yes (named formula). Small. |

`gRptFrom2x` is **twice** the selected period. One fetch then serves both the current window and the
prior-period delta, and feeds the monthly trend bars. Tasks get no prior-period delta — there is no
history to compare against.

Dimensions load **once per session**, not per period change:

| # | Collection | Source |
|---|---|---|
| D1 | `colRptClients` | `taskmaster_clients` — gives `client_name` + `client_coverage` |
| D2 | `colRptProducts` | `taskmaster_products` — gives `product_uid` + `product_type_path` |
| D3 | `colRptCoverage` | `Choices([@taskmaster_clients].client_coverage)` |
| D4 | `colRptProdL1` | `Distinct(mapping_producttype, level1)` |

**D3 and D4 are the vocabularies, and they must come from the dimension lists rather than from the
transactions.** A gap is an *absent* group. Deriving the axes from the data would delete exactly the
cells you are looking for. This is the same lesson `scrHome`'s donut already records — a category
only exists when a row has that value.

`project_coverage` and `client_coverage` still carry PLACEHOLDER values in the golden source, so
coverage is bound with `Choices()` at runtime and never a literal — the pattern `scrProjects`
already lands.

### 2. Fold once, at the finest grain

Everything renders from small pre-aggregated collections. **No `CountRows`, `LookUp` or `Filter`
over a fact collection may appear in any gallery `Items` or row property** — that is the N+1, and a
40-row people gallery each scanning 800 tasks is 32,000 row-scans *per repaint*.

| Fold | Rows | Built from |
|---|---|---|
| `colRptPrjMap` | ~hundreds | project ID → activity family L1, coverage, manager, supporter |
| `colRptPersonSrc` | ~2× tasks | tasks unpivoted on `task_lead` / `task_supporter`, each row already tagged with activity family via `colRptPrjMap` |
| `colRptPerson` | ~20–50 | one row per person, every measure precomputed |
| `colRptTxEnriched` | ≤ F3 | each transaction tagged with `client_coverage` + product type L1 |
| `colRptMonths` | 12–24 | written-out month buckets |
| `colRptGrid` | nCov × nProd | full cross product, counts joined in |
| `colRptCcy` | ≤5 | per-currency notional totals |

**Person attribution: exactly two paths, both from tasks.** A task counts once for its
`task_lead` ("owns") and separately for its `task_supporter` ("supports"). The two are **never
summed into one workload number** — that would double-count the desk total. Both columns are
single Person and indexed, so the unpivot is exact.

**`transaction_sales` IS NOT A THIRD PATH** (user-confirmed 2026-08-17). It is sales-side, not
desk-side: the person who sold the trade did not do the desk work the screen is measuring. It
stays out of `colRptPerson` entirely. A sales-to-transaction view may come later and is a
different question from "where does desk time go".

**Activity family / product L1 extraction.** The `*_path` columns store levels joined by `" | "` and
the separator is part of the stored data. Take level 1 with `Find`/`Left` rather than `Split`, and
bucket blanks explicitly:

```powerapps
With( { s: Trim(Coalesce(project_type_path, "")) },
    With( { i: Find(" | ", s) },
        If( IsBlank(s), "Unclassified", If( i > 0, Left(s, i - 1), s ) ) ) )
```

**Month bucketing** uses an integer key — `Year(d) * 12 + Month(d)` — not date comparison. Exact, and
it sidesteps every timezone and month-length edge.

**Positional rows** use the established `Sequence(CountRows(...))` + `Index(...)` idiom from
`scrHome`. The grid's cell index maps to row/col with `RoundDown((s-1)/nProd,0)+1` and
`Mod(s-1,nProd)+1`, which also hands the SVG heatmap the coordinates it needs.

### 3. Refetch only when the period changes

| Interaction | Refetch | Refold | Cost |
|---|:-:|:-:|---|
| Period change | yes (F1–F5) | yes | the only network cost on the screen |
| Scope change (Me / My projects / Desk) | no | no | re-filter `colRptPerson` (~40 rows) |
| Coverage filter | no | no | re-filter `colRptGrid` / `colRptTxEnriched` |
| Tap a person | no | no | overlay reads existing folds |
| Screen revisit | no | no | guarded on `gRptKey <> gRptLoadedKey` |
| Refresh button | yes | yes | explicit, user-initiated |

The person detail is an **overlay, not a screen** — a `Navigate` would cost a fresh `OnVisible` and
throw away every fold.

---

## Three guards that are correctness, not polish

**Explicit Column Selection.** ECS is on by default and trims retrieved columns to those it can
prove are used. Microsoft documents that **column lineage is occasionally lost when data moves
through collections and variables, and ECS then drops the column**. This is the most
collection-heavy screen in the app, so it is the most exposed. **Every `ClearCollect` names its
columns with `ShowColumns`.** A dropped column here renders as a blank number, which across the
one-way gap returns only as "it didn't work".

**Truncation banner.** Every fact fetch compares its own `CountRows` against the data row limit
(2,000). If any fetch comes back at the cap, a full-width amber bar states which one and that the
figures below are a floor, not a total. A report that silently undercounts is worse than no report,
and this is the only place the app can detect it.

**Vocabulary drift.** Fixed-vocabulary breakdowns (`task_output_format`, `task_status`, `task_stage`)
carry an explicit **"Other"** bucket counting rows matching none of the enumerated values, plus
**"Unspecified"** for genuine blanks on optional columns. If Other is ever non-zero, SharePoint and
`schema.yaml` disagree — visible on sight instead of silently reweighting every share.

---

## Layout

Body is a vertical `GroupContainer` / AutoLayout with `LayoutOverflowY: Scroll`, offset by
`gTheme.Space.HeaderH`. Sections stack, so there is **no manual Y arithmetic** — the current screen's
`HeaderH + Gutter + 220 + Gutter + 60 + Gap` chains are a maintenance trap and go.

`cmpAppBar` stays declared **last** for positional z-order, `ActiveKey: =2`, unchanged.

### Band 0 — Control bar (fixed, outside the scroll body)

Period strip · Scope strip · coverage combo · refresh + "as at HH:MM" · truncation banner.

Both strips are `cmpSelection` — confirmed working since 2026-08-13, fed from `Choices()` where the
vocabulary is data. Period: Quarter · 90 days · YTD · 12 months. Scope: Me · My projects · Desk.

### Band 1 — Desk pulse

Four tiles, horizontal AutoLayout: **Open tasks · Overdue · Transactions (period) · Open issues.**
Transactions carries a prior-period delta; the task tiles do not, and do not pretend to.

### Band 2 — People *(primary)*

The tallest band. Section header states the measurement basis in its subtitle. One gallery row per
person (~40 max), tappable column headers sorting a ~40-row collection:

| Person | Owns | Supports | Overdue | Health | Done | Median days | On-time % | Tx |
|---|---|---|---|---|---|---|---|---|

- **Health** is an inline stacked G/A/R bar — a plain `Image` + SVG data URI, **not** `cmpKpiRing`.
  A canvas component cannot be inserted into a gallery (MS Learn, known limitations #4) and the
  validator now fails on it.
- **Median days** = cycle time, `task_date_start` → `task_date_completion`, over the period's
  completions. The one real duration signal in the model.
- **On-time %** = completions where `task_date_completion <= task_date_target`, of those with a
  target set. The denominator excludes blank targets and the caption says so.
- **Tx** = transactions on projects the person manages or supports — impact as a **count**, because
  C5 forbids a blended notional.

Tapping a row opens the **person overlay**: their activity-family mix, output-format mix, open-by-
stage, their projects with completion %, their transaction count. Every figure comes from folds
already in memory — zero refetch. That is the payoff for folding at person grain.

### Band 3 — Where the work sits

Two 50% panels, then a full-width strip:

- **By activity family** — horizontal bars, top 6 + Other, share of open tasks. Joined through the
  parent project.
- **By output format** — same, fixed vocabulary + Unspecified + Other. Direct on the task, no join.
- **Median cycle time by activity family** — the elapsed-time counterpart to the two volume charts.

Scope-aware, and filtered further when a person is selected.

### Band 4 — How projects are trending

Built entirely from dated events, since no history exists:

- **Combo chart** — bars: projects started per month (`project_date_start`); bars: completed per
  month (`project_date_complete`); line: **cumulative net open** (started − completed, running).
  That line is the direct answer to "how are projects trending" and needs no snapshot list.
- **Ageing panel** — open projects bucketed by days since start (<30 · 30–90 · 90–180 · 180+), the
  `Stalled` count, and the count with no target date set.

Archived projects are outside `ActiveProjects`, so their completions are not counted. Stated on the
provenance line.

### Band 5 — Transactions *(secondary)*

- **Monthly trend** — count bars, current window solid, prior window greyed.
- **Per-currency notional** — up to five small tiles, one per currency. Never summed.
- **Coverage × product-type-L1 heatmap** — one SVG `Image`, cell shade by count, zero cells drawn
  empty with a hairline border so a gap is visible rather than absent. **Legibility ceiling: about
  60 cells** (e.g. 6 coverage × 10 product types). Past that the heatmap is suppressed and the gap
  list carries the section alone.
- **Ranked gap list** — every zero cell, sorted, each row carrying the number of clients in that
  coverage group so the opportunity is sized: *"Coverage B — 14 clients, no Rates transactions."*
  This is what makes the section actionable rather than decorative.

### Band 6 — Footer

A provenance line: window in force, archived work excluded, truncation state.

---

## SVG rules

All charts are SVG data URIs in `Image` controls, per the pattern already proven on `scrHome`.

- **Every coordinate is a whole number.** Fractions must be rendered with `Text()`, which drags the
  locale decimal separator into an SVG attribute; an attribute Power Fx cannot render is an *empty*
  attribute, and an empty `stroke-dasharray` draws a solid ring, not a thin arc. Scale the viewBox
  (10× natural size) to keep precision.
- **Build the data as a collection first**, never inline in the `Image` formula. A chart that draws
  nothing is indistinguishable from a chart whose data never arrived; a collection can be opened in
  Studio's Collections pane, which splits "the maths is wrong" from "there is nothing to plot".
- Colours are injected unencoded and must stay app-trusted constants. **Coverage and product names
  come from list data and are rendered as text in the heatmap — `EncodeHTML` them.**

---

## Collection namespace

**Everything new is prefixed `colRpt*` / `gRpt*`.** The current `scrReports` collects into
`colMyTasks` and `colMyProjects` — *the same names `scrHome` uses*. Today both screens apply
identical "mine" filters so the collision is benign; the moment this screen goes desk-wide, Home's
KPIs would silently read desk-wide data. The existing reuse is dropped.

Retired with the rebuild: `gRptOpen`, `gRptOnTrack`, `gRptAtRisk`, `gRptPortfolio` and the three
`cmpKpiRing` instances. The licence card is already gone.

`OnVisible` keeps the `gUserEmail` self-heal. `App.OnStart` is non-blocking, and these are
imperative `Set`s — they run once and never re-fire, so a blank `gUserEmail` would latch the whole
screen at zero.

---

## Hand-off

Full screen replacement, not an edit. Per the standing rule the user **deletes `scrReports` in
Studio before pasting it back**, so no orphaned controls survive. `tools/validate_pa_yaml.py` must
pass first, and it now hard-fails on a component inside a gallery — the per-row health bar is a
plain `Image` for that reason.

## Schema asks

Small, and none of them block the build:

1. **Index `task_date_completion`** (`taskmaster_tasks`, DateTime). F2's window filter rides on it.
   It is combined with two indexed predicates so it will hold for now, but it is the cheap insurance
   and indexes cannot be added past 20,000 items.
2. **Real `client_coverage` values.** The gap grid's row vocabulary *is* this column; PLACEHOLDER
   values make the grid meaningless. Already an open thread covering four columns.
3. ~~Confirm `transaction_sales` is sales-side, not desk-side.~~ **CONFIRMED 2026-08-17 — do not
   use it.** It is sales-side, so it is **not** a person-productivity attribution path and must not
   appear in `colRptPerson`. The user notes a later analysis may relate salespeople to
   transactions; that is a **separate view**, not a fourth column in the desk workload unpivot —
   folding it in would attribute desk effort to people who did none of it.
