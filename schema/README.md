# schema/ — the golden source

**`schema.yaml` defines the SharePoint backend.** The repo is authoritative; SharePoint is the
downstream apply-target. Edit the YAML first, then make the lists reflect it — the same one-way
direction as app source (`.claude/context/air-gap.md`).

```
edit schema.yaml  →  apply in SharePoint  →  set  provisioned: applied
```

## Files
- **`schema.yaml`** — the golden source. Every list and column: internal name, type, required,
  indexed, choice values, lookup target, and `review:` flags for open recommendations.
- **`incoming-lists.md`** — provenance only: which screenshot each list was transcribed from.

The model's *shape*, its delegation/join costs and the open consequences live in
**`.claude/context/schema.md`** — that brief points here for columns rather than repeating them,
so the two cannot drift.

## Rules
- **`name:` IS the internal name.** SharePoint freezes it at creation; a later rename changes only
  the display label. Create the column with exactly this name.
- **Never invent a column.** Every field token in authored Power Fx must resolve to a `name:` here.
  (This is what the proposed column-token validator hook would enforce.)
- **`provisioned:`** tracks reality per list — `pending` (defined here, not yet in SharePoint),
  `applied` (lists match this file), `unknown`. It is the schema analogue of `docs/build-history.md`.
- **Type changes after creation are destructive.** Decide the `open_recommendations` *before*
  provisioning, not after.

## Applying a change
1. Edit `schema.yaml` (and note the reasoning in `.claude/memory/` if it's a real decision).
2. Apply it in SharePoint — create/alter the columns exactly as named.
3. Flip `provisioned:` and bump `meta.version`.
4. Anything already authored against the old shape needs re-auditing (`pre-paste-review`).
