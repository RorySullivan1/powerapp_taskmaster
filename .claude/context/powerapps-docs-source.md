# powerapps-docs — the authoritative control & layout source

`github.com/MicrosoftDocs/powerapps-docs` (branch `main`) is the **source markdown** behind
`learn.microsoft.com/power-apps`. It is the most comprehensive, greppable reference for what
canvas-app **controls, layouts and properties do**. Consult it whenever grounding a control's
semantics, a layout behaviour, or the meaning of a property.

## How to read it — fetch on demand, no clone
- **Rendered + searchable (fastest first stop):** the already-connected **Microsoft Learn MCP** —
  `microsoft_docs_search` then `microsoft_docs_fetch`. Same content, chunked for search.
- **Raw source file (WebFetch):**
  `https://raw.githubusercontent.com/MicrosoftDocs/powerapps-docs/main/<path>`
- **Browse / list a folder (gh):** `gh api repos/MicrosoftDocs/powerapps-docs/contents/<path>` —
  list a folder, then fetch the `control-*.md` you need. This is how you grep the whole control set.

## The paths that matter
The docs root is the `powerapps-docs/` folder inside the repo. Canvas-app material:
- **Classic controls** — `powerapps-docs/maker/canvas-apps/controls/control-*.md`
  (50 files: `control-button.md`, `control-combo-box.md`, `control-grid-container.md`, …)
- **Modern (Fluent) controls** — `.../controls/modern-controls/modern-control-*.md` (34 items)
- **All-properties reference** — `.../controls/reference-properties.md`
- **Layout / responsive** — `.../canvas-apps/create-responsive-layout.md`,
  `.../canvas-apps/build-responsive-apps.md`
- **Scale / performance** — `.../canvas-apps/working-with-large-apps.md`

## What it grounds — and the hard limit (READ THIS)
These docs ground **semantics and DISPLAY-property names**: what a control is, what it does, what a
property means. They do **NOT** give the pa-yaml `Control:` token, its `@version`, the `Variant:`
string, or the property TOKENS. The dialect renames on the way into code view (the container's
"Gap" → `LayoutGap`, "Direction" → `LayoutDirection`; the Grid container's tokens are still unknown).

So this source answers *"what is this control and what are its properties?"* — the exact pasteable
token still comes from a **Studio code-view**, per the air gap. **Ground meaning here; ground tokens
against `tools/studio-enums.json`.** Worked example of the split: the Grid container — semantics
grounded from `control-grid-container.md`, tokens still pending a code-view — see
`tools/studio-enums.json ▸ _gridContainerNotes`.

## Relation to the other sources
- `tools/studio-enums.json` — the **grounded pa-yaml tokens** (Studio code-view / photo provenance). Authoritative for what to type.
- `docs/reference/powerapps-canvas-yaml.instructions.md` — the pa-yaml authoring guide (structure + Power Fx), with this repo's correction table on top.
- This repo (powerapps-docs) — the **meaning** layer: control catalogue, property semantics, layout behaviour.
