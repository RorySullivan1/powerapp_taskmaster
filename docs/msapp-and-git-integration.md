# Can this repo be packaged into a `.msapp`?

**No, and it is worth being precise about why, because the reason changed.** Asked and answered
2026-08-03. This note exists so it isn't re-litigated.

## The three blockers

### 1. The tooling is deprecated

`pac canvas pack` / `pac canvas unpack` are **deprecated**. Microsoft's own guidance is to use
Power Platform Git integration instead. The `--processCanvasApps` parameter on `pac solution` uses
the same legacy engine and is deprecating with it. The separate community-facing tool, **PASopa**,
carries an explicit *"please don't use the experimental tool PASOPA in production"* warning from
its own maintainers.

Separately: the CLI cannot be installed in this repo's environment — the .NET install is blocked by
the agent proxy. So even the deprecated route isn't runnable from here.

### 2. `.pa.yaml` is a *representation*, not the thing that loads — this is the decisive one

From MS Learn (*View source code files for canvas apps*):

> The `.pa.yaml` files are **read-only** and should only be used to review changes made in Power
> Apps Studio. **These files are not used when an app is loading.**

An `.msapp` is a zip whose **JSON control tree** is what Studio actually loads; `\Src\*.pa.yaml` is
a human-readable mirror written alongside it. Dropping this repo's authored YAML into `\Src` and
zipping it would produce an app that opens **empty**.

Building a genuine `.msapp` therefore means hand-authoring `CanvasManifest.json`, `Header.json`,
`Properties.json`, the per-control JSON, `Entropy/`, and a computed `Checksum.json` — internals that
are undocumented and checksum-validated. That is a reverse-engineering project whose most likely
output is a file Studio refuses to open, and **under a one-way gap a refusal is the worst possible
result**: no diagnostic, no partial success, just "it didn't work."

Note the asymmetry with what we already do: **code-view paste consumes the YAML dialect directly**,
which is why that channel works and this one doesn't. The paste target and the file-format target
are not the same surface.

### 3. Nothing is bound yet

Even a perfect `.msapp` carries `DataSources/` entries pointing at a real site URL and real list
GUIDs. Those don't exist until the lists are provisioned, and the one-way gap means they can't be
read back into the repo afterwards.

## What would actually retire the clipboard: Git integration

**Power Platform Git integration** stores canvas app source as `.pa.yaml` and — unlike the file
formats above — explicitly supports editing in the repository:

> You can do minor edits directly in the repository. Any changes are restored with the app when you
> pull changes to your environment.

That is a genuine two-way channel, and it is the only supported one. The constraints are real
though, and all three need checking on the work machine:

| | |
|---|---|
| **Host** | **Azure DevOps**, not GitHub. The GitHub integration for canvas apps was experimental and is **retired**. |
| **Scope** | Dataverse **solutions** — the app has to live in one |
| **Flow** | publish → commit. The repo mirrors a *published* app |
| **Caveat** | "Avoid making *significant* changes directly in the `.pa.yaml` files"; apps containing code components can't be edited in the repo at all |

**Open question for the work machine:** is Azure DevOps available, and can this app live in a
solution? If yes, Git integration is worth more than any packaging trick — it would replace the
clipboard entirely and make the gap two-way. It cannot be settled from this side.

## Recommendation

**Keep pasting.** The code-view channel works — `scrAdmin` landed through it. Components have
since regressed (see `docs/build-history.md`), and the response to that is to split each one into a typed
contract and a pasteable body, not to abandon the channel: a packaging route whose failure mode is
a file Studio silently refuses to open is strictly worse than one that at least reports an error.

## A naming inconsistency — found here, since fixed

Screens used to be named `scr*.fx.yaml`. But `*.fx.yaml` is the extension of the **retired
experimental format** used by `pac canvas unpack`, and these files have always contained pa-yaml
v3.0 — so they were named after a format they are not. Harmless until you know what the extension
means, then actively misleading.

**Renamed to `*.pa.yaml` on 2026-08-03.** Every authored file now carries the extension of the one
schema version that is still active, matching what Git integration and the `\Src` folder of a
`.msapp` use. `App.Formulas.pa.fx` keeps its own extension deliberately: it is a Power Fx snippet
for the formula bar, not YAML and not a paste payload.

## Sources

- [Microsoft Power Platform CLI canvas command group](https://learn.microsoft.com/power-platform/developer/cli/reference/canvas) — pack/unpack deprecation
- [View source code files for canvas apps](https://learn.microsoft.com/power-apps/maker/canvas-apps/power-apps-yaml) — `.pa.yaml` read-only, not used when loading; retired format table
- [Source control for canvas apps (Git integration)](https://learn.microsoft.com/power-platform/alm/git-integration/canvas-apps-git-integration)
- [Natively connect your environments to source control](https://learn.microsoft.com/power-platform/release-plan/2024wave2/power-apps/connect-environment-source-control) — Azure DevOps; distinct from the experimental GitHub integration
- [Don't use PASOPA in production — PowerApps-Tooling discussion #758](https://github.com/microsoft/PowerApps-Tooling/discussions/758)
