---
name: studio-transfer
description: >
  Expert at moving canvas Power App source between Power Apps Studio (on a work machine)
  and this repo across the manual clipboard air gap — the pulled→authored→landed lifecycle
  and the code-view mechanics that make it work. Use this skill whenever the task involves
  getting Power Fx / control YAML into or out of Studio by hand: "pull the app", "paste this
  into Studio", "copy the control code", "why won't my YAML paste", "the paste created
  Gallery1_1", "how do I get App.OnStart in", "is the repo in sync with the live app",
  "log this paste", "did this land". Trigger on the mechanics of the transfer channel —
  code view (View code / Ctrl+C / Ctrl+V), the App-object formula-bar exception, paste-time
  validation, rename-and-log after paste, clipboard permission for make.powerapps.com,
  .pa.yaml vs code-view YAML, `pac canvas download`, the round-trip test. Implicit signals:
  any uncertainty about whether the repo matches the running app, a rejected paste, a control
  that landed with a suffixed name, or a request to author formulas that will later be pasted.
  Boundaries: the *content* of the formulas — delegation, column-type policy, Person patching —
  is power-fx-development; auditing authored Power Fx before a paste is the pre-paste-review
  agent; the list schema is sharepoint-list-architecture. This skill owns the *transfer
  channel and its discipline*, not what the code says.
---

# Studio Transfer Skill

You move canvas-app source across a **manual clipboard air gap**: Power Apps Studio runs on
a work machine; this repo lives on a personal machine; there is no connector, MCP server,
tenant auth, CI, or linter between them. **The only channel is the clipboard, moved by a
human, one paste at a time.** Your job is to make each crossing deliberate, small enough to
diagnose, and recorded — so the repo stays a faithful mirror of a Studio that you cannot
query. Lead with the mechanics that matter for *this* crossing; never assume the repo
matches the live app.

## Core principles (these are rules)

1. **Studio is the source of truth; the repo is a mirror.** The running app is authoritative.
   The repo reflects what was *pulled* or *landed*, nothing more. A confident answer against
   stale repo state is worse than no answer.
2. **When unsure whether the repo matches the live app, stop and ask for a fresh pull.**
   Do not reason about, edit, or audit formulas you can't confirm are current. Uncertainty
   about freshness is a full stop, not a caveat.
3. **Every round trip costs human effort.** Few large *correct* pastes beat many small
   speculative ones. Get the formula right (and audited — see the pre-paste-review agent)
   *before* asking a human to paste it.
4. **Studio's paste-time validation is the only check that exists.** Keep each paste small
   enough that a rejection points at an obvious cause. A 400-line screen that won't paste
   tells you nothing; one control at a time tells you exactly what broke.
5. **Record every crossing in the paste log.** An unlogged paste is a drift you can't
   reconstruct. The log is how a future session knows what actually landed and under what name.

## The round-trip test — run this before trusting the channel

Do this **first**, once, on this app, before authoring anything for paste. It establishes
empirically what today's Studio actually emits and accepts:

1. Pick one simple existing control in Studio. Right-click it → **View code**, **Copy code**.
2. Paste it into `studio/pulled/` here, unchanged. This is your reference sample.
3. Paste the same YAML back into Studio (any screen) → confirm it lands as a new control and
   validates.
4. Only once that clean round trip works do you trust the channel for authored changes.

If a control survives copy-out-and-paste-back unchanged, the code-view dialect is stable for
this app. If it doesn't, narrow to the smallest control that does and treat that as the unit
of transfer.

## The channel — code view mechanics

Code view (GA **17 Mar 2025**) is the interactive channel. Grounded on Microsoft Learn
*Use code view for canvas app controls*:

- **Turn on the Power Fx formula bar** (app **Settings**) or View code isn't available.
- **Pull:** right-click a control (tree view or canvas) → **View code**; copy via the menu,
  **Ctrl+C**, or the **Copy code** button. Code view shows the selected control **and all its
  child controls** — copying a container brings its subtree.
- **Land:** paste via the menu or **Ctrl+V**. Pasting **creates a new control** after
  validation — it is **never** an in-place patch. Use the exact **YAML Studio generated**;
  it is validated before the control is created, so hand-edited shapes get rejected.
- **Paste assigns a suffixed name** (`Gallery1` → `Gallery1_1`). **Rename immediately** to the
  intended name and **log both** the intended name and the suffix Studio gave, so the next
  pull reconciles.
- **Browser clipboard permission** is required. The first paste prompts; if it fails, allow
  **`https://make.powerapps.com`** for clipboard access in the browser (Edge: add it to the
  allowed sites).

### Two hard limitations — design around them (official *Known limitations*)

- **The App Object has no code view.** `App.OnStart`, `App.Formulas`, and named formulas
  **cannot** be copied or pasted through code view. They go through the **formula bar only** —
  paste the body into the formula bar by hand. Treat App-level code as a separate,
  formula-bar-only transfer path, tracked in `src/patches/`, not `studio/pulled/`.
- **The code-view pane is not editable.** You cannot edit code inside code view — pasting
  creates, it never patches. To change a control, author the new YAML here, paste to create,
  rename, and delete the old one (or patch its properties in the formula bar).

## Two artifacts, one is read-only — don't confuse them

There are two YAML surfaces and they are **not** interchangeable. Grounded on Microsoft Learn
*View source code files for canvas apps* and *Source control for canvas apps*:

| Surface | What it is | Can you paste it into Studio? |
|---|---|---|
| **Code-view YAML** | What **View code / Copy code / Paste code** produce and consume, interactively, per control | **Yes** — this is the interactive create channel. Use Studio's own output verbatim. |
| **`*.pa.yaml` source** | The single **active** source-control schema, in the `\Src` of an exported `.msapp` (or a Git-integration repo). **Read-only** — "not used when an app is loading"; changes to the file are ignored/lost. Editing, merging, conflict resolution supported **only in Power Platform Git Integration**, and only after you **publish**. | **No** — it's a *review* artifact, not a paste source. Don't try to paste `.pa.yaml` through code view. |

Consequences for this repo:
- `studio/pulled/` holds **code-view YAML** — the paste-dialect reference you imitate when
  authoring changes.
- If you also export a `.msapp` and run **`pac canvas download`** (current CLI path;
  `pac canvas unpack`/pack and the `.fx.yaml` experimental format are **retired** — do not
  build on them), the extracted `\Src\*.pa.yaml` is a **complete, read-only** reference for
  *reasoning* about the whole app. Keep it separate from the paste-dialect folder.
- The `.pa.yaml` schema is in active development and may change — treat it as reference, and
  re-pull rather than trusting an old export.

## The pulled → authored → landed lifecycle

1. **Pulled** (`studio/pulled/`) — code-view YAML copied out of Studio, unchanged. The
   baseline the repo mirrors. Stamp it with the pull date (in `CLAUDE.local.md`).
2. **Authored** (`src/authored/`, `src/patches/`) — the change, written here against the
   pulled baseline, using the paste dialect. Not yet in the app. Formula *content* follows
   `power-fx-development`; App-level bodies go to `src/patches/` for the formula bar.
3. **Audited** — run the **pre-paste-review agent** on the authored change. It returns a
   paste / do-not-paste verdict. Do not hand a human a paste that hasn't passed.
4. **Landed** — a human pastes it into Studio; it validates and creates the control; they
   rename it; you **record the paste** (date, target, intended name, Studio's suffix,
   outcome) in the paste log. Only now is it real.
5. **Reconciled** — on the next pull, the `pull-reconcile` command diffs the fresh pull
   against the prior snapshot and flags any authored file that never landed or any drift.

An authored file that has not landed is **not** in the app. Never describe the app as if
authored-but-unlanded work is live.

## Watch Out

1. **Assuming the repo is current.** It reflects the last pull/land, not the live app. If you
   can't point to the pull that proves a formula is current, stop and ask for a fresh pull.
2. **Big speculative pastes.** A large paste that Studio rejects wastes a human round trip and
   hides the cause. Author small, audited units; let validation point at one thing.
3. **Forgetting the App-object exception.** Trying to paste `App.OnStart` through code view
   fails silently to exist — there's no App code view. It's formula-bar-only.
4. **Losing the rename.** Paste names collide-suffix (`_1`). If you don't rename and log
   immediately, the next pull is full of `Control_1` noise you can't map back.
5. **Pasting `.pa.yaml`.** It's read-only review output, not a paste source. Imitate the
   **code-view** dialect for anything you intend to land.

## Out of scope — defer

- **Formula *content*** — delegation, column-type policy, Person/Claims patching, aggregation
  rules → **power-fx-development** (matrix in its `delegation.md`).
- **Auditing an authored change before paste** (non-delegable expressions, schema violations,
  paste/do-not-paste verdict) → the **pre-paste-review** agent.
- **The list schema and internal names** the formulas bind to → **sharepoint-list-architecture**
  and the `schema` context brief.
- **Orchestrating a whole change** (freshness → author → audit → hand off → record) → the
  **change-end-to-end** workflow, which invokes this skill for the transfer steps.
