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
4. **Positive control:** *now* drag the green bar and re-check its formula bar. If
   dragging turns `=Parent.Width - 400` into a number, the instrument can see
   freezing — which is what makes a negative result in steps 1–3 mean anything.

### Result — 2026-08-13, run by the user in Studio

**All four steps ran. Every layout formula survived the paste, as a formula.**

- Steps 1–3: the probes came through with their formulas intact. Typing into the
  box moved the dark blue bar, and the light blue bar chained off it moved with it,
  so the formulas were **live after the paste** — not constants that happened to
  equal the right number. Backward reference, forward reference, `Parent`
  arithmetic and the container's own `Width` all held.
- Step 4, the positive control: dragging behaved as MS Learn documents. **So the
  instrument could see freezing, and did not see it on paste.** That is what makes
  this a real negative rather than an inconclusive one.

**The rule was wrong, and it was wrong in a specific, repeatable way: an inference
was written down in the voice of its citation.** The MS Learn quote said *dragging*;
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
