# 2026-08-19 16:00 · issue22-derived-health

**Goal:** Issue #22 — task health stops being user-set and becomes derived

## What happened
- **Health is now DERIVED. `scrTaskEdit` has no health control.** Two user decisions settled it
  before any code was written (both asked, both answered):
  1. **`issue_type`'s vocabulary changed** — the user had ALREADY replaced the five values
     (Approval, Process, Compliance, Branding, Technical) with SEVEN: Approval, Change Request,
     Question, Other, Blockage, Exception, Limitation. schema.yaml now mirrors that.
  2. **Hybrid derivation**, not fully-stored.
- **THE TWO HALVES, and why they are split — this is the whole design:**
  - **STORED** in `task_status`, from the task's OPEN issues: type in
    Blockage/Exception/Limitation, or impact Critical → Red; any other open issue → Amber;
    none → Green.
  - **LIVE, NEVER STORED**: not Completed AND past `task_date_target` → Red. Overdue changes
    **with no write** — a task turns red at midnight — so a stored copy is only ever as fresh as
    the last save. `task_date_target` is on the task row, so folding it in at read time costs
    NO join and stays delegable.
  - Full rules live in **`rollups.task_health` in schema.yaml**, deliberately in ONE place; the
    call sites point at it rather than restating it.

## Gotchas & dead ends
- **AMBER IS THE RESIDUAL ("any other open issue"), NOT the four amber types enumerated.**
  Enumerated, a type added in SharePoint and not added to the app falls through to GREEN — an
  allow-list failing CLOSED, silently, on the one signal that exists to warn people. As a
  residual it fails SAFE: an unknown or blank type reads Amber, which is visible and fixable.
  Same lesson as `ActiveProjects`, but here the cost of failing closed is much higher.
- **A NEW TASK MUST BE GREEN WITHOUT A QUERY.** In New mode there is no ID, and
  `issue_task_name.Id = Blank()` matches every issue that has NO task — which would open a
  brand-new task at Red. `scrTaskEdit` guards with `If(gEditMode = "Edit", …)`. Do not remove it.
- **The RAW issues list, never the `OpenIssues` named formula.** `OpenIssues` also excludes
  archived projects, which would drive every task under an archived project to Green instead of
  leaving it alone. These queries are already scoped to one task, so per CLAUDE.md they read raw.
- **Narrow server-side, test locally.** `issue_task_name` and `issue_status` are INDEXED so the
  fetch delegates; `issue_type` and `issue_impact` are NOT indexed and are only ever tested
  against the few rows that come back. Written as one flat Filter the whole query goes
  non-delegable and silently reads a page of the issues list instead of one task's issues.
- **The task link can MOVE, so an issue save recomputes TWO tasks** — the one gained and the one
  lost. The old id is captured BEFORE the Patch (`gIssOldTask`); after it, the old value is gone.
  Same shape on delete: the row that knows the task id is about to be removed, so read it first.
- **NO DOUBLE `Select()`.** The first design called the recompute button once per task with a
  global set between calls — that assumes `Select()` runs synchronously in sequence, which is
  not grounded. Replaced with: seed a COLLECTION (`colHlTasks`) of ids, `Select()` ONCE, and let
  the button `ForAll` over it. No ordering assumption anywhere.
- **A hidden button beat inlining, but only just.** A control can only be `Select()`ed from its
  own screen, so there is no single shared copy — it is 2 duplicated bodies (scrIssueEdit,
  scrProject) versus 3 inline copies. The bodies were diffed after writing: **33 code lines
  identical.** Keep them that way. `Select()` on `Visible: =false` is PROVEN, not folklore —
  tests/README.md:289, probe run 2026-08-18.
- **A task save does NOT change the stored half** (it depends only on issues), so `scrTaskEdit`'s
  save was NOT strictly a required recompute point. It rewrites health anyway: one delegable
  query, and it makes opening a task repair any drift.
- Completed tasks get NO overdue fold in scrReports — a finished task is not at risk for having
  landed late, and its Gc/Ac/Rc are zero regardless.

## State at end
- Authored, 22/22 valid. Six files: schema.yaml, scrTaskEdit, scrIssueEdit, scrProject,
  scrProjectEdit (a comment), scrReports, plus two reference docs.
- **FOUR SCREENS ARE QUEUED FOR PASTE: scrTaskEdit, scrIssueEdit, scrProject, scrReports.**

## Open threads
- **`issue_type`'s seven values are TAKEN ON THE USER'S WORD.** If SharePoint's Choice does not
  hold exactly `Blockage` / `Exception` / `Limitation`, those issues quietly read Amber instead
  of Red — no error, just an under-warning. Worth one look at the column before trusting a Green.
- **Existing rows are stale until touched.** Nothing back-fills `task_status`: a task keeps its
  last user-chosen health until an issue on it changes or someone saves it. Overdue is live so
  it is right immediately; the issue-derived half is not. **No bulk recompute exists** — decide
  whether one is wanted.
- The health strip's removal leaves `colTkPriority` alone on its row at FillPortions 1, so the
  priority strip now spans the full width — same as `selTkStage` already does, so it is
  consistent, but it is a visible change nobody asked for. Cosmetic; revisit if disliked.
