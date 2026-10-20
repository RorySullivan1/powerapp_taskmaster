# Landing checklist: everything waiting on you, in one pass

Every open issue is something only you can do: a paste, a live test, or a SharePoint or Power
Automate job. This is all of them in one pass, grouped by where you'll be working. Each item
links its issue, which has the full detail. Note the results as you go, then paste the
**report-back block** at the end into one message, and each issue gets closed or turned into a
bug from that.

Order matters in only two places: paste scrQuickTx (A1) before testing it, and set the phase
default (C1) before you investigate missing projects (D3).

## A. Power Apps Studio: pastes and deletes

- **A1 · scrQuickTx (#108).** Delete the screen, paste `src/Screens/scrQuickTx.pa.yaml`, then
  check the property values on cmpQtPick, the screen's cmpPicker instance. A paste can drop a
  component instance's custom property values, so re-type any that come in blank from the
  source. Then, in Preview (F5):
  1. Add a row, open its output pop-up, and press OK without changing the name or date.
  2. Change the row's label and its trade date. The output's name and date should follow the
     row.
  3. Open the pop-up again, type your own output name, and press OK. Change the row's label
     again: this time the output name must stay as you typed it.
  4. Save. The output in SharePoint should carry the row's final label and date, apart from
     the name you typed yourself.
  5. Pick a long date, such as 28 September 2026, in the trade-date column. It must not be
     clipped (#114).
- **A2 · The six dead components (#129).** Follow "The Studio clean-up" in
  `docs/notes/components.md`: delete the six, check that the Components list matches the ten in
  `src/Components/`, then save and reopen.
- **Optional:** the same PR (#135) also corrected comments in scrProject, scrIssueEdit,
  scrReports and scrTransactionEdit. Their formulas are unchanged, so re-pasting them only keeps
  Studio's comments in step with the repo.

## B. The live app: tests (epic #110)

Use Preview (F5) or the published app. Behaviour formulas don't run in the editor.

- **B1 · The completion gate and the delete confirms (#125).**
  1. On scrTaskEdit, add an output with **Approval Required** on and no Approval ID. Set the
     stage to **Completed** and save. It must be blocked with *"Output '<name>': Approval ID"*.
  2. Add the ID and save again. It must go through.
  3. Delete a throwaway task from scrTaskEdit, and a throwaway transaction from scrProject. The
     confirm dialog must open and state the output and issue counts. Cancel must change
     nothing. Confirm must delete the item and its outputs.
- **B2 · scrReports (#127).**
  1. The charts fill in rather than sitting on "Loading…".
  2. Pick a manager in **Scope**: every KPI and chart changes, and the "as at" time doesn't.
  3. Note whether the truncation banner ever appears. It only fires when a fetch reaches the
     data row limit, so "never seen" is a valid result.
  4. In a period with transactions in two currencies, the trend bar splits per currency.
- **B3 · A performance baseline (#128).** Open **Live Monitor** (Studio → Advanced tools →
  Open live monitor). Load scrHome, scrProjects, scrProject on a busy project, and scrReports. For each
  one, note the number of data calls, the largest payload, and roughly how long until the screen
  is usable.

## C. SharePoint: list settings

- **C1 · `project_phase` default (#119).** taskmaster_projects → List settings → `project_phase`
  → Default value **Not Started**.
- **C2 · Indexes and defaults (#120).** In List settings → **Indexed columns**:
  - Is `taskmaster_taskproduct.taskproduct_project_archived` indexed? What is its default? How
    many rows are blank? Back-fill any blanks to **No**.
  - Is `taskmaster_tasks.task_supporter` indexed?
- **C3 · Choice values (#121).** Copy the choice list from List settings for `project_coverage`,
  `client_type`, `client_coverage` and `product_assetclass`, keeping the exact casing.

## D. SharePoint: data

- **D1 · Start-date back-fill (#117).** Run the flow in `docs/notes/backfill-project-date-start.md`.
  Note how many rows it updated, and that a re-run finds 0 blanks.
- **D2 · Complete projects at 100% (#118).** Filter taskmaster_projects on
  `project_phase = Complete` and set `project_perc_completion` to **100**. For a few dozen rows,
  edit in grid view. For more, use the same flow shape as D1, changing only:
  - **Get items → Filter Query:** `project_phase eq 'Complete'`
  - **MERGE body:** `{ "project_perc_completion": 100 }`

  Then check: sort scrProjects by % descending, and every Complete project should sit at 100.
- **D3 · Missing projects (#123).** Do this after C1. Build two views and note the row count of
  each:
  - taskmaster_projects where `project_phase` is empty;
  - taskmaster_tasks where `task_project_archived` is empty.

  Back-fill any blanks: phase to **Not Started**, archived to **No**. Then check whether the
  missing projects now show in the app.
- **D4 · Requestor departments (#122).** Your own back-fill. Just report when it's done.

## E. Power Automate: the archival flow (#124)

Open the flow and answer two questions:
1. Does it select projects by phase, by the age of `project_date_complete`, or both?
2. Does it read the project again immediately before it writes **Archived** and the five
   `*_project_archived` flags?

If it doesn't re-read the project, add the check. Add **SharePoint → Get item** (the same project
ID), then **Condition:** `body('Get_item')?['project_phase']?['Value']` *is equal to*
`Complete`. Move the archive writes into the **If yes** branch and leave **If no** empty. A
project reopened partway through a run is then skipped rather than archived.

## Report-back block

Copy this, fill it in, and send it as one message:

```
A1 scrQuickTx paste + follow-the-row (1-4) + date width (5): works / doesn't — first error:
A2 six components deleted, app reopens clean: yes / no
B1 gate blocks / ID lets it through / task confirm / transaction confirm: _ / _ / _ / _
B2 charts fill / scope / banner seen? / two-currency split: _ / _ / _ / _
B3 scrHome / scrProjects / scrProject / scrReports — calls, largest payload, seconds:
C1 phase default set: yes / no
C2 taskproduct_project_archived indexed _, default _, blanks _ ; task_supporter indexed _
C3 project_coverage: … | client_type: … | client_coverage: … | product_assetclass: …
D1 rows updated _, re-run blanks _
D2 done, Complete projects all at 100: yes / no
D3 blank phase _ , blank task archived _ , missing projects now visible: yes / no
D4 requestor departments back-filled: yes / no
E  selects on _ ; re-reads before writing: yes / no / added
```
