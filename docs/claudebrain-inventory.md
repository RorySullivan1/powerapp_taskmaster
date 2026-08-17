# claudeBrain inventory — for `powerapp_taskmaster`

What exists in [`RorySullivan1/claudeBrain`](https://github.com/RorySullivan1/claudeBrain)
that could serve this project, where it lives, and an **adopt / adapt / ignore**
recommendation. claudeBrain is authoritative on structure; this brief's domain drives
which assets matter.

**Reuse convention (claudeBrain's own):** reuse is *by copy* — take the folder from
`example-project/.claude/<layer>/` into the matching layer here. Never fork a skill; if a
skill needs changing, change the canonical `SKILL.md` **upstream** and re-copy.

**Placement test applied throughout:** *would another project want this?* If yes → it
belongs in claudeBrain (propose upstream, copy here). If it is only meaningful here (the
schema, the paste log, pulled Studio state) → it lives in this repo only.

> **Status: awaiting decision.** Nothing below has been copied in. Approve the adopt list
> (§1–§2) and answer the blocking questions (see `docs/` companion / chat) before the copy
> pass and the context docs are built.

---

## Snapshot: what the brief expected vs. what is actually there

The brief (§2) told me to "specifically look for, and expect to adopt" several things. Two
of its assumptions turned out **false**, and that changes the plan:

| Brief expected | Reality in claudeBrain | Consequence |
|---|---|---|
| A `taskmaster` **Python package** with a Graph/SharePoint wrapper for provisioning + schema snapshot | **Does not exist.** No Python package anywhere; "TaskMaster" appears only as an example *VSTO* project name in `coding-standards`. The only Graph asset is the `graph-api-integration` **skill** (reference, not runnable code). | Provisioning route (Q11) is genuinely unresolved. No wrapper to run; the schema snapshot is authored by hand from whatever route is chosen. |
| A **QIS strategy taxonomy** to source `tmIndices` RiskPremium / AssetClass values from (§6) | **Not present.** The quant skills (`quantitative-finance`, `backtesting-validation`) teach *methodology*, not a named risk-premium vocabulary. | `tmIndices` taxonomy has no upstream to mirror → open question (relates to Q4/Q5). A *session-level* `quant-investment-strategist` skill exists in this Claude Code environment, but it is **not** a claudeBrain asset. |
| Existing Power Platform / SharePoint / Graph skills to prefer over authoring new ones | **Present and strong** — a full 8-skill Power Platform family added 2026-07-24 (memory log `2026-07-24-1338-power-platform-skill-family.md`), facts verified against Microsoft Learn. | The brief's "Power Fx expertise" and much of the schema/reporting expertise is **already authored**. Adopt, don't re-write. |
| PnP / CSOM taxonomy-read capability (§6 says term-store reads need CSOM or PnP, *not* Graph) | **Absent.** `graph-api-integration` explicitly scopes *out* managed-metadata/term-store. | Gap — flagged under §5. |

---

## 1. Adopt — direct-domain Power Platform family (copy verbatim)

The core of this project. All eight were built together, cross-reference each other cleanly
by `description:` boundary lines, and map almost 1:1 onto the brief's domain asks. **Copy
each folder** from `example-project/.claude/skills/<name>/` → `.claude/skills/<name>/`.

| Asset | Path | Serves (brief §) | Recommendation |
|---|---|---|---|
| `power-fx-development` (+ `delegation.md` sidecar) | `…/skills/power-fx-development/` | The brief's **"Power Fx expertise" skill** (§4). Carries the delegation matrix, column-type policy, Person/Claims patching, aggregation rules — exactly §5. | **ADOPT.** Do **not** author a new Power Fx skill (brief §11). This *is* it. |
| `power-fx-review` | `…/skills/power-fx-review/` | Delegation/perf/correctness audit checklist. | **ADOPT.** The brief's **pre-paste review agent** (§4) should *defer to this skill's checklist*, not duplicate it — see §3. |
| `power-apps-components` | `…/skills/power-apps-components/` | Reusable components + HtmlText rich content (§7 components: nav, cards, badges, chips, dialogs). | **ADOPT.** |
| `sharepoint-list-architecture` | `…/skills/sharepoint-list-architecture/` | Column-type/index/threshold/relationship design behind §6. | **ADOPT.** The **schema context doc** (§4) is the *concrete instance* (this app's real columns + internal names); this skill is the *how-to*. Keep them DRY (§3). |
| `sharepoint-column-formatting` | `…/skills/sharepoint-column-formatting/` | Status pills / colour-from-lookups in list views (§7 status badge). | **ADOPT.** |
| `graph-api-integration` (+ `endpoints.md`) | `…/skills/graph-api-integration/` | Provisioning over Graph, the egress/extract path (§6, §7). | **ADOPT** — but see the **PnP/CSOM gap** (§5); it does not cover term-store reads. |
| ~~`power-bi-dax`~~ | — | The embedded Power BI dashboard measures (§7). | **REMOVED 2026-08-17** — Power BI is out of scope. |
| ~~`power-query-m`~~ | — | Loading SharePoint lists into Power BI (§7). | **REMOVED 2026-08-17** — Power BI is out of scope. |

---

## 2. Adopt — operational infrastructure

| Asset | Path | Why | Recommendation |
|---|---|---|---|
| `session-memory` (skill + `scripts/memory.py`) | `…/skills/session-memory/` | **Explicitly named** in the brief (§2). This project spans many sessions and accumulates decisions that must survive them. | **ADOPT.** Requires its SessionStart / Stop / PreCompact / UserPromptSubmit lifecycle hooks to actually auto-load `INDEX.md` (see hooks row). |
| `knowledge-router` (skill + `scripts/context.py`) | `…/skills/knowledge-router/` | The context-notes tier. The brief says adopt "**if the context layer grows past a handful of docs**" — it will (schema, app-structure, decisions, open-questions, manifest, + notes). | **ADOPT.** Owns the `context/notes/` + `INDEX.md` machinery; the schema/decisions docs are flat briefs, discrete facts become notes. |
| Hook machinery: `build-hooks.py`, `catalog.py` + operational fragments (`session-start*.json`, `context-start.json`, `pre-compact.json`, `stop.json`, `user-prompt-submit.json`, `post-tool-use-catalog.json`) + generated `settings.json` | `…/hooks/` | These are the **plumbing the adopted operational skills need**, not domain enforcement. `session-memory`/`knowledge-router` INDEX auto-loading and CATALOG freshness depend on them. `build-hooks.py` compiles fragments → `settings.json`; `catalog.py` generates `CATALOG.md`. | **ADAPT (adopt the machinery + operational lifecycle fragments).** Distinct from the *domain* enforcement hook the brief wants only *proposed* (the column-token validator) — see §4. |
| `CATALOG.md` generation + `/reindex` command | `…/commands/reindex.md`, `…/hooks/catalog.py` | Keeps the capability catalog current so `CLAUDE.md` can point rather than enumerate (brief: "capabilities described by category"). | **ADOPT** (comes with the hook machinery). |
| Repo skeleton & lean session-contract shape: `example-project/CLAUDE.md`, `CLAUDE.local.md`, `.claude/README.md`, `.claude/context/README.md`, `.claude/context/INDEX.md`, per-layer `README.md`s | `example-project/` root + `…/.claude/` | The canonical produced layout the brief says a reader must recognise (§10). Gives the **lean, points-not-inlines** `CLAUDE.md` shape for the session contract (§4). | **ADOPT as templates** — copy the scaffold, replace contents with this project's specifics. |

---

## 3. Adapt — patterns to imitate when authoring the net-new assets

Not copied wholesale; used as the **template** for the this-project assets the brief asks
me to author (§4). Reading them is how I avoid re-deriving conventions.

| Upstream asset | Path | Template for | Note |
|---|---|---|---|
| `goal-auditor` (agent) | `…/agents/goal-auditor.md` | The brief's **pre-paste review agent** (§4). | **Exact match** for the "objective brain" pattern the brief demands: read-only (`tools: Read, Grep, Glob, Bash`, `permissionMode: plan`), determines *what* is wrong, never edits, returns a verdict + evidence. Author the pre-paste agent modelled on this; its checklist *defers to* the adopted `power-fx-review` skill. |
| `software-architect` (agent) | `…/agents/software-architect.md` | Optional help designing the **app-structure** context doc (§7). | Objective structural brain; useful but not required. |
| `author-asset` (workflow) + `/add-*` commands | `…/workflows/author-asset.md`, `.claude/commands/add-*.md` | The build process itself — scaffold → fill → wire → verify, without re-exploring. | Follow this workflow to build the net-new assets in one batched pass. |
| `ship-version` (workflow) + `version-set`/`version-ship` commands + `.meta/version` | `…/workflows/`, `…/commands/`, `example-project/.meta/` | Optional model for the brief's **end-to-end change workflow** (§4) and any versioned releases. | The end-to-end workflow's spine is the Studio *round-trip* (freshness → author → audit → hand off → record), not semver shipping. Reuse the *shape* (explicit STOP conditions, gates) but not the release machinery unless versioned releases are wanted. |
| `context-vs-skill`, `skill-authoring`, `agent-authoring`, `workflow-authoring` (meta-skills) | `.claude/skills/` (factory) | The authoring rules for every net-new asset. | Already read. Keep the schema doc (reference) and the SharePoint skill (behavior) DRY per `context-vs-skill`'s single-source rule. |

---

## 4. Author net-new (this project only — the air gap has no upstream equivalent)

None of these exist in claudeBrain; the clipboard/air-gap workflow is unique to this setup.
The brief anticipated all of them (§4). **Placement flags** note which are general enough to
*propose upstream* to claudeBrain (per the placement test) versus which are inherently local.

| To author | Kind | Placement | Notes |
|---|---|---|---|
| Studio transfer discipline (clipboard bridge, code-view mechanics, pulled→authored→landed lifecycle, the round-trip test) | skill | **Propose upstream** — reusable for any air-gapped canvas-app-via-clipboard workflow | Opens with the round-trip test (§5). No Power Fx yet. |
| Pre-paste review | agent | **Propose upstream** (generic objective-brain) | Read-only; audits authored Power Fx for non-delegable expressions + schema violations; returns findings + paste / do-not-paste verdict. Modelled on `goal-auditor`; defers to `power-fx-review` for the checklist. |
| End-to-end change | workflow | Mixed — mostly local (freshness/paste hand-off) | Freshness check → author → audit → choose mechanism → hand off → record. Explicit STOP conditions (§4). |
| Pull reconciliation | command | Local | Human pastes fresh Studio state; diff vs prior snapshot; flag drift + stale authored files. |
| Schema | context (brief) | Local (concrete instance data) | §6 written up as reference; the real internal names go here after provisioning. |
| App structure | context (brief) | Local | §7. |
| Decisions | context (brief) or seed `session-memory` | Local | §8 with reasoning preserved. **Placement call (Q for approval):** §8 is *decisions with rationale* — that is exactly `session-memory`'s Decisions ledger. Recommend seeding memory's append-only Decisions rather than a static doc, to avoid two homes. |
| Open questions | context (brief) | Local | §9 minus whatever gets answered now. |
| Context manifest | context (README manifest + `INDEX.md`) | Local | Per claudeBrain convention (`context/README.md` Manifest + knowledge-router `INDEX.md`). |
| Local notes | root `CLAUDE.local.md`, **gitignored** | Local | Studio session URL, last pull date, unlanded pastes. |
| Working skeleton | dirs + files | Local | Dirs for pulled Studio state, schema snapshot, authored source, formula-bar patches, docs; an empty **paste log** with column headers; `.gitignore` (local notes, session logs, pulled snapshots). |
| **Column-token validator hook** | hook | **Propose only, do not build** (brief §4, §10) | Write-time check: grep authored YAML for column tokens, validate against the schema snapshot — "never invent a column name". Strongest candidate; with no CI, a hook is the only enforcement. Noted in the session contract with a one-line rationale, per the brief. |

---

## 5. Gaps in claudeBrain this project exposes

1. **No `taskmaster` package / no runnable provisioning wrapper.** Only the
   `graph-api-integration` skill (reference). Provisioning is a decision (Q11), then hand-run
   wherever tenant auth lives (not this air-gapped repo).
2. **No PnP / CSOM coverage.** `graph-api-integration` explicitly excludes managed-metadata /
   term-store, which §6 says must be synced via **CSOM or PnP, not Graph**. If term-store sync
   is in scope, that expertise is missing upstream — candidate to propose.
3. **No QIS / desk strategy taxonomy.** `tmIndices` RiskPremium / AssetClass have no upstream
   vocabulary to mirror (brief §6 assumed one). Open question.
4. **No air-gap / clipboard / Studio-transfer discipline, no pre-paste-review agent, no
   pull-reconciliation command.** All net-new (§4) — correctly anticipated by the brief.
5. **Naming standards / session-contract "as a discrete asset"** (brief §2): the *session-
   contract shape* exists (`example-project/CLAUDE.md`); naming standards are embedded in
   `sharepoint-list-architecture` (frozen internal names) and `power-fx-development` (variable
   prefixes `g`/`loc`/`col`) rather than a standalone doc. No separate asset needed.

---

## 6. Ignore — present but out of domain (one-line reason each)

| Asset(s) | Path | Reason to ignore |
|---|---|---|
| VBA family: `vba-development`, `-review`, `-maintenance`, `-distribution`, `-userforms`, `-code-test-writing`, `vba-addin-building`; `vba-developer` agent | `…/skills/vba-*`, `…/agents/vba-developer.md` | Office macro stack; nothing in a canvas Power App. |
| VSTO family: `VSTO-development`, `-review`, `-maintenance`, `-distribution`; `vsto-developer` agent | `…/skills/VSTO-*`, `…/agents/vsto-developer.md` | C#/.NET Office add-ins; not this app. |
| Python family: `python-development`, `-review`, `-maintenance`, `-deployment`; `python-developer` agent; `coding-standards` | `…/skills/python-*`, `…/agents/python-developer.md` | No Python codebase in this repo (the air gap keeps runnable code out; provisioning runs elsewhere). Revisit only if a provisioning script lands here. |
| Quant family: `quantitative-finance`, `backtesting-validation`, `quant-code-review`, `financial-timeseries-analysis`; `finance-quantitative-developer`, `data-analyst` agents | `…/skills/`, `…/agents/` | Analytics methodology, not app-building. |
| Branding → presentation pipeline: `branding`, `presentation-design`, `deck-builder`, `one-pager-builder`, `brochure-builder`, `pamphlet-builder`, `report-builder`; `presentation-architect` agent | `…/skills/`, `…/agents/` | Document/deck production, not an app. |
| Docs skills: `technical-documentation-drafter`, `user-guide-drafter`, `development-mapping` | `…/skills/` | Authoring docs; not needed to build the app. (`user-guide-drafter` optional for end-user docs later.) |
| GitHub: `github-comments`, `github-issues`, `github-pull-requests`, `github-releases`; `github-operator` agent | `…/skills/github-*`, `…/agents/github-operator.md` | The harness already provides GitHub MCP + house attribution conventions. |
| Context-economy meta: `token-optimizer`, `skill-distiller`, `agent-finder`; `token-manager` agent | `…/skills/`, `…/agents/` | Useful meta-tooling, not core. Optional — adopt later if sessions get token-heavy. |
| Roadmap machinery: `roadmap-set`/`roadmap-status` commands, `advance-roadmap-step` workflow, roadmap hooks, `.meta/roadmap/` | `example-project/.claude/`, `example-project/.meta/` | Multi-stage product roadmap; heavier than this project needs. Optional. |

---

## 7. Recommended adopt list (the decision to approve)

**Adopt now (copy in):**
- All 8 Power Platform skills (§1).
- `session-memory` + `knowledge-router` (§2).
- The hook machinery + operational lifecycle fragments + `catalog.py`/`/reindex` (§2).
- The repo-skeleton / session-contract templates (§2).

**Adapt (imitate, author net-new):**
- `goal-auditor` → pre-paste review agent; the `author-asset` workflow + `/add-*` for the build.
- Optionally the `ship-version`/version machinery *shape* for the end-to-end workflow.

**Ignore:** everything in §6.

**Author here (after questions answered):** the net-new assets in §4, the context docs, the
skeleton, and the **proposed** (not built) column-token validator hook.

**Do not proceed** until: (a) this adopt list is approved, and (b) the blocking questions are
answered. Two of the brief's own assumptions (the `taskmaster` package, the QIS taxonomy) are
void, so at least the provisioning and taxonomy questions now matter more than the brief assumed.
