---
name: powerapp-canvas-controls
description: >
  The grounded control catalogue for canvas-app YAML — which `Control:` tokens, `Variant:`
  values, enum members and OUTPUT properties actually exist, and which are guesses. Use this
  skill whenever a control is being chosen, added, or swapped: "which control should I use",
  "what's the token for a dropdown / date picker / container", "is Icon.Table real", "what
  does a combobox return", "convert this to a modern control", "why did the paste fail on
  this control", "add a text input / gallery / tab list". Also use before writing ANY new
  control into `src/authored/` — an ungrounded token fails the whole paste and comes back only
  as "it didn't work". Covers: classic vs modern control families, version suffixes, gallery
  `BrowseLayout_*` variants, the 180-value classic `Icon` enum, `GroupContainer` auto-layout,
  and the output property of every control in use (`.Text`, `.Value`, `.Selected.Value`,
  `.SelectedDate`). Boundaries: the FORMULAS inside a control's properties are
  powerapp-canvas-development and power-fx-development; screen layout and geometry are
  powerapp-canvas-design; getting the YAML into Studio is studio-transfer; reusable component
  contracts are power-apps-components. This skill owns *what a control is called and what it
  gives back*.
---

# Canvas Controls — the grounded catalogue

**The single rule: never author a control token you cannot point at evidence for.**

An unknown `Control:` or `Variant:` fails the *entire* paste. Across a one-way gap that returns
as "it didn't work" with no detail, and you then revise blind. Every token below is either
grounded (read off a real Studio artefact) or explicitly marked as a guess.

`tools/studio-enums.json` is the machine-readable copy; `tools/validate_pa_yaml.py` enforces it.

---

## The generic docs will get you rejected

Microsoft's YAML guidance lists control types as `Label`, `Button`, `TextInput`, `Container`,
`Dropdown`. **Studio's code view does not emit those names.** It emits versioned, sometimes
prefixed tokens:

| Generic doc says | Studio actually writes |
|---|---|
| `Button` | `Classic/Button@2.2.0` or `ModernButton@1.0.0` |
| `TextInput` | `Classic/TextInput@2.3.2` or `ModernTextInput@1.0.0` |
| `Container` | `GroupContainer@1.5.0` + `Variant: AutoLayout` |
| `Dropdown` / `Combobox` | `ModernCombobox@1.0.0` |
| `DatePicker` | `ModernDatePicker@1.0.0` |
| `Timer` | `Timer` — no prefix, no version |

Treat the generic docs as a guide to *structure*, never to *tokens*.

## Grounded tokens

**Classic family** — `Label@2.5.1`, `Rectangle@2.3.0`, `Classic/Icon@2.5.0`,
`Classic/TextInput@2.3.2`, `Classic/Button@2.2.0`, `Gallery@2.15.0`, `Image@2.2.3`,
`HtmlViewer@2.1.0`, `Timer`, `CanvasComponent`.

`Classic/ComboBox@2.4.0`, `Form@2.4.4` (`Variant: Classic`), `TypedDataCard@1.0.7`
(`Variant: ClassicTextualEdit`).

**Modern family** — `ModernTextInput@1.0.0`, `ModernNumberInput@1.0.0`, `ModernCombobox@1.0.0`,
`ModernDatePicker@1.0.0`, `ModernTabList@1.0.0`, `ModernButton@1.0.0`,
`GroupContainer@1.5.0` (`Variant: AutoLayout`).

**`Classic/ComboBox@2.4.0` and `ModernCombobox@1.0.0` are different controls.** Studio generates
the classic one inside data cards; the modern one is what you insert by hand today. The classic
adds `Chevron*` styling properties and takes `DefaultSelectedItems` to seed the selection —
which is how a card wires it up:

```yaml
Items: =Choices([@asset_library].'asset_owner')
DefaultSelectedItems: =Parent.Default
SelectMultiple: =false
DisplayMode: =Parent.DisplayMode
PaddingLeft: =If(Self.DisplayMode = DisplayMode.Edit, 5, 0)
```

Version suffixes are optional — Studio uses the current version if omitted — so a version
mismatch is not a failure mode. **Only the control name and the `Variant` matter.**

## Output properties — get these wrong and every formula breaks

| Control | Read it as | Note |
|---|---|---|
| `ModernTextInput` | `.Text` | **Unchanged from classic** — converting inputs is a property rename only |
| `ModernNumberInput` | `.Value` | a real number; `TriggerOutput` was removed from this control |
| `ModernCombobox` | `.Selected.Value` | with `SelectMultiple: =false`, `Selected` is a record |
| `ModernDatePicker` | `.SelectedDate` | `Blank()` when unset |
| `ModernTabList` | `.Selected.Value` | the tab label |
| `Gallery` | `.AllItems`, `.Selected` | **`.Items` is WRITE-ONLY** — reading it is an error |

## Gallery variants

Not `Vertical` / `Horizontal`. The real shape is `BrowseLayout_<Orientation>_<Template>_ver5.0`:

- `BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0` — confirmed from Studio
- `BrowseLayout_Horizontal_TwoTextOneImageVariant_ver5.0`
- `BrowseLayout_Vertical_OneTextVariant_ver5.0`
- `BrowseLayout_Flexible_SocialFeed_ver5.0`

The template part only picks the default child layout, which pasted children replace — so any
vertical variant works. An unrecognised variant renders the gallery as a black block.

## Icons

The classic `Icon` enum has exactly **180 values**, recovered from `References/Templates.json`
inside a real `.msapp`. `Icon.Back`, `Icon.Documents` and `Icon.Table` **do not exist** —
they are `Icon.BackArrow`, `Icon.Document`, `Icon.DetailList`. The validator checks every
`Icon.*` against the list and suggests the nearest real name.

`ModernButton`'s `Icon` is different: a **string** Fluent name (`Icon: ="Checkmark"`), not the
classic enum.

## Auto-layout container

```yaml
- frmScroll:
    Control: GroupContainer@1.5.0
    Variant: AutoLayout
    Properties:
      LayoutDirection:  =LayoutDirection.Vertical      # or .Horizontal
      LayoutAlignItems: =LayoutAlignItems.Center       # Start/End/Stretch per docs
      LayoutGap:        =8
      LayoutOverflowY:  =LayoutOverflow.Scroll         # or .Hide
      PaddingTop: =8   PaddingBottom: =8   PaddingLeft: =8   PaddingRight: =8
```

Children carry `LayoutMinWidth` / `LayoutMinHeight` and **no X/Y** — see
powerapp-canvas-design for why that is the most important property in the whole dialect.

Still inferred, never seen non-default: `LayoutJustifyContent`, `LayoutWrap`, `FillPortions`,
and the non-AutoLayout variant name.

## The one property still not proven

`DefaultSelectedItems` on **`ModernCombobox@1.0.0`** — the property that seeds a combobox's
current value when editing. It is **confirmed on `Classic/ComboBox@2.4.0`** and listed for the
Fluent combo box family on MS Learn, but never yet seen on the modern control itself. Treat it
as corroborated, not proven: keep it, and if a paste is rejected delete that one line — the
only loss is the pre-selection on an Edit.

## Quoting a column inside a formula

Studio writes `Choices([@asset_library].'asset_owner')` — a **single-quoted identifier**. Quotes
are only *required* when the identifier needs escaping, so this repo's unquoted snake_case form
is equally valid; Studio is just being defensive. Do not confuse this with a double-quoted
string, which since 3.24042 is wrong in `ShowColumns`, `Ungroup`, `AddColumns` and friends.

## Edit form and data cards

```yaml
- Form1:
    Control: Form@2.4.4
    Variant: Classic
    Layout: Vertical                 # a top-level key, not a property
    Properties:
      DataSource: =asset_library
    Children:
      - asset_name_DataCard1:
          Control: TypedDataCard@1.0.7
          Variant: ClassicTextualEdit
          IsLocked: true             # Studio locks generated cards
          Properties:
            DataField: ="Title"                       # a STRING — the internal name
            Default: =ThisItem.asset_name             # value IN, from the form's Item
            Update: =DataCardValue1.Text              # value OUT, read by SubmitForm
            DisplayName: =DataSourceInfo([@asset_library], DataSourceInfo.DisplayName, 'Title')
            MaxLength:   =DataSourceInfo([@asset_library], DataSourceInfo.MaxLength, 'Title')
            Required: =false
          Children:
            - DataCardKey1:                # MetadataKey: FieldName    — the caption
            - DataCardValue1:              # MetadataKey: FieldValue   — the input
            - ErrorMessage1:               # MetadataKey: ErrorMessage — validation text
```

**The card is the contract.** `Default` is the way in, `Update` is the way out, and the
children bind back to the card through `Parent`:

```powerapps
Text:        =Parent.DisplayName
Default:     =Parent.Default
MaxLength:   =Parent.MaxLength
DisplayMode: =Parent.DisplayMode
BorderColor: =If(IsBlank(Parent.Error), Parent.BorderColor, Color.Red)
```

`MetadataKey` (`FieldName` / `FieldValue` / `ErrorMessage`) is what tells Studio which child
plays which role — swap the input control and keep the key. `Layout:`, `MetadataKey:` and
`IsLocked:` are all first-class pa-yaml keys, now confirmed in the wild.

Note `DataSourceInfo`'s column argument is a **single-quoted identifier** (`'Title'`), not a
double-quoted string — consistent with the 3.24042 identifier change.

**When a form is the right tool:** a straightforward CRUD screen over one list, where you want
`SubmitForm`, `Form.Error`, `Form.Unsaved` and per-field validation for free.

**When it is not:** anything needing a *guarded write per column*. This app writes optional
Choice, expanded-user (Person) and expanded-taxonomy (Managed Metadata) columns in separate
`Patch` calls so one bad field can't take the whole record down, and it stages child rows
before the parent exists. A single `SubmitForm` cannot express that. Forms and hand-rolled
`Patch` screens are both legitimate — pick per screen, and say which you picked and why.

## Choosing between classic and modern

Prefer modern for anything a user types into or picks from — it removes hand-parsing:

- a date picker cannot produce an unparseable date, so `DateValue()` and its "⚠ not a date"
  echo label both disappear;
- a number input cannot produce a non-number, so `Value()` and its `IsError` guard disappear.

**Keep classic where the modern control can't do the job.** The transparent full-template
gallery hit target needs `Fill: =RGBA(0,0,0,0)` and `BorderThickness: =0`, which a Fluent
button does not expose — those stay `Classic/Button@2.2.0`.

## How to ground a token you don't have

In order of cost:

1. **Unzip an `.msapp`** — it is a zip. `References/Templates.json` holds enum tables as
   pipe-delimited runs. This is how the 180-value Icon enum was recovered.
   ```bash
   unzip -o app.msapp -d /tmp/app
   grep -oE '[A-Za-z0-9_]+(\|[A-Za-z0-9_]+){20,}' /tmp/app/References/Templates.json
   ```
2. **Ask for a code-view photo or paste.** Insert the control in Studio, open code view,
   send it. Studio prints only NON-DEFAULT properties, so set the property you care about to
   something non-default first or it won't appear.
3. **MS Learn** for output properties and enum members — the docs describe those well even
   when they never name the token.
4. **Ship a grounded fallback** if none of the above lands. Drawing a hamburger from three
   Rectangles beats guessing `Icon.Hamburger`.

Record whatever you learn in `tools/studio-enums.json` and the validator's allow-list, with
its provenance. A token grounded once should never need grounding twice.
