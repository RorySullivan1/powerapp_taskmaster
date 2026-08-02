# MEMORY INDEX  ·  keep ≤ ~80 lines

## State            (rewrite in place — current truth only, ≤ ~10 lines)
- **Phase:** `.claude/` asset set built (the "workshop"). **No** Power Fx or `.pa.yaml` authored
  yet — that's the next phase, and it goes through the air gap (see `studio-transfer`).
- **Backend:** 8 `tm*` SharePoint lists, provisioned **manually** → internal names are
  ⟨capture⟩ placeholders in `context/schema.md` until columns exist; snapshot must hold TRUE names.
- **Reporting:** Power BI embedded, **licence-gated** — native nav is primary, empty state for
  unlicensed. Tickets are **full ticket-level, primary store** → delegation/indexing critical.
- **Air gap:** Studio (work machine) ↔ repo (personal machine) via **manual clipboard only**.
  When unsure the repo mirrors the live app → stop, ask for a fresh pull (`/pull-reconcile`).
- **Template:** PM-tracker (SQL-backed) is the **screen/nav blueprint** only — rebuild on our
  SharePoint schema (`docs/screen-map.md`). Pattern candidates in `docs/powerapp-patterns-distillation.md`.

## Decisions        (append-only; supersede, never delete)
- [2026-07-26] Project is parent; Task/Ticket/Issue are peers (not variants) — why: distinct kinds — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-07-26] Three lists, not one discriminated list — why: a discriminator nulls ⅔ of columns + misleads Owner/PercentComplete — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-07-26] Only Tasks roll up into completion; Tickets/Issues surface alongside — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-07-26] No snapshot/metrics list — why: existed only for Sum-delegation; Power BI imports whole; do NOT reintroduce — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-07-26] Products/indices are stubs; ISIN is the egress contract, sync one-way in — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-07-26] Notional is the only value column (bias: favours large low-margin trades = issuance volume) — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-07-26] Not a book of record — internal KPI only, no retention obligation — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-07-26] Q1 → FULL ticket-level rows as primary store — cost: max delegation/threshold exposure, indexing mandatory — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-07-26] Q2 → NOT everyone Power BI-licensed → native nav primary + empty state; dashboard can't carry nav — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-07-26] Q11 → MANUAL (SharePoint UI) provisioning — cost: _x0020_ name risk + no term-store sync route — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-07-26] Adopt list approved "as recommended"; column-token validator hook proposed not built — sessions/2026-07-26-1726-repo-init-decisions.md
- [2026-08-02] PM-tracker template = blueprint not plumbing (SQL-backed; reuse screens/nav, NOT its data layer/SQL-view aggregation) — sessions/2026-08-02-1702-external-repo-review.md

## Threads          (open items; remove when closed)
- Open questions Q3–Q10, Q12, Q13 + Q2b (PBI workspace/refresh/embed) + Q5 (index master?) + tmIndices taxonomy source → `.claude/context/open-questions.md`
- Propose upstream to claudeBrain: `studio-transfer` skill + `pre-paste-review` agent (both general); flag PnP/CSOM gap.
- Decide whether to build the column-token validator write-time hook.
- Author dual-use skills C1 SVG-in-PowerApps (native fallback visuals for unlicensed PBI) + C2 editable-table (tickets tab)? → `docs/powerapp-patterns-distillation.md`. Awaiting go.
- Reconsider Q11 provisioning vs the flow-as-list-provisioner pattern (repeatable clean internal names).

## Log              (append-only pointers)
- 2026-07-26 1726 | repo init: adopt + author .claude asset set; foundational decisions | sessions/2026-07-26-1726-repo-init-decisions.md
- 2026-08-02 1702 | review aprildunnam + PM-tracker; distillation + template decision + screen map | sessions/2026-08-02-1702-external-repo-review.md
