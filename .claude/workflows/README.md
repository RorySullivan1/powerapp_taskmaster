# workflows/

**Multi-step orchestrations.** Where a command is one shot, a workflow runs the whole
sequence — it loops, branches, and hands between agents and commands. Each is a
markdown recipe Claude follows; nothing here executes on its own.

## Format

One markdown file per workflow: `<name>.md` — purpose and inputs, ordered steps naming
the agent or command each invokes (reference `../agents/` and `../commands/` rather than
re-describing them), control flow, and explicit **stop / success conditions**.

Author with the **workflow-authoring** skill and scaffold with `/add-workflow`.

## Built

- `change-end-to-end` — one canvas-app change from intent to landed-in-Studio: author,
  validate, audit with `pre-paste-review`, hand off, record. The spine of the air gap.
- `screen-build` — build or rebuild a whole screen.
- `control-grounding` — settle an unknown control, property, or enum from public
  sources before it is written into `src/`.
- `author-asset` — the default path for any "build me a skill / agent / set of assets"
  request: scope → load conventions once → scaffold via the `add-*` commands → batch
  the wiring → verify structurally.

## The air-gap rule

A workflow that touches app source **stops at the hand-off**. Its terminal step is a
note telling the human what to paste and what to check in Studio — the gap is crossed by
a person, one way, and the only signal that returns is "it works / it doesn't". Never
write a step that claims a change is live.
