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

## `scrProbe-rerun-block.pa.yaml` — how does a screen re-run a behaviour block in place?

**Status: NOT YET RUN.** Blocks the `scrProject` half of issue #15.

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
