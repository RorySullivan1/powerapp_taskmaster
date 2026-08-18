# 2026-08-18 · Issue #13 — output audience gates the approval id

## What was asked
Implement issue #13 ("REWORK - Output Approval"): add `task_output_audience` to the task
schema and require an approval id whenever the audience is not "Internal Only". The user
asked for a plan comment on the issue first, then approved it ("Plan looks good - execute
on it").

## The ambiguity, and how it was settled
The issue carried TWO different rules in two sentences — *"enforce task-**completion**
logic"* and *"it **must** have an id"*. Those are not the same requirement, and the choice
between them changes both the schema and the screen. Asked the user rather than guessing:

1. **The approval-id requirement bites ONLY at stage `Completed`.** The external approval
   portal issues that id late in the lifecycle; demanding it on every save would block
   ordinary drafting.
2. **The audience IS required whenever the Output section is on.** This removes the blank
   third state the approval rule would otherwise have to reason about.

Both are in the Decisions ledger. Do not relitigate them.

## What was built (`eb65524`)
- **`schema/schema.yaml`** — `task_output_audience`, Choice, `required: false`, five values.
  `join_cost` stays 7 (Choice costs no join). No index — never a filter predicate.
- **`src/Screens/scrTaskEdit.pa.yaml`** — eight edits: `OnVisible` seed + `colTkAudOpts` from
  `Choices()` + `Reset`; `cboTkAudience` into the existing 62px `rowTkOut1` (row height
  unchanged, so no other geometry moved); `tglTkOutput.Default` counts an audience as output
  data; conditional approval caption; two enforcement clauses in `lblTkMissing`; the audience
  written alongside its siblings in the save.
- **Records** — a *Constraints SharePoint cannot hold* section in `.claude/context/schema.md`,
  a pointer bullet in `docs/notes/edit-screens.md`, the Decision entry in this INDEX.

## Why the enforcement is where it is
`required: false` on BOTH columns is deliberate. SharePoint cannot express "required only
when another field is set", so marking either required at the list level would reject every
task that produces no output at all. **`lblTkMissing` is therefore the only enforcement,
and anything writing outside `scrTaskEdit` bypasses it entirely.** `btnTkSave` was left
alone — no `DisplayMode` gate, because a disabled button cannot fire `OnSelect` and cannot
say why it refused.

## Accepted consequence
An EXISTING task holding output data but no audience is blocked from saving at all until an
audience is picked — not merely from completing. Flagged to the user before building; they
approved the plan with that consequence stated.

## Deviation from the posted plan
The blocked-save message is `"an approval ID before completing"`, not the longer wording in
the plan comment. `lblTkMissing` is a 48px label sharing an 88px action bar with two buttons,
and concatenated with the six existing clauses the long string risked clipping — which would
have hidden the very message that explains the block.

## Return signal from the gap (user, this session)
**All 10 components and all 11 screens are landed.** The only open paste is the `scrTaskEdit`
re-paste. State and Threads were corrected: entries still calling `scrReports` "the single
largest unverified thing in the repo" and `scrProjectEdit` "UNPASTED" were closed, and the
#14 thread no longer claims "nothing was written".

## Branch note
`claude/powerapp-repo-init-xymvlm` was 0 ahead / 19 behind `main` — its PR had already
merged — so it was restarted from `origin/main` rather than stacked on merged history.

## Left undone, deliberately
- **`.claude/context/schema.md` says `taskmaster_tasks` join_cost is 8; `schema.yaml` says 7.**
  Pre-existing drift from the `task_category` Managed-Metadata retype. The golden source is
  right; the brief is stale and gets read for delegation decisions.
- **A stale comment in `scrTaskEdit`'s reconcile block** still says products are "Gated on the
  same toggle as every other output field" directly above the comment explaining they are
  emphatically not. Leftover from #14's fix.
