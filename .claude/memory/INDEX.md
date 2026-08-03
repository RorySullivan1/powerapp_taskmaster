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
- **Phase-3 CRUD AUTHORED (2026-08-03):** 4 edit screens + `cmpTermPicker` (11 components, 11
  screens, 22/22 valid). Managed metadata is writable by reading `Choices()` directly — no cache
  list. **Nothing landed** — blocked on provisioning and the Office 365 Users connection.
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
- [2026-08-03] C9 APPLIED: task_stage/task_status/issue_status now REQUIRED with defaults (Not Started/Green/Open) — no blank-value gap; green%+amber-red% now sum to 100 — schema/schema.yaml v1.6.0
- [2026-08-03] Added `HANDOFF.md` — the one-way delivery runbook (repo→work machine→Studio). Stage 1 is a SMOKE TEST using scrReference/scrAdmin (only units needing no components, no App.Formulas, no data sources) to isolate the channel before anything else. **Claude maintains `paste-log.md`** — the human cannot write to this repo, so entries come from their chat reports — HANDOFF.md
- [2026-08-03] Component paste FAILED → root-caused against Microsoft's OFFICIAL pa-yaml v3.0 schema (fetched, vendored `tools/pa.schema.v3.0.yaml`): `Parameters` must be a SEQUENCE (was `{}`), and Output/OutputFunction/Action may NOT carry `Default` (formula belongs in the component's `Properties:` map). Built `tools/validate_pa_yaml.py` — run before EVERY hand-off; 17/17 now valid — paste-log.md
- [2026-08-03] scrAdmin LANDED — screen dialect + grounded control tokens CONFIRMED. Unstyled theme is expected (App.Formulas not yet pasted) — paste-log.md
- [2026-08-03] Kanban DEMOTED to a swap-in variant; scrProject ships a flat stage-grouped Vertical gallery. Why: `Variant: Horizontal` is ungrounded and sat mid-file gating the whole Tasks tab — under a one-way gap that risks the entire screen for a nicer layout. Kanban preserved at `src/authored/variants/` with swap instructions — src/authored/scrProject.pa.yaml
- [2026-08-03] 2nd audit fixed: `IsError(Errors(...))` NEVER gates (Errors returns a TABLE → use IsEmpty); success Notify+Back() were unconditional (failed save said 'Saved' and navigated away); edit state now seeded into GLOBALS in OnVisible rather than trusting cmpSelection's internal selection (Reset can't reach inside a component instance → silent wrong write); rollup now REFUSES to write past the row limit rather than persisting a truncated average — src/authored/scrTask.pa.yaml
- [2026-08-03] C10 — MM STAYS (user decision). Cascading term picker VALIDATED: Graph termStore `children` endpoints (GA Aug-2021) walk the hierarchy and yield term GUIDs → nesting detection falls out of the API; `TermStore.Read.All` is **DELEGATED ONLY** (app-only unsupported). The old 'Graph can't do MM' note is narrower than it read — it's the list-column VALUE, not the term store. WRITE via SharePoint connector `SPListExpandedTaxonomy` + `WssId:-1` is COMMUNITY-confirmed only = riskiest construct in the app. Recommend caching terms into a flat `taskmaster_terms` list so the cascade is delegable Filters with ZERO runtime dependency — docs/managed-metadata-picker.md
- [2026-08-03] Q12 (Power Automate / custom connector) is now **BLOCKING** — two required MM columns mean no project can be created from the app without a term source — .claude/context/open-questions.md
- [2026-08-03] C10 ARCHITECTURE DECIDED = **cache, not live Graph**. `taskmaster_terms` is now a real list in the golden source (flat, parent-pointer); the cascade is delegable `Filter`s on indexed `term_parent_guid`. Deciding argument was NOT speed — a flow call per dropdown level makes every create form depend on a flow being healthy at RUNTIME, the one thing this gap can't debug. Cache degrades to a stale vocabulary instead. **Narrows Q12 to population only** — the app pastes with no flow at all — schema/schema.yaml v1.8.0
- [2026-08-03] `cmpTermPicker` authored — 4 progressively-revealed vertical galleries. TWO load-bearing decisions: (1) a `"— select —"` SENTINEL row per level, because a gallery's `Selected` returns its first row until touched and would otherwise auto-pick a path the user never chose into a REQUIRED column (Coalesce treats `""` as blank, hence the empty-string guid); (2) CHAIN VALIDATION — a level's value counts only if that row is really a child of the level above, so a stale deeper pick after re-picking level 1 is discarded rather than written. Resolution runs once on a hidden `lblPick` label; all 4 outputs read it (a custom prop referencing another custom prop of the same component is unverified). `IsComplete` COUNTS children rather than trusting cached `term_is_leaf` — src/authored/components/cmpTermPicker.pa.yaml
- [2026-08-03] Four CRUD screens authored (`scrProjectEdit`/`scrTaskEdit`/`scrTransactionEdit`/`scrIssueEdit`) — shared pattern in `src/authored/_EDIT-NOTES.md`: seed globals in OnVisible + write from them; normalised picker records ({DisplayName,Mail} / {Id,Value}, empty-record null state, never IsBlank on a Blank()-inferred type); overlay galleries declared LAST (positional z-order = dropdown behaviour without an ungrounded ComboBox); dates typed + `DateValue()` + echo label; optional fields as separate GUARDED patches (Power Fx can't conditionally omit a record field, and `{Value:""}` isn't legal) — src/authored/_EDIT-NOTES.md
- [2026-08-03] SAVE-GATE pattern corrected repo-wide: `FirstError` exists ONLY inside `IfError`'s fallback, so the fallback stashes `FirstError.Message` into `g*Err` and success sits behind `Len(g*Err) = 0`. Every `IfError` argument is a SINGLE statement — no `;` chains inside a function argument (unverified across the gap). Supersedes the `IsBlank(gSaved)` gate — src/authored/
- [2026-08-03] `scrProjectEdit` stages children locally (required Lookup needs the parent ID, which only exists post-insert) then writes them. On partial failure the parent is ALREADY saved and can't be rolled back → successes leave staging, failures stay + are listed, and the screen FLIPS to Edit mode against the project it just created. That flip is load-bearing: Save again retries only what failed and CANNOT create a second project. `IfError(value, fallback, default)` classifies each row in one pass — src/authored/scrProjectEdit.pa.yaml
- [2026-08-03] People pickers use `Office365Users.SearchUser` (first-party; returns DisplayName/Mail). Cost = a Studio PREREQUISITE — the Office 365 Users connection must be added BEFORE the edit screens are pasted, or the paste fails on an unrecognised name. Now a numbered HANDOFF step — HANDOFF.md
- [2026-08-03] C5 write landed on the transaction form: `transaction_notional_usd` is written in the SAME statement as the native notional, from a STATIC `FxToUsd` table in App.Formulas, with the USD figure echoed live. Rates are placeholders and will go stale → raised as **Q14**. Form REFUSES to save a notional whose currency has no rate rather than quietly using 1 — src/patches/App.Formulas.pa.fx
- [2026-08-03] **Q12 ANSWERED = YES, Power Automate is available.** Unblocks three things that were queued behind it: the scheduled Graph-termStore flow that populates `taskmaster_terms` (C10), the flow-as-list-provisioner route (Q11-bis), and the extract flow (Q7). NOTE the app needs NO flow at runtime — that was the whole point of the C10 cache decision, and it still holds — .claude/context/open-questions.md
- [2026-08-03] **Q11-bis ADOPTED — flow-as-provisioner supersedes the manual-UI Q11 pick.** Its recommendation was explicitly conditional on Q12, which is now yes. Internal names set explicitly at creation kills the `_x0020_` risk, and it's re-runnable dev→test→prod (helps Q13). Manual UI stays the fallback. TO AUTHOR: the provisioning flow for 9 lists — .claude/context/open-questions.md
- [2026-08-03] **Q14 ANSWERED — C5 REVERSED. No FX in the app at all.** `transaction_notional_usd` is dropped (commented out in the golden source, DO NOT PROVISION), `FxToUsd` removed from App.Formulas, and the transaction form writes only the native notional + currency. Why: a write-time rate FREEZES whatever number the app held on the trade date and nothing downstream can correct it; report-time conversion can be restated, back-dated and audited. **CONSEQUENCE — no cross-currency figure can be shown ANYWHERE in the app**; scrProject's transactions tab now totals PER CURRENCY (five enumerated Sums, not Distinct/Concat — no novel scope-shadowing construct mid-file under a one-way gap) and the old USD column shows the product instead of a permanently blank number. **Power BI now OWES an FX dimension + a trade-date conversion measure** — schema/schema.yaml v1.9.0
- [2026-08-03] **COMPONENT PASTE REGRESSED — blocker.** Whole-definition paste stopped working after earlier successes; screens don't load without components. Working theory (unconfirmed, no error text yet): a component is a **CONTRACT** (custom properties — *no paste gesture exists*, they're typed into the property pane) plus a **BODY** (child controls — ordinary dialect, pastes like a screen). A whole `ComponentDefinitions:` paste asks one channel to carry both. Response: `tools/split_components.py` generates `BUILD-SHEET.md` (contract, in creation order) + `bodies/*.children.pa.yaml` (comment-free control sequence). Add properties BEFORE pasting the body — controls reference them by name — src/authored/components/BUILD-SHEET.md
- [2026-08-03] **Only FOUR control tokens are actually PROVEN** — the ones in `scrAdmin`, the sole confirmed crossing: `Label@2.5.1`, `Rectangle@2.3.0`, `Classic/Icon@2.5.0`, `Gallery@2.15.0` (Vertical). `Classic/Button@2.2.0` and `Classic/TextInput@2.3.2` are NOT proven despite being used everywhere. Acted on the worst case: `cmpSelection` moved off `Variant: Horizontal` (self-flagged unconfirmed, instantiated by 7 screens) to **Vertical + `WrapCount = CountRows(Items)`**, which lays all items across one row — a horizontal strip from the only variant that has landed — src/authored/components/cmpSelection.pa.yaml
- [2026-08-03] **.msapp PACKAGING IS A DEAD END — settled, do not re-litigate.** Three independent reasons: (1) `pac canvas pack`/`unpack` are **DEPRECATED** by Microsoft (use Git integration instead), and PASopa carries an explicit "don't use in production" warning from its own maintainers; (2) the decisive one — **`.pa.yaml` files are READ-ONLY representations and are NOT used when an app loads** (MS Learn, power-apps-yaml). An app loads from the JSON control tree inside the .msapp, so dropping our authored YAML into `\Src` would produce an app that opens EMPTY. Building a real .msapp means hand-authoring CanvasManifest/Header/Properties JSON + Entropy + a computed Checksum.json — reverse-engineering with a high chance of a file Studio simply refuses to open, which under a one-way gap is the worst outcome (no diagnostic); (3) data-source bindings need real site URL + list GUIDs that don't exist until provisioning. **The code-view paste channel is PROVEN** (scrAdmin + components landed) — do not trade it for this — docs/msapp-and-git-integration.md
- [2026-08-03] **The one route that could retire the clipboard: Power Platform GIT INTEGRATION.** Studio commits/pulls canvas source as `.pa.yaml`, and *minor* edits made directly in the repo ARE restored on pull. BUT: it is **Azure DevOps**, not GitHub (the GitHub canvas integration was experimental and is RETIRED), it works on Dataverse **solutions**, and the flow is publish→commit. Worth investigating on the work machine; cannot be settled from this side — .claude/context/open-questions.md
- [2026-08-03] **CORRECTION (user-reported from Studio): components ARE code-view-pasteable, and several LANDED.** The repo had asserted the opposite since Phase 1 — that canvas components must be rebuilt by hand in the component editor and that their control tokens were therefore "documentation, not a paste payload". Both wrong. Consequence: component tokens are held to the same standard as screen tokens — `HtmlViewer@2.1.0` and `Classic/Timer@2.1.0` are now real paste risks and the first suspects if `cmpStatusPill`/`cmpChoicePill`/`cmpToast` are rejected — paste-log.md
- [2026-08-03] **C10 REVISED SAME DAY — the `taskmaster_terms` cache list is DELETED.** User challenged the double-store; they were right. `Choices([@list].mmColumn)` returns the term set from the term store with **Label, Path, Guid, WssId**, and **`Path` is the FULL hierarchical path** (`EMEA;UK;London`) — so the hierarchy is already in the data and the cascade is prefix matching (`StartsWith(childPath, parentPath & ";")`). No mirror, no refresh flow, no drift; term store stays the single source of truth. My delegation argument for the cache didn't survive either: a term set small enough to use is small enough to hold in memory — schema/schema.yaml v2.0.0
- [2026-08-03] **MM WRITE now hands the connector its OWN record back:** `LookUp(Choices([@list].col), Path = <picked path>)`. This RETIRES the hand-built `SPListExpandedTaxonomy` + `WssId:-1` literal that was the least-proven construct in the app, and sidesteps the live `Guid` vs `TermGuid` field-name ambiguity since nothing we author names it. Person is now the ONLY hand-built complex shape left (no `Choices()` exists for Person) — docs/managed-metadata-picker.md
- [2026-08-03] **The one real MM limit: `Choices()` on an MM column is capped at 20 TERMS** by the connector, not configurable (multiple independent sources + an open MS Ideas request). If a set outgrows it, swap ONE binding for a flow-fed collection in the same `{Label, Path}` shape — component unchanged, and it's an in-memory collection, still not a second store. **`Path` delimiter (`;`) is NOT first-party documented** → it's a `PathDelimiter` component input and the picker prints a raw path on screen, so first paste settles it — src/authored/components/cmpTermPicker.pa.yaml
- [2026-08-03] **Power BI licence gate DECIDED = SOFT GATE.** Reports stays visible but greyed for unlicensed users and still opens, landing on the empty-state card + the three licence-free KPI rings. Never hidden — a hidden feature is one nobody knows to request a licence for. `gHasPowerBiLicence` stays `false` (everyone treated as unlicensed) until a real signal exists; worst case is a licensed user seeing the fallback rings and one extra click, vs. an unlicensed user hitting a broken embed. Nav + Reports both read that one line, so a future signal is a one-line change — src/patches/App.Formulas.pa.fx

## Threads          (open items; remove when closed)
- Open questions Q3–Q10, Q13 + Q2b (PBI workspace/refresh/embed) + Q5 (index master?) + tmIndices taxonomy source → `.claude/context/open-questions.md`
- Propose upstream to claudeBrain: `studio-transfer` + `pre-paste-review` + the new `power-apps-svg` / `power-apps-editable-table` skills (all general); flag PnP/CSOM gap.
- Decide whether to build the column-token validator write-time hook.
- **Paste order (no round-trip — one-way):** in Studio create screens `scr{Home,Reports,Projects,
  Reference,Admin}`; PASTE the components via code view (they are pasteable); paste screen control-groups
  (one/time) → `App.Formulas` LAST → set Data row limit 2000. Gallery `Variant` is now `Vertical`
  (best-grounded); button-nav is the fallback if a screen paste fails. Need tablet-vs-phone target.
- **Licence gate SETTLED (soft gate, greyed-but-reachable).** Only optional follow-up left: supply
  a real signal for `gHasPowerBiLicence` (config allow-list column or Entra group) — a one-line
  change, since nav and the Reports screen both read it.
- **Component transfer CORRECTED 2026-08-03:** components **ARE** code-view-pasteable and several
  have LANDED. The repo had assumed the opposite (rebuild by hand in the component editor) — wrong,
  and wrong in the expensive direction. Consequence: their control tokens are a **real paste
  payload**, so `HtmlViewer@2.1.0` / `Classic/Timer@2.1.0` / gallery `Variant` are genuine risks,
  not documentation. → `components/_COMPONENTS-NOTES.md`.
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


- **Next physical step:** HANDOFF.md Stage 1 smoke test (paste scrReference) — proves the channel before the expensive component build.

- **C10 CLOSED — no cache, no seeding, nothing to provision.** Two things to watch at first paste,
  both visible on screen: the raw term **path** the picker prints (confirms the `;` delimiter), and
  whether any vocabulary is losing terms to the **20-term `Choices()` cap**.
- **One hand-built write shape is still UNEXECUTED against this tenant:** expanded USER for Person
  columns (`ClaimPrefix`). Not first-party; isolated in its own `Patch`. The MM write no longer
  belongs on this list — it hands back the connector's own record. Cheapest test = save ONE project
  with ONE region.
- **Power BI OWES the blended notional (consequence of Q14).** An FX dimension (currency, rate,
  effective date) + a measure converting `transaction_notional` at the trade date. Until it exists
  there is no cross-currency figure anywhere — accepted cost, not an oversight.
- **One Power Automate flow to author, unblocked (Q12 = yes):** the list-provisioning flow, **8
  lists** with explicit internal names — supersedes manual UI. *(The term-store sync flow that was
  here is no longer needed: the app reads the term store directly.)*
- **Studio prerequisite before the edit screens:** add the **Office 365 Users** connection. An
  unrecognised connector name is a PASTE failure, not a runtime one.

## Log              (append-only pointers)
- 2026-07-26 1726 | repo init: adopt + author .claude asset set; foundational decisions | sessions/2026-07-26-1726-repo-init-decisions.md
- 2026-08-02 1702 | review aprildunnam + PM-tracker; distillation + template decision + screen map | sessions/2026-08-02-1702-external-repo-review.md
- 2026-08-02 1411 | Phase-1 core shell authored (theme + NavMenu + 5 screens); pre-paste audit; dialect corrected to modern structured schema | sessions/2026-08-02-1411-phase1-core-shell.md
- 2026-08-02 1520 | 6 reusable components authored (v3.0 ComponentDefinitions); audit found+fixed cmpSelection double-fire + Output-reads-var | sessions/2026-08-02-1411-phase1-core-shell.md
- 2026-08-02 1545 | merged PR#2 shell + PR#3 components to main; +4 extra components (cmpSectionHeader/ConfirmDialog/Toast/KpiRing SVG), audit PASTE-clean | sessions/2026-08-02-1411-phase1-core-shell.md
- 2026-08-02 1610 | merged PR#4; Phase-2 composition — component instances (static data) on Home/Reports/Projects; instance dialect grounded; audit clean (only known gates) | sessions/2026-08-02-1411-phase1-core-shell.md
- 2026-08-03 | schema intake → golden source → data layer → pa-yaml validator → C10 cache decision + cmpTermPicker → four CRUD screens with staged children | sessions/2026-08-03-crud-screens-and-term-picker.md
- 2026-08-03 | Q12/Q14/licence-gate answered: FX conversion moved to Power BI (C5 reversed), flow-as-provisioner adopted, soft licence gate | sessions/2026-08-03-crud-screens-and-term-picker.md
- 2026-08-03 | C10 revised: cache list deleted, picker cascades on the term Path from Choices(), MM write hands back the connector's own record | sessions/2026-08-03-crud-screens-and-term-picker.md
