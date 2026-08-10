# Core-shell — build notes, paste order, and the confirmation gate

Phase-1 shell authored from `docs/screen-map.md` (theme + Table-driven nav + screen
shells + empty states), now with a **Phase-2 composition pass** that drops component
instances onto Home/Reports/Projects with **static** data. **Data-independent** — no
`tm*` column tokens, so it is paste-ready before any SharePoint list is provisioned.
Nothing here is "in the app" until a human pastes it and it validates; log each crossing
in `../../paste-log.md`.

## Phase-2 composition + data binding

`scrHome`, `scrReports`, `scrProjects` now instantiate components (`components/`):

- **scrHome** — `cmpSectionHeader` + three `cmpStatusCard` KPI tiles + a `cmpKpiRing`,
  plus a `cmpToast` and a full-screen `cmpConfirmDialog` wired to a demo "Archive" button.
- **scrReports** — three `cmpKpiRing`s as the **licence-free Q2 fallback** (shown when
  `Not(gHasPowerBiLicence)`), beside the licence card.
- **scrProjects** — `cmpSectionHeader` + a `cmpSelection` filter strip.

Key facts:
- **Instance dialect (v3.0):** `Control: CanvasComponent` + `ComponentName: cmpX` +
  `Properties:` (base props `X/Y/Width/Height` **and** custom props). Instances have **no
  `Children:`**. The referenced components must **exist in the app first** — recreate them
  (see `components/_COMPONENTS-NOTES.md`) before pasting these screens.
- **Demo UI-state globals** (no schema, no `OnStart` — blank is falsy): `gToastMsg`,
  `gToastTone`, `gConfirmOpen`.
- **Data is now bound (2026-08-03).** `scrHome`, `scrProjects` and `scrReports` carry live,
  delegable queries against `schema/schema.yaml`'s columns. The shape everywhere is
  **filter server-side → aggregate locally**, because `CountRows`/`Average` never delegate
  to SharePoint. `scrReference` / `scrAdmin` remain shells.
- **Prerequisite:** these three screens **cannot paste until the lists are provisioned** and
  added as data sources — Studio can't bind to a list that doesn't exist. The two shells and
  the components still paste at any time.
- **Scope is deliberate on Reports:** an org-wide count can't be exact in-app (it only counts
  the rows already pulled), so every ring is scoped to your tasks or the active-projects list.
  Org-wide analysis stays in Power BI.
- **Not yet composed:** the pills (`cmpStatusPill`/`cmpChoicePill`/`cmpUiKit`) and
  `cmpEditableGrid` are gallery/data-bound — they land when the data galleries are wired.

## Files

| File | Transfer path | What it is |
|---|---|---|
| `../patches/App.Formulas.pa.fx` | **Formula bar only** (App object has no code view) | `gUserEmail`, `Theme`, `NavMenu`, `gHasPowerBiLicence` |
| `scrHome.pa.yaml` | Code view | Landing shell — the reference header+nav template |
| `scrReports.pa.yaml` | Code view | Reports shell + the Q2 unlicensed empty-state card |
| `scrProjects.pa.yaml` | Code view | Projects shell + search box + empty placeholder |
| `scrReference.pa.yaml` | Code view | Clients/Products/Indices shell placeholder |
| `scrAdmin.pa.yaml` | Code view | Admin shell placeholder — **landed, but from a stale copy carrying `Variant: CONFIRM_BlankVertical`. See paste-log.** |
| `scrProject.pa.yaml` | Code view | **Project detail — three tabs** (kanban / dense transactions table / issue feed) |
| `scrTaskEdit.pa.yaml` | Code view | **Task edit** — the SOLE writer of a task, and the live home of the C3 rollup write-back. (Superseded `scrTask`, deleted 2026-08-10.) |

## Paste order (dependencies are real)

1. **Create five blank screens** in Studio, rename them exactly:
   `scrHome`, `scrReports`, `scrProjects`, `scrReference`, `scrAdmin`.
   (`NavMenu` holds live Screen references — they must exist by those names first.)
2. **Recreate the components** in the component editor (`components/_COMPONENTS-NOTES.md`).
3. **Paste `App.Formulas`** into the formula bar — **now step 3, not last.** The data-bound
   screens reference `StageWeights`, which is defined there, so it must exist before they paste.
4. **Paste each screen's controls** via code view (one screen at a time, onto a blank screen;
   rename any `_1` suffix back and log it). The header + nav block is identical across screens.
   `scrHome` / `scrProjects` / `scrReports` additionally require their **lists provisioned and
   added as data sources** — they cannot paste before that.
5. Set the app's **Data row limit to 2000** (schema.md) while you're in Settings.
6. Verify nav: each entry highlights the active screen and navigates.

## Dialect — modern structured schema (corrected after pre-paste audit)

The files were **first authored in the retired inline `Name As type:` dialect** (that's
what `pac canvas unpack` emits — the format `studio-transfer` calls retired). The pre-paste
audit caught this against positive evidence: the example's **native** `.msapp` source
(`/example` → `Src/*.pa.yaml`) is the **modern structured schema**. The five screens were
**converted** to match it, using **real control-version tokens read from that genuine
export**:

| Control | Token (grounded in the example export) | Variant |
|---|---|---|
| Screen | *(top-level under `Screens:`)* | — |
| Rectangle | `Rectangle@2.3.0` | none |
| Label | `Label@2.5.1` | none |
| Icon | `Classic/Icon@2.5.0` | none |
| Text input | `Classic/TextInput@2.3.2` | none |
| Gallery | `Gallery@2.15.0` | `Vertical` (resolved from public evidence) |

Two dialect rules applied during conversion:
- **No `ZIndex`** — z-order is **positional** (later child in `Children:` renders on top).
  Every screen's children are ordered background-first, so the layering is correct.
- Modern controls (Rectangle/Label) carry no `Variant`; Classic controls here (Icon/TextInput)
  also declared without one, matching the export.

## The one paste-critical token — SETTLED (was wrong for a week)

The air gap is **one-way** (repo → Studio; only binary "works/doesn't" returns), so there is
**no round-trip** to confirm a token against — unknowns must be resolved from **public sources**
or shipped as **grounded fallbacks**. The token that gated every screen paste was the gallery
`Variant`, and the first answer here was **wrong**:

- ~~`Variant: Vertical`~~ **never existed.** It made every gallery render as a black block, which
  I first misdiagnosed as a zero-alpha fill problem. A photo of Studio's own code view settled it.
- **Correct form:** `BrowseLayout_<Orientation>_<Template>_ver5.0`. This repo uses
  `BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0` throughout — confirmed against Studio
  output, and the validator now rejects anything off the known list.
- **Grounded fallback if a gallery ever fails again:** rebuild that surface from plain
  `Classic/Button@2.2.0` controls — the paste-safest token there is. It loses the DRY of a
  data-bound gallery but guarantees a working screen, and a failed paste can only be reported as
  "didn't work," so having the recovery pre-written avoids a revise-blind loop.

Everything else the screens use is a **grounded token** read from the real example export
(`Rectangle@2.3.0`, `Label@2.5.1`, `Classic/Icon@2.5.0`, `Classic/TextInput@2.3.2`,
`Classic/Button@2.2.0`, `Image@2.2.3`). Version suffixes are optional — Studio uses the current
version if omitted — so a version mismatch is not a failure mode; only the control *name* and
`Variant` matter.

## Deliberate deviations from the blueprint (rationale)

- **Nav and the header are ONE component — `cmpAppBar` — and the rail flies out.**
  Originally the header block plus a nav gallery was copy-pasted into all eight nav screens, on
  the reasoning that components are the hardest thing to move across the gap. That reasoning
  held until the component channel was proven; it now is (contract typed by hand, body pasted
  via code view), so the whole shell collapsed into one definition with eight instances.

  The rail is no longer a permanent 240px column. It overlays the content when the hamburger is
  tapped and a scrim dismisses it, so screens start their content at `Theme.Space.Gutter` and use
  the full width. `Theme.Space.NavW` survives only as the rail's own width.

  **The instance `Height` carries the whole design:**
  `Height: =If(gNavOpen, Parent.Height, Theme.Space.HeaderH)`. A component intercepts every click
  in its bounds regardless of fill — the lesson that cost a preview session below — so closed it
  must own only its 64px strip. The instance is declared **last** on each screen so positional
  z-order floats the fly-out over the content.

  `cmpAppBar` **cannot Navigate** (a component can't see app screens): it exposes `SelectedKey`
  and raises `OnNavigate`, and the screen runs the `Switch` then `Set(gNavOpen, false)`. That is
  the only reason `NavMenu` carries a numeric `Key` rather than a screen — *a screen reference in
  a table is perfectly legal*, contrary to an earlier note here.

- **Absolute positioning tied to `Parent.Width/Height` + `Theme.Space.*`**, not nested
  responsive containers (T15). Simpler to paste one control at a time and diagnose. Revisit
  if a phone layout is required (open thread: tablet-vs-phone target).

## Open TODO for you (shapes the UX) — the Power BI licence gate

`gHasPowerBiLicence` in `App.Formulas` is hardcoded `false`. There is **no in-app Power BI
licence API**, so the signal must be chosen deliberately (a `tmLookups`/allow-list flag, or
an Entra group check). It drives both the greyed **Reports** nav entry and the Reports
empty-state vs. embed. Decide **hide vs. grey** for the unlicensed nav entry — currently the
shell *greys but still navigates* (the empty-state card explains it). See the TODO comment
in `App.Formulas.pa.fx`.
