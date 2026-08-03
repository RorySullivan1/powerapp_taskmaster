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

**Keep pasting.** The code-view channel is *proven* — `scrAdmin` landed, and components landed
after the dialect fix. Trading a working channel for an unproven packaging exercise is a bad bet,
especially when the failure mode is silent.

## A naming inconsistency worth knowing about

This repo names screens `scr*.fx.yaml` and components `cmp*.pa.yaml`. **Both contain pa-yaml v3.0**
and both validate against `tools/pa.schema.v3.0.yaml`. But `*.fx.yaml` is the file extension of the
**retired experimental format** used by `pac canvas unpack` — so the screen files are named after a
format they are not. Cosmetic today; genuinely misleading to a future reader. Renaming them to
`.pa.yaml` is a mechanical change plus doc references.

## Sources

- [Microsoft Power Platform CLI canvas command group](https://learn.microsoft.com/power-platform/developer/cli/reference/canvas) — pack/unpack deprecation
- [View source code files for canvas apps](https://learn.microsoft.com/power-apps/maker/canvas-apps/power-apps-yaml) — `.pa.yaml` read-only, not used when loading; retired format table
- [Source control for canvas apps (Git integration)](https://learn.microsoft.com/power-platform/alm/git-integration/canvas-apps-git-integration)
- [Natively connect your environments to source control](https://learn.microsoft.com/power-platform/release-plan/2024wave2/power-apps/connect-environment-source-control) — Azure DevOps; distinct from the experimental GitHub integration
- [Don't use PASOPA in production — PowerApps-Tooling discussion #758](https://github.com/microsoft/PowerApps-Tooling/discussions/758)
