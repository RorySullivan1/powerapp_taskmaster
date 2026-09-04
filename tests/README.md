# tests/ — probe screens for settling claims about Studio

Across the air gap the only instrument available is a **paste and a pair of eyes**.
There is no linter, no CI and no round trip, so a claim about how Studio behaves
either gets tested deliberately or it becomes folklore that shapes the whole app.
This directory holds the deliberate tests.

A probe here is **not app source**. It never ships, nothing in `src/` may reference
it, and the validator ignores this directory — it scans `src/` only, which is why
adding probes does not move the `22/22` count. Validate one explicitly:

    python3 tools/validate_pa_yaml.py tests/<file>.pa.yaml

**Rules a probe must follow**, or its result proves nothing:

1. **Self-contained.** No `gTheme`, no data source, no component, every colour a
   literal. If the probe depends on the app being right, a null result cannot be
   distinguished from the app being wrong.
2. **Only tokens this app has already landed.** A probe that fails to paste
   because of an unverified token has tested the token, not the claim.
3. **One claim per probe**, with the sub-cases separated so a partial result is
   still readable.
4. **Carry a positive control** — a step known to produce the effect. Without one,
   "nothing happened" might mean the claim is false *or* that the instrument
   cannot see the effect at all, and those are very different answers.
   **And give every sub-case its OWN instrument.** A positive control that moves
   the same counter as the thing being measured makes the result unreadable no
   matter how carefully the run is done — the two contributions cannot be told
   apart afterwards. `scrProbeRerun`'s sub-case D was lost exactly this way.
5. **Record the result in this file.** A probe with no recorded outcome is worse
   than no probe: the next session re-runs it, or worse, assumes it confirmed
   whatever the repo already believed.

---

## `scrProbe-layout-freeze.pa.yaml` — do layout formulas survive a code-view paste?

**Status: RUN 2026-08-13. THE CLAIM IS FALSE — layout formulas SURVIVE a paste.**

### The claim under test

`.claude/skills/powerapp-canvas-design` §4, *"Layout formulas FREEZE on paste"*, is
the single most load-bearing design rule in this repo. It is why every screen
positions controls with absolute `gTheme.Space.*` arithmetic instead of off their
neighbours, why `scrProjects`' gallery carries a six-line comment about `Y=193`,
and why the validator emits a NOTE on any cross-control geometry reference.

It rests on this MS Learn quote:

> *"After you write formulas for the X, Y, Width and Height properties of a
> control, your formulas will be overwritten with constant values if you
> subsequently **drag the control in the canvas editor**."*

**That quote is about dragging.** The step from there to "a paste positions
controls, therefore a paste freezes them" is an inference that was written down as
fact and never separately grounded. The one piece of field evidence — a gallery
that landed at `Y=193` on top of its own filter row — has at least two other
explanations: the referenced control genuinely was not placed yet at that instant,
or the reference broke because Studio suffixed the target to `txtProjSearch_1`.

### The probes

Screen name is `scrProbe`. Paste onto a blank screen of that name.

| Probe | Colour | Isolates |
|---|---|---|
| P4 | dark blue | `Width` driven by a text box — changeable at **runtime**, no dragging |
| P2 | light blue | `X` off a control declared **earlier** |
| P3 | amber | `X` off a control declared **later** (the case `Y=193` blames) |
| P1 | green | `Width: =Parent.Width - 400` |
| P5 | white box | an auto-layout container whose **own** `Width` is a formula |

P4 is the decisive one. **A frozen constant and a live formula are identical the
instant they land** — the only way to separate them is to change what the formula
depends on without touching the control.

### Protocol

1. **Read before touching.** Click each probe, check the formula bar for `X` /
   `Width`. Formula = survived, number = froze. Do not drag anything yet: dragging
   is the documented overwrite, so touching a control destroys its result.
2. **Type `600`** into the box and pause. If the dark blue bar stretches, formulas
   are live. The light blue bar is chained off it and should slide right too.
3. **Read the readout label.** It recomputes live regardless, so any value that
   disagrees with its `(expect …)` is a control that froze while the label did not.
4. **Optional, and not load-bearing:** *now* nudge the green bar and re-check its
   formula bar, to see direct manipulation replace the formula with a number.
   Step 2 already settles the question on its own — a control that moves when its
   input changes is running a formula — so treat this as a demonstration rather
   than the control the conclusion rests on.

### Result — 2026-08-13, run by the user in Studio

**All four steps ran. Every layout formula survived the paste, as a formula.**

- Steps 1–3: the probes came through with their formulas intact. Typing into the
  box moved the dark blue bar, and the light blue bar chained off it moved with it,
  so the formulas were **live after the paste** — not constants that happened to
  equal the right number. Backward reference, forward reference, `Parent`
  arithmetic and the container's own `Width` all held.
- **Step 2 is the whole finding, and it is positive evidence rather than absence of
  it.** A constant cannot change when its input changes. Something that recomputes
  is a formula. The planned positive control was designed for a weaker version of
  this test — one that could only read numbers off the screen — and the conclusion
  does not depend on it.
- **Step 4 is NOT claimed.** The user's report was that *manually setting a property
  yields a literal*, which is a different and broader statement than "dragging
  freezes": direct manipulation of any kind — drag, resize handle, the position/size
  boxes in the properties pane — writes back a number, because a number is what the
  gesture produces. The formula bar is the one place that keeps what you type. That
  covers what was observed; a clean drag-specific trial was not run and is not needed.

**The rule was wrong, and it was wrong in a specific, repeatable way: an inference
was written down in the voice of its citation.** (And in writing up this very
result I did it again — asserting step 4 confirmed the drag behaviour when the
user had reported something adjacent. Corrected the same day, by the user.) The MS Learn quote said *dragging*;
the skill said *pasting* and kept the quote directly beneath it, so every later
reader — including several sessions of me — checked the citation, saw a real
Microsoft sentence, and moved on. A false claim with a true quote attached to it is
far more durable than one with no evidence at all.

**What actually caused the `Y=193` gallery, since something did.** The original
2026-08-04 report (`docs/build-history.md`, now annotated as superseded) was
first-hand and specific: *"in github i see the dynamic calculation… but on paste the
gallery's Y value becomes hardcoded."* That observation was real. It was also
uncontrolled, and this probe did not reproduce it.

The reconciliation that fits both results: **a reference that fails to RESOLVE gets
replaced by a constant, while one that resolves stays a formula.** If a pasted
control lands as `txtProjSearch_1`, every reference to `txtProjSearch` in that paste
points at the old control or at nothing. That is a different mechanism from
freezing, and it is already avoided by deleting a screen before pasting it back —
which is this project's practice and why nothing has landed at `Y=193` since.

**Open sub-question, NOT tested here:** P3 referenced a control that *does* exist
later in the same paste. The unresolvable case — a reference to a name that is not
in the paste at all — was never probed. If that turns out to write a constant, the
2026-08-04 report is fully explained and the rule becomes "references are fine as
long as the name survives the paste". Worth a second probe before anyone relies on
cross-screen or cross-component references.

### What changed as a result

Corrected 2026-08-13: `.claude/skills/powerapp-canvas-design` §4 and §5, the
`studio-transfer` note on auto-layout being "the one layout that survives", the
validator's cross-control NOTE (`tools/validate_pa_yaml.py`), the memory Decisions
entry, and the defensive comments in `src/Screens/scrProjects.pa.yaml`.

**The authored geometry in `src/` was NOT rewritten.** Absolute `gTheme.Space.*`
arithmetic is still correct and still readable; it is simply no longer *compulsory*.
Converting 11 screens to relative positioning is a real change with real regression
risk across a one-way gap, and it buys responsiveness this fixed-canvas tablet app
does not currently need. It is now available, not required.

---

## `scrProbe-junction-write.pa.yaml` — why is the junction write rejected?

**Status: NOT YET RUN.** Written 2026-08-18 for issue #14.

### The claim under test

`scrTaskEdit` saves the task row and then writes task↔product links to
`taskmaster_taskproduct`. The task saves; the links never appear. The write
**compiles** — and a property in compile error runs nothing at all, so the task
would not have saved either — which makes this a **runtime** rejection, the one
class this repo has no instrument for. The reconcile carried no `IfError`, so
SharePoint's message was discarded at the point it was produced.

The probe performs that one `Collect` alone and shows the message verbatim.

### Why this one names a data source

Rule 1 says a probe names none, so that a null result cannot be confused with the
app being wrong. Here **the data source is the claim** — there is nothing else to
test. Every other rule is kept: no `gTheme`, no component, literal colours, one
claim, a positive control, and this entry.

### Reading the result

Three buttons, in order. They answer different questions and the order matters:

| Press | Result | Means |
|---|---|---|
| **1 CONTROL** | fails | the instrument, connection or permissions are broken — nothing below means anything |
| **2 JUNCTION** | names an error | that message is the answer; fix SharePoint, not the app |
| **2 JUNCTION** | "no error" | the write did not throw — which is **not** the same as landing |
| **3 COUNT** | 0 after a clean 2 | the write is being **silently dropped**, the worst case and the one no `IfError` can catch |

`taskmaster_taskproduct` and `taskmaster_tasks` must both be in the Data pane
before pasting. A screen paste never adds a data source, and an unknown name makes
`OnSelect` a compile error that runs nothing — which would imitate the very silence
under investigation.

Delete the PROBE task row and any PROBE link afterwards.

---

## `scrProbe-date-null-delegation.pa.yaml` — does `dateColumn = Blank()` delegate?

**Status: NOT YET RUN.** Written 2026-08-19 for issue #35.

### The claim under test

`scrReports` fetches **every** live completed task and bounds the report window locally.
The stated reason is sound: `task_date_completion` is optional and `>= gRptFrom` is false
for a blank date, so a bare server-side bound would silently drop every dateless completed
task out of Done and the medians.

But that rules out a bare `>=`, not a bound that **keeps** the blanks:

```
   task_stage.Value = "Completed"
&& ( task_date_completion >= gPbCutoff || task_date_completion = Blank() )
```

`= Blank()` delegates for several SharePoint column types where `IsBlank()` never does.
Whether a **DateTime** column's null test folds is the open question, and it decides #35
outright — bound the heaviest of the five report fetches, or close won't-fix.

### Why there are two instruments, and which one is the verdict

**Delegation is invisible below the data row limit.** On a small list a non-delegating query
returns exactly the right rows, so counts cannot settle this on their own — this is the trap
to avoid, not a detail. The reading that counts is **Studio's own delegation warning**, one
per label, which is static and needs no data at all. The row-limit-1 count is corroboration.

### The sub-cases

| Label | Filter | Decides |
|---|---|---|
| **A** | `task_stage.Value = "Completed"` on the data source | **Positive control.** Must be clean |
| **B** | `Len(task_name) > 3` | **Negative control.** Must warn |
| **C** | `task_date_completion = Blank()` alone | Whether the null test is the problem by itself |
| **D** | the full predicate over `taskmaster_tasks` | Whether the Or-arm costs delegation |
| **E** | the full predicate over `LiveTasks` | **The shipping shape** — scrReports filters the named formula, not the source |
| **F** | today's unbounded count vs the windowed count | Whether #35 is worth anything even if it delegates |

A and B are the pair that makes the run readable: **if A warns or B does not, Studio is not
flagging what it claims to and nothing else on the screen means anything.** Each sub-case is
its own label, so no two share an instrument.

**D vs E is not redundant.** This repo has already been burned by a named formula behaving
differently from the data source underneath it — `ShowColumns` over one reads text columns
back as an ERROR type — so "delegates over the source" would not license the shipping shape.

### Protocol

1. Paste onto a blank screen named `scrProbeDateNull`. `taskmaster_tasks` must be in the
   Data pane; `LiveTasks` is an App named formula and already exists.
2. **Read the warnings.** Click each of A–F and check the formula bar and the App checker.
   Check A and B first and stop if either is wrong.
3. Optional corroboration: set Data row limit to 1, press SET CUTOFF, read the counts. A
   delegable filter still finds a matching row; a non-delegable one downloads one row and
   tests it locally, so it usually shows 0.
4. **Put the data row limit back to 2000** — and `gDataRowLimit` in `App.OnStart` must match
   whatever it ends on, or every truncation sentinel in the app goes dead.

### How to read it

- **C, D and E all clean** → bound the fetch on `gRptFrom` in `btnRptLoad`, keeping the
  dateless rows. `colRptDone` and `gRptDoneNoDate` keep working unchanged.
- **C clean but D or E warns** → the Or-arm is the cost, not the null test. Record it; the
  fix would have to be shaped differently, and #35 as written does not apply.
- **C warns** → `= Blank()` does not fold on DateTime. Close #35 won't-fix with this as the
  evidence; the current unbounded shape is already optimal and `gRptTrunc` remains the guard.
- **F shows the two counts close together** → #35 buys little either way, which is worth
  knowing before authoring anything.

### Result — 2026-08-19, run by the user in Studio

```
A  Delegation warning. CountRows Operation not supported
B  Delegation warning. Len & task_name large data set warning
C  Delegation warning. CountRows not supported
D  Delegation warning. CountRows not supported
E  Delegation warning. CountRows not supported
F  Delegation warning. CountRows not supported & task_date_completion - large dataset
```

**`task_date_completion = Blank()` DELEGATES. `IsBlank(task_date_completion)` DOES NOT.**
That is the asymmetry #35 was written on, confirmed on a DateTime column.

#### The probe has a design flaw, and it nearly cost the run

**Every sub-case is wrapped in `CountRows`, which is itself non-delegable**, so all six labels
carry an identical `CountRows Operation not supported` warning that says nothing about the
`Filter` inside it. That is rule 4 again — *an instrument must not produce the same signal as
the thing being measured* — and it is the second time this directory has been bitten by it
after `scrProbeRerun`'s sub-case D. **A gallery `Items`, or `First(Filter(...)).task_name`,
would have carried no aggregate and read cleanly.** Fix it that way before reusing this file.

#### Why the run is still readable

Subtract the constant `CountRows` warning and read what is left per label:

| Label | Predicate warning after subtracting CountRows | Reads as |
|---|---|---|
| **A** | none | `=` on an indexed Choice is clean — positive control passed |
| **B** | `Len & task_name` | non-delegable predicate flagged — negative control passed |
| **C** | none | `task_date_completion = Blank()` alone delegates |
| **D** | none | the full predicate delegates over the data source |
| **E** | none | and over `LiveTasks` — the shape #35 would ship |
| **F** | `task_date_completion - large dataset` | flagged, because **F is the only sub-case using `IsBlank()`** |

**F is what makes C, D and E evidence of absence rather than absence of evidence.** It shows
Studio will report a `task_date_completion` predicate warning *alongside* the CountRows warning
on the same label — so the checker is not stopping at the first problem, and it is actively
examining this column. C/D/E staying silent is therefore a reading, not a gap.

F earned that by accident: it was written to measure scale, and it happens to use `IsBlank()`
where C/D/E use `= Blank()`. **The probe was saved by a control it did not know it had.** Do
not take that as vindication of the design — take it as the reason to fix the `CountRows`
wrapper before the next probe leans on this file.

#### Residual risk, and why it is not zero

Studio's delegation checker is the documented instrument, not a guarantee. If the predicate
turns out NOT to fold, the failure is not merely a lost optimisation: the whole `Filter` goes
local, so the fetch degrades from *completed tasks* to *the first 2,000 live tasks, then
filtered* — and **`gRptTrunc` would not catch it**, because it tests `CountRows(colRptDoneAll)`
*after* that local filter, which can sit well under the limit. Corroborate with the
data-row-limit-1 count before shipping the bound.

#### Corroboration — run 2026-08-19, data row limit = 1

**The count went 0 → 1 when SET CUTOFF was pressed.** With the limit at 1, a non-delegating
filter downloads one row and tests it locally, which for this predicate lands on 0 unless that
single row happens to match; a delegating one asks the server for a match and gets 1. The two
instruments agree, so the bound was shipped.

**What this does NOT rule out:** one row matching by chance. It is corroboration of the
warning reading, not an independent proof — the warnings, and F in particular, remain the
evidence this rests on.

#### What changed as a result

`scrReports.btnRptLoad` now bounds `colRptDoneAll` on `gRptFrom` with the null arm beside it.
**The comment there tells the next reader not to "tidy" `= Blank()` into `IsBlank()`** — it
reads as the same test, un-delegates the whole fetch, and fails silently.

---

## `scrProbe-mine-predicate.pa.yaml` — does `project_manager.Email = gUserEmail` match anything?

**Status: NOT YET RUN.** Written 2026-09-04 for issue #46, sub-issue of #45.

### The claim under test

Turning on **Only show my projects** empties the gallery. It is not a rendering fault —
`ProjectsEmptyLabel` fires its own sentence — so the `Items` predicate is returning zero
rows. Three candidates produce that identical symptom and cannot be separated from this
side of the gap:

- **A** — the predicate works, but "mine" means *managed by me* and nothing else
- **B** — a case mismatch between the lowercased `gUserEmail` and the raw stored `.Email`
- **C** — `gUserEmail` is blank when `Items` first evaluates

### Why this departs from the sub-case table in #46

**#46 specifies `CountRows(Filter(...))` for five of its six sub-cases. That is rule 4
violated in exactly the way this directory has already paid for twice.** `CountRows` is
itself non-delegable, so every such label carries an identical *"CountRows Operation not
supported"* that says nothing whatever about the `Filter` inside it. `scrProbeRerun` lost
sub-case D to a shared instrument; `scrProbe-date-null-delegation` was readable only
because one sub-case happened to carry a second warning **by accident**, and its write-up
ends by telling the next author to fix it:

> *"A gallery `Items`, or `First(Filter(...)).task_name`, would have carried no aggregate
> and read cleanly. Fix it that way before reusing this file."*

So the instruments are split into two blocks that never share a label:

| Block | Instrument | Read it for |
|---|---|---|
| **DELEGATION** | `First(Filter(…)).project_name` — no aggregate anywhere | **The verdict.** A warning on one of these rows is about the `Filter` |
| **MAGNITUDE** | the `CountRows` figures #46 asked for, quarantined | Numbers only. Every row warns about `CountRows`; that warning is noise |

`First(…)` answers "greater than zero" without an aggregate: a project name means the
predicate matched, `-- no match --` means it did not.

### The sub-cases

| Row | Expression | Decides |
|---|---|---|
| **PC** | `phase = "Active"` | **Positive control.** `=` on an indexed Choice — must be CLEAN |
| **NC** | `Lower(manager) = Lower(me)` | **Negative control** — `Lower()` on a column must WARN. Also #46's case 6, the local ground truth |
| **3** | `manager.Email = gUserEmail` | The shipping predicate, exactly as `galProjects.Items` writes it |
| **4** | `manager.Email = User().Email` | **B** — does un-lowercased match where lowercased did not |
| **5** | `supporter.Email = User().Email` | **A** — and the delegation reading #48 needs before putting this column in an `Or` |
| **7** | raw list, `manager.Email = User().Email` | **E**, isolated — is the nested `Filter` over `ActiveProjects` the problem, or the predicate? |

**NC is what makes silence on rows 3/4/5 a reading rather than a gap.** It proves Studio is
actively examining a `project_manager` predicate and will report one; the date-null probe
only got that property by luck.

**Row 7 is not redundant with row 4.** This repo has already been burned by a named formula
behaving differently from the source beneath it — `ShowColumns` over one reads text columns
back as an ERROR type — and #45 candidate E blames the nested-`Filter` shape rather than the
person column. 4 clean and 7 clean clears the shape; 7 clean and 4 warning convicts it.

### Protocol

1. Create a blank screen named exactly `scrProbeMine` and set its `Fill` in the formula bar.
   `taskmaster_projects` must be in the Data pane; `ActiveProjects` is an App named formula
   and already exists.
2. Paste the `Children:` block. Nothing needs pressing — every row is a property formula.
3. **Read the DELEGATION block first, and check PC and NC before anything else.** If PC warns
   or NC does not, Studio is not flagging what it claims and no other row means anything.
4. Then read MAGNITUDE for numbers. **M6 larger than M3 is the finding to watch for** — it
   means rows exist that the shipping predicate misses.
5. Optional, and the same corroboration the date-null probe used: set the data row limit to 1
   and re-read. **Put it back to 2000 afterwards**, or every truncation sentinel in the app
   goes dead.

### How to read it

- **3 finds a project** → the predicate is fine; the cause is **A**, go to #48.
- **3 no-match, 4 finds one** → **B**, casing. Go to #49.
- **3 and 4 no-match, NC finds one** → the fold is dropping rows. **D** or **E**, go to #47.
- **5 finds one where 3 did not** → **A**, and the tester is exactly the affected profile.
- **`gUserEmail` empty** → **C**, and nothing else on the sheet can be trusted.

Also record, per row: whether Studio shows a delegation warning, and if Live Monitor is
available, the row count the server actually returned. #45 candidate D turns on that reading.

### Result

**Not yet run.**

---

## `scrProbeRerun.pa.yaml` + `scrProbeRerunB.pa.yaml` — how does a screen re-run a behaviour block in place?

**Status: RUN 2026-08-18 by the user in Studio. BOTH ANSWERS ARE POSITIVE — `Select()` fires
on a hidden control (A/B/C), and `Navigate()` to the current screen DOES re-run `OnVisible` (D).**

### Why this has to be settled before the code is written

Deleting a task, transaction or issue from `scrProject` invalidates every derived
value that screen computes in `OnVisible`: `project_phase`, the weighted completion
rollup, and the open-issue / open-task counts. **`OnVisible` does not re-run after an
in-screen delete**, so the screen would keep showing — and keep writing back — numbers
that no longer match the data.

Copying that ~45-line derivation into each of the three delete handlers is the one
outcome to avoid: it would create four writers of `project_phase` and
`project_perc_completion` that can disagree. The block needs **one home and several
callers**, and there is no grounded way to do that yet.

### The claim under test

**A screen can re-run its own setup block in place.** Four mechanisms, separated so a
partial result is still readable.

MS Learn describes `Navigate` as setting *"the **OnVisible** property of the **new**
screen"*, and says `Back` and `Navigate` *"change only which screen is displayed"*. It
never addresses the case where the new screen **is** the current screen — so
self-navigation is **undefined, not supported**, and shipping it would be a guess.
`Select()` is documented and this app already depends on it (`Select(Parent)` inside
`cmpSelection`), but whether it fires on a control the user cannot see is folklore in
both directions.

| Sub-case | Mechanism | Decides |
|---|---|---|
| A | `Select()` on a normal visible button | Whether the worker-control pattern works at all |
| B | `Select()` on a 1×1 transparent button (`Visible: =true`) | The shape a real worker on `scrProject` would take |
| C | `Select()` on a `Visible: =false` button | Whether the worker can be hidden outright |
| D | `Navigate()` to the screen you are already on | The one-line repair proposed on issue #15 |

### Setting it up

**One file per screen, because you paste one screen at a time.**

1. **Create BOTH blank screens first**, named exactly `scrProbeRerun` and `scrProbeRerunB`.
   They navigate to each other by name, so the dependency is **circular** — no paste order
   fixes it. A missing partner screen makes `Navigate()` a compile error and the button
   silently does nothing, which reads exactly like a negative result.
2. **Set the screen properties in the formula bar.** Screens are not controls, so these
   cannot be pasted. Each file lists its own in the header. **Missing the `OnVisible` on
   `scrProbeRerun` leaves every counter at 0 and makes the whole probe look like a failure.**
3. **Paste the `Children:` block** of each file onto its screen. Order no longer matters.
4. **Check the tree for `_1` suffixes** on `btnRrWorkVis`, `btnRrWorkTiny` and
   `btnRrWorkHidden`. Buttons A/B/C call those **by name**, so a suffix leaves the call
   dangling and they do nothing for a reason that has nothing to do with the claim. Rename
   any that suffixed before running. These names exist nowhere else in the app, so a
   collision is not expected — check anyway.

### Protocol

1. **Run the POSITIVE CONTROL first** — the green round-trip button, then "back to the
   probe". `OnVisible fired` must increase by 1. If it does not, the probe cannot see
   `OnVisible` at all and **no other result on the screen means anything**. Stop there.
2. Reset the counters.
3. Press A, B and C once each. Note which worker counters move.
4. Press D once. If `OnVisible fired` rises, self-navigation re-runs `OnVisible`.

### How to read it

- **D works** → issue #15 uses the one-line `Navigate( scrProject )` repair.
- **D does nothing, B or C works** → the derivation moves into a worker control's
  `OnSelect`, called by both `OnVisible` and each delete handler. One copy, several
  callers, no duplication.
- **D does nothing and only A works** → the worker has to be a real visible control;
  it gets parked in the action row rather than hidden.
- **Nothing but A works** and a visible worker is unacceptable → fall back to inlining
  a trimmed recompute, and accept the duplication with a comment saying why.

This probe carries no data source, so it can be pasted onto a blank screen at any time.

### Result — 2026-08-18, run by the user in Studio

**Positive control passed.** The round trip raised `OnVisible fired` by 1, so the instrument
could see `OnVisible` and the rest of the run is readable.

```
OnVisible fired:  9
A · visible worker:      5
B · 1x1 transparent:     5
C · hidden worker:       5
```

**A, B and C are equal.** `Select()` fired every time on all three, including the worker with
`Visible: =false`. So the folklore that `Select()` silently no-ops on an invisible control is
**false here** — a worker control holding a reusable behaviour block does not have to be
smuggled onto the screen as a 1×1 transparent button. It can simply be hidden.

That is what issue #15 needed, and it is reusable well beyond it: **a screen can now keep one
copy of a behaviour block in a hidden control's `OnSelect` and call it from anywhere.**

### Sub-case D — settled on a second pass, after a probe-design flaw

**First run: unreadable.** D shared the `OnVisible` counter with the positive control, and the
probe never recorded how many round trips were taken, so 9 fires fitted both "D works, 3 round
trips" and "D does nothing, 8 round trips". Every other sub-case had its own counter and came
back unambiguous.

**The design error is the durable lesson:** a positive control must not share an instrument with
the thing being measured. Rule 4 above now says so.

**Second run, using the one-press procedure — reset, press D once → `OnVisible fired: 1`.**
So **`Navigate()` to the screen you are already on DOES re-run `OnVisible`.** MS Learn does not
document this; it defines `Navigate` in terms of "the NEW screen". The behaviour is grounded by
this probe, not by the docs, which matters if it ever changes.

### Why issue #15 still uses the hidden worker rather than D

Both work, so this was a choice, not a constraint:

- **No screen transition.** D repaints the whole screen on every delete; the worker is invisible.
- **No back-stack perturbation.** `scrProject` already carries a comment explaining that it
  navigates to an *explicit destination rather than `Back()`*, because `Back()` alternates
  between the two most recently displayed screens and that caused a real bug on this screen.
  Self-navigation pushes a screen onto its own history — the same class of hazard.
- **The block gets a name.** `Select( btnPrjRecompute )` says what it does at each call site;
  `Navigate( scrProject )` says "reload everything" and leaves the reader to infer why.

D stays the cheaper option for any screen that genuinely wants a full reload, and the choice is
reversible in one line.
