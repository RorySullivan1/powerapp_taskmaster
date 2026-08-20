# 5 · Validation and enforcement

**There is no CI.** No pipeline runs on push, nothing lints downstream, and Studio's paste-time
validation is the only check on the far side of the gap. What follows is the entire safety net.

## Run before any hand-off

```bash
pip install -r tools/requirements.txt
python3 tools/validate_pa_yaml.py
```

Two passes, and the second is the one that matters most:

1. **Schema** — structure, against Microsoft's official pa-yaml v3.0 schema (vendored at
   `tools/pa.schema.v3.0.yaml`).
2. **Tokens** — the values the schema deliberately leaves open. The official schema declares
   `Control:` as anything and `Variant:` as any non-empty string, so **a made-up control name
   validates perfectly and still cannot work.** This pass checks every control token, gallery
   variant and `Icon.*` value against `tools/studio-enums.json` — an allow-list recovered from
   real Studio output, including the complete 180-value classic `Icon` enum.

It also catches three ways an edit corrupts content while the file still parses: a stray `#`
inside a formula, a ` #` inside a plain YAML scalar (YAML eats it and the rest of the line, so
no check on the parsed document could ever see it), and a comment left at column 0.

## The other tools

| Tool | What it catches |
|---|---|
| `tools/audit_globals.py` | A global that is read but never `Set()` anywhere. The YAML is valid, so this is invisible here and only surfaces when a human opens the screen in Studio — a wasted round trip across a one-way gap. |
| `tools/audit_container_padding.py` | An auto-layout child sized `=Parent.Width` inside a padded container, which overflows by exactly the parent's horizontal padding. Nesting compounds it. Has known false positives — read the flagged line before acting. |
| `tools/balance_check.py` | Unbalanced brackets in Power Fx, string literals and comments handled properly. |
| `tools/formula_bar_body.py` | Not a check — emits `App.OnStart` / `App.Formulas` ready for the formula-bar channel. |

## The hooks

Compiled from `.claude/hooks/*.json` into `.claude/settings.json` by `build-hooks.py`. **Edit
the fragments, never `settings.json`** — it is generated.

- **Column guard** (`pre_write_column_guard.py`) — blocks a `Write`/`Edit` under `src/` that
  names a column absent from `schema/schema.yaml`, and suggests the nearest real one. It judges
  only snake_case tokens already in the columns' prefix namespace, strips comments first (screens
  legitimately discuss retired columns), and **fails open on anything it cannot parse**. This is
  what turns "never invent a column name" from prose into enforcement.
- **Overlay reachability** (a NOTE from the validator, not a failure) — flags a control with an
  `OnSelect` declared *before* a full-template overlay in a gallery row: the failure mode that
  renders and hovers perfectly and simply does nothing. It is deliberately a note. It cannot
  prove a reduced width is reduced *enough*, and an auto-layout child carries no `X` at all, so
  it can say "confirm this is reachable" but never "this is broken".
- **Read and output guards** — keep oversized reads and verbose command output out of context.

## What none of this can catch

Delegation. Whether a formula folds to the server or silently caps at the data row limit is a
property of the query, not of the file, and no static check here decides it. That is what the
`pre-paste-review` agent and the `power-fx-review` skill are for — and what Live Monitor in
Studio confirms, on the other side of the gap.
