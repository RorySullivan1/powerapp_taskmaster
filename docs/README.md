# docs/

Two kinds of document live here, and they are written for different moments.

## Manuals — written for someone arriving now

[**`manuals/`**](manuals/) is the documentation section proper: what the app is and how it is
maintained, in their current shape.

- [**User manual**](manuals/user/) — for people on the desk who use EQD Taskmaster
- [**Maintainer manual**](manuals/maintainer/) — for whoever changes this repo and carries the
  change into Studio

Manuals describe; they never define. The golden sources are `schema/schema.yaml`, `src/`,
`.claude/memory/` and `docs/build-history.md` — see [`manuals/README.md`](manuals/README.md).

## Notes and history — written at the moment of building

| File | What it is |
|---|---|
| `build-history.md` | **The paste log.** Every crossing of the air gap, newest first. A record, not a narrative — nothing is "in the app" without a row here. |
| `reports-screen-design.md` | The design of `scrReports`: what it can and cannot do, the fold-once architecture, the SVG rules |
| `screen-map.md` | The original screen-by-screen build blueprint. Historical — parts of it name surfaces the app did not end up with |
| `powerapp-patterns-distillation.md` | Patterns distilled from the PM-tracker template the build started from |
| `managed-metadata-picker.md` | The Managed Metadata problem and the picker that replaced it |
| `msapp-and-git-integration.md` | `.msapp` structure and what the CLI can and cannot do here |
| `claudebrain-inventory.md` | Inventory of the `.claude/` asset set as it stood when written |
| `notes/` | Build notes per area — `components.md`, `edit-screens.md`, `shell-screens.md` |

These are kept because they record *why* something was built the way it was. They are not
maintained as current descriptions of the app; when they disagree with the manuals or with a
golden source, they are the older voice.
