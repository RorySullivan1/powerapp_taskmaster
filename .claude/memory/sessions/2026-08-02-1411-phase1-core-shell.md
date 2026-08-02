# 2026-08-02 14:11 · phase1-core-shell

**Goal:** Author Phase-1 core shell (theme + Table-driven nav + 5 screen shells + empty states); correct dialect to modern structured schema after pre-paste audit

## What happened
- Added `/example/` to `.gitignore` (local PowerApp dev reference, kept out of the mirror).
- Unpacked `example/Project Tracker.msapp` with **`pac canvas unpack`** (user's ask) →
  confirmed the known PM-tracker blueprint: SQL-backed, absolute X/Y, native pie chart,
  `Navigate()`-button nav. Reused screen inventory + native-nav idea; ignored its plumbing.
- Authored the **first Power Fx in the repo** (Phase 1, data-independent — no `tm*` tokens):
  - `src/patches/App.Formulas.pa.fx` — `gUserEmail`, `Theme` (colour/size/space record),
    `NavMenu` (Table of {Title,Icon,Screen,NeedsLicence} — pattern T6), `gHasPowerBiLicence`.
    Formula-bar-only path; must paste LAST (holds live Screen refs).
  - 5 screen shells `src/authored/scr{Home,Reports,Projects,Reference,Admin}.fx.yaml` —
    header band + left nav gallery bound to `NavMenu` + content/empty-state. `scrReports`
    carries the real Q2 unlicensed empty-state card.
  - `src/authored/_SHELL-NOTES.md` — paste order, dialect table, confirmation gate.
- Ran **pre-paste-review agent** → verdict DO-NOT-PASTE, but on a *dialect* blocker, not
  content (Power Fx / refs / named-formula purity / Icon enums all PASS; zero schema tokens).
- **Acted on the finding:** converted all 5 screens from the retired inline dialect to the
  **modern structured schema**, grounded on real tokens read from the example's native
  `Src/*.pa.yaml`. Validated all 5 parse as YAML with correct structure.

## Gotchas & dead ends
- **`pac canvas unpack` emits the RETIRED inline dialect** (`Name As type:`, ZIndex, layout
  templates like `screen.'phoneLayout...'`). I imitated it at first — wrong target. The
  paste/code-view dialect is the **modern structured schema**: `Screens:` → `ScreenName:` →
  `Properties:`/`Children:` → `- Name:` `Control: Type@version` `Properties:`. The example's
  *native* `.msapp` `Src/*.pa.yaml` (via plain unzip) is in this modern schema — that's the
  dialect evidence, NOT the pac output.
- **No `ZIndex` in the modern schema** — z-order is **positional** (later child = on top).
  Ordered every screen's children background-first.
- **Real control-version tokens** (from the export): `Rectangle@2.3.0`, `Label@2.5.1`,
  `Classic/Icon@2.5.0`, `Classic/TextInput@2.3.2`, `Gallery@2.15.0`, `Classic/Button@2.2.0`.
  Rectangle/Label/Icon/TextInput carry **no `Variant`**.
- **One token still unknown:** the blank-vertical **Gallery `Variant`** (example only has the
  browse-template variant, which brings predefined children — wrong for custom nav rows).
  Left as placeholder `CONFIRM_BlankVertical`; needs the round-trip sample.

## State at end
- Phase-1 shell authored + audited + dialect-corrected. **Not landed** — paste-log still empty;
  nothing is in the live app. Blocked only on the work-machine round-trip (gallery variant +
  first confirmation the channel round-trips at all).
- Nav built as **per-screen gallery bound to `NavMenu`**, NOT a reusable component (deliberate:
  components are hardest to paste; `NavMenu` already gives T6's DRY intent). Component upgrade
  deferred until the channel is proven.

## Components pass (later same session)
- Built **6 reusable components** in `src/authored/components/` (v3.0 `.pa.yaml`
  `ComponentDefinitions`, grounded on `microsoft/PowerApps-Tooling` v3.0 schema):
  `cmpUiKit` (OutputFunction HTML-builders: StatusPillHtml/ChoicePillHtml/PersonChipHtml/Initials),
  `cmpStatusPill`, `cmpChoicePill`, `cmpStatusCard`, `cmpSelection`, `cmpEditableGrid`.
- **Design driver — "no canvas component inside a gallery/form":** display pills/chips/person
  chips → `cmpUiKit` OutputFunctions returning HtmlText (callable from a plain HtmlText control
  in a gallery row). Interactive chip (`cmpChoicePill`) stays a component (HtmlText can't click).
  Components **inline the Theme palette** (isolation — can't read `App.Formulas`).
- **Component schema learned (v3.0):** `ComponentDefinitions:` → `DefinitionType: CanvasComponent`,
  `CustomProperties` (PropertyKind ∈ Input|Output|InputFunction|OutputFunction|Event|Action;
  function/event use `ReturnType` + a `Parameters` MAP; Input can set `RaiseOnReset`),
  `Properties` (incl. component `OnReset`), `Children`.
- **pre-paste audit found 2 real defects in `cmpSelection` — FIXED:**
  (1) gallery `OnSelect` AND button `OnSelect` both raised `OnChange` → double-fire;
  (2) Output `Selected` read a hand-managed component var `_selId`.
  Fix: deleted `_selId`; gallery owns selection natively — `Selected = galSel.Selected`,
  seed via `galSel.Default = LookUp(Items, Id=DefaultId)`, highlight via `ThisItem.IsSelected`,
  raise `OnChange` from the button only. Other 5 components were content-clean.
- **Gotcha:** YAML — a Power Fx record literal with `: ` (e.g. `{ Id: 0 }`) inside an INLINE
  `Default:`/`OnChange:` value breaks the parser (reads as a mapping). Use a block scalar `|`
  (already needed for `Table(...)` defaults). No-space `{Id:0}` also works but block scalar is safer.
- **Component transfer caveat:** code view historically used a now-retired "early preview" dialect;
  component defs likely DON'T round-trip via code-view paste. Reliable path = recreate from the
  contract tables in the Studio component editor / a component library. YAML = spec of record.
- Unconfirmed tokens: `HtmlViewer@2.1.0` (HTML control) + gallery `Variant` placeholders.

## Open threads
- **Round-trip test (now the hard blocker):** on the work machine, create the 5 screens named
  `scr{Home,Reports,Projects,Reference,Admin}`, insert one blank vertical gallery → View code →
  drop into `studio/pulled/`, read its `Variant:`, find/replace `CONFIRM_BlankVertical` in the
  5 files. Then paste screens (one at a time) → `App.Formulas` last → set Data row limit 2000.
- **Licence-gate signal (user decision):** `gHasPowerBiLicence` hardcoded `false`; no in-app
  Power BI API — pick a source (tmLookups flag / Entra group) and hide-vs-grey for Reports nav.
- Tablet-vs-phone target still unspecified (affects responsive layout choice).
- Zero-risk fallback documented: `Classic/Button@2.2.0` nav (loses NavMenu DRY) if gallery balks.
