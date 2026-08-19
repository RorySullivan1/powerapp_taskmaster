# 2026-08-19 15:37 · issue21-approval-flag

**Goal:** Issue #21 — rework scrTaskEdit approvals onto a per-task flag

## What happened
- **#21 supersedes the approval half of #13.** #13 derived "does this need an approval id"
  from the AUDIENCE VALUE (`Internal Only` = no, everything else = yes). #21 replaces that
  with an explicit per-task boolean, `task_output_approval_flag`, which the user has ALREADY
  CREATED IN SHAREPOINT (stated in the issue, default No).
- **New gate:** `Output on` AND `stage = Completed` AND `approval flag on` AND `id blank`
  → blocked. The audience VALUE now gates nothing.
- Changes, all authored, 22/22 valid:
  - `schema/schema.yaml` — `task_output_approval_flag` added (Boolean, default false) directly
    above the id it governs; `task_output_audience` desc rewritten to say it gates nothing.
  - `src/Screens/scrTaskEdit.pa.yaml` — new `colTkApprovalReq` column (caption +
    `tglTkApprovalReq`) inserted BETWEEN the audience and the approval id inside `rowTkOut1`;
    `lblTkApprovalCap`'s "· required to complete" rekeyed from `gTkAudience` to the toggle;
    `lblTkMissing`'s approval clause rekeyed likewise; `Reset(tglTkApprovalReq)` added to
    `OnVisible`; `tglTkOutput.Default` ORs the flag in; the Patch writes the flag.
  - `.claude/context/schema.md` and `docs/notes/edit-screens.md` — both stated the old
    audience rule as fact and are corrected.

## Gotchas & dead ends
- **THE AUDIENCE-REQUIRED RULE WAS KEPT ON PURPOSE.** `lblTkMissing` still demands an audience
  whenever the Output section is on. #21 says "remove the conditionality based on the audience
  TYPE" — that is the Internal-Only-vs-everything-else test, not "audience is optional now".
  Removing it would have been an unasked-for behaviour change. **Flagged to the user; if they
  wanted it gone too, that is a one-line deletion in `lblTkMissing`.**
- **`lblTkMissing` genuinely blocks the save** — checked, don't re-check. `btnTkSave` is
  DELIBERATELY always enabled (a disabled button cannot fire `OnSelect` and cannot say why —
  reported 2026-08-10 as "I clicked Save and nothing happened"); the enforcement is
  `If(Len(lblTkMissing.Text) > 0, Notify(...), <save>)` inside `OnSelect`.
- **No bypass exists.** `scrTaskEdit` is the only writer that can move an EXISTING task to
  Completed. `scrProjectEdit:1296` patches `taskmaster_tasks` but only `Defaults()` — new rows,
  whose flag is false — and `scrReports:131` is a projection, not a write.
- **A hidden control keeps its value**, so `tglTkApprovalReq.Value` is safe to read in the Patch
  while `rowTkOut1` is hidden (`Visible: =tglTkOutput.Value`).
- Boolean idiom copied from the grounded precedent rather than invented: seed with
  `Coalesce(<col>, false)` (`scrProductEdit:263`), write the bare boolean (`scrProductEdit:609`).
- Gating the flag's WRITE on `tglTkOutput` is deliberate and is NOT the mistake the products
  reconcile records. That warning is about the junction, where gating made the toggle a silent
  DELETE of link rows. A scalar boolean is recoverable and its four sibling output columns are
  all gated the same way.
- Layout arithmetic done at author time, not eyeballed: `rowTkOut1` is 1190 wide
  (1366 − 48 bodyRoot padding − 48 secTkOutput − 40), three columns need 200 + 150 + 200 + 40
  of gaps = **590 minimum**, and the fixed 150 leaves 500 each to the two flex columns.
  Heights 18 + 4 + 30 = 52 in a 62 row. No collision at any width this app targets.

## State at end
- Authored, validated 22/22, pushed to `claude/powerapp-repo-init-xymvlm` AND to `main`
  (user asked for main; both were clean fast-forwards, nothing unrelated rode along).
- **LANDED IN STUDIO (user, 2026-08-19)**, together with `scrHome`. Paste queue empty.
- **`task_output_approval_flag`'s internal name is CONFIRMED by the user** — the one risk
  flagged before the paste (a display name with spaces yielding a different internal name)
  is closed. The Patch target is right.

## Open threads
- **NOT YET EXERCISED — the gate has never blocked a save.** It was unexercised under #13 and
  this reworks it, so no version of this rule has ever run in anger. The test is: a task with
  Output on, `Approval required?` on, the id EMPTY, stage moved to Completed, Save — expect
  the save refused and `lblTkMissing` naming "an approval ID before completing".
- **#21 is still OPEN on GitHub.** Landed but unexercised; closing it is the user's call.
- One judgement call still unconfirmed: the audience-required-when-Output-on rule was KEPT.
  If the user meant #21 to drop that too, it is a one-line deletion in `lblTkMissing`.
