# 2026-09-04 15:26 · issue-51-probes-authored

**Goal:** Author both #51 probes to isolate the two claims holding galProjects.Items at 16 branches

## What happened
- **Reviewed the open backlog and found it smaller than INDEX said.** #45–#49 are CLOSED
  (`968b7a1` landed #48: mine is manager-OR-supporter, empty-state ladder reordered). Only the
  **#50** epic remains, with #51 probe / #52 named formulas / #53 collapse the search axis.
- **Executed #51 — the whole critical path.** #52 and #53 are blocked on its readings by their
  own text, and the standing rule (epic, INDEX, CLAUDE.md) is that this epic starts with a probe.
  Two files, one claim each per rule 3, both validated, both written up in `tests/README.md`
  with a `Result — PENDING` section:
  - `tests/scrProbe-startswith-empty.pa.yaml` → `scrProbeSW` (claim 1)
  - `tests/scrProbe-namedformula-filter.pa.yaml` → `scrProbeNF` (claim 2)
- **`OpenProjects` added to `App.Formulas`** — `ActiveProjects`' vocabulary minus `"Complete"`.
  Required by probe row 8 and by #52.
- Commits `612dfb3` (probes) and `4b1df23` (memory), pushed to
  `claude/powerapp-repo-init-xymvlm`. Validator: 22/22 on `src/`, 2/2 on the probes.
- Commented on #51 recording both departures, since whoever runs it needs to know the issue's
  own table was superseded.

## Gotchas & dead ends
- **#51's sub-case table specifies an instrument that could not have answered the question, in
  two independent ways.** Worth knowing before trusting a table in a future issue:
  1. `CountRows` on every case — the rule-4 violation this directory has now paid for three
     times. `CountRows` is itself non-delegable, so every label carries the same
     *"CountRows Operation not supported"* and says nothing about the `Filter` inside it.
  2. **`CountRows(ActiveProjects)` does not return `N`.** 2000+ projects against a 2000 data row
     limit means it returns THE CEILING — a truncation, not a total — so "case 2 should equal N"
     is unmeasurable as written. **This is the more dangerous of the two**, because the number
     looks like an answer.
- **Fix for (2): measure match-all over a BOUNDED subset.** Count one phase, then the same phase
  AND'd with the `StartsWith`; equal AND below 2000 proves the `StartsWith` removed nothing. Two
  phases are offered because neither's size is knowable from this side of the gap — a pair
  reading 0/0 or 2000/2000 proves nothing.
- **The pairs are the verdict specifically because they read without noticing a warning.** The
  #46 run came back *"delegation warnings were not recorded on this pass"* — so on this gap, a
  conclusion that depends on the human spotting a delegation warning is a conclusion that may
  not arrive. Design instruments that print their own answer.
- **Claim 2's failure mode is an ERROR, not an empty result, and those must not look alike.**
  Every row there is wrapped in `IfError` printing one of three outcomes: a project name,
  `-- no rows (no error) --`, or `!! ERROR: <message>`. A no-match on the literal `"ab"` is
  expected and is NOT the finding.
- **Four rows added that #51 does not have**, each isolating a variable the recorded claims
  confound: **5b** (same Person subfield, non-empty argument — with 5c as its control this
  closes the #17 post-mortem on its own, whatever else the sheet says) and **6ns / 6r / 8ns**
  (the claim names `Sort`, a bare `Filter` and a named formula at once; each row holds two still
  and varies the third — the move that cleared the named formula in #46).
- `tools/validate_pa_yaml.py` takes FILES, not a directory: `validate_pa_yaml.py src/` throws
  `IsADirectoryError`. Run it bare to scan `src/`, or name probe files explicitly.
- The repo reads `ModernTextInput` via **`.Text`**, not `.Value` — the probe matches the
  shipping `txtProjSearch` exactly, because a probe on a different reader tests a different
  construct.

## State at end
- **NOTHING HAS CROSSED THE GAP THIS SESSION.** Everything below is authored and unverified.
- **PASTE QUEUE, in order:** (1) `OpenProjects` into `App.Formulas` via the **formula bar**, not
  code view; (2) the `scrProbeSW` children; (3) the `scrProbeNF` children. Leave the search box
  empty for the first read of `scrProbeSW`.
- This is ON TOP of the paste queue INDEX already carried (`scrHome`'s Division-by-0 fix, the
  raw-list audit, the three health derivations) — none of that is confirmed live either.
- #52 and #53 remain BLOCKED. #50 is unchanged.

## Open threads
- **Run both probes and record the results in `tests/README.md`** — including a null result,
  per rule 5. Both write-ups end in `Result — PENDING`.
- **Then one of two paths, and both are worth doing:**
  - Claims fall → build #52 (branches name a source instead of restating a vocabulary) and #53
    (16 branches → 8), in that order; #53 rebases onto the shortened branches, which is much
    less to edit. Target is ~155 lines → ~30.
  - Claims hold → close #52/#53 won't-fix and replace the comment at
    `scrProjects.pa.yaml:160-165` with the grounded two-rule version: the ban belongs to
    `StartsWith` over **Person/Choice subfields** (MS Learn note 20), and separately the empty
    argument does not behave as a match-all. The comment currently says "do not factor it away"
    and cannot say why.
- **If claim 2 stands, DELETE `OpenProjects` in the same pass** — it is inert (no screen
  references it) but a named formula nothing uses is dead weight, and it is a formula-bar paste
  to remove.
- **Row 5b closes the #17 post-mortem independently of #50's outcome.** Record that reading even
  if the rest of the sheet is ambiguous; the 2026-08-19 ledger entry called that half
  unsettleable and it no longer is.
