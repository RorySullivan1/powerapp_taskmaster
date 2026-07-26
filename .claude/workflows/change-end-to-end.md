---
description: >
  Orchestrate one canvas-app change from intent to landed-in-Studio across the clipboard air
  gap — freshness check → author → pre-paste audit → choose transfer mechanism → human paste
  hand-off → record. Use when the user wants to make and land an app change end to end, "take
  this change through to Studio", "author and paste this", or asks how a change gets from the
  repo into the live app. Invokes the studio-transfer / power-fx-development skills, the
  pre-paste-review agent, and the pull-reconcile command; stops at the human paste gate.
---

# change-end-to-end

Take one canvas-app change from intent to landed-in-Studio across the clipboard air gap,
safely: confirm freshness, author, audit, choose the transfer mechanism, hand off to a human
for paste, and record what landed. The orchestration is the value — the work lives in the
skills, the agent, and the command it invokes.

**Inputs:** a described change to the app, and a repo whose `studio/pulled/` baseline is (or
can be made) current.
**Output:** an authored, audited change either **landed** in Studio and recorded in the paste
log, or **stopped** before a wasted paste — with the reason and the next step.

## Steps

1. **Confirm freshness.** Check the last-pull date (`CLAUDE.local.md`) and the paste log
   against the change's scope. If the repo may not mirror the live app for the controls being
   touched, **stop and ask the human for a fresh pull** (run `/pull-reconcile` when it
   arrives). Freshness is a precondition, not a nicety. → hand-off: a baseline you trust.

2. **Author the change.** Apply the **`power-fx-development`** skill to write the formulas and
   the **`studio-transfer`** skill for the paste-dialect shape; put control YAML in
   `src/authored/` and any App-object body in `src/patches/`. Bind every column to the
   **`schema`** brief's internal names — never invent one. → hand-off: authored files.

3. **Audit before paste.** Spawn the **`../agents/pre-paste-review.md`** agent on the authored
   files. It returns findings + a **PASTE / DO-NOT-PASTE** verdict (schema + delegation +
   paste-shape + freshness). → hand-off: the verdict.

4. **Choose the transfer mechanism.** Per `studio-transfer`: control(s) → **code view**
   (paste creates a new control, validated); App-object code (`App.OnStart`/`App.Formulas`/
   named formulas) → **formula bar only** (no App code view). Keep each unit small enough that
   a rejection localizes. → hand-off: a paste plan (which unit, which channel, target screen).

5. **Hand off for paste (human gate).** Present the audited YAML and the paste plan to the
   human to paste into Studio. This is the air gap — you cannot paste. Ask them to confirm it
   validated, then **rename** the suffixed control (`_1`) to its intended name. → hand-off:
   the landed name + Studio's suffix + outcome.

6. **Record.** Append the paste to the paste log (date, target screen, intended name, Studio
   suffix, outcome). If the change carried a decision worth keeping, log it via
   **`session-memory`**. → done.

## Control flow / STOP conditions

- **Bail (freshness):** step 1 finds the baseline may be stale for the touched controls →
  **stop**; request a fresh pull and run `/pull-reconcile`. Never author against state you
  can't confirm.
- **Loop (audit):** step 3 returns **DO-NOT-PASTE** → return to step 2 with the agent's fixes;
  re-audit. Repeat until PASTE. Never hand a human a paste that hasn't passed. Terminal state:
  a PASTE verdict (or the human explicitly overrides, recorded).
- **Gate (paste):** step 5 is a human action across the air gap — the workflow **pauses** for
  it and does not proceed until the human confirms the outcome. Never claim a change is live
  before the human confirms it validated.
- **Success:** the change validated in Studio, was renamed, and is recorded in the paste log →
  done; report what landed and under what name.
- **Partial:** authored + audited PASTE but not yet pasted (human unavailable) → stop and
  report it as *authored, not landed*; it is **not** in the app until step 5 completes.

## Invokes
- Skills: `studio-transfer`, `power-fx-development` (+ `power-fx-review` when reviewing an
  existing formula), `sharepoint-list-architecture` (when the change needs a schema decision),
  `session-memory`.
- Agents: `../agents/pre-paste-review.md`.
- Commands: `../commands/pull-reconcile.md`.
- Context: `../context/schema.md` (internal names), `../context/app-structure.md`.
