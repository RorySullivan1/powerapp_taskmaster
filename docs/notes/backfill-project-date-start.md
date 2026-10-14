# One-off back-fill: `project_date_start` from `Created`

**Why:** `project_date_start` was optional and was never defaulted, so many projects have no start
date. scrReports' "projects started" trend counts by this column, so those projects are missing
from it. From now on the app fills the date itself: scrProject stamps it the first time work is
seen to start (see `schema/schema.yaml`). That stamp only fires when someone opens a project. This
flow fixes the existing blanks once, by copying each project's **Created** date into
`project_date_start` wherever it's empty.

It never touches a project that already has a start date. Run it **once**, after scrProject has
been pasted, so the two can't race.

## Before you start: check two names

The REST call needs SharePoint's **internal** names, which this repo has never confirmed for these
two:

1. **The column.** Open the list in SharePoint and go to **List settings**. Click the start date
   column and read the end of the page URL: `...&Field=<InternalName>`. If it says
   `project_date_start`, use that. If it says anything else, use what it says everywhere
   `project_date_start` appears below.
2. **The list.** This flow uses the list's **display title** (`taskmaster_projects`). If the title
   in SharePoint differs, use that instead.

## The flow (Power Automate, instant / manually triggered)

1. **Trigger:** *Manually trigger a flow*.
2. **SharePoint → Get items**
   - **Site Address:** the Taskmaster site.
   - **List Name:** `taskmaster_projects`.
   - **Filter Query:** `project_date_start eq null`
   - **Top Count:** `5000`.
   - Under the action's **Settings**, turn **Pagination** on, with **Threshold** `5000`.
   - The list is under the 5,000-item view threshold today, so filtering on this unindexed column
     works. Past 5,000 it would need an index on `project_date_start` first.
3. **Apply to each**, over the `value` from *Get items*, containing:
   **SharePoint → Send an HTTP request to SharePoint**
   - **Method:** `POST`
   - **Uri:** `_api/web/lists/getbytitle('taskmaster_projects')/items(@{items('Apply_to_each')?['ID']})`
   - **Headers:**

     | Key | Value |
     |---|---|
     | `Accept` | `application/json;odata=nometadata` |
     | `Content-Type` | `application/json;odata=nometadata` |
     | `IF-MATCH` | `*` |
     | `X-HTTP-Method` | `MERGE` |

   - **Body:** `{ "project_date_start": "@{items('Apply_to_each')?['Created']}" }`

   MERGE writes only the one column named in the body. The standard *Update item* action would make
   you re-supply every required column, including the Person claims.

## Check it worked

- **Run the flow once.** Every iteration should return **204 No Content**.
- **Re-run *Get items* on its own** (or filter the list view on an empty start date): it should
  return **0 items**.
- **Spot-check a few projects:** each start date should equal its Created date, and projects that
  already had a start date should be unchanged.
- **Then tell the next session it ran.** It goes into `.claude/memory/INDEX.md`, and the "need a
  one-off back-fill" wording in `schema/schema.yaml` gets updated to say it has been done.
