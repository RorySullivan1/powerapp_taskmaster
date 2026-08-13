# 2026-08-13 17:39 · scrhome-dashboard

**Goal:** Rebuild scrHome as a dashboard: four inert metric cards, my-tasks and my-issues
galleries, chart placeholders + KPI ring

## What happened
- **`scrHome` rewritten end to end.** Everything below the app bar is now ONE auto-layout
  tree (`bodyRoot`, vertical, `LayoutOverflowY: Scroll`) — no child carries an X or a Y,
  so the screen cannot collide at any width and cannot be nudged by a drag in Studio.
  Bands: `wrapHdr` 60 · `rowCards` 96 · `rowLists` fills · `rowCharts` 200.
  `rowLists.Height = Parent.Height - 452` (48 padding + 48 gaps + 60 + 96 + 200).
- **Four metric cards, deliberately inert** — projects led, tasks led, issues on my
  projects, issues assigned to me. Built as plain `GroupContainer` cards, NOT
  `cmpStatusCard`: that component carries a full-bleed transparent button with a hover
  wash, so it reads as tappable and the user asked for non-clickable.
- **Two work lists** — `galMyTasks` (open tasks I lead) and `galMyIssues` (open issues
  assigned to me), both across every live project. Columns are status glyph · priority
  (or impact) · item name · project name. Both rows navigate to the PARENT PROJECT, not
  to the item.
- **Charts band** — `pnlTimeline` (FillPortions 3) + two donut placeholders + the
  `cmpKpiRing` completion ring. Placeholders are static grey SVG data URIs so they read
  as unfinished; the ring is the one real visual.
- **Removed:** the "Archive a project…" button and, with it, `cmpConfirmHome`
  (`cmpConfirmDialog`) — the modal had no other trigger on this screen. The Refresh
  action on `cmpSectionHeader` is kept and now also `Refresh(taskmaster_projects)`.
- 22/22 files valid. Committed on `main`.

## Gotchas & dead ends
- **The cross-list join has no delegable single query.** There is no
  `issue_project_manager` column, and `issue_project_id.Id in colMyProjects.ID` does NOT
  delegate — it caps at the data row limit and undercounts SILENTLY. "Issues on my
  projects" is therefore `Sum( ForAll(colMyProjects As p, CountRows(Filter(OpenIssues,
  issue_project_id.Id = p.ID))), Value )`: one delegable round trip PER PROJECT MANAGED.
  Cost grows with how many projects one person owns, not with the size of the issues list.
  MS Learn confirms the shape — "if the result of the formula is a single value, the
  resulting table is a single-column table", column `Value`.
- **`colMyTasks` is now LEAD-ONLY.** It previously carried
  `task_lead.Email = gUserEmail || task_supporter.Email = gUserEmail`. The dashboard says
  "tasks led", so supporter is gone — which also changes what the KPI ring averages over.
  The ring's caption says "task(s) you lead" so the two cannot silently disagree.
- **"Issues owned" reads as `issue_assignee`, not `issue_owner`.** `issue_owner` is the
  un-indexed who-raised-it stamp; an Or-arm on it would drop delegation for the whole
  filter. Assignee is the resolver and the only indexed, delegable choice. ASSUMPTION —
  flagged to the user, not confirmed.
- **The project name on a child row must be resolved app-side.** `task_project_id` /
  `issue_project_id` are Lookups whose canvas value DISPLAYS THE NUMERIC ID, not
  `project_name` — one `LookUp(taskmaster_projects, ID = ThisItem.*_project_id.Id,
  project_name)` per visible row.
- **The row hit button re-LookUps the project and can MISS.** scrProject derives a phase
  and can Patch it, so navigating there on a blank record would write against nothing —
  both galleries refuse and Notify instead.
- **Refresh duplicates the whole OnVisible block.** There is no shared function to call.
  A divergence shows up as the dashboard reading one set of numbers on open and another
  after a Refresh, with nothing to say which is right — the two blocks carry a comment
  saying they must stay identical.
- **Task "status" is the LIFECYCLE glyph (`task_stage`), not the RAG health column
  (`task_status`).** Chosen for consistency with scrProject / scrProjects, which both use
  the stage progression. Reversible in one control if the user wants the traffic light.

## State at end
- `scrHome` joins the paste queue — it was the ONLY screen not on it.
- `cmpStatusCard` and `cmpConfirmDialog` now have NO consumer anywhere in `src/`.
  Their files are kept; they are Studio housekeeping candidates alongside the six already
  listed.

## Open threads
- Confirm "issues owned" = `issue_assignee` (assumed) rather than `issue_owner`.
- The three chart placeholders need a real implementation — timeline, tasks by stage,
  issues by impact. No charting control is grounded for this dialect yet.
- Everything already open: SharePoint `project_phase` default, the unverified live
  `issue_status`/`issue_type`/`issue_impact` values, Studio component housekeeping.
