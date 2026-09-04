# 2026-09-04 19:58 · scrprojects-ready-banner

**Goal:** Show a green "Ready To Mark Completed" banner on any scrProjects row at 100% not yet phased Complete

## What happened
- Branch `claude/projects-ready-to-complete-banner`, cut off `main` at the user's
  explicit instruction rather than the standing `claude/powerapp-repo-init-xymvlm`.
  Checked first: `scrProjects.pa.yaml` was byte-identical on both, and the other
  branch's 11 commits had already merged as PR #57, so the base costs nothing.
- `galProjects` → `rowBody` gains one nesting level on its right-hand pair:
  - `colDuePct` — horizontal auto-layout wrapping the existing `rowDue` +
    `rowPercent` UNCHANGED. `FillPortions: 3`, `LayoutMinWidth: 310` (= their old
    2 + 1 and 190 + 16 + 104). `Visible` = NOT ready.
  - `rowReadyBanner` — the next sibling, same 3 portions / 310 floor, `Height: 40`,
    `Fill: gTheme.Color.Success`, holding one centred `rowReadyText` label.
    `Visible` = ready.
- Ready is `Coalesce(project_perc_completion, 0) >= 100 &&
  Coalesce(project_phase.Value, "") <> "Complete"`.
- **A SIBLING SWAP, NOT AN OVERLAY.** An absolute overlay needs `rowDue.X`, and an
  auto-layout child has no X to reference. A hidden child takes no space, so hiding
  `colDuePct` hands its exact slot to the banner — same picture, zero geometry,
  correct at any width. This is `cmpLookupField`'s landed pick-button/chip swap
  reused; the design skill already names it as the replacement for the
  absolute-overlay pattern, and this is its second use.
- **NO `OnSelect` ON THE BANNER.** `galProjectsHit` spans the template and is
  declared last, so it already navigates. An OnSelect here would render, hover and
  silently do nothing — the failure `overlay_reachability()` exists to NOTE.
- Validator 22/22. No schema change; both columns read are long since provisioned.

## Gotchas & dead ends
- **THE ONE THAT NEARLY SHIPPED: `Fill` ON A LABEL.** The banner was first authored
  as a single `Label@2.5.1` with `Fill: gTheme.Color.Success`. Parsing every control
  in `src/` found **270 landed `Label@2.5.1` instances and NOT ONE sets `Fill`** — an
  unverified property, which across this gap fails the WHOLE screen paste and returns
  as "it didn't work". Rebuilt as a filled `GroupContainer` wrapping a transparent
  Label, the shape already landed as `cmpLookupField`'s `lfChip`.
  **RULE, and it generalises past this screen: before typing a property onto a
  control, parse every instance of that control in `src/` and check the property has
  landed before. It is a ten-second script against a blind round trip.** The same
  script then cleared all three new controls, property by property.
- A near-miss on `src/Screens/scrProject.pa.yaml:799` — `Fill: =gTheme.Color.Success`
  is there, but on a **Button**, not a Label. Reading the grep hit without checking
  the control type would have "grounded" the wrong thing.
- MS Learn does NOT state that a hidden child takes no space in an auto-layout
  container; the search returned nothing on it. The claim is grounded instead by
  `.claude/skills/powerapp-canvas-design` and, decisively, by `cmpLookupField`
  working in the landed app. Field evidence, not documentation.
- A first splice put the nested sequence items level with their `Children:` key —
  valid YAML, but not this repo's style. Re-indented to 2 under the key.
- A comment claiming the nesting left the other columns' widths untouched was
  overstated and got corrected: folding two children into one container removes one
  of the row's gaps and moves that 16px inside the container, shifting every column
  by up to ~7px at the design width.

## State at end
- **AUTHORED, NOT PASTED.** Committed `7a2f286` and pushed to
  `claude/projects-ready-to-complete-banner`. No PR opened — the user did not ask.
- Proof when it is pasted: a project at 100% still phased Active shows the green box
  in place of its due date and percent, and clicking it opens the project.
- A project already phased `Complete` is deliberately EXCLUDED — only reachable with
  "Show completed" on, where the notice would be noise. `Archived` never reaches this
  gallery at all.

## Open threads
- Whether the banner should fire on 100% regardless of phase. Offered to the user as
  a one-clause edit in two places; not answered.
