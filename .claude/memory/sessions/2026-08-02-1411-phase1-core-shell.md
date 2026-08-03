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

## Merge + extras pass (later same session)
- **Merged to main:** PR #2 (core shell) + PR #3 (component kit), both merge commits, branches
  deleted. Two disjoint-file PRs off main → conflict-free, order-independent. GitHub numbering:
  shell=PR#2, components=PR#3 (repo-init was #1).
- **Built 4 more components** on `feat/component-kit-extras` (10 total): `cmpSectionHeader`,
  `cmpConfirmDialog` (full-screen scrim+card modal, Destructive mode), `cmpToast` (self-dismissing;
  `Show()` action + internal Timer + `_show` var), `cmpKpiRing` (SVG percent ring in Image@2.2.3 —
  the licence-free Reports visual for Q2).
- **cmpKpiRing SVG** (grounded on power-apps-svg): circumference-100 `stroke-dasharray='<pct> <100-pct>'`,
  `r=15.9155`, colour from Power Fx. Colours passed as **hex text** to avoid Color→hex conversion;
  injected unencoded (app-trusted — do NOT bind to list data).
- **cmpToast** respected the prior cmpSelection lesson: `_show` read only by child controls'
  `Visible`/`Start`, never by an Output property.
- **pre-paste audit: PASTE — content-clean, zero defects.** Only gate = documented
  `Classic/Timer@2.1.0` token (cmpToast); the other 3 use grounded tokens only. → PR #4.

## Phase-2 composition pass (static data; user chose the unblocked path)
- Merged PR#4. User said "move on to phase 2"; chose **compose components with static data**
  (Phase-2 DATA binding is blocked — schema.md ⟨capture⟩, no pull). Branch `feat/phase2-compose-components`.
- **Grounded the component-INSTANCE dialect** (v3.0, from the schema): `Control: CanvasComponent`
  + `ComponentName: cmpX` + `Properties:` (base props X/Y/W/H AND custom props). Instances have
  **NO `Children:`**. Built-in controls keep `Control: Type@version` (+ optional `Variant`/`Group`).
- Composed 6/10 components: **scrHome** = cmpSectionHeader + 3×cmpStatusCard + cmpKpiRing +
  cmpToast + cmpConfirmDialog (demo globals gToastMsg/gToastTone/gConfirmOpen; no OnStart —
  blank is falsy). **scrReports** = 3×cmpKpiRing as the Q2 licence-free fallback (Visible=
  Not(gHasPowerBiLicence)). **scrProjects** = cmpSectionHeader + cmpSelection filter strip.
- Remaining 4 (cmpUiKit pills, cmpStatusPill, cmpChoicePill, cmpEditableGrid) are gallery/data-
  bound → compose when the data galleries are wired (post-provisioning).
- **Gotcha (3rd time):** colon-space in an inline value — `"Filter: "` inside `OnChange:` — broke
  YAML parse. Block scalar `|` fixes it. Every live query left as `TODO(Phase-2-data)`.
- **pre-paste audit: DO-NOT-PASTE but ZERO new content defects** — every instance prop resolves
  against its definition, all Fx correct, zero tm* tokens. Only the known gates (components must
  exist first; gallery `Variant`). → PR #5.

## Open threads
- **Round-trip test (now the hard blocker):** on the work machine, create the 5 screens named
  `scr{Home,Reports,Projects,Reference,Admin}`, insert one blank vertical gallery → View code →
  drop into `studio/pulled/`, read its `Variant:`, find/replace `CONFIRM_BlankVertical` in the
  5 files. Then paste screens (one at a time) → `App.Formulas` last → set Data row limit 2000.
- **Licence-gate signal (user decision):** `gHasPowerBiLicence` hardcoded `false`; no in-app
  Power BI API — pick a source (tmLookups flag / Entra group) and hide-vs-grey for Reports nav.
- Tablet-vs-phone target still unspecified (affects responsive layout choice).
- Zero-risk fallback documented: `Classic/Button@2.2.0` nav (loses NavMenu DRY) if gallery balks.
