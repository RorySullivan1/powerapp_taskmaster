# Core-shell — build notes, paste order, and the confirmation gate

Phase-1 shell authored from `docs/screen-map.md` (theme + Table-driven nav + screen
shells + empty states), now with a **Phase-2 composition pass** that drops component
instances onto Home/Reports/Projects with **static** data. **Data-independent** — no
`tm*` column tokens, so it is paste-ready before any SharePoint list is provisioned.
Nothing here is "in the app" until a human pastes it and it validates; log each crossing
in `../../paste-log.md`.

## Phase-2 composition (static data)

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
- **All values are static.** Every live query is a `TODO(Phase-2-data)` comment (KPI counts,
  ring `Percent`, project filter) — they need provisioned lists + true internal names.
- **Not yet composed:** the pills (`cmpStatusPill`/`cmpChoicePill`/`cmpUiKit`) and
  `cmpEditableGrid` are gallery/data-bound — they land when the data galleries are wired.

## Files

| File | Transfer path | What it is |
|---|---|---|
| `../patches/App.Formulas.pa.fx` | **Formula bar only** (App object has no code view) | `gUserEmail`, `Theme`, `NavMenu`, `gHasPowerBiLicence` |
| `scrHome.fx.yaml` | Code view | Landing shell — the reference header+nav template |
| `scrReports.fx.yaml` | Code view | Reports shell + the Q2 unlicensed empty-state card |
| `scrProjects.fx.yaml` | Code view | Projects shell + search box + empty placeholder |
| `scrReference.fx.yaml` | Code view | Clients/Products/Indices shell placeholder |
| `scrAdmin.fx.yaml` | Code view | Admin shell placeholder |

## Paste order (dependencies are real)

1. **Create five blank screens** in Studio, rename them exactly:
   `scrHome`, `scrReports`, `scrProjects`, `scrReference`, `scrAdmin`.
   (`NavMenu` holds live Screen references — they must exist by those names first.)
2. **Paste each screen's controls** via code view (one screen at a time; rename any
   `_1` suffix back and log it). The header + nav block is identical across screens.
3. **Paste `App.Formulas`** last, into the formula bar. Screen refs now resolve.
4. Set the app's **Data row limit to 2000** (schema.md) while you're in Settings.
5. Verify nav: each entry highlights the active screen and navigates.

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

## The one paste-critical token — resolved, with a fallback (one-way gap)

The air gap is **one-way** (repo → Studio; only binary "works/doesn't" returns), so there is
**no round-trip** to confirm a token against — unknowns must be resolved from **public sources**
or shipped as **grounded fallbacks**. The only token that gates a screen paste is the
`NavGallery` `Variant`:

- **Resolved to `Vertical`** (with the versioned `Gallery@2.15.0`) from public evidence: the
  modern source-code format pairs `Gallery@2.15.0` with `Variant: Vertical` for a plain vertical
  gallery. (The older/code-view value some sources show is `galleryVertical` — if `Vertical` is
  rejected, that is the one alternative to try.)
- **Grounded fallback if the gallery paste fails:** rebuild the nav from plain
  `Classic/Button@2.2.0` controls (`OnSelect: =Navigate(scrX, ScreenTransition.Fade)`) — a fully
  grounded token, paste-safest of all. It loses `NavMenu`-driven DRY (5 buttons per screen), but
  guarantees a navigable shell. Since a failed screen paste can only be reported as "didn't work,"
  this is the instant recovery — no revise-blind loop.

Everything else the screens use is a **grounded token** read from the real example export
(`Rectangle@2.3.0`, `Label@2.5.1`, `Classic/Icon@2.5.0`, `Classic/TextInput@2.3.2`,
`Classic/Button@2.2.0`, `Image@2.2.3`). Version suffixes are optional — Studio uses the current
version if omitted — so a version mismatch is not a failure mode; only the control *name* and
`Variant` matter.

## Deliberate deviations from the blueprint (rationale)

- **Nav is a per-screen gallery bound to `NavMenu`, not a reusable component.**
  `screen-map.md` calls for one nav *component* (T6). A canvas component can't code-view-paste
  across the one-way gap at all (it's hand-recreated in the component editor), whereas the
  screen — with its inline nav gallery — *does* paste. The `NavMenu` named formula already
  delivers T6's real intent — *screen refs as data, one source of truth for menu items* — with
  far lower transfer risk. The header + nav block is duplicated across the five screens as the
  cost of this.
  **Upgrade path (optional):** once you're comfortable recreating components by hand, lift the
  nav gallery into a component and place it on each screen; `NavMenu` stays as its Items source.

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
