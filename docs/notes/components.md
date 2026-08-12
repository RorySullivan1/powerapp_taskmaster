# Reusable components — contracts, constraints, and transfer

**Four of the original ten were deleted 2026-08-11** — see "Removed" below. The table
below is also PARTIAL: `cmpAppBar`, `cmpNestedSelect`, `cmpPicker` and
`cmpLookupField` were built after it was written and were never added
(`cmpPicker` replaced `cmpPeoplePicker` + `cmpRecordPicker` on 2026-08-12). `.claude/CATALOG.md`
is the generated, always-current inventory; this file is the contract notes.

Authored in the **v3.0
`.pa.yaml` `ComponentDefinitions`** schema (grounded on the official schema:
`microsoft/PowerApps-Tooling` `schemas/pa-yaml/v3.0/pa.schema.yaml`). Data-independent —
no `tm*` tokens. Colours **inline** the `App.Formulas` `Theme` palette because a component
is isolated and can't read app globals; keep the hex/RGBA in step with `Theme`.

## The set

| File | What it is | Kind | Key contract |
|---|---|---|---|
| `cmpStatusCard.pa.yaml` | Tappable KPI/summary card | Component | in: `Title,Value,Caption,Trend,Accent`; event: `OnSelect` |
| `cmpSelection.pa.yaml` | Single-select strip over `Items` | Component | in: `Items,DefaultId`; out: `Selected`; event: `OnChange` |
| `cmpSectionHeader.pa.yaml` | Section title + subtitle + action | Component | in: `Title,Subtitle,ActionLabel,ShowAction`; event: `OnAction` |
| `cmpConfirmDialog.pa.yaml` | Modal confirm (scrim + card) | Component | in: `Visible,Title,Message,ConfirmLabel,CancelLabel,Destructive`; events: `OnConfirm,OnCancel` |
| `cmpToast.pa.yaml` | Self-dismissing toast | Component | in: `IsOpen,Message,Tone,Duration`; event: `OnDismiss` |
| `cmpKpiRing.pa.yaml` | SVG percent ring (licence-free) | Component | in: `Percent,Label,AccentHex,TrackHex` |

## Removed 2026-08-11 — four components, 462 lines, zero instances

`cmpUiKit` (129), `cmpEditableGrid` (192), `cmpStatusPill` (75) and `cmpChoicePill` (66)
were **never instantiated by any screen** — confirmed by an exhaustive `ComponentName:`
and function-call scan. An unused component definition still ships inside the `.msapp`
and loads at app start, so they were pure payload and maintenance surface.

`cmpUiKit` in particular could not work as built: its `OutputFunction`s are uncallable
without a screen-level instance, and no screen has one. Its tone-to-colour logic was also
deliberately duplicated into `cmpStatusPill`, so there were three implementations of one
pill and none of them in use.

**What was lost, honestly:** galleries render status as flat muted text
(`scrProjects` row meta, `scrReference` client meta) where a coloured pill would read
better. Adopting the pills was the alternative to deleting them, and it was considered —
it needs an `HtmlText` control per gallery row plus a screen-level `cmpUiKit` instance.
The deletion is recoverable from git if that is ever wanted; the definitions are at
`e16688c^`.

**The size win is only real once they are deleted in STUDIO too** — removing them from the
repo does not shrink the running app.

## The rule that shaped the original design: **no component inside a gallery/form**

Power Apps forbids placing a canvas component inside a gallery or form, which is why the
pill renderers were built as `OutputFunction`s returning HtmlText rather than as
components. That constraint is still true and still worth knowing before anyone builds a
per-row renderer: **in a gallery row it has to be an HtmlText control**, never a component
instance.


## Gallery `Variant` tokens — the real ones

**`Variant: Vertical` is not a thing.** That was a guess this repo carried for weeks. Studio's own
generated code view names them `BrowseLayout_<Orientation>_<Template>_ver5.0`:

| Variant | Status |
|---|---|
| `BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0` | **CONFIRMED** — read off Studio's code view |
| `BrowseLayout_Horizontal_TwoTextOneImageVariant_ver5.0` | corroborated from published `.pa.yaml` |
| `BrowseLayout_Vertical_OneTextVariant_ver5.0` | corroborated |
| `BrowseLayout_Flexible_SocialFeed_ver5.0` | corroborated |

The template part only picks the *default* child layout — the children you paste replace it — so any
vertical variant will do. All 49 galleries in this repo use the confirmed one.

This is very likely what caused `cmpTermPicker` to render black: an unrecognised variant leaves the
gallery with no template to style itself from. The explicit surface fills added for that are kept —
a picker should be a panel regardless — but the variant was probably the actual cause.

## The black component was the Variant, not the Fill

`cmpTermPicker` rendered black and `RGBA(0, 0, 0, 0)` looked like the culprit — black at zero alpha,
and the picker was the first component with genuinely exposed background. That was wrong. The cause
was the invalid gallery `Variant` (see above); with a real variant the picker loads correctly.

The galleries and row buttons are back to transparent. The **component's** own `Fill` stays an
opaque white, but as design rather than repair: four narrow columns leave the caption strip, hint
strip and inter-column gaps visible, and a picker should read as a panel. Every other component
keeps `RGBA(0, 0, 0, 0)`, and transparency is now known to work.

**Worth keeping as a habit:** a rendering oddity was blamed on the nearest suspicious-looking
property when the real fault was a token three lines above it. Prefer confirming the token first.

## Column names are IDENTIFIERS, not strings

Power Apps **3.24042** (April 2024) changed the column-name arguments of
`AddColumns` / `DropColumns` / `RenameColumns` / `ShowColumns`, `GroupBy` / `Ungroup`, `Search` and
`DataSourceInfo` from quoted strings to identifiers:

```powerapps
Ungroup( t, v )                       // correct
Ungroup( t, "v" )                     // "expecting an identifier name"
ShowColumns( Choices(...), Label, Path )
```

Existing apps were migrated automatically. **This repo authors from scratch, so nothing migrates
it for us** — and most examples online predate the change. `tools/validate_pa_yaml.py` checks it,
per argument position, because which arguments are column names differs by function (`AddColumns`'
even arguments are formulas; `Search`'s second is the search text).

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
- **`Timer`** — **CONFIRMED 2026-08-03, and the authored token was WRONG.** `cmpToast` had
  `Classic/Timer@2.1.0`; the control is plain **`Timer`**, no `Classic/` prefix. Written
  without a version suffix — the schema treats it as optional and Studio uses the current
  version, which beats inventing a number nothing can check.

**Every control token in the kit is now confirmed.** `tools/validate_pa_yaml.py` emits no
token warnings at all; if it ever does, something new was authored against a guess.

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
- *(historical)* `bodies/<name>.children.pa.yaml` held the control body alone, generated for the
  two-part paste. Removed 2026-08-05 — a component is one whole file again.

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
- `cmpToast` — set `Message`/`Tone`, then flip ONE flag: `Set(gToastShow, false)` then
  `Set(gToastShow, true)`. That flag is passed to BOTH the instance's `Visible` and the
  component's `IsOpen`, and inside, `IsOpen` drives the children's `Visible` **and** the timer
  (`Start: =IsOpen`, `Reset: =!IsOpen`). The old `Show()` action and internal `_show` variable
  are gone — two sources of truth plus a `Reset()` racing the timer's `Start` is why the toast
  appeared and never dismissed (2026-08-04).
- `cmpKpiRing` — colours are **hex text** (`AccentHex`/`TrackHex`) so they drop into the SVG
  without a Color→hex conversion; the ring uses the circumference-100 `stroke-dasharray` trick.
- `cmpSectionHeader` — grounded tokens only; `ShowAction`/`OnAction` make the button optional.
