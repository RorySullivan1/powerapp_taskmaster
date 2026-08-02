# MEMORY INDEX  ·  keep ≤ ~80 lines

## State            (rewrite in place — current truth only, ≤ ~10 lines)
- **Phase:** Phase-1 **core shell + component kit AUTHORED** (first Power Fx in the repo):
  `App.Formulas` (theme + `NavMenu` T6 + `gUserEmail`) in `src/patches/`; 5 screen shells
  `scr{Home,Reports,Projects,Reference,Admin}` + **6 components** in `src/authored/components/`
  (`cmpUiKit` HTML-builder fns, `cmpStatusPill`, `cmpChoicePill`, `cmpStatusCard`, `cmpSelection`,
  `cmpEditableGrid`). Data-independent (no `tm*` tokens). Both sets audited → **NOT landed**
  (paste-log empty). See `_SHELL-NOTES.md` + `components/_COMPONENTS-NOTES.md`.
- **Dialect (learned):** paste target is the **modern structured schema** (`Screens:`/`Children:`/
  `Control: Type@version`, positional z-order, no ZIndex) — NOT `pac canvas unpack`'s retired
  inline `As type:` format. Files converted with real tokens from the example export.
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
- [2026-08-02] Authored dual-use skills `power-apps-svg` + `power-apps-editable-table` (SVG grounded on MS Learn data-URI/EncodeUrl) — sessions/2026-08-02-1702-external-repo-review.md
- [2026-08-02] Q11-bis: RECOMMEND flow-as-list-provisioner over manual UI IF Power Automate available (Q12) — repeatable, kills _x0020_ risk; not yet chosen — .claude/context/open-questions.md
- [2026-08-02] Phase-1 nav built as per-screen gallery bound to `NavMenu`, NOT a reusable component — why: components are hardest to paste across the air gap; NavMenu already gives T6's DRY intent. Component upgrade deferred until channel proven — sessions/2026-08-02-1411-phase1-core-shell.md
- [2026-08-02] Paste/code-view dialect = modern STRUCTURED schema (Control:Type@version, positional z-order, no ZIndex); `pac canvas unpack`'s inline `As type:` is the RETIRED format — do not author to it — sessions/2026-08-02-1411-phase1-core-shell.md
- [2026-08-02] Components authored in v3.0 `.pa.yaml` `ComponentDefinitions`; display pills/chips delivered as `cmpUiKit` OutputFunction HTML-builders (canvas components CAN'T sit in a gallery), interactive chip stays a component; components inline Theme (can't read app globals) — sessions/2026-08-02-1411-phase1-core-shell.md

## Threads          (open items; remove when closed)
- Open questions Q3–Q10, Q12, Q13 + Q2b (PBI workspace/refresh/embed) + Q5 (index master?) + tmIndices taxonomy source → `.claude/context/open-questions.md`
- Propose upstream to claudeBrain: `studio-transfer` + `pre-paste-review` + the new `power-apps-svg` / `power-apps-editable-table` skills (all general); flag PnP/CSOM gap.
- Decide whether to build the column-token validator write-time hook.
- **Q11-bis decision pending:** adopt flow-as-provisioner? Blocks on Q12 (Power Automate available?). If yes, supersede the manual-UI Q11 decision. → `.claude/context/open-questions.md`.
- **Phase-1 shell HARD-BLOCKED on the round-trip test:** on the work machine create screens
  `scr{Home,Reports,Projects,Reference,Admin}`, insert one blank vertical gallery → View code →
  drop into `studio/pulled/`, read its `Variant:`, find/replace `CONFIRM_BlankVertical` in the 5
  files. Then paste screens (one/time) → `App.Formulas` LAST → set Data row limit 2000. Also need
  tablet-vs-phone target. → `src/authored/_SHELL-NOTES.md`, `docs/screen-map.md`.
- **Licence-gate signal (user decision):** `gHasPowerBiLicence` hardcoded `false`; no in-app Power
  BI API — choose a source (tmLookups flag / Entra group) + hide-vs-grey for the Reports nav entry.
- **Component unconfirmed tokens (round-trip):** `HtmlViewer@2.1.0` + gallery `Variant`
  placeholders. **Component transfer:** recreate from contract tables in the Studio component
  editor / library — code-view paste unproven for component defs. → `components/_COMPONENTS-NOTES.md`.
- **Extras offered, not built:** `cmpSectionHeader`, `cmpConfirmDialog`, `cmpToast`, `cmpKpiRing`
  (SVG ring — the licence-free Reports visual for Q2). Wire the 6 built ones into screens in Phase 2.

## Log              (append-only pointers)
- 2026-07-26 1726 | repo init: adopt + author .claude asset set; foundational decisions | sessions/2026-07-26-1726-repo-init-decisions.md
- 2026-08-02 1702 | review aprildunnam + PM-tracker; distillation + template decision + screen map | sessions/2026-08-02-1702-external-repo-review.md
- 2026-08-02 1411 | Phase-1 core shell authored (theme + NavMenu + 5 screens); pre-paste audit; dialect corrected to modern structured schema | sessions/2026-08-02-1411-phase1-core-shell.md
- 2026-08-02 1520 | 6 reusable components authored (v3.0 ComponentDefinitions); audit found+fixed cmpSelection double-fire + Output-reads-var | sessions/2026-08-02-1411-phase1-core-shell.md
