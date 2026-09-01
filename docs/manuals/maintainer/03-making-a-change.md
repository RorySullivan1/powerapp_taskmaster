# 3 · Making a change, end to end

The full workflow is `.claude/workflows/change-end-to-end.md`, and the
`powerapp-canvas-developer` agent runs it. This chapter is the human-readable version of the
same path, for when you are doing it yourself.

## The path

**1 · Locate.** One unit per file: a screen is `src/Screens/scr*.pa.yaml`, a component is
`src/Components/cmp*.pa.yaml`, the App object is `src/App.pa.yaml`. Read the file's header
comment first — every screen carries the rules that screen breaks if they are ignored, and they
are there because each one was paid for.

**2 · Check what is already settled.** `.claude/memory/INDEX.md` holds the decisions ledger.
A settled call is not to be relitigated; if you are about to reverse one, that is a decision of
its own and it gets logged, not quietly made.

**3 · Author.** Every column token must resolve to a `name:` in `schema/schema.yaml`, and every
control token to a real one (`tools/studio-enums.json`). Geometry is computed, not eyeballed —
band arithmetic is written in the screen headers, and changing one band height means changing
the number that other bands subtract.

**4 · Validate.**

```bash
python3 tools/validate_pa_yaml.py
```

Plus the audits when they apply — see [chapter 5](05-validation-and-enforcement.md).

**5 · Audit before hand-off.** The `pre-paste-review` agent is read-only and returns a
**paste / do-not-paste** verdict against the schema and the delegation rules. Use it on anything
non-trivial. It is the last gate that exists on this side of the gap.

**6 · Hand off.** Say exactly what a human must do in Studio: which screen, which channel (code
view or formula bar), in what order, and what "it worked" looks like. Keep each paste small
enough that a rejection is diagnosable.

**7 · Log the crossing.** A row in `docs/build-history.md` once the human confirms. **An
unlogged paste is drift you cannot reconstruct** — the log is the only record of what the
running app actually contains. If Studio suffixed a pasted control's name (`Gallery1_1`), the
rename-and-log rule in the `studio-transfer` skill applies.

**8 · Record the decision.** Anything that a future session could relitigate goes in
`.claude/memory/`, not into a comment in `src/` and not into a context brief.

## Committing

`.claude/memory/` **is committed** — the remote environment is ephemeral, so uncommitted memory
does not survive the session. Commit source, schema, memory and docs together when they belong
to the same change.

## Things that must stay in step

The gap makes duplication dangerous, so these are the pairs that will go silently wrong if one
half moves without the other. **Check this list before every hand-off that touches them.**

| This | Must equal | Symptom when it drifts |
|---|---|---|
| `gDataRowLimit` in `App.OnStart` (and the seeds in `scrHome` / `scrReports`) | **Studio › Settings › General › Data row limit** | Every truncation sentinel compares against the wrong ceiling and goes dead silently. Power Fx cannot read the setting, so nothing in the app can catch this. `grep -rn gDataRowLimit src/` |
| `gStageWeights` in `App.OnStart` | `rollups.project_perc_completion.stage_weights` in `schema.yaml` | Completion percentages stop matching the schema's definition of them |
| The colours inlined in `src/Components/*` | `gTheme` in `App.OnStart` | Components drift from the app's palette — a component is isolated and cannot read app globals |
| `gNavMenu` keys in `App.OnStart` | The `Switch` in each screen's `OnNavigate` | A nav entry navigates nowhere |
| The phase allow-list in `App.Formulas` `ActiveProjects` | `project_phase` choice values in `schema.yaml` | A phase added to the column and not to the formula makes those projects **vanish** from the app rather than error — the allow-list fails closed, deliberately |
| Every column token in `src/` | `schema/schema.yaml` | Enforced by the column-guard hook; see [chapter 5](05-validation-and-enforcement.md) |
