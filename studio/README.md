# studio/ — pulled Studio state (the mirror)

Studio is the source of truth; this holds what was pulled out of it.

- `pulled/` — **code-view YAML** copied from Studio (right-click → View code → Copy code),
  unchanged. The baseline the repo mirrors and the **paste dialect** you imitate when authoring.
- `pulled-src/` — *optional* read-only `*.pa.yaml` export (`pac canvas download` / `.msapp \Src`)
  for whole-app reasoning. **Read-only** — never a paste source.
- `snapshots/` — transient, dated raw pulls (working scratch). **Gitignored.**

Update the baseline via `/pull-reconcile` after each pull; record the pull date in
`CLAUDE.local.md`. See the `studio-transfer` skill.
