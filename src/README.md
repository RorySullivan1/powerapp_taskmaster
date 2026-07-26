# src/ — authored source, pending the air gap

Changes written here against the `studio/pulled/` baseline. **Authored ≠ landed** — nothing here
is in the app until a human pastes it and Studio validates it (then log it in `paste-log.md`).

- `authored/` — control YAML in the **code-view paste dialect**, to paste via code view
  (creates a new control, validated). Formula *content* follows `power-fx-development`.
- `patches/` — **App-object** bodies (`App.OnStart`, `App.Formulas`, named formulas). The App
  object has **no code view** — these are pasted into the **formula bar** by hand.

Audit with the `pre-paste-review` agent before any hand-off. Orchestrate with `change-end-to-end`.
