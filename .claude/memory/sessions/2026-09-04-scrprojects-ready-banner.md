# 2026-09-04 — scrProjects: "Ready To Mark Completed" banner

Branch `claude/projects-ready-to-complete-banner`, cut off `main` at the user's
explicit instruction (not the standing `claude/powerapp-repo-init-xymvlm`).
`scrProjects.pa.yaml` was byte-identical on both, so the base costs nothing.

## What the user asked for
A project at 100% shows a large green box reading **"Ready To Mark Completed"**,
covering the due-date-to-percent stretch of the gallery row. Purely a notice —
clicking it opens the project like any other part of the row.

## What was built
`galProjects` → `rowBody` gains one nesting level on its right-hand pair:

- `colDuePct` — horizontal auto-layout wrapping the existing `rowDue` + `rowPercent`
  unchanged. `FillPortions: 3`, `LayoutMinWidth: 310` (= their old 2 + 1 and
  190 + 16 + 104). `Visible` = NOT ready.
- `rowReadyBanner` — the next sibling, same 3 portions / 310 floor, `Height: 40`,
  `Fill: gTheme.Color.Success`, holding one centred `rowReadyText` label.
  `Visible` = ready.

Ready is `Coalesce(project_perc_completion, 0) >= 100 &&
Coalesce(project_phase.Value, "") <> "Complete"`.

## The three calls worth keeping
1. **A SIBLING SWAP, NOT AN OVERLAY.** An absolute overlay would need the X of
   `rowDue`, and an auto-layout child has no X to reference. Because a hidden child
   takes no space, hiding `colDuePct` hands its exact slot to the banner — same
   visible result, zero geometry, correct at any width. This is `cmpLookupField`'s
   landed pick-button/chip swap, reused. **The design skill already names this as
   the replacement for the absolute-overlay pattern; this is a second use of it.**
2. **NO `Fill` ON A LABEL.** The banner was first written as one `Label@2.5.1` with
   `Fill: gTheme.Color.Success`. A parse of `src/` showed **270 landed Label
   instances and not one of them sets `Fill`** — so it was an unverified token, and
   an unverified token fails the whole screen paste, not just itself. Rebuilt as a
   filled `GroupContainer` wrapping a transparent Label, which IS landed (lfChip).
   **The check is cheap and should be routine: parse every control of that type in
   `src/` and see whether the property has ever landed, before typing it.**
3. **NO `OnSelect` ON THE BANNER.** `galProjectsHit` spans the template and is
   declared last, so it is already on top and already navigates. An `OnSelect` here
   would render, hover, and silently do nothing — the exact failure the validator's
   `overlay_reachability()` NOTE exists to catch.

## Excluded deliberately
A project already in the **Complete** phase does NOT get the banner — it is only
reachable with "Show completed" on, and telling someone to mark complete something
already complete is noise. `Archived` never reaches this gallery at all.

## State
Validator 22/22. **AUTHORED, NOT PASTED.** No schema change, no SharePoint work —
both columns it reads are long since provisioned.
