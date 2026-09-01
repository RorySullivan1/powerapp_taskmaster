# 6 · Reports

Desk-wide analytics, drawn natively in the app. There is no Power BI licence involved and no
external report to open — every chart here is drawn by the app itself.

## The two controls

| Control | What it does |
|---|---|
| **Period** — `1W` / `1M` / `1QTR` | The window every dated figure is measured over. Defaults to `1QTR`. Changing it **refetches** from SharePoint. |
| **Scope** | Narrows to one project manager's projects. Leave it empty for the whole desk. Changing it re-filters what is already loaded — it does not refetch. |

Beside them is a stamp reading **"as at …"** with the time of the last fetch — or *"Not loaded"*
before the first one, or *"Loading…"* during it.

**The screen does not refresh itself.** Figures are those of the last fetch. Change the period
(or return to the screen) to pull fresh data.

## What is on it

Headline counts across the top — open tasks, open issues and transactions, on live projects
across the desk — then chart bands:

- **Projects by status**, and **projects started, completed, net open** over the window
- **Open tasks due, today and the next two weeks**
- **Open tasks by health**, **by region**, **by activity family**, **by output audience** and
  **by requestor**
- **Transactions by product type**
- **Project leads by transaction count** (top 6)

Selecting a person opens a panel over the screen listing their tasks with due date, health and
when each was opened. Close it to return — you have not left the screen, so nothing is refetched.

## Reading it honestly

The line under the charts states the window, that archived work is excluded, whether any fetch
hit the row limit, and that notional is per currency only. Read it before quoting a number.

Three limits are structural, not bugs:

1. **No history.** Every trend on this screen is built from *dated events* — when a transaction
   was booked, a task completed, a project started or finished. Nothing records what a status or
   a completion percentage was last month, so "completion over time" is not something this
   screen can show.
2. **No blended notional.** Notional appears per currency, never summed across currencies.
   See [the currency rule](04-tasks-transactions-issues.md#the-currency-rule).
3. **A row ceiling.** Totals are computed in the app over rows it fetched, and there is a limit
   on how many it can fetch. When a fetch hits that ceiling a banner appears:

   > Hit the data row limit on: … — every figure below is a **FLOOR, not a total**.

   Treat every number on the screen as a minimum while that banner is showing, and tell whoever
   maintains the app ([chapter 7](07-limits-and-troubleshooting.md#the-row-limit-banner)).

## Reports vs Home

Reports is the desk over a period. [Home](02-home.md) is you, right now, with no period at all.
The two are answering different questions and will not agree.
