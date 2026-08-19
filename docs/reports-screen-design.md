# scrReports — design

The reporting screen, rebuilt as **native analytics for every user**. Primary purpose: understand
**where people spend their time and how their projects are trending**. Secondary: **transactions
broken down by product type and currency**.

This is a design note, not source. The authored screen is `src/Screens/scrReports.pa.yaml`; every
field token below resolves to a `name:` in `schema/schema.yaml`. Where the two disagree the source
wins — parts of this note predate the current screen.

---

## Decisions this design rests on

Three were settled with the user on 2026-08-17 and belong in the Decisions ledger:

1. **Coverage is not a reporting axis.** The coverage × product-type grid, the ranked offering-gap
   list and the coverage filter that fed them are all gone. Nothing on the screen groups by
   `client_coverage` any more, so `taskmaster_clients` is not fetched at all.
2. **Power BI is OUT OF SCOPE entirely (2026-08-17).** Not demoted — dropped. `scrReports` is
   the analytics surface, full stop, and every chart on it is SVG. **This voids the
   `app-structure.md` rule** "do not rebuild the aggregate dashboard as native charts to dodge the
   licence gap": native charts are the design now, not a dodge. `gHasPowerBiLicence`,
   `NeedsLicence` and `cmpAppBar.HasLicence` are all deleted from the source.
3. **Effort is proxied, and labelled as such.** The model has no hours or effort column. "Where time
   goes" is measured as **task volume** — by activity family, output audience, requestor and region
   — with elapsed duration surviving only as the per-person **median days** and **on-time %**. The
   standalone median-cycle-time-by-family chart is gone, and **`task_output_format` is no longer
   reported anywhere**: the output breakdown groups by audience, which is the enforced column. The screen says "volume and elapsed time"
   on its face and never calls either "effort".

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
  only**. CROSS-CURRENCY CONVERSION IS OUT OF SCOPE (user, 2026-08-17) and is handled by other tools outside this project. The screen never
  shows a cross-currency total and must not be asked to.
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
| F2 | `colRptDoneAll` | `Filter(LiveTasks, task_stage.Value = "Completed")` | Yes — indexed Choice `=`. **Bounded on stage alone**; the period is applied locally into `colRptDone`. The old `&& task_date_completion >= gRptFrom` was false for a blank date, so a task completed without one never entered the collection and every completion measure read empty. Completed work accumulates, so this fetch is the one the truncation banner has to watch. |
| F3 | `colRptTx` | `Filter(taskmaster_transactions, transaction_project_archived = false && transaction_date >= gRptFrom2x)` | Yes — both indexed. **This is the load-bearing bound**; transactions grow fastest. |
| F4 | `colRptPrj` | `ActiveProjects` | Yes (named formula). Bounded in the hundreds. |
| F5 | `colRptIss` | `OpenIssues` | Yes (named formula). Small. |

`gRptFrom2x` is **twice** the selected period. One fetch then serves both the current window and the
prior-period delta, and feeds the monthly trend bars. Tasks get no prior-period delta — there is no
history to compare against.

Dimensions load **once per session**, not per period change:

| # | Collection | Source |
|---|---|---|
| D1 | `colRptProducts` | `taskmaster_products` — gives `product_uid` + `product_type_path` |

One dimension, because only one is still joined to. The product pies derive their slices from the
transactions themselves and no longer need a vocabulary list: they answer "what did we trade", not
"what have we never traded", so an absent group is correctly absent.

The output-format chart is the exception and still binds `Choices([@taskmaster_tasks].task_output_format)`
inline, because a format nobody currently uses should still show as a zero — the same lesson
`scrHome`'s donut records.

### 2. Fold once, at the finest grain

Everything renders from small pre-aggregated collections. **No `CountRows`, `LookUp` or `Filter`
over a fact collection may appear in any gallery `Items` or row property** — that is the N+1, and a
40-row people gallery each scanning 800 tasks is 32,000 row-scans *per repaint*.

| Fold | Rows | Built from |
|---|---|---|
| `colRptPrjMap` | ~hundreds | project ID → activity family L1, region L1, requestor, manager, supporter |
| `colRptOpenTag` | = F1 | each open task tagged with family, region, requestor and audience off **one** hoisted project lookup — and the ONLY place that join happens |
| `colRptPersonSrc` | ~2× tasks | tasks unpivoted on `task_lead` / `task_supporter`, each row carrying its measures **and the task itself** — name, health, start, due — plus a `Dup` flag. **No project lookup**: the family and format it used to carry fed overlay mini-charts that no longer exist |
| `colRptPerson` | ~20–50 | one row per person, every measure precomputed |
| `colRptPTask` | one person's tasks | built on row tap, feeds the overlay, refetches nothing |
| `colRptTxEnriched` | ≤ F3 | each transaction tagged with product type L1 **and L2**, its project's lead, currency, date, notional — two lookups, one per dimension |
| `*Pie` folds | ≤7 each | slice `Pct` and `Off` as whole percentages from a running cumulative |
| `colRptTxSeg` | buckets × currencies | per-bar currency segments with the running `Base` each stacks on |
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

| Person | Owns | Supports | Overdue | Health | Done | Median days | On-time % |
|---|---|---|---|---|---|---|---|

- **Health** is an inline stacked G/A/R bar — a plain `Image` + SVG data URI, **not** `cmpKpiRing`.
  A canvas component cannot be inserted into a gallery (MS Learn, known limitations #4) and the
  validator now fails on it.
- **Median days** = cycle time, `task_date_start` → `task_date_completion`, over the period's
  completions. The one real duration signal in the model.
- **On-time %** = completions where `task_date_completion <= task_date_target`, of those with a
  target set. The denominator excludes blank targets and the caption says so.
- **No Tx column.** It counted transactions on projects the person *manages*, which is project-level
  attribution in a row of task-level measures. Band 5 carries transaction volume properly.
- **The subtitle states two gaps**: open tasks with no supporter, and completed tasks with no
  completion date. The second cannot be placed in a period, so it counts in every one — a Done total
  that does not move with the window has to say why.

Tapping a row opens the **person overlay**: a plain list of their tasks — name, stage, health, date
opened, and due date with days left or overdue in parentheses on open work only. It reads
`colRptPersonSrc`, already in memory, and drops the duplicate row a person holds when they are both
lead and supporter. Zero refetch — that is the payoff for folding at person grain.

### Band 3 — Where the work sits

Four panels in one row, each `FillPortions: =1` at `LayoutMinWidth: =260` — about 1100px before the
row overflows:

- **By activity family** — horizontal bars, top 6 + Other, share of open tasks. Joined through the
  parent project.
- **By output audience** — a **pie**, fixed vocabulary + Unspecified + Other. Direct on the task, no
  join. `task_output_audience` rather than `task_output_format` because **`scrTaskEdit` blocks the
  save until an audience is picked whenever the Output section is on**, while format is never
  enforced and will accumulate blanks indefinitely. The column is younger than the open backlog, so
  Unspecified mostly means "predates the column" — the subtitle states its size, because on a pie
  that case and a broken report look identical. A non-zero Other outranks it in the subtitle: rarer,
  and a genuine data question.
- **By requestor** — bars, top 6 + Other, `project_requestor` through the parent project. The
  column is optional, so `Unassigned` is a real bucket and its size is stated even when it falls
  outside the top six.
- **By region** — a **pie** on level 1 of `project_region_path`.

### Band 4 — How projects are trending

Three columns, read left to right as **past · present · future**. `FillPortions` 2 : 1 : 2 — the two
bar charts carry up to 13 and 15 categories and need the room; the pie is a 320×150 box and does not.
The minimums add to ~950px, under both band 3 and band 5, so this band never sets the scroll width.

**Only the left panel is bound by the period strip.** The other two are not, and each says so on its
face — that is the whole reason they sit together.

- **Combo chart** *(window)* — bars: projects started per bucket (`project_date_start`); bars:
  completed per bucket (`project_date_complete`); line: **cumulative net open** (started − completed,
  running). That line is the direct answer to "how are projects trending" and needs no snapshot list,
  because it is built from dated **events** rather than stateful columns.
- **Projects by status** *(snapshot)* — a **pie** on `project_phase`, over a **fixed five-value
  sequence** rather than `Distinct`: the vocabulary is closed, so enumerating it holds lifecycle
  order and pins one colour per phase across refreshes. Archived is outside `ActiveProjects` and so
  is absent by construction. The count of open projects with **no target date** rides on the
  subtitle — the one datum from the retired ageing strip that nothing else on the screen carries.
- **Due next** *(forward)* — bars of open tasks by `task_date_target`, **today plus a fortnight**,
  15 fixed bars. Keyed on `Today()`, so the period strip does not move it. Weekends are shaded and
  today's bar is darkened. The three populations that are **not** in a bar — overdue, due beyond the
  fortnight, no target date — are counted on the subtitle, for the same reason `gRptDoneNoDate` is:
  a total that does not reconcile is worse than one that explains itself.

The combo chart's viewBox is **480 wide, not 900**. `ImagePosition.Fit` scales the box to the
control, so the box it carried while it owned the whole band would shrink a 15pt label to ~7px in a
third-width column; halving the box halves the downscale instead of shrinking the type. Labels drop
to every other bucket once the window yields more than 8.

Archived projects are outside `ActiveProjects`, so their completions are not counted. Stated on the
provenance line.

### Band 5 — Transactions *(secondary)*

Three columns, read left to right as **who · when · what**. `FillPortions` 1 : 2 : 2 — the trend
and the pies carry 900- and 320-wide viewBoxes and need the room; the lead bars are a six-row list
and do not.

- **By project lead** — bars, top 6 + Other, count of transactions on projects that person
  **manages**. This is the measure that was wrong beside the per-person *task* figures and is right
  here: project-level attribution, in the transactions band, labelled as such on the panel. A count,
  never a notional.
- **Trend bars** — the current window **split into currency segments**, the prior window greyed
  behind it. Colours are keyed on the currency *value*, never on rank, so EUR is the same colour on
  every load and two periods can be compared by eye.
- **Per-currency notional** — up to five small tiles, one per currency, never summed. The tiles carry
  the same colour Switch as the bars, which makes them the chart's legend.
- **By product type** — two pies **side by side**, level 1 and level 2 of `product_type_path`, top
  5 + Other on each.
  A product whose path has one segment counts under *Top level only* rather than being dropped, so
  the pies reconcile with the transaction count beside them.

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
2. ~~Real `client_coverage` values.~~ **NOT AN ASK — the screen does not need them.** The grid's
   row vocabulary is read with `Choices()` at runtime (D3), so whatever the column holds is what
   renders, and real values landing in SharePoint need no app change at all. What is outstanding is
   narrower and is a DOCUMENTATION issue: `schema.yaml` still records PLACEHOLDER values for this
   column and three others, so the golden source misdescribes SharePoint. That is worth fixing for
   anyone reading the schema to learn the vocabulary — it does not gate this build.

   The only value-dependent thing here is CARDINALITY, and it is already handled at runtime: past
   roughly 60 cells the heatmap suppresses itself and the ranked gap list carries the section.
3. ~~Confirm `transaction_sales` is sales-side, not desk-side.~~ **CONFIRMED 2026-08-17 — do not
   use it.** It is sales-side, so it is **not** a person-productivity attribution path and must not
   appear in `colRptPerson`. The user notes a later analysis may relate salespeople to
   transactions; that is a **separate view**, not a fourth column in the desk workload unpivot —
   folding it in would attribute desk effort to people who did none of it.
