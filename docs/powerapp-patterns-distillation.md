# PowerApp patterns distillation — reusable techniques for skills/agents

Distilled from two external repos, for capture as reusable Claude Code assets. Per claudeBrain's
**placement test** ("would another project want this? → it belongs in claudeBrain"), everything
here that is transferable is a **claudeBrain-upstream candidate**, not a `powerapp_taskmaster`
asset — this doc is the *proposal*, grounded in real source, of what to extend or build there.

**Sources**
- `aprildunnam/PowerApps` — ~25 sample apps/templates (mostly packaged binaries; readable value in
  two unpacked source trees + a few text gems). 20 techniques catalogued (T1–T20 below).
- `Mohd-Abbas-Rizvi/PowerApp-Project-Project-Manager-and-Tracker` — a SQL-backed project/task
  tracker; assessed as a **structural template** (see §E).

**Fold-first discipline** (from `skill-authoring`/`skill-distiller`): default to **extending** an
existing skill; author a **new** skill only where nothing covers the technique. Most of what
follows extends the eight adopted Power Platform skills; only three are genuine gaps.

**Air-gap caveat (governs all of it):** every snippet was read from an **export** dialect
(`.pa.yaml`/`.fx.yaml`) or legacy `.msapp` JSON — **not** the code-view *paste* dialect our
`studio-transfer` skill governs, and none is paste-tested. Treat each as a **pattern to
re-author** through the `pulled→authored→landed` lifecycle, with column tokens re-resolved
against our `schema.md` (these samples' `Employee`/`BillTo`/`Mon` names are theirs, not our `tm*`).

---

## A. Already covered by our adopted skills — validation, no action

These April patterns confirm our skills are aimed right; **do not re-capture** (they already live
in the skill bodies):

| Technique | Already in |
|---|---|
| T1 relative-date range filter (`Weekday(Today(),StartOfWeek.Monday)` math, two-sided delegable bound) | `power-fx-development` (delegation + date) |
| T2 `App.Formulas` + `Sequence`/`ForAll` over `Set`/`OnStart` | `power-fx-development` (named formulas) |
| T4 Person-column patch — `@odata.type` `SPListExpandedUser` + `"i:0#.f\|membership\|"` claims | `power-fx-development` (Person patching) — **verbatim match** |
| T5 repeated `Office365Users.ManagerV2` → hoist to `With` | `power-fx-review` (perf) + `graph-api-integration` |
| T11 `IsMatch`/`Match`-enum validation | `power-fx-development` |
| T13 anti-join `Not(x in Filter(...))` delegation caution | `power-fx-review` / `delegation.md` |
| T14 checkbox→`Collect` multi-select, `IsEmpty` nav guard | `power-fx-development` |
| T15 auto-layout containers, `FillPortions`, `ScreenSize` breakpoint | `power-apps-components` (responsive) |
| T16 `PowerAppsTheme.Colors.*` ramp; T17 Navigate-with-context, `Concurrent` OnVisible | `power-apps-components` / `power-fx-development` |

---

## B. Extend an existing skill — concrete recipes to add upstream

Net-new *examples/recipes* worth folding into a skill's body or a sidecar:

| # | Technique | Extend | What to add |
|---|---|---|---|
| T6 | **Nav component driven by a `Table({Name,Icon,Page})`** — screen references passed *as data*; `OnSelect: Navigate(ThisItem.Page)`; default `App.ActiveScreen` keeps it self-valid | `power-apps-components` | A "reusable app-nav component" recipe (directly relevant to our native-nav decision). |
| T7 | **Key/value `Styles` table as a component theming channel** — `LookUp(Comp.Styles, Key="Fill").Value` with fallback chain | `power-apps-components` | A "skinnable component without dozens of properties" recipe. |
| T9 | **Timer-init for components** (`Timer.AutoStart = IsBlank(_guard)`) — the standard "components have no OnStart" workaround | `power-apps-components` | Component-lifecycle note. |
| T8 | **Calendar/date-range picker on a 42-cell `WrapCount:7` gallery** — first-day math `DateAdd(_firstOfMonth, -(Mod(Weekday(_firstOfMonth)-2,7)+1), Days)` | `power-apps-components` | Capture as a **reference note** (heavy; reference impl, not inline). |
| T12 | **Sortable `yyyymmddhmm` companion Number column** for delegable date filter/sort | `sharepoint-list-architecture` (+ `power-fx-development` why) | Schema-side delegation workaround; **also useful to us** (see §D). |
| T3-lite / T17 | Copy-from-history (`ClearCollect(coll, Filter(src, week = prior))`), parallel `OnVisible` | `power-fx-development` | Small idioms worth an example. |

---

## C. Genuine gaps → candidate NEW skills (and each is dual-use for *our* app)

Nothing in the family covers these. All three are strong claudeBrain-upstream candidates **and**
directly useful to `powerapp_taskmaster` — which strengthens the case to author them:

### C1 — `power-apps-svg` (or a `power-apps-components` sidecar): **SVG rendered in an Image control**  *(from T10)*
- **Pattern:** `Image.Image = "data:image/svg+xml," & EncodeUrl("<svg …>…</svg>")`; drive a progress
  ring via `stroke-dasharray='" & pct & " " & (100-pct) & "'`. Gauges, donuts, KPI rings, custom
  icons — zero image assets, no PCF.
- **Why new:** distinct surface from `sharepoint-column-formatting` (list-cell JSON) and from
  `power-apps-components`' HtmlText. Vector rendering *inside the app* has no home.
- **Why it matters to us:** **not everyone is Power BI-licensed** (our Q2). SVG rings/gauges are
  exactly the **native visual fallback** for the licence-gated dashboard's empty state — real KPIs
  without Power BI. High-value.

### C2 — `power-apps-editable-table` (recipe/skill): **grid-in-a-gallery**  *(from T3)*
- **Pattern:** collection-backed gallery (`Items = colRows`); per-row inputs `Value: =ThisItem.X`;
  add = `Patch` current + `Collect` blank; delete = `Remove(coll, ThisItem)`; bulk-save =
  `ForAll(gallery.AllItems, Patch(Source, Defaults(Source), {…}))`. The `Defaults(source)` (new)
  vs `ThisRecord` (update) distinction is the classic trap.
- **Why new:** Power Apps has no native editable grid; this is *the* community answer and it's not
  in any skill. Most-reused single pattern in April's repo.
- **Why it matters to us:** our project-detail **tickets tab is a "dense numeric table"**, and bulk
  task edits fit this exactly.

### C3 — Reference note (not a full skill): **Teams deep-linking / embedding**  *(from T19)*
- **Pattern:** the two `teams.microsoft.com/l/entity/…` URL shapes, the URL-encoded `subEntityId`
  JSON `context`, read in-app via `Param("subEntityId")`; the `_djb2_msteams_prefix_…` tab entity id.
- **Why note, not skill:** it's a small set of load-bearing verbatim facts, not a behavior. No
  existing skill owns Teams integration; if Teams embedding recurs, promote to a skill later.

---

## D. Reference-note facts + a provisioning idea relevant to *us* now

- **Flow-as-list-provisioner** *(T18)* — April ships each template's backend as an importable
  **Power Automate flow** that creates the SharePoint lists/columns from a site URL. **This is
  directly relevant to our Q11/Q12:** we chose *manual UI* provisioning (high `_x0020_` risk, no
  repeatability) partly because there was no wrapper. A provisioner **flow** is a middle path that
  sets clean internal names repeatably — worth reconsidering Q11 against. Capture as a note/thread.
- **Lookup-column patch shape** *(T4 variant)* — `{'@odata.type':"#…SPListExpandedReference",
  Id:…, Value:…}`. We decided **no Lookup columns**, so low relevance to us, but a real
  claudeBrain fact (pairs with the Person shape already in `power-fx-development`).
- **Calendar first-day formula** *(T8)* and the **`@odata.type` magic strings** — verbatim facts for
  an upstream note; the Person one is already in our skill.

---

## E. The PM-tracker repo as a "core template" — blueprint yes, plumbing no

`Mohd-Abbas-Rizvi/…Project-Manager-and-Tracker` is a **SQL Server-backed** tracker (`ProjectTrackerDB`;
`[dbo].[User]/[ProjectTask]/[Projects]/[Account]`; a `vw_TaskStatusSummary` SQL view; a `FlowPT`
task-assignment email flow). Six screens + a pie dashboard, native `Navigate`.

- **Reuse (blueprint):** the **screen inventory & native-nav flow** (User/Client/Project/Task mgmt +
  Dashboard) — validates our plan and matches our "native nav primary" decision; the
  **task-assignment→email flow** (our Q12); **FK-by-integer-ID + client-side selection**
  (`Filter(child, FK = Gallery.Selected.ID)`) — matches our "no Lookup columns" decision.
- **Do NOT port (plumbing):** it's **SQL** — delegates aggregates/`contains`/`Sum` server-side that
  **SharePoint does not**; its dashboard aggregates via a **SQL view = the "snapshot list" we
  rejected**; **auto-increment PKs** (we derive keys from built-in `ID` in a 2nd write);
  dropdowns/role columns (ours are `tmLookups`); `UserID/UserName` (ours are **Person** columns).
  It also lacks our **Ticket** and **Issue** peers — our model is a superset.
- **How to use it:** as the UX skeleton to **rebuild against our SharePoint schema** via code-view
  paste, re-deriving every data formula through `power-fx-development`'s delegation rules. It's a
  read-only `.pa.yaml` export anyway, so "template" = *learn-and-rebuild* — consistent with our air gap.

---

## F. Recommendation

1. **Propose upstream to claudeBrain** (they're for "other PowerApp dev"): the **§B recipe
   extensions**, and the three **§C candidates** — with C1 (SVG) and C2 (editable-table) as new
   sidecars/skills, C3 (Teams) as a note.
2. **Author here now, dual-use**, if desired: **C1 SVG** (native fallback visuals for unlicensed
   users) and **C2 editable-table** (tickets tab) earn their place in *our* app too — I can draft
   them so they're both usable here and upstream-ready.
3. **Reconsider Q11** against the **flow-as-provisioner** pattern (§D) — it may beat manual UI.
4. **PM-tracker** → use as the §E blueprint for the screen map; do not port its data layer.
