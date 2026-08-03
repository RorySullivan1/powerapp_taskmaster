# 2026-08-03 15:26 · windows-tooling-fix

**Goal:** Fix Windows-breaking pre-paste tooling and confirm authored .pa.yaml matches the example export

## What happened
- User asked (from a Windows machine) to review `example/Project Tracker.msapp` and use its
  syntax to correct errors in the buildout. Unzipped the .msapp → `Src/*.pa.yaml` is genuine
  Studio-emitted modern-schema source (App + 6 screens; SQL-backed, no components/App.Formulas).
- **Cross-checked the authored app source against that ground truth — it is CORRECT.** Every
  control token matches the example (`Label@2.5.1`, `Rectangle@2.3.0`, `Classic/Icon@2.5.0`,
  `Classic/Button@2.2.0`, `Classic/TextInput@2.3.2`, `Gallery@2.15.0`, `Image@2.2.3`); structure
  (Screens/Children/Control/Properties, positional z-order, no ZIndex) matches; no retired inline
  `As type:` dialect. The component-instance dialect `Control: CanvasComponent` + `ComponentName:`
  matches the ENFORCED const in the bundled v3.0 schema (the schema's own snippet says
  `Control: Component` — stale; we use the right one). **No authored .pa.yaml needed editing.**
- The real errors were in the tooling — all Windows-specific, which is why the machine was flagged:
  1. `tools/validate_pa_yaml.py` read files as cp1252 (Windows default) → crashed on the first
     em-dash and validated only 14/22 files (everything after `scrProject`, incl. all edit
     screens). Added `encoding="utf-8"` to both reads → now 22/22 valid.
  2. `tools/split_components.py` same encoding bug on 1 read + 2 writes; also rendered every
     function parameter as ``None`` because it did `q.get('Name')` on a single-key map
     `{label:{DataType:Text}}`. Fixed encoding + param parsing → BUILD-SHEET now shows
     `label: Text, tone: Text (optional)`.
  3. No dependency manifest — first run is ModuleNotFoundError (jsonschema, ruamel.yaml). Added
     `tools/requirements.txt`.

## Gotchas & dead ends
- Left alone on purpose (valid, not errors): bare `|` block scalars (functionally identical to
  Studio's `|+`/`|-` for a Power Fx string); curly quotes at scrProjectEdit.pa.yaml:1522 (literal
  content inside straight-quoted strings).
- The example does NOT contain a blank gallery — its only gallery Variant is the long
  `BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0` template string — so it can neither
  confirm nor refute our `Variant: Vertical`. Not relitigated (settled decision + button fallback).

## State at end
- Authored source unchanged and confirmed example-conformant; tooling now runs on Windows.
- Changed files: tools/validate_pa_yaml.py, tools/split_components.py, tools/requirements.txt (new),
  src/authored/components/BUILD-SHEET.md (regenerated). Body files byte-identical. Nothing committed.

## Part 2 — .msapp packing (user asked to "pac" a testable build)
- User overrode the settled "msapp is a dead end" call, asking for a packed .msapp for testing.
  Confirmed scope via question → chose the **smoke-test** option.
- Installed `pac` 2.10.1 as a dotnet global tool (dotnet 10 present; pac was not).
- Empirical findings that refine the dead-end reasoning:
  * `pac canvas pack` (Experimental `.fx.yaml`, source format 0.30) round-trips the example fine.
  * `--layout SourceCode` (modern `.pa.yaml`) REJECTS the example: DocVersion 1.346 < min 1.348.
    → our authored `.pa.yaml` is NOT directly packable; must convert to old `.fx.yaml`.
  * Old `.fx.yaml`: GLOBAL control namespace (unique names across all screens — PA3008 if not),
    explicit `ZIndex:`, `Name As type.variant:`. pac regenerates Controls/*.json + Checksum on pack.
- Built `build/EQD-Taskmaster-smoke.msapp`: scrReference + scrAdmin shells (old .fx.yaml, on the
  example scaffold), our blue theme + title + placeholder, button-nav between them. NO data
  sources / components / App.Formulas. Verified: pack exit 0, round-trips through pac (both
  screens, control tree regenerated Controls/295-296.json), zip integrity OK.
- Delivered to `build/` with a README + reproducible `build/smoke-src/*.fx.yaml`.
- **STILL UNCONFIRMED: whether Studio opens it** — that's the user's binary test (one-way gap).

## Open threads
- Two control tokens still UNVERIFIED (validator NOTEs them): `HtmlViewer@2.1.0`,
  `Classic/Timer@2.1.0` — example has neither to ground them.
- Gallery `Variant: Vertical` remains round-trip-gated; button-nav fallback stands.
- **AWAITING user's Studio test of `build/EQD-Taskmaster-smoke.msapp`.** If it opens: the pack
  channel is viable for data-independent units, and next step could be a components/theme build.
  If not: the error text is the first real diagnostic for the pack route.
