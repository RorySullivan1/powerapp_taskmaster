# 2 · The air gap

Power Apps Studio runs on a **work machine**. This repo lives on a **personal machine**. Between
them there is no connector, no MCP server, no tenant auth, no CI, no linter and no test run —
**only the clipboard, moved by a human, and it runs ONE WAY: repo → Studio.**

Read `.claude/context/air-gap.md` for the brief, and the `studio-transfer` skill for the
mechanics. This chapter is only the consequences, because they are what governs day-to-day work.

## The four consequences

**1. Nothing comes back.** No pull, no export, no code-view sample. The only return signal is a
human saying *"it worked"* or *"it didn't."* You cannot inspect the app to find out what it
currently contains — `docs/build-history.md` is the only record of that.

**2. Studio edits are invisible drift.** A control dragged in Studio, a formula tweaked in the
formula bar, a screen renamed — none of it reaches the repo, and the next paste of that file
overwrites it. Author here; treat these files as the truth.

**3. Unknowns get resolved, not deferred.** There is no round-trip that could confirm a
guessed control token or dialect quirk. Resolve it from public sources — MS Learn, the
`microsoft/PowerApps-Tooling` schema, a public `.msapp` (the enum tables are inside
`References/Templates.json`) — or ship a grounded fallback and keep the nicer-but-unverified
variant documented as the thing to try if the paste is rejected. `tools/studio-enums.json` is
where already-grounded tokens live; check it before declaring anything ungroundable.

**4. Studio's paste-time validation is the only downstream check.** So each paste has to be
small enough that a rejection points at an obvious cause, and correct enough that it usually
does not. A few large correct pastes beat many small speculative ones — every paste costs a
human's attention on another machine.

## What crosses through which channel

| Unit | Channel |
|---|---|
| A screen or a component | Studio **code view** (View code → paste) |
| `App.OnStart` and `App.Formulas` | The **formula bar** — the App object has no code view |

`python3 tools/formula_bar_body.py onstart --bare` emits a comment-free body for the formula-bar
channel. Use it when the full paste fails: the leading `=` is a pa-yaml marker rather than part
of the formula, and a collapsed formula bar can eat everything after the first `//` comment.

## Before you believe a failure report

**Ask for a browser refresh first.** Studio's editor can keep showing an old component
definition after its body has changed, so the app behaves as though the edit never happened.
That has already cost two rounds of rewriting correct code (2026-08-04, `cmpToast`). Across a
one-way gap a false negative is expensive — it looks like an authoring bug and sends you
revising blind.
