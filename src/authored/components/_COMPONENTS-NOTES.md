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

## Property KIND matters more than it looks

An **Output** property's formula is evaluated **inside** the component, so it can freely reference
the component's own child controls — `=If(IsBlank(galSel.Selected), …, galSel.Selected)` is fine.

An **Input** property's `Default` is evaluated in the **consumer's** scope, so it cannot see them at
all. Create an output as an input by mistake and you get a name-scope error pointing at the child
control, which reads like "you may not reference your own controls" and is really "this property is
the wrong kind".

That cost a round trip on `cmpSelection.Selected` (2026-08-03). If a property errors on a child
reference, **check its kind before changing the formula.**

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
- **Gallery `Variant`** — now **`Vertical` everywhere**. `cmpSelection` used `Horizontal`, which
  its own comment flagged as unconfirmed; with seven screens instantiating it, that was the single
  highest-leverage paste risk in the repo. It is now a vertical gallery with
  `WrapCount = CountRows(Items)`, which lays every item across one row — a horizontal strip built
  from the only variant that has actually landed. (`scrAdmin`, the one confirmed crossing, used
  `Gallery@2.15.0` vertical.)
- **`HtmlViewer@2.1.0`** — **CONFIRMED 2026-08-03.** `cmpStatusPill`'s body pasted with it; the
  only failure in that unit was the HtmlText *value* (a bad regex), not the control token. So
  `cmpChoicePill` and `cmpUiKit`'s HTML output no longer carry a token risk either.
- **`Classic/Timer@2.1.0`** (`cmpToast`) is still a best-effort name and is now the **last
  unverified token in the kit**. If `cmpToast`'s body is rejected, that is the first suspect —
  report the error. Fallback: drop the Timer and let the app own timing (visual-only toast +
  `Visible`).

## Transfer — a component crosses in TWO parts

This section has now been wrong in both directions, so here is the settled version.

- First it said components can't be pasted at all and must be rebuilt by hand. **Too pessimistic.**
- Then, after a Studio report that several had landed, it said the files are paste payloads.
  **Too optimistic** — that stopped working, which is what forced the distinction below.

A component definition is **two things**, and Studio takes them through two different channels:

| Part | What it is | How it gets in |
|---|---|---|
| **Contract** | custom properties, plus the component-level formulas backing the Output / OutputFunction / Action ones | **Typed** into the property pane. There is no paste gesture for a custom property — nothing in this YAML can shortcut it |
| **Body** | the child controls | **Pasted** via code view, exactly like a screen |

Pasting a whole `ComponentDefinitions:` document asks one channel to carry both. That is the
most likely reason a whole-file paste fails while the controls inside it are perfectly valid.

**So use the split, not the raw file:**
- `BUILD-SHEET.md` — every custom property, its kind, type and formula, in creation order.
- `bodies/<name>.children.pa.yaml` — the control body alone, comment-free, ready to paste.

Both are **generated** from the `.pa.yaml` files here, which stay the source of record:

```
python tools/split_components.py
```

**Add the custom properties before pasting the body.** The controls reference them by name
(`cmpSelection.Items`), and a reference to a property that doesn't exist yet fails the paste.

What that changes:
- **The dialect matters.** These are `ComponentDefinitions` in pa-yaml v3.0, and Studio validates
  them at paste time — which is exactly how the `Parameters`-must-be-a-sequence error was found.
  Run `python tools/validate_pa_yaml.py` before carrying anything across.
- **Paste one at a time** and report the outcome, so a rejection points at one component.
- **`cmpUiKit` has no controls at all** — it is pure OutputFunction properties. There is nothing to
  paste; it is built entirely from the build sheet.
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
