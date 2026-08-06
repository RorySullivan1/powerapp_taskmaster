# 2026-08-06 20:59 · classic-combobox-and-corruption

**Goal:** Convert every combo box to Classic/ComboBox@2.4.0; found and repaired duplicate-key corruption in scrProjectEdit

## What happened
- A Studio code-view export (photo) showed a control this repo had authored as
  `ModernCombobox` coming back as **`Classic/ComboBox@2.4.0`**, carrying our own
  `Sort(Distinct(Filter(...)))` Items formula intact. The user said "fix it across all
  instances", so **all 10 combo boxes in `src/` are now the classic control**: 7 on
  `scrProjectEdit`, 3 in `cmpNestedSelect`. `ModernCombobox` no longer appears in `src/`.
- The display column moves with the family: `ItemDisplayText: =ThisItem.Value` →
  `DisplayFields: =["Value"]` **and** `SearchFields: =["Value"]`. The modern property on a
  classic control renders **blank rows** — the most likely cause of "the region component
  does not work" / "all I see is select and a blue box".
- Confirmed on MS Learn `controls/control-combo-box` that `IsSearchable`, `SearchFields`,
  `DisplayFields` and `InputTextPlaceholder` are all first-party on the classic control, so
  the converted instances author nothing inferred.
- **Discovered `src/Screens/scrProjectEdit.pa.yaml` was structurally corrupt** — see below.
  Rebuilt it from the last clean commit and re-applied every intended fix by hand.

## Gotchas & dead ends
- **THE BIG ONE — duplicate YAML keys are invisible.** Commit `445f59d` doubled
  `scrProjectEdit` from 2760 → 5984 lines: 132 controls with two copies of their
  `Control`/`Variant`/`Properties`/`Children`, **360 duplicate keys**. PyYAML keeps the
  *last* of a duplicate key silently, so the file loaded, schema-validated, and reported
  `24/24 valid` while half of it was invisible to the parser — and to every edit made
  against it. This is also the real explanation for the abandoned `FillPortions` sweep:
  edits landed in the copy the parser discards, which is why "253 lines inserted, parser
  saw 0". The duplication was **nested, not a flat 2×**, so mechanical dedup was not
  provably correct.
- **Fix:** `duplicate_keys()` added to `tools/validate_pa_yaml.py`, run before schema
  validation. Verified it FAILs the corrupted blob (0/1) and passes the rebuild (24/24).
  Never trust "valid" from a YAML tool that does not reject duplicate keys.
- **Recovery method that worked** (reuse it): find the last clean commit, restore it, then
  recover the intended change set with `comm` over `sort -u` of both files — the sorted
  line-set diff is immune to the duplication and showed all six behaviour fixes in ~20
  lines. Then diff the rebuild back against the corrupt file and confirm every remaining
  difference is intentional.
- The single-slash `/ insert.` that looked like a Power Fx syntax error was a **grep
  context-separator artefact**, not a real defect. Read the file before believing grep.

## State at end
- `scrProjectEdit.pa.yaml`: 2752 lines, **183 controls** (identical to what the parser saw
  in the corrupt file — nothing lost), 0 duplicate keys, 24/24 valid.
- Six fixes from `445f59d` re-applied verbatim: rollup guard `2000`→`500` (2000 could never
  fire under a 500-row limit); completion date no longer blanked when phase leaves Complete;
  coverage conditional record literal removed; coverage clear-arm added; both
  `cmpNestedSelect` instances `Width: =760` → `=Parent.Width - 48`; class note rewritten to
  describe the + / ✓ picker. `ResetSignal` deliberately NOT restored — `d6d8092` retired it.
- Three superseded comment generations stacked in `OnVisible` and at the classification
  Patches were collapsed to one accurate line each.
- Recorded in `tools/studio-enums.json` (props + `props_source`) and the
  `powerapp-canvas-controls` skill (repo-wide classic-combo-box callout, the display-column
  trap, the `Value` column rule, the token table row).

## CORRECTION (same day, after modern controls were activated)
- **The classic conversion was a misdiagnosis and has been reverted.** Modern controls are
  **ENABLED**; the user activated them and said *"all modern controls can remain"*. All 10 combo
  boxes are `ModernCombobox@1.0.0` with `ItemDisplayText: =ThisItem.Value`.
- **The real defect was the VERSION TOKEN.** `@x.y.z` in a pa-yaml token is the TEMPLATE version,
  not the revision number Studio shows in its properties pane. Studio reports the combo box as
  **1.1.1**; `ModernCombobox@1.1.1` rejects the whole paste as an unknown control — which is the
  "error on trying to input the nestedselect" that started the detour. MS Learn's YAML example on
  `modern-controls/modern-control-combobox` emits **`@1.0.0`** on the *updated* control (same page
  documents DelayOutput, typed enums, SelectMultiple defaulting true). Every other modern token in
  this repo is `@1.0.0` — that should have been the tell.
- **Never derive a `@version` from a number a human read off Studio's UI.** Take it from an export
  or a first-party YAML sample.
- The duplicate-key finding and the six re-applied fixes below are UNAFFECTED — that repair stands.

## Open threads
- **Unverified in Studio:** whether the region picker renders now that the token is `@1.0.0` and
  the display column is `ItemDisplayText`. The user reports the last push pasted correctly;
  whether the picker POPULATES is the open question.
- ~~Why classic?~~ **CLOSED — modern controls are on; it was the `@1.1.1` token.** No other
  modern control needs changing.
- Clearing a picker between records is still unsolved (`ResetSignal` removed as ungrounded).
- `schema.yaml`'s `migration:` section still reads `PLANNED — nothing applied`, so
  `scrProjectEdit` binds `project_region_id/_path` and `project_type_id/_path` columns that
  may not exist on `taskmaster_projects` yet.
- Still open from the earlier review: `ClearCollect` of the mapping lists hits the silent
  500-row cap; two staged galleries hardcode `Width: =1316`; the `FillPortions` sweep across
  the auto-layout children was never done.
