# Archival flow: add the output log (`taskmaster_output`)

**Issue #101 (epic #93).** The archival flow lives outside this repo, in Power Automate. When it
archives a project it sets `*_project_archived = true` on that project's tasks, transactions,
issues and comments. This note adds the fifth child list, **`taskmaster_output`**, to the same flow.

**Why it matters:**
- `LiveOutputs` in App.Formulas is `Filter( taskmaster_output, output_project_archived = false )`.
- scrReports counts outputs through that formula. So an archived project's outputs keep showing
  in the reports until this flag is set.
- scrProject reads the raw list, so a project you open directly still lists its outputs,
  archived or not.

## The step to add

Put it next to the step that flags the project's comments (`taskmaster_projectcomments`). Use
the same project ID variable that the other child steps use.

1. **SharePoint → Get items**
   - **Site Address:** the Taskmaster site.
   - **List Name:** `taskmaster_output`. The name is singular.
   - **Filter Query:** `output_project_id eq @{<the project ID>}`. This column is indexed, so the
     filter works at any list size.
   - **Top Count:** `5000`.
   - In the action's **Settings**, turn **Pagination** on with **Threshold** `5000`. Without it,
     *Get items* returns only the first 100 rows.
2. **Apply to each**, over the `value` from *Get items*, containing:
   **SharePoint → Send an HTTP request to SharePoint**
   - **Method:** `POST`
   - **Uri:** `_api/web/lists/getbytitle('taskmaster_output')/items(@{items('Apply_to_each')?['ID']})`
     (use the loop's real name if it isn't `Apply_to_each`)
   - **Headers:**

     | Key | Value |
     |---|---|
     | `Accept` | `application/json;odata=nometadata` |
     | `Content-Type` | `application/json;odata=nometadata` |
     | `IF-MATCH` | `*` |
     | `X-HTTP-Method` | `MERGE` |

   - **Body:** `{ "output_project_archived": true }`

**Use MERGE, not *Update item*.** `taskmaster_output` has six required columns: name, project
id, format, audience, language and branding. *Update item* makes you re-supply every one of
them on every row, and the Choice columns would need their exact values. A MERGE writes only
the one column named in the body.

**If the flow can also un-archive a project,** add the same step to that branch with
`{ "output_project_archived": false }`. Otherwise a restored project's outputs stay out of
the reports.

**Check the internal name first.** Open List settings and click the column. If the URL doesn't
end in `Field=output_project_archived`, use the name it shows in the body instead.

## Check it worked (the #101 acceptance)

1. Log two outputs on a test project. Use scrProject's Outputs panel or a task.
2. Archive the project with the flow. Every MERGE should return **204 No Content**.
3. In SharePoint, both output rows show `output_project_archived` = **Yes**.
4. In the app:
   - On scrReports, the outputs pies drop by two after **Refresh**.
   - Opened directly, scrProject still lists both outputs.
