# EQD Taskmaster — user manual

For people who use the app. No Power Apps knowledge assumed, and nothing here asks you to open
Studio or SharePoint.

## Contents

1. [Getting started](01-getting-started.md) — what the app is, how to move around it, the
   conventions every screen shares
2. [Home](02-home.md) — your personal dashboard
3. [Projects](03-projects.md) — finding a project, and what a project screen shows
4. [Tasks, transactions and issues](04-tasks-transactions-issues.md) — the three kinds of work
   under a project
5. [Reference data](05-reference-data.md) — clients and products
6. [Reports](06-reports.md) — the desk-level charts, and how to read them honestly
7. [When something looks wrong](07-limits-and-troubleshooting.md) — row limits, stale figures,
   saves that fail

## What this app is

A work-management app for the EQD desk. **Projects** are the parent; each one carries **tasks**
(the work), **transactions** (the trades) and **issues** (what is going wrong). On top of that
sit a personal dashboard and a desk-wide reporting screen.

Everything you enter is stored in SharePoint lists. Nothing is stored in the app itself, so
what you save is immediately what a colleague sees when they next load the screen.

## Two things worth knowing up front

- **The app never shows a mixed-currency total.** Transactions are recorded in their native
  currency and the app does not convert. See [transactions](04-tasks-transactions-issues.md#transactions).
- **Some figures are computed by the app, not typed by anyone** — a project's completion
  percentage and a task's health. If they look wrong, the fix is usually to correct the
  underlying tasks or issues, not to hunt for a field to edit. See
  [derived figures](07-limits-and-troubleshooting.md#derived-figures-look-stale).
