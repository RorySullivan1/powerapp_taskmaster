# 7 · When a paste fails

The report you get is binary: *"it didn't work."* This chapter is the order to work through,
cheapest first.

## 0 · Ask for a browser refresh

Studio's editor can keep showing an old component definition after its body has changed, so the
app behaves as if the edit never happened. Confirmed 2026-08-04. Always rule this out first — a
false negative sends you rewriting correct code blind.

## 1 · Ask which channel and which unit

A screen and a component go through **code view**. `App.OnStart` and `App.Formulas` go through
the **formula bar**, because the App object has no code view. A formula-bar paste has its own
two failure modes:

- The leading `=` is a pa-yaml marker, not part of the formula. Pasting it yields `==` and an
  error that reads like a syntax fault in the first statement.
- `//` runs to end of line, and a collapsed formula bar flattens newlines — so the opening
  comment swallows the entire property and **nothing gets set**: no `gTheme`, no `gNavMenu`,
  nothing. `python3 tools/formula_bar_body.py onstart --bare` emits a comment-free body.

## 2 · Re-run the checks

```bash
python3 tools/validate_pa_yaml.py
python3 tools/balance_check.py <file>
python3 tools/audit_globals.py
```

An ungrounded `Control:` or `Variant:` token fails the whole paste, and the official schema will
not catch it — the token pass will.

## 3 · Work through the known causes

| Symptom | Likely cause |
|---|---|
| Whole paste rejected | An ungrounded control token, variant or `Icon.*` value; or a structural shape the schema rejects (a mapping where a sequence is required) |
| Pasted, but a global reference does not resolve | A global read but never `Set()` — `audit_globals.py` |
| Pasted, renders correctly, but nothing is clickable | Z-order. It is positional in this dialect: overlays and pickers are declared **last**, and a full-template hit button must stop short of the row's delete icon or it swallows every tap meant for it |
| A control landed with a suffixed name (`Gallery1_1`) | Studio deduplicated. Apply the rename-and-log rule in the `studio-transfer` skill |
| Geometry collapsed after an edit in Studio | Someone **dragged** a control. Direct manipulation replaces the X/Y/Width/Height formula with a constant. Change geometry in the source, never with the mouse |
| A child overflows its container to the right | `=Parent.Width` inside a padded auto-layout parent — `audit_container_padding.py` |
| Saves fail against a Choice column | Writing `{Value: ""}` to an unset Choice fails. Optional Choice columns go in as `If(cond, value, Blank())` |
| A save reports success but nothing was written | `Errors()` returns a table, so `IsError(Errors(...))` never fires. Capture `FirstError.Message` inside `IfError`'s fallback and gate on it |
| A Person write fails | The claims prefix. `gClaimPrefix` + the lowercased UPN is a community-confirmed shape, not first-party — suspect it first |

## 4 · Shrink the unit

If the cause is still not obvious, split the paste. A 400-line screen that will not paste tells
you nothing; one control group at a time tells you exactly what broke. This is the whole reason
paste units are kept small.

## 5 · Log it either way

A failed crossing is still information about what the app contains. Record what was attempted
and the outcome — `docs/build-history.md` is the only record of the running app's state, and a
gap in it is a gap in what any future session can know.
