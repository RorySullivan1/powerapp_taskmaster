# 2026-08-11 13:25 · scrproject-padding-overflow

**Goal:** Fix overlapping labels in the scrProject task list and shrink cardInfo's generated fact values to 12pt

## What happened
- Reported from Studio as *"the items in scrProject task list have labels that are overlapping"*
  plus *"the cardInfo generated values are too large, make them a size 12"*. No render available —
  diagnosed entirely by arithmetic against the authored source.
- **Root cause: `Parent.Width` in a padded auto-layout container is the container's OUTER width,
  padding included — it is NOT the content box.** A child written `Width: =Parent.Width` is
  *placed* at the content-box left edge but *sized* to the outer width, so it hangs off the right
  by exactly `PaddingLeft + PaddingRight`. Every child of a padded container on `scrProject` had
  it — the screen never subtracted padding anywhere.
- Resolved at 1366x768, and this is the reported defect exactly:

  | control | was | now |
  |---|---|---|
  | `rowWork` | 24 .. **1390** — 24px off-screen (bodyRoot padding 24) | 24 .. 1342 |
  | `galTasks` | 40 .. **850** — 16px past its own card (secTasks padding 16) | 40 .. 818 |
  | `cellTaskWho` | 615 .. **842** | 600 .. 810 |

  `colIssues` begins at **850**, so "Assigned to" was drawn 24px past the tasks card border and
  8px into the issues column.
- Fixed on all **12** affected children: `- 48` under bodyRoot's 24px padding (`cardInfo`,
  `rowWork`), `- 32` under the three cards' 16px padding (`rowTasksHead`, `lblTasksEmpty`,
  `galTasks`, `rowTxHead`, `lblTxEmpty`, `galTransactions`, `rowIssuesHead`, `rowIssuesCols`,
  `lblIssuesEmpty`, `galIssues`). `rowWork.Height` likewise now subtracts bodyRoot's TOP+BOTTOM
  padding (`=Parent.Height - 48 - 172 - Theme.Space.Gap`).
- `cardInfo`: the 8 `lblFactVal*` dropped `Theme.Size.Body` (14) -> `Theme.Size.Small` (12).
  Captions were already 12, so hierarchy now rests on `FontWeight.Semibold` + `TextPrimary` vs the
  caption's regular `TextMuted`. **`lblProjName` deliberately left at `H2`** — card title, not a
  captioned fact; flagged to the user as a reversible call.
- Band arithmetic + the padding rule written into the screen's header comment (design skill §1) so
  Studio's numbers can be eyeballed without evaluating `Theme.Space.*` by hand.
- 24/24 valid. Committed `c1ce06b`, pushed to `claude/powerapp-repo-init-xymvlm`.

## Gotchas & dead ends
- **`scrProjectEdit` already had the answer.** It has ALWAYS written `=Parent.Width - 48` inside
  its 24-padded containers — ~40 occurrences. The idiom was proven in-repo; `scrProject` simply
  never applied it. Grepping the reference screen for `Parent.Width -` was what settled it. **When
  a container screen looks wrong on its right-hand side, check the padding subtraction FIRST.**
- **Dead end — chased three wrong theories before the arithmetic.** (1) Paste-time freezing of the
  gallery cells: rejected, because X *and* Width freeze off the same `TemplateWidth`, so they stay
  internally consistent and cannot overlap each other. (2) Text overflow between cells: rejected, a
  Label with `AutoHeight: false` wraps and CLIPS, it never bleeds horizontally. (3) Row-to-row
  vertical collision: rejected, cells are 51 high in a `TemplateSize: 52` with the rule at Y=51.
  The authored cell geometry (20/50/30 with ±8 insets) was correct the whole time — **the defect
  was upstream, in how wide the gallery itself was.**
- **`Wrap: =false` on the row cells was considered and NOT authored.** It would make a 52px table
  row read better, but the token is used nowhere in this repo and is ungrounded for
  `Label@2.5.1` — a wrong property fails the whole paste and returns only "it didn't work".
- **A `GroupContainer` inside a gallery template was considered and NOT authored** as the
  freeze-immune fix. It is the textbook §5 answer, but no Studio code-view grounds a container as a
  gallery-template child, and the padding fix solves the actual defect without a new construct.
- The three gallery `Height` formulas (`Parent.Height - 80`, `- 108`) are each ~6-8px *conservative*
  vs the true content budget and are governed by `FillPortions: =1` anyway — left alone deliberately
  to keep the human's paste diff small.

## State at end
- `scrProject` is the only screen audited for this bug. **The other container screens were NOT
  checked** — `scrTaskEdit` (38 auto-layout containers) and `scrIssueEdit` are the obvious next
  candidates; `scrProjectEdit` is known-clean since it is where the correct idiom came from.
- Nothing landed in Studio yet. Hand-off given as **13 formula-bar edits, not a screen paste** —
  re-pasting re-evaluates every layout formula mid-paste, before the container tree is laid out,
  which is the class of thing that put wrong numbers in there originally. The 8 `Size` edits are
  paste-safe (font size does not freeze).

## Open threads
- **Await the binary from Studio.** If labels still overlap after these 13 edits, the padding
  overflow is ruled out as the cause — the useful report back is *which two labels* touch and
  whether the columns sit too far left or too far right.
- **Sweep `scrTaskEdit` and `scrIssueEdit` for the same `Width: =Parent.Width`-inside-padding
  bug.** It is mechanical: for each auto-layout container with `PaddingLeft`/`PaddingRight`, every
  child's `Width` must subtract their sum.
- **Hook candidate, now with evidence.** CLAUDE.md already proposes a column-token validator; this
  session argues for a second one — a write-time check on `src/` that flags any child whose `Width`
  is `=Parent.Width` when the parent declares horizontal padding. It is pure arithmetic over the
  YAML tree, needs no Studio, and would have caught this at author time.
