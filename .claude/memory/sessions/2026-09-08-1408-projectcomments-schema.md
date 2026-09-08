# 2026-09-08 14:08 · projectcomments-schema

**Goal:** Review epic #60 and land the schema half of #61 (taskmaster_projectcomments)

## What happened
- Read epic #60 and all five sub-issues (#61–#65) and checked their claims against the
  repo rather than trusting them. All three load-bearing ones hold: the Number FK, the
  phase-derivation exclusion (`scrProject.pa.yaml:142-155` sums `nT + nX + nI`), and the
  per-arm error globals in the delete cascade (`scrProject.pa.yaml:726-756`).
- Landed #61's REPO half: the five-column `taskmaster_projectcomments` block in
  `schema/schema.yaml`, inserted after `taskmaster_issues`, `provisioned: pending`,
  `join_cost: 1`.
- Verified the guard hook by feeding `pre_write_column_guard.py` a synthetic Edit payload:
  it accepts `projectcomment_date` and rejects `projectcomment_bogus` with
  "did you mean projectcomment_author?". That is #61's first Done-when, tested rather
  than assumed. Validator 22/22.
- Updated `.claude/context/schema.md` (list table, relationship diagram, the Number-FK
  note, the fourth archived flag) and `.claude/context/app-structure.md` (the "three peers"
  bullet is now three-plus-comments, with the not-a-peer-for-derivation caveat).
- Committed and pushed to `claude/powerapp-repo-init-xymvlm` (f2cad7f).

## Gotchas & dead ends
- **The epic under-states its own best argument.** #60 justifies the Number FK as "zero
  joins". The real reason is delegation: `<lookup>.Id = <id>` does NOT delegate, which is
  why the three existing folds go over the named formulas — a raw-list fetch came back
  EMPTY for recent projects because the archived backlog filled the page first. The Number
  FK is what lets the comments fold read the raw list safely. Written into the schema
  comments, the brief and the ledger so nobody "fixes" the inconsistency later.
- `.claude/context/app-structure.md` is a stale DESIGN brief, not a record of the built app
  (it still says "No Lookup columns", "tmLookups", "three tabs"). Edited minimally — a
  rewrite is a separate job and was not this one.
- `mcp__github__issue_read get_sub_issues` on #60 returns ~66k chars and overflows the tool
  limit. Parse the persisted JSON with python and print one issue at a time.
- `projectcomment_author` is indexed but no v1 query filters on it (the gallery compares it
  locally). Kept as filed — harmless on a fresh list — and noted in the column desc.

## State at end
- #61 repo half DONE. **The epic is blocked on the user in Studio** and cannot move here:
  create the list with those exact internal names (they freeze at creation), index the four
  marked columns, rich text OFF on the Note, then ADD IT AS A DATA SOURCE BY HAND — a screen
  paste never adds one.
- Nothing authored on #62/#63/#64 — the guard hook would allow it now, but authoring against
  a list that does not exist risks a paste that fails on the first Patch.

## The 2026-08-12 system-columns finding was FALSE (settled same session)
- The user pushed back on the five-column design: SharePoint generates author and date
  already. Checked it rather than defending the ledger. MS Learn documents no such
  connector limitation, and `the_app_caches_the_column_set` in schema.yaml describes a
  mechanism that produces exactly the reported symptom.
- User tested `First(taskmaster_issues).'Created By'.DisplayName` in Studio: **both
  `Created` and `'Created By'` resolve.** The 2026-08-12 entry generalised one failed
  reference into a schema rule and it stood for four weeks.
- `taskmaster_projectcomments` re-cut to THREE columns before provisioning — the last
  moment that was free. #63's Patch loses the expanded-user Person shape entirely.
- `issue_owner` / `issue_date_open` STAY: live, populated, written by three screens.
  Rule going forward is in the maintainer manual — a NEW list prefers the system columns,
  an existing one keeps what it has.
- Corrected in `schema.yaml` (x3), `docs/manuals/maintainer/04-schema-changes.md`,
  `.claude/context/schema.md`, and the ledger (refuted in place, per convention).

## Open threads
- **GitHub #60/#61/#62/#63 still describe the five-column design** and are the spec an
  implementer would follow. Not yet edited — outward-facing, so ask first.
- **Is `Created` offered in that list's index settings?** Load-bearing: without an index the
  newest-first Sort stops delegating past 5,000 rows, and it fails silently at scale rather
  than loudly on day one. Fallback if it cannot be indexed or the Sort warns: an app-stamped
  DateTime, i.e. the column just deleted.
- **Row height in `galCmt` is the one unresolved design call.** #62 punts to "fixed template,
  ~3 lines, clipped". A Note column either truncates or needs a flexible-height gallery
  variant, and no such variant is grounded anywhere in this app or in `studio-enums.json`.
  Settle it before authoring, so #62/#63/#64 can go out as ONE scrProject paste.
- #65 is external (Power Automate, work machine) and unverifiable from here.
