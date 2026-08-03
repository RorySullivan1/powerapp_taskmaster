# MEMORY INDEX  ·  keep ≤ ~80 lines

## State            (rewrite in place — current truth only, ≤ ~10 lines)
- **Phase:** Phase-1 **core shell + component kit AUTHORED** (first Power Fx in the repo):
  `App.Formulas` (theme + `NavMenu` T6 + `gUserEmail`) in `src/patches/`; 5 screen shells
  `scr{Home,Reports,Projects,Reference,Admin}` + **10 components** in `src/authored/components/`
  (`cmpUiKit` fns, `cmpStatusPill`, `cmpChoicePill`, `cmpStatusCard`, `cmpSelection`,
  `cmpEditableGrid`, `cmpSectionHeader`, `cmpConfirmDialog`, `cmpToast`, `cmpKpiRing` SVG).
  Data-independent (no `tm*` tokens). All audited → **NOT landed** (paste-log empty).
  See `_SHELL-NOTES.md` + `components/_COMPONENTS-NOTES.md`.
- **Phase-2 composition done (static data):** `scrHome`/`scrReports`/`scrProjects` now instantiate
  6 components (cards+ring+toast+confirm on Home, 3 KPI rings as the Q2 fallback on Reports,
  section-header+selection on Projects). Instance dialect = `Control: CanvasComponent` +
  `ComponentName:` + `Properties:`, no `Children:`. Live queries left as `TODO(Phase-2-data)`.
  Real data binding still blocked on provisioning (⟨capture⟩ names) + a pull. Merged PR#2/3/4.
- **Dialect (learned):** paste target is the **modern structured schema** (`Screens:`/`Children:`/
  `Control: Type@version`, positional z-order, no ZIndex) — NOT `pac canvas unpack`'s retired
  inline `As type:` format. Files converted with real tokens from the example export.
- **Backend:** 8 `tm*` SharePoint lists, provisioned **manually** → internal names are
  ⟨capture⟩ placeholders in `context/schema.md` until columns exist; snapshot must hold TRUE names.
- **Reporting:** Power BI embedded, **licence-gated** — native nav is primary, empty state for
  unlicensed. Tickets are **full ticket-level, primary store** → delegation/indexing critical.
- **Air gap is ONE-WAY (corrected 2026-08-02):** repo → clipboard → Studio only. The work
  machine's output CANNOT come back into the repo/Claude's view — the ONLY return signal is the
  user's binary "it works / it doesn't." So: **no pulls, no returned code-view samples, no
  round-trip.** `studio/pulled/`, `/pull-reconcile`, and "repo mirrors Studio / Studio is source
  of truth" are premised on a return channel that does NOT exist → treat the **repo as the
  authoritative authored source**, Studio as a downstream apply-target (Studio-only edits are
  invisible drift, lost forever). Consequences: (1) unknown tokens (gallery `Variant`,
  `HtmlViewer@2.1.0`, `Classic/Timer@2.1.0`) must be resolved by ME from PUBLIC sources (MS Learn,
  PowerApps-Tooling repo, public .msapp) — they can't be confirmed by a return sample; (2) every
  manual paste is costly and returns only works/doesn't → **maximise first-try correctness; prefer
  grounded constructs, ship safe FALLBACKS for anything unverifiable** (e.g. button nav vs the
  gallery). The `studio-transfer` skill + CLAUDE.md still describe a two-way gap — they need fixing.
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
- [2026-08-02] Authored dual-use skills `power-apps-svg` + `power-apps-editable-table` (SVG grounded on MS Learn data-URI/EncodeUrl) — sessions/2026-08-02-1702-external-repo-review.md
- [2026-08-02] Q11-bis: RECOMMEND flow-as-list-provisioner over manual UI IF Power Automate available (Q12) — repeatable, kills _x0020_ risk; not yet chosen — .claude/context/open-questions.md
- [2026-08-02] Phase-1 nav built as per-screen gallery bound to `NavMenu`, NOT a reusable component — why: components are hardest to paste across the air gap; NavMenu already gives T6's DRY intent. Component upgrade deferred until channel proven — sessions/2026-08-02-1411-phase1-core-shell.md
- [2026-08-02] Paste/code-view dialect = modern STRUCTURED schema (Control:Type@version, positional z-order, no ZIndex); `pac canvas unpack`'s inline `As type:` is the RETIRED format — do not author to it — sessions/2026-08-02-1411-phase1-core-shell.md
- [2026-08-02] Components authored in v3.0 `.pa.yaml` `ComponentDefinitions`; display pills/chips delivered as `cmpUiKit` OutputFunction HTML-builders (canvas components CAN'T sit in a gallery), interactive chip stays a component; components inline Theme (can't read app globals) — sessions/2026-08-02-1411-phase1-core-shell.md
- [2026-08-02] **Air gap is ONE-WAY** (user-corrected): repo→Studio only; sole return signal is binary "works/doesn't." Kills pull/round-trip/pull-reconcile; repo is authoritative source not mirror. → resolve unknown tokens from PUBLIC sources; ship safe fallbacks; maximise first-try paste success — sessions/2026-08-02-1411-phase1-core-shell.md
- [2026-08-02] SCHEMA: snake_case `taskmaster_*`/`asset_approval` is canonical, supersedes the PascalCase tm* model (user-confirmed) — schema/incoming-lists.md
- [2026-08-02] Schema promoted to canonical (7 lists, snake_case). Model uses Lookup + Managed Metadata + multi-Person throughout — accepted as the user's design; consequences documented rather than relitigated — .claude/context/schema.md
- [2026-08-02] task_status split into TWO Choice cols: `task_status`=health (Green/Amber/Red) + `task_stage`=lifecycle (values TBD); `task_output_format`+`task_client_stage` MM→Choice — why: Choice costs no join & sorts; tasks 11→8 joins, J1 resolved — .claude/context/schema.md
- [2026-08-02] **`schema/schema.yaml` is the GOLDEN SOURCE** — repo DEFINES the SharePoint lists, SharePoint applies them (`provisioned:` per list). Inverts the old 'capture true names from SP' model; mirrors the one-way gap. context/schema.md keeps shape+costs only, never columns (DRY) — schema/README.md
- [2026-08-02] `task_stage` values fixed: Not Started, Planning, Drafting, Under Review, Finalizing, Complete, Archived — unblocks the delegable Or-of-equals open-task filter — schema/schema.yaml
- [2026-08-03] Schema recs C4/C5/C8 APPLIED: `task_date_start` Calculated→DateTime(indexed); added `transaction_notional_usd` (only cross-currency-safe column); renamed `Issue_owner`→`issue_owner`(Person), `product_UID`→`product_uid`. schema.yaml v1.2.0 — schema/schema.yaml
- [2026-08-03] C1 RESOLVED: multi-person → single `task_supporter`/`project_supporter` (1 extra person, indexed). 'Mine' now fully delegable via `lead.Email = me || supporter.Email = me`; join cost unchanged (tasks 8) — schema/schema.yaml
- [2026-08-03] C3 RESOLVED: `project_perc_completion` = weighted mean of child task-stage weights (0/10/35/60/85/100, Archived excluded), WRITER = **app-side** — app patches parent on task-stage change. `StageWeights` named formula + write-back snippet in `src/patches/App.Formulas.pa.fx`. Cost: stale if SP edited directly — schema/schema.yaml
- [2026-08-03] C6 BY DESIGN: three region columns are intentional — approval_region is broad-stroke, project/client_region are granular, never used together. No conformed dimension; separate PBI dimensions; do NOT 'fix' — .claude/context/schema.md
- [2026-08-03] Phase-2 DATA bound on scrHome/scrProjects/scrReports: one delegable Filter per screen → local aggregation (CountRows/Average never delegate). galProjects uses If-of-independent-Filters so each branch folds. Reports rings deliberately SCOPED (my tasks / active projects) — org-wide counts can't be exact in-app. Trends zeroed, not faked — src/authored/
- [2026-08-03] Pre-paste audit → DO-NOT-PASTE; 6 real defects fixed: `Sort(If(..))` does NOT fold (Sort moved INSIDE each branch); unscoped colActiveProjects → scoped to my projects; redundant+risky IsBlank search guard dropped; Navigate-to-self doesn't re-fire OnVisible (refresh now inlines the collects); PASTE ORDER now App.Formulas BEFORE data screens (they need StageWeights); cmpConfirmDialog custom prop `Visible` collided with the base prop → renamed `IsOpen` — src/authored/
- [2026-08-03] C9 raised: task_stage/task_status/issue_status are OPTIONAL → blank rows drop out of every enumerated Choice filter (silent undercount). Recommend required-with-default. UNDECIDED — schema/schema.yaml

## Threads          (open items; remove when closed)
- Open questions Q3–Q10, Q12, Q13 + Q2b (PBI workspace/refresh/embed) + Q5 (index master?) + tmIndices taxonomy source → `.claude/context/open-questions.md`
- Propose upstream to claudeBrain: `studio-transfer` + `pre-paste-review` + the new `power-apps-svg` / `power-apps-editable-table` skills (all general); flag PnP/CSOM gap.
- Decide whether to build the column-token validator write-time hook.
- **Q11-bis decision pending:** adopt flow-as-provisioner? Blocks on Q12 (Power Automate available?). If yes, supersede the manual-UI Q11 decision. → `.claude/context/open-questions.md`.
- **Paste order (no round-trip — one-way):** in Studio create screens `scr{Home,Reports,Projects,
  Reference,Admin}`; recreate the components in the component editor; paste screen control-groups
  (one/time) → `App.Formulas` LAST → set Data row limit 2000. Gallery `Variant` is now `Vertical`
  (best-grounded); button-nav is the fallback if a screen paste fails. Need tablet-vs-phone target.
- **Licence-gate signal (user decision):** `gHasPowerBiLicence` hardcoded `false`; no in-app Power
  BI API — choose a source (tmLookups flag / Entra group) + hide-vs-grey for the Reports nav entry.
- **Component transfer:** recreate the 10 components from the contract tables in the Studio
  component editor / a library (components are NOT code-view-pasted). Their control tokens
  (`HtmlViewer`, `Classic/Timer`, gallery `Variant`) are spec-only — can't fail a paste. →
  `components/_COMPONENTS-NOTES.md`.
- **Follow-up:** run `/reindex` to regenerate CATALOG (pull-reconcile now deprecated). Minor
  incidental two-way mentions left in `build-hooks.py`/`claudebrain-inventory.md`.
- **Phase-2 component composition DONE for 6/10** (static data on Home/Reports/Projects).
  Remaining 4 are gallery/data-bound → compose when data galleries wired: `cmpUiKit` pills +
  `cmpStatusPill`/`cmpChoicePill` in row templates, `cmpEditableGrid` on the Tickets tab.
- **Phase-2 DATA bound + audited (2026-08-03)**; blockers fixed, but still DO-NOT-PASTE on the PREREQUISITE: nothing is provisioned and paste-log is empty. Was blocked on provisioning (true internal names — `schema.md`
  ⟨capture⟩) + a confirmed pull. Every live query is a `TODO(Phase-2-data)` in the screens.

- **Schema intake COMPLETE (7 lists) and promoted to `.claude/context/schema.md`.** Outstanding: `asset_library` schema never supplied (blocks `task_output_asset`).
- **Schema open_recommendations (now EDITABLE — repo is golden source): C1** multi-person no delegable filter;  Settle BEFORE provisioning — names/types freeze at creation. → `schema/schema.yaml` open_recommendations
- **Schema consequences needing a call** (→ `context/schema.md` §Consequences): **C1** multi-person cols have no delegable filter; **C4** `task_date_start` is Calculated (nothing delegates); **C5** no USD-normalised notional; **C3** no writer for `project_perc_completion`; **C6** region modelled 3 ways; **C8** casing anomalies before provisioning.

- **C9 pending:** make the three optional Choice cols required-with-default, or accept the undercount. → `schema/schema.yaml`

## Log              (append-only pointers)
- 2026-07-26 1726 | repo init: adopt + author .claude asset set; foundational decisions | sessions/2026-07-26-1726-repo-init-decisions.md
- 2026-08-02 1702 | review aprildunnam + PM-tracker; distillation + template decision + screen map | sessions/2026-08-02-1702-external-repo-review.md
- 2026-08-02 1411 | Phase-1 core shell authored (theme + NavMenu + 5 screens); pre-paste audit; dialect corrected to modern structured schema | sessions/2026-08-02-1411-phase1-core-shell.md
- 2026-08-02 1520 | 6 reusable components authored (v3.0 ComponentDefinitions); audit found+fixed cmpSelection double-fire + Output-reads-var | sessions/2026-08-02-1411-phase1-core-shell.md
- 2026-08-02 1545 | merged PR#2 shell + PR#3 components to main; +4 extra components (cmpSectionHeader/ConfirmDialog/Toast/KpiRing SVG), audit PASTE-clean | sessions/2026-08-02-1411-phase1-core-shell.md
- 2026-08-02 1610 | merged PR#4; Phase-2 composition — component instances (static data) on Home/Reports/Projects; instance dialect grounded; audit clean (only known gates) | sessions/2026-08-02-1411-phase1-core-shell.md
