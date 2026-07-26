# 2026-07-26 17:26 · repo-init-decisions

**Goal:** Initialize the .claude asset set for the EQD taskmaster PowerApp; record foundational decisions

## What happened
- Cloned `RorySullivan1/claudeBrain` (authoritative on structure); read the layer taxonomy,
  example-project layout, the four meta-skills, and the Power Platform skill family.
- Produced `docs/claudebrain-inventory.md` (adopt/adapt/ignore). User **approved the adopt list
  "as recommended."**
- Copied in (by claudeBrain's copy convention): 8 Power Platform skills + `session-memory` +
  `knowledge-router` + the operational hook/catalog machinery + repo-skeleton templates.
- Authored net-new (air-gap-specific): `studio-transfer` skill, `pre-paste-review` agent,
  `change-end-to-end` workflow, `pull-reconcile` command, context briefs (`schema`,
  `app-structure`, `open-questions`), the working skeleton, and this memory seed.
- Verified version-sensitive Studio facts against Microsoft Learn (see gotchas).

## Foundational decisions (the "why" — do not relitigate)
- **Project is the parent; Task/Ticket/Issue are peers**, no intermediate level. Three
  *different kinds* of record, not variants of one thing.
- **Three lists, not one discriminated list** — a type discriminator would leave ⅔ of columns
  null and make Owner/PercentComplete actively misleading on non-work rows.
- **Only Tasks roll up into completion.** Tickets and Issues surface alongside, never inside.
- **No snapshot/metrics list.** It existed only because Power Fx can't delegate `Sum`; Power BI
  imports lists whole and removes the reason. Two sets of numbers that can disagree is worse
  than one. Consequence: in-app-aggregation denormalisations are gone — `BusinessUnit` stays on
  projects alone. **Do not reintroduce it.**
- **Products and indices are stubs.** Economics live in the existing ISIN-keyed structured-
  product database; sync is one-directional in; **ISIN is the egress contract.**
- **Notional is the only value column.** Known bias: favours large low-margin trades — correct
  if the measure is issuance volume.
- **Not a book of record.** Internal KPI/value assessment; no retention obligation.

## Decisions taken this session (answers to blocking/elevated questions)
- **Full ticket-level rows as the primary store** (Q1). `tmTickets` holds every trade row and
  drives figures. Why: user wants per-trade granularity as primary. Cost accepted: max
  delegation/5000-threshold exposure → indexing mandatory, every query delegable, USD
  normalised at write.
- **Not everyone is Power BI-licensed** (Q2). Dashboard can't carry core nav → native
  licence-independent navigation + a real empty state for unlicensed users. Don't rebuild the
  aggregate dashboard as native charts to dodge the gap.
- **Manual (SharePoint UI) provisioning** (Q11). Why chosen by user despite risk. Cost: high
  `_x0020_` internal-name mangling risk + no repeatability + **no automated term-store sync**
  route (claudeBrain has no PnP/CSOM skill). Mitigation: schema snapshot must record **true**
  internal names (⟨capture⟩ placeholders until columns exist); `pull-reconcile` cross-checks them.
- **Adopt list approved "as recommended"** — includes the operational hook/catalog machinery
  (lifecycle only); the domain column-token validator hook is **proposed, not built** (see
  CLAUDE.md → Hook candidates).

## Gotchas & dead ends
- **Brief assumptions that were void:** (1) no `taskmaster` Python package exists in claudeBrain
  — the assumed Graph/SharePoint provisioning wrapper is absent (only the `graph-api-integration`
  *skill*). (2) No QIS strategy taxonomy in claudeBrain — `tmIndices` RiskPremium/AssetClass have
  no upstream vocabulary; do not invent (open, Q5/taxonomy).
- **Studio facts verified on Microsoft Learn (refine the brief):** Code view GA **17 Mar 2025**;
  requires the Power Fx formula bar on; **App Object has no code view** and the **code-view pane
  isn't editable** (both official *Known limitations*) → App code via formula bar only. The
  **preview copy/paste dialect is retired**; the single **active** schema is `*.pa.yaml`, which
  is **read-only** ("not used when an app is loading"; edit/merge only via Git Integration, after
  publish). `.fx.yaml` + `pac canvas unpack`/pack **retired**; current export is `pac canvas
  download` / `.msapp \Src`. So the brief's "two dialects" → a cleaner split: **interactive
  code-view YAML (paste-to-create)** vs **read-only `.pa.yaml` (review only)**.
- `catalog.py` resolves its tree from `$CLAUDE_PROJECT_DIR` (fallback cwd) — set it when running.

## State at end
- `.claude/` populated: 11 skills, 1 agent, 1 command, 1 workflow, context briefs, memory,
  operational hooks (settings.json generated), CATALOG.md. CLAUDE.md + CLAUDE.local.md + skeleton
  + .gitignore in place. No Power Fx or `.pa.yaml` authored (correct — this task was the workshop).
- All 8 Power Platform skills' facts were pre-verified against Microsoft Learn upstream
  (claudeBrain memory 2026-07-24) and re-confirmed for the Studio-transfer additions.

## Open threads
- The non-blocking open questions (Q3–Q10, Q12, Q13) + Q2b (workspace/refresh/embed) + Q5 (index
  master) + the `tmIndices` taxonomy source — tracked in `.claude/context/open-questions.md`.
- **Propose upstream to claudeBrain:** the `studio-transfer` skill and `pre-paste-review` agent
  are general to any air-gapped canvas-app-via-clipboard workflow (placement test). Also a
  PnP/CSOM skill gap and the `.msapp`/code-view facts are worth contributing back.
- **Column-token validator hook** proposed, not built — decide whether to build it next.
