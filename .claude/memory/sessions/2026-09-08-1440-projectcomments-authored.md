# 2026-09-08 14:40 · projectcomments-authored

**Goal:** Author #62/#63/#64 as one scrProject paste after the user provisioned taskmaster_projectcomments

## What happened
-

## Gotchas & dead ends
-

## State at end
-

## Open threads
-

## What the user reported
`taskmaster_projectcomments` created in SharePoint with the three columns, the FK and the
archived flag indexed, `Created` / `Created By` confirmed indexable, and the list CONNECTED as a
data source in Studio. That unblocked everything below.

## What landed in the repo (not yet in Studio)
`schema.yaml` → `provisioned: live`. One `scrProject` paste carrying #62, #63 and #64:

- **Fetch (#62).** Fourth arm of `btnPrjRecompute`'s `Concurrent`, `ClearCollect( colProjectCmt,
  Sort( Filter( taskmaster_projectcomments, projectcomment_project_id = gSelProject.ID ),
  Created, SortOrder.Descending ) )`. Raw list, not a named formula — the indexed Number FK folds,
  so there is no archived backlog to page through and no fourth named formula to add. The archived
  flag is deliberately NOT a predicate: the FK already scopes to one project, and testing it would
  blank the thread of an archived project you are looking at.
- **Phase derivation.** Untouched, with a comment saying comments are excluded on purpose.
- **Layout (#62).** `colIssues` was the card; it is now a plain column holding `secIssues` over
  `secComments`, both `FillPortions: 1` — the `colLists` shape. Gallery floors 132 → 88.
- **Row (#62).** Text left (`FillPortions 3`), author over date right (150 fixed). Manager rows get
  an accent `Rectangle` plus a tint; `TemplateSize` 64, so a long Note clips rather than scrolls.
- **Dialog (#63).** `mdCmtScrim` / `mdCmtBg` / `mdCmtBody` / `mdCmtPost` / `mdCmtCancel`, declared
  LAST, every part gated on `gCmtOpen`. Double-tap guard `gCmtSaving`, Post always enabled with a
  nudge label, `Reset(txtCmtBody)` on open, trust-the-record on `gCmtScrap.ID`, comments-only
  refetch on success.
- **Cascade (#64).** `gPrDelNC` joins the guard `Concurrent` and the `>= 500` block; a third
  parallel arm `RemoveIf` with `gPrDelErrC` / `gPrDelScrapC`; `Clear(colProjectCmt)` on success.

## Open / next
- **The paste is the next action and it is the user's.** One screen, one bit back.
- `Created` is indexable but not indexed. Harmless until 5,000 rows, then the Sort stops delegating.
- Long comments clip at ~46px. Accepted for v1; the fix would be a taller `TemplateSize`.
- The issues gallery visibly shrank. If the split is wrong the lever is the two `FillPortions`.
- #65 (external archival flow sets the fourth flag) is all that remains in #60.

## Second pass (same day): comments are no longer append-only
User asked for a detail popup on click, with edit/delete restricted to the commenter, and a
character-capped preview with an ellipsis in the row.

- `cellCmtText` → 120-char preview, `Char(13)`/`Char(10)` flattened to spaces first, ellipsis
  only when earned. `galCommentsHit` spans the FULL template (no delete icon in this template).
- `mdCv` appended after `mdCmt`: one `ModernTextInput` switching `DisplayMode` View↔Edit,
  Close / Edit / Delete when reading, Save / Cancel when editing.
- `gCmtCanEdit` computed once in the hit button = author AND project not archived.
- Delete = fourth `gDelKind` on `cmpPrjConfirmDel`; `mdCv` closes first because the confirm
  component is declared earlier and would open underneath it.
- `btnPrjCmtFetch` extracted so the post and edit paths share one refetch.
- schema.yaml: `Created`/`Created By` indexed; item-level permissions recorded as the real
  enforcement of author-only editing.
- GitHub #60/#62/#63 bodies rewritten — they still described the five-column design, which is
  what made the remote contradict the repo.

## Open
- **STILL TO DO IN SHAREPOINT: Item-level Permissions on `taskmaster_projectcomments`.**
- Unverified: whether a long comment scrolls in `DisplayMode.View`. Check on the render.
- No "edited" marker: it would need `Modified`, which is not among the confirmed system columns.

## LANDED — 2026-09-08
User pasted `scrProject` and confirmed the comment functionality works. #61–#64 closed.

The paste is all-or-nothing, so it grounds every token in the file — see the INDEX Decision of
this date for the five shapes that are now usable without re-deriving them.

Still open, neither of them a paste:
- **#65** external archival flow (`projectcomment_project_archived`).
- **Item-level Permissions** on `taskmaster_projectcomments` in SharePoint.

Not exercised by "it works", so not proven:
- the project-delete cascade's fourth arm (deleting a whole project that has comments);
- whether a long comment scrolls in `DisplayMode.View`.
