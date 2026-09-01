# 7 · When something looks wrong

## A list seems to be missing rows

The app reads a bounded number of rows per query. Screens that aggregate say so when they hit
that ceiling — see [the row-limit banner](#the-row-limit-banner). A browse list that looks short
is more often a filter: check **Show completed**, **Only show my projects**, and the coverage
filter on [Projects](03-projects.md#finding-a-project).

Also remember that **search matches from the start of a name**. Searching `review` will not find
*Q3 review*.

## The row-limit banner

On [Reports](06-reports.md), a banner reading *"Hit the data row limit on: … — every figure below
is a FLOOR, not a total"* means one of the fetches ran out of room before it ran out of data.
Every figure on the screen is then a minimum, not a total.

Nothing you can do in the app fixes it. Report it — it is a signal that the data has outgrown
the current settings, and it needs the app's maintainer.

## Derived figures look stale

Two figures are computed by the app rather than typed by anyone:

| Figure | Comes from | Moves when |
|---|---|---|
| A project's **completion ring** | The stages of its tasks | A task's stage changes **in the app** |
| A task's **health** | Its open issues, plus its target date | An issue against it is raised, re-typed or closed **in the app**; and at midnight, when an overdue task turns red |

Both are recomputed by the app when work changes **through the app**. A row edited directly in
SharePoint, or loaded by a bulk import, leaves them stale until the next in-app change to that
project or task — opening and saving the affected task or issue is enough to repair it.

## A save failed

The form stays open with your entries intact and tells you what went wrong. Common causes:

- **A required field is empty.** Look for the **"Still required:"** line.
- **A duplicate product ID.** See [reference data](05-reference-data.md#product-ids-must-be-unique).
- **A transient SharePoint error.** Press Save again.

If a save keeps failing on the same record, note the message and report it — the message is the
useful part.

## A number here disagrees with a number there

Check what each one is counting before assuming one is wrong:

- **Home** counts your work, right now, with no period.
- **Reports** counts the desk's work over the chosen period and scope, as at the last fetch.
- **A project screen** counts that project only.

Reports also excludes archived work and, on live-project figures, completed projects.

## Something is genuinely broken

Report it with: the **screen**, what you **did**, what you **expected**, what **happened**, and
the exact text of any message. The app cannot be diagnosed from "it didn't work" — the message
and the sequence are what make a fix possible.
