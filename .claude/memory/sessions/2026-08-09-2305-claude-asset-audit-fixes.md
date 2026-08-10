# 2026-08-09 23:05 · claude-asset-audit-fixes

**Goal:** Max-effort code review of .claude PowerApp/PowerFx/MS-Office assets; fix top-10 + lower-severity findings

## What happened
- `/code-review [max]` scoped (by arg) to the `.claude/` knowledge assets, not a code diff. 8 finder
  agents by category → verified against source + MS Learn → fixed. 13 files, +103/−63. No `src/` or
  `schema/` touched, so nothing crosses the air gap.
- **Top-10 fixed:** (1,2) editable-table worked examples used `.ThisItem` on `AllItems` rows and a
  malformed `Patch(Source, ForAll(...))` wrapper — both broke the pattern; (3) `studio-enums.json`
  keyed concrete `@1.0.0` on the 4 controls the controls-skill calls version-UNKNOWN
  (Button/NumberInput/TabList/Slider) → renamed to `_modernX_TOKEN_UNKNOWN`; (4) enums ModernCombobox
  self-contradiction (@1.0.0 vs @1.1.1) fixed to @1.1.1; (5) pre-paste-review "confirm freshness"
  gate contradicted the one-way gap → rewrote to "ground, don't gate on freshness"; (6) pre-paste
  column check pointed at `context/schema.md` (no columns) → repointed to `schema/schema.yaml`;
  (7) sharepoint "12-join wall" → **8** (MS Learn: blocked above 8 joins; 12 is only maximal-view
  return); (8) graph `$filter` needs `Prefer: HonorNonIndexedQueriesWarningMayFailRandomly` header +
  `eq` is case-INsensitive; (9) DAX `TOTALYTD` year-end is the **4th** arg, not 3rd; (10) `=Blank()`
  delegates on simple columns only, NOT Person/Lookup/Choice.
- **Lower-severity fixed:** design §5 container's own Height freezes on paste (only children's X/Y are
  immune); DAX running total `ALL('Date'[Date])` → `ALL('Date')` (single-col form breaks on Month/Year
  axis); ModernNumberInput output row marked reference-only; `pac canvas download` recipe split into two
  real alternatives (`-d` extract OR `-f`+Expand-Archive); power-query-m multi-value Person/Lookup =
  `[Table]` → `Table.ExpandTableColumn`.

## Gotchas & dead ends
- **`float` claim was CORRECT — do not "fix" it.** sharepoint-column-formatting says "`float` no longer
  supported"; a finder called it invented, but MS Learn formatting-syntax-reference explicitly states
  *"Float style prop no longer supported in custom formatter."* Verifying the negative claim before
  editing prevented deleting a correct note. Lesson: absence-of-doc ≠ evidence; fetch the reference.
- `validate_pa_yaml.py` `KNOWN_CONTROLS` (the paste-gating allow-list) never contained the 4 bogus
  `@1.0.0` tokens, and `catalogue_gaps()` only checks allow-listed tokens — so renaming those enums keys
  is safe. The enums file had drifted AHEAD of the enforcement layer.

## State at end
- All 15 edits landed and verified: `studio-enums.json` valid JSON, `catalogue_gaps()` clean, residual
  greps clean. Coherence fixes applied (editable-table intro prose, pre-paste description frontmatter).

## Schema change (same session) — output-approval de-lookuped
- User decision: drop the output-approval lookup; approvals now live in a SEPARATE portal (out of
  scope). `task_output_approval` (Lookup→asset_approval) → **`task_output_approval_id` (Text)**, a
  free-text pointer. User chose to **retire `asset_approval` fully**.
- schema.yaml: column retyped; `asset_approval` block commented out (RETIRED, DEPROVISION in SP);
  C6 updated (region now two ways — approval_region gone).
- scrTaskEdit: removed `gTkApproval` seed, `txtTkApprovalSearch`, `chipTkApproval` (+children),
  and the `galTkApproval` gallery over asset_approval; added one `txtTkApprovalId` ModernTextInput
  (Default from gEditTask.task_output_approval_id, Reset in OnVisible); save writes the trimmed text,
  still gated by `tglTkOutput`, clears on edit-with-section-off. Validator 1/1 valid.
- context/schema.md: list table, relationship diagram, C6, C8 note, index shortlist all updated.
- incoming-lists.md left untouched (provenance/historical record of what came in).
- **Studio hand-off owed:** add a Text column `task_output_approval_id` to the live taskmaster_tasks
  list, and re-land scrTaskEdit (or per-property edit) — a paste to a non-existent column fails.

## Open threads
- **Deprovision `asset_approval` in SharePoint** (list is now orphaned; golden source says remove).
- **Add `task_output_approval_id` (Text) to the live `taskmaster_tasks` list** before pasting scrTaskEdit.
- Possible future hook: a write-time validator cross-checking every version token in `studio-enums.json`
  against the "IN USE / UNKNOWN" lists in the controls skill (would have caught findings #3/#4
  mechanically). Not built.
- Minor un-fixed: `studio-enums.json` KNOWN_CONTROLS comment claims `ModernCombobox@1.0.0` is "kept
  allow-listed as a fallback" but no such key exists in the dict — cosmetic, left as-is.
