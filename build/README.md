# build/ — generated artifacts (NOT authored source)

Everything here is **generated** and safe to delete. Authored source stays in
`src/authored/` (modern `.pa.yaml`); this folder holds packed `.msapp` builds for testing.

## `EQD-Taskmaster-smoke.msapp`

A **smoke-test** canvas app produced with `pac canvas pack` (Power Platform CLI 2.10.1)
on 2026-08-03. Purpose: prove the **repo → .msapp → Studio open** channel end-to-end,
as an alternative to the code-view paste channel.

**Scope is deliberately minimal** (see the session decision): two data-independent shell
screens — `scrReference` and `scrAdmin` — with the EQD header, blue theme, a placeholder
card, and **button navigation** between them. **No data sources, no components, no
App.Formulas.** It is the shell's *look*, not its live formulas.

### How to test (the only check the air gap allows)
1. Open Power Apps Studio on the work machine → **Apps → Import canvas app** (or open the
   `.msapp` directly) and load `EQD-Taskmaster-smoke.msapp`.
2. Confirm it **opens without error**, shows the two screens, and the Reference⇄Admin
   buttons navigate.
3. Report back **works / doesn't** — that binary is the return signal (one-way gap).

### How it was built (reproducible)
- Source screens: `build/smoke-src/*.fx.yaml` (old inline dialect — required by the packer).
- Scaffold: the example's own `pac canvas unpack` output (manifest, entropy, pkgs, control
  templates), with the example's screens removed and `ScreenOrder` repointed.
- `pac canvas pack --msapp EQD-Taskmaster-smoke.msapp --sources <scaffold>`.

### Hard-won facts (why it isn't just "pack our repo")
- Only the **deprecated Experimental `.fx.yaml`** layout packs here; `--layout SourceCode`
  (modern `.pa.yaml`) rejects the example: *DocVersion 1.346 < minimum 1.348*. Our authored
  `.pa.yaml` is therefore **not directly packable** — it must be converted to `.fx.yaml`.
- The old `.fx.yaml` format uses a **global control namespace** (names unique across *all*
  screens — hence the example's `1/4/6` suffixes) and **explicit `ZIndex:`**.
- Packing the full app is not attempted: the data-bound screens reference 8 unprovisioned
  SharePoint lists + Office365Users + 11 components that can't resolve without a real tenant.
- **The proven channel is still code-view paste** (`scrAdmin` + components have landed that
  way). This build is a channel experiment, not a replacement.
