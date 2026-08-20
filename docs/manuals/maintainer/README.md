# EQD Taskmaster — maintainer manual

For whoever changes this repo and carries the change into the running app. It assumes you can
read Power Fx and YAML, and that you have access to the app in Power Apps Studio on the work
machine.

## Contents

1. [The repo and where authority sits](01-repo-and-authority.md)
2. [The air gap](02-the-air-gap.md) — the one constraint that shapes everything else
3. [Making a change, end to end](03-making-a-change.md)
4. [Changing the schema](04-schema-changes.md)
5. [Validation and enforcement](05-validation-and-enforcement.md)
6. [Records and conventions](06-records-and-conventions.md)
7. [When a paste fails](07-troubleshooting-a-paste.md)

## The shortest possible orientation

- **This repo is the app's source of truth.** The running app in Studio is downstream of it.
- **Nothing flows back from Studio.** A change reaches the app because a human pasted it, and
  the only feedback is "it worked" or "it didn't."
- **`schema/schema.yaml` defines the SharePoint backend.** SharePoint is provisioned to match
  it, not the other way round.
- **The app is built.** Eleven screens, ten components and the App object are authored here and
  live in the app. The work is editing and refining, not creating.
- **There is no CI, no test run and no linter downstream.** `tools/validate_pa_yaml.py` and the
  `.claude/hooks/` guards are the entire safety net. Run them.

## Where the deep material lives

This manual is the map. The detail is in assets that Claude Code loads on demand and that a
human can read directly:

| Need | Go to |
|---|---|
| The transfer channel and its discipline | `.claude/skills/studio-transfer/` |
| Writing `.pa.yaml` and Power Fx for this dialect | `.claude/skills/powerapp-canvas-development/`, `power-fx-development` |
| Which control token actually exists | `.claude/skills/powerapp-canvas-controls/`, `tools/studio-enums.json` |
| Layout and geometry | `.claude/skills/powerapp-canvas-design/` |
| The model's shape and its delegation costs | `.claude/context/schema.md` |
| Decisions already settled | `.claude/memory/INDEX.md` |
| The full asset inventory | `.claude/CATALOG.md` (regenerate with `/reindex`) |
