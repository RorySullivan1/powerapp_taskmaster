---
description: "[DEPRECATED — the air gap is one-way; nothing is ever pulled from Studio] Formerly reconciled a fresh Studio pull against the repo."
argument-hint: (inoperative — no pull exists)
---

> # ⚠️ DEPRECATED — this command does not apply
> The air gap is **one-way** (repo → Studio). **Nothing is ever pulled from Studio** — there is no
> fresh state to reconcile, no baseline to update, no drift to diff. This command was written
> assuming a two-way channel that does not exist. **Do not run it.**
>
> What replaces it:
> - **The repo is the authoritative source.** There is no "live app state" to sync back. Studio-only
>   edits are invisible drift, lost — mirror any such change back here by hand or it's gone.
> - **Internal column names** (the one still-real concern below, §4) are captured **by hand** into
>   `.claude/context/schema.md` when you provision, since no pull can expose them.
> - See the **`studio-transfer`** skill (one-way principles) and `CLAUDE.md` "The air gap".
>
> The original two-way procedure is preserved below for historical context only.

---

A human has pasted **fresh Studio state** (code-view YAML, or an exported `.msapp`/`pac canvas
download` `\Src`) into this repo. Reconcile it against what the repo believed was true. The
goal is to re-establish `studio/pulled/` as a trustworthy mirror and to surface everything that
drifted while the repo was blind.

Follow the **`studio-transfer`** skill for the lifecycle and dialect rules; do not re-derive them.

## 1. Locate the fresh pull

Find the newly pasted state. Expected home: `studio/pulled/` (code-view YAML) or
`studio/pulled-src/` (a read-only `.pa.yaml` export for whole-app reasoning). If the human
dropped it elsewhere or inline, ask where it is; don't guess. Note the scope from `$ARGUMENTS`
(one screen/control, or the full app) — a partial pull only reconciles what it covers.

## 2. Diff against the prior snapshot

Compare the fresh pull to the previous `studio/pulled/` content (git is the prior snapshot —
`git diff` / `git status` on the pulled paths). Classify every difference:

- **Expected drift** — a change the paste log says *we* landed. Confirm it matches what we
  authored; mark reconciled.
- **Unexpected drift** — a change in Studio the repo didn't author (someone edited the live
  app directly, or a rename/suffix we never logged). Flag it prominently; it is the whole
  reason to reconcile. Reconstruct what happened from the paste log where you can.
- **Missing** — something the repo has that the fresh pull doesn't (a control we thought landed
  but isn't there). Flag as *never landed* or *removed in Studio*.

## 3. Flag stale authored files

For each file in `src/authored/` and `src/patches/`: is it now reflected in the fresh pull?
- **Landed** — present in the pull → it's real; note it and consider archiving it out of
  "authored/pending".
- **Not landed** — absent from the pull → it is **pending**, not live. List every such file so
  no one describes it as in the app.
- **Superseded** — the pull shows a different version at that control → the authored file is
  stale; flag it for rework against the new baseline.

## 4. Cross-check internal column names (manual-provisioning drift)

This project provisions lists **manually in the SharePoint UI**, so internal names can drift
from intent (spaces become `_x0020_`, a recreated column gets a different internal name). If
the pull exposes any field reference, spot-check it against `.claude/context/schema.md`. Any
mismatch is a schema-snapshot bug — flag it to be fixed in the snapshot (the snapshot must
record **true** internal names, not intended ones).

## 5. Update the baseline and the record

- Make the fresh pull the new `studio/pulled/` baseline (for the scope pulled).
- Update the **last-pull date** and scope in `CLAUDE.local.md`.
- Note any reconciled/landed entries in the **paste log**.
- If drift revealed a decision or a gotcha worth keeping, log it via **`session-memory`**.

## 6. Report

Return a tight reconciliation summary:
- **Scope** of this pull (full app or which parts).
- **Drift:** expected (reconciled) vs **unexpected** (needs attention), each with the control.
- **Authored files:** landed / pending / superseded.
- **Schema mismatches:** any internal-name drift to fix in the snapshot.
- **Baseline:** confirmed updated + new last-pull date.

If the pull's scope is partial, say explicitly which parts of the app remain **unverified** —
those stay untrusted until their own pull.
