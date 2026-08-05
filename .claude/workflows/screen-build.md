# Workflow — build or rebuild a screen

Ordered because each step's output is the next step's input. Skipping the early ones is how
you discover a wrong column name after the paste.

## 1. Ground the data (schema first)
- Every column the screen reads or writes resolves to a `name:` in `schema/schema.yaml`.
- Missing column → change the schema first, and note whether SharePoint needs re-provisioning.
- Check `multi:` on any Person / Managed Metadata column you touch. Wrong arity breaks the
  read *and* the write.

## 2. Ground the controls
- List the control types the screen needs. Check each against
  `powerapp-canvas-controls` / `tools/studio-enums.json`.
- Ungrounded? Unzip an `.msapp` (`References/Templates.json`), ask for a code-view photo, or
  design around it with proven tokens. **Do not guess.**
- Prefer controls that remove hand-parsing (date picker, number input, combobox).

## 3. Plan the layout in bands
- Write the resolved band table into the screen's header comment.
- Decide absolute vs auto-layout container. Container wins whenever content stacks — its
  children cannot have positions frozen on paste.
- Fixed furniture (header, action bar) stays absolute and OPAQUE.

## 4. Author
- Column tokens from the schema, control tokens from the catalogue.
- Overlays and modals declared LAST; gallery rows get a transparent full-template hit button.
- Multi-line and `: `-bearing formulas as block scalars.

## 5. Check geometry
- Pairwise rectangle intersection over every control on the screen and inside every modal.
- Intentional overlaps only, and one-directional.

## 6. Validate
- `python tools/validate_pa_yaml.py` → schema, tokens, icons, `IfError` typing, gallery
  `OnSelect`, cross-file component contracts, positioning-off-another-control.
- New failure class → new lint, same change.

## 7. Audit
- **pre-paste-review** agent for a paste / do-not-paste verdict.

## 8. Hand off
- Update `BUILD-BOOK.md` with anything typed by hand in Studio.
- State the paste order, the inferred tokens and their fallbacks, and what to report back.

## 9. Record
- `paste-log.md` row when the outcome comes back.
- A decision in `.claude/memory/INDEX.md` if it settles something.
