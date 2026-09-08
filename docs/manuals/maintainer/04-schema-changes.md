# 4 · Changing the schema

`schema/schema.yaml` is the **golden source** for the SharePoint backend. The direction is
always:

```
edit schema.yaml  →  apply it in SharePoint  →  flip provisioned:  →  bump meta.version
```

`schema/README.md` holds the file's own rules; `.claude/context/schema.md` holds the model's
shape, its delegation and join costs, and the consequences that are still open. Neither repeats
the columns — `schema.yaml` is the only place those live.

## The rules that bite

- **`name:` IS the internal name.** SharePoint freezes it at creation; renaming later changes
  only the display label. Create the column with exactly this name.
- **Type changes after creation are destructive.** A Managed Metadata column cannot be converted
  in place at all — it is delete-and-recreate, and a recreated column comes back empty. Settle
  the `open_recommendations` **before** provisioning, not after.
- **Never invent a column.** Every field token in authored Power Fx must resolve to a `name:`
  here. This is enforced, not advisory — see [chapter 5](05-validation-and-enforcement.md).
- **`provisioned:` tracks reality per list**, and it is the schema's analogue of the paste log.
  Do not flip it on intent.
- **The system columns ARE app-readable** (confirmed in Studio 2026-09-08). `Created`,
  `Modified`, `Created By`, `Modified By` exist on every list and resolve from Power Fx —
  quote the two-word names. Prefer them over an app-stamped provenance column on a NEW list.
  Two caveats: they are **read-only**, so nothing can be backdated or re-attributed; and they
  are **not indexed by default**, so a sort or filter on `Created` needs an index like any
  other column. Older lists carry app-stamped equivalents (`issue_owner`, `issue_date_open`)
  and keep them — swapping would strand the provenance already in those rows.

## After a schema change

Anything already authored against the old shape needs re-auditing — run the `pre-paste-review`
agent over the screens that touch the changed list. And check the
[stay-in-step table](03-making-a-change.md#things-that-must-stay-in-step): a change to
`project_phase`'s values or to the stage weights has an app-side half.

## Rollups are app-written

`project_perc_completion` and the stored half of `task_health` are computed and patched **by the
app**, at the points documented in `schema.yaml`'s `rollups:` block. Two consequences:

1. A row edited directly in SharePoint, or bulk-imported, leaves them stale until the next
   in-app change to that project or task.
2. The live half of `task_health` (overdue and not complete → Red) is **deliberately not
   stored**, because it changes with no write — a task turns red at midnight. Every reader has
   to fold it in at read time. A reader that shows `task_status` raw will under-report Red.
