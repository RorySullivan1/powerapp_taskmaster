# 2 · Home

Your personal dashboard, and the screen the app opens on. Everything on it is filtered to **you**
— your projects, your tasks, your issues. Nothing here is a desk-wide figure; that is
[Reports](06-reports.md).

## The four cards

Across the top sit read-only metric cards — the counts of what you lead and own. They are
summaries, not buttons to fill in: the numbers move when the underlying work moves.

## The three lists

| List | What it holds |
|---|---|
| **Projects I lead** | Live projects where you are the project manager |
| **Open tasks I lead** | Tasks still open that you lead, with **days to due** |
| **Open issues I own** | Issues assigned to you and still open |

There is also **Open issues on my projects** — issues raised against projects you manage, whoever
owns them. That one exists so a project manager sees trouble on their patch even when the issue
belongs to someone else.

Selecting a row opens the thing it names. Where a list is empty you get a plain sentence saying
so ("Nothing open — no live project has you as its manager"), not a blank panel.

## The charts

A band of small SVG charts sits below the cards:

- **Tasks by stage** — where your open tasks sit in the lifecycle
- **Open tasks by health** — the red / amber / green split
- **Issues by impact** — how severe your open issues are

Health is **derived, not typed** — see [derived figures](07-limits-and-troubleshooting.md#derived-figures-look-stale).

## Creating from here

**＋ New project** starts a project with you as its manager. Everything else — tasks,
transactions, issues — is created from the project it belongs to, not from Home.

## Why Home may differ from Reports

Home counts *your* work. Reports counts the desk's, over a chosen period and scope. Two
different questions; expect two different numbers.
