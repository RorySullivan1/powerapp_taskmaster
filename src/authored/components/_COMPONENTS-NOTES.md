# Reusable components — contracts, constraints, and transfer

Ten reusable UI building blocks for the EQD Taskmaster app, authored in the **v3.0
`.pa.yaml` `ComponentDefinitions`** schema (grounded on the official schema:
`microsoft/PowerApps-Tooling` `schemas/pa-yaml/v3.0/pa.schema.yaml`). Data-independent —
no `tm*` tokens. Colours **inline** the `App.Formulas` `Theme` palette because a component
is isolated and can't read app globals; keep the hex/RGBA in step with `Theme`.

## The set

| File | What it is | Kind | Key contract |
|---|---|---|---|
| `cmpUiKit.pa.yaml` | Pill/chip/person **HTML builders** | Function library | `StatusPillHtml(label,tone)`, `ChoicePillHtml(label,selected)`, `PersonChipHtml(name)`, `Initials(name)` → all `OutputFunction` returning HtmlText |
| `cmpStatusPill.pa.yaml` | Status badge (screen-level) | Component | in: `Label`, `Tone` |
| `cmpChoicePill.pa.yaml` | Clickable filter chip | Component | in: `Label`, `Selected`; event: `OnSelect` |
| `cmpStatusCard.pa.yaml` | Tappable KPI/summary card | Component | in: `Title,Value,Caption,Trend,Accent`; event: `OnSelect` |
| `cmpSelection.pa.yaml` | Single-select strip over `Items` | Component | in: `Items,DefaultId`; out: `Selected`; event: `OnChange` |
| `cmpEditableGrid.pa.yaml` | Editable grid, bulk-save | Component | in: `Items`; out: `EditedItems,RowCount`; action: `AddRow`; event: `OnCommit` |
| `cmpSectionHeader.pa.yaml` | Section title + subtitle + action | Component | in: `Title,Subtitle,ActionLabel,ShowAction`; event: `OnAction` |
| `cmpConfirmDialog.pa.yaml` | Modal confirm (scrim + card) | Component | in: `Visible,Title,Message,ConfirmLabel,CancelLabel,Destructive`; events: `OnConfirm,OnCancel` |
| `cmpToast.pa.yaml` | Self-dismissing toast | Component | in: `Message,Tone,Duration`; action: `Show`; event: `OnDismiss` |
| `cmpKpiRing.pa.yaml` | SVG percent ring (licence-free) | Component | in: `Percent,Label,AccentHex,TrackHex` |

## The one rule that shaped the design: **no component inside a gallery/form**

Power Apps forbids placing a canvas component inside a gallery or form. Status/choice
pills and person chips are almost always **cell renderers inside gallery rows**, so they
**can't** be components there. Hence:

- **In a gallery row** → drop a plain **HtmlText** control and call a `cmpUiKit` function:
  ```
  HtmlText = cmpUiKit.StatusPillHtml(ThisItem.Status, "auto")
  HtmlText = cmpUiKit.PersonChipHtml(ThisItem.OwnerName)
  ```
- **On a screen** (detail header, filter bar — not in a gallery) → use the components
  `cmpStatusPill` / `cmpChoicePill`.
- `cmpChoicePill` **must** be a component (not a function): it's clickable and raises an
  event; HtmlText can't take a click. `cmpUiKit.ChoicePillHtml` is its display-only twin.
- The tone→colour logic is intentionally duplicated between `cmpStatusPill` and
  `cmpUiKit.StatusPillHtml` (a component can't call another component). Keep them in step.

> Alternative worth knowing: the `cmpUiKit` functions could instead be **user-defined
> functions** in `App.Formulas` (no component, no transfer pain). Kept as a component here
> because you asked for components and it packages them as one importable unit.

## Control tokens — and why they DO gate a paste

**Corrected 2026-08-03 (user-reported): components ARE code-view-pasteable, and several have
landed.** This file previously claimed the opposite and told you to rebuild each one by hand in
the component editor. That was wrong — and it was wrong in the expensive direction, because it
turned a paste into a manual rebuild.

The consequence for everything below: a component's control **tokens are a paste payload, not
documentation**. They are held to exactly the same standard as the screens — an unverified token
is a failed paste, reported back only as "it didn't work".

- Grounded tokens (from the example export): `Rectangle@2.3.0`, `Label@2.5.1`,
  `Classic/Icon@2.5.0`, `Classic/TextInput@2.3.2`, `Classic/Button@2.2.0`, `Image@2.2.3`.
- **Gallery `Variant`** — resolved to `Vertical` (`cmpEditableGrid`) / `Horizontal`
  (`cmpSelection`) from public evidence, matching the screens. (Version suffixes are optional —
  Studio uses the current version if omitted.)
- **`HtmlViewer@2.1.0`** (`cmpStatusPill`/`cmpChoicePill`) and **`Classic/Timer@2.1.0`**
  (`cmpToast`) are best-effort names for the "HTML text" and "Timer" controls. **Under the
  correction above these are now a real risk**, not free: if either component is rejected, the
  token is the first suspect. Report the error and I'll ground the name. Fallback for the toast
  if the Timer token is wrong: drop it and let the app own timing (visual-only toast +
  `Visible`).

## Transfer — components DO cross by paste

**Corrected 2026-08-03 from a Studio report: these files are paste payloads.** Paste each one
the same way as a screen, via code view. Several have already landed this way.

What that changes:
- **The dialect matters.** These are `ComponentDefinitions` in pa-yaml v3.0, and Studio validates
  them at paste time — which is exactly how the `Parameters`-must-be-a-sequence error was found.
  Run `python tools/validate_pa_yaml.py` before carrying anything across.
- **Paste one at a time** and report the outcome, so a rejection points at one component.
- A **component library** can't hold data sources or Power Automate flows — pass data in via
  Input properties (all eleven already do).
- Since nothing returns to the repo, these files remain the **authoritative source**: if you
  tweak a component in Studio, tell me and I'll mirror it here, or it's lost.

## Where these plug into the shell (Phase 2)

- Home / Reports SVG-fallback: `cmpStatusCard` tiles (Value/Trend computed in-app).
- Project detail **Tickets tab**: `cmpEditableGrid` (specialise the 3 demo columns to the
  real `tmTickets` value columns; do the bulk `Patch` per `power-apps-editable-table`).
- Any task/issue gallery: `cmpUiKit.StatusPillHtml` + `PersonChipHtml` in the row template.
- Filter bars / project pickers: `cmpChoicePill`, `cmpSelection`.
- Every content section: `cmpSectionHeader`. Destructive actions (archive/delete):
  `cmpConfirmDialog`. Save/patch feedback: `cmpToast`. Reports SVG-fallback for unlicensed
  users (Q2): `cmpKpiRing` (Percent computed in-app from a delegable-filtered count).

## Deferred to sibling skills (not in these files)

- Delegation-safe `Patch`/`Collect` for the grid's bulk save, and any real data sourcing →
  `power-fx-development` / `power-apps-editable-table`.
- The Power Fx that computes a ring's `Percent` (delegable-filtered, bounded count) →
  `power-fx-development`. The SVG technique itself is grounded on `power-apps-svg`.

## Notes on the four screen-furniture components

- `cmpConfirmDialog` — place the instance **full-screen**; the app owns `Visible` and closes
  it in `OnConfirm`/`OnCancel`. Scrim tap = cancel. `Destructive` reddens the confirm button.
- `cmpToast` — set `Message`/`Tone`, then call `cmpToast_1.Show()`; internal `_show` var +
  Timer auto-dismiss after `Duration`. (`_show` is read by child controls only — not by an
  Output property — so it stays within component rules.)
- `cmpKpiRing` — colours are **hex text** (`AccentHex`/`TrackHex`) so they drop into the SVG
  without a Color→hex conversion; the ring uses the circumference-100 `stroke-dasharray` trick.
- `cmpSectionHeader` — grounded tokens only; `ShowAction`/`OnAction` make the button optional.
