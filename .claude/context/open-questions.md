# Open questions

Unresolved decisions that will shape the schema, the app, or the provisioning route. Answered
ones are recorded (with their reasoning) in the `session-memory` Decisions ledger, not here —
this doc holds only what is **still open**. Resolve a question → move it to memory as a
decision and delete it here.

## Answered on 2026-07-26 (see `.claude/memory/INDEX.md` → Decisions)

- **Q1 Ticket-level rows** → **Yes, full ticket-level as the primary store.** `tmTickets`
  holds every trade row and drives figures. Consequence: max delegation/threshold exposure →
  indexing mandatory, every query delegable.
- **Q2 Power BI licensing** → **MOOT (2026-08-17): Power BI is out of scope entirely.** No
  embed, no licence gate, no sub-items. Reporting is native and every chart is SVG. What
  survives is the reasoning, not the gate: navigation never depends on a reporting surface.
- **Q11 Provisioning route** → **Manual (SharePoint UI)** *(under reconsideration — see Q11-bis).*
  High `_x0020_` internal-name risk; the schema snapshot must capture **true** internal names. No
  automated term-store sync path.

## Answered on 2026-08-03 (see `.claude/memory/INDEX.md` → Decisions)

- **Q12 Power Automate availability** → **YES, available.** Still useful for the
  **flow-as-list-provisioner** route (Q11-bis, whose recommendation was explicitly conditional on
  this) and the extract flow (Q7). **No longer needed for C10 at all** — the term picker reads the
  term store directly via `Choices()`, so there is no cache list to populate and no flow in that
  path unless a term set exceeds 20 terms.
- **Q14 FX rates** → **do not convert in the app at all.** `transaction_notional_usd` is dropped;
  the app stores currency + amount and converts nothing. **SETTLED 2026-08-17: cross-currency
  conversion is OUT OF SCOPE for this project and other tools handle it.** Power BI's departure
  left it briefly unowned; it is now deliberately unowned. No blended notional anywhere, ever.
  See `.claude/context/schema.md` → C5.
- **Power BI licence gate** → **REMOVED 2026-08-17.** Power BI is out of scope; `gHasPowerBiLicence`,
  `NeedsLicence` and `cmpAppBar.HasLicence` are all deleted.
- ~~**Q2b Power BI workspace / refresh / embedded-vs-linked.**~~ CLOSED 2026-08-17 — out of scope. Which workspace hosts the report,
  how often it refreshes, and whether it's embedded or linked. Needed before the reporting
  panel is real. *(Was a sub-part of the answered Q2; the licence question is settled, these
  aren't.)*
- **Q5 Is there an index master?** If not, `tmIndices` is a **real** list, not a stub — changes
  its seeding route and columns. **Blocks** the `tmIndices` taxonomy.
- **Taxonomy source for `tmIndices` (RiskPremium / AssetClass).** The brief assumed a desk QIS
  strategy vocabulary lived in claudeBrain to mirror — **it does not.** No terms until the desk
  supplies its actual vocabulary. Do not invent. (A session-level `quant-investment-strategist`
  skill exists in the Claude Code environment but is **not** a project asset and is not
  authoritative for the desk's terms.)

## Open (record; not yet blocking)

- **Q3 Business-unit values, and can a project span two?** If a project can belong to more than
  one BU, the dimension needs its **own list + a junction** rather than a single `BusinessUnit`
  text column on `tmProjects`.
- **Q4 Product/index stub seeding** — route, cadence, and what happens when a ticket references
  an **unknown ISIN** (reject? create a stub? queue?). Interacts with Q5 and Q11 (manual route →
  seeding is by hand until a route exists).
- **Q6 Can a task serve more than one transaction?** `TicketId` on `tmTasks` assumes **one**.
  If many, that becomes a junction (`tmLinks`-style) instead of a single FK.
- **Q7 Extract contents and delivery route** — which fields travel with the ISIN/IndexTicker
  key, and how the extract is delivered (Power Automate flow preferred over in-app `Download()`,
  which truncates at 2,000 rows). Depends on Q12.
- **Q8 Which issue types need a lifecycle** — drives the `NA` `IssueStatus` and the triage screen.
- **Q9 Scale — expected rows at 12 and 36 months.** Directly governs the `tmTickets`/`tmTasks`
  index plan; above 5,000 items indexing is mandatory and must be created **while the list is
  small** (adding indexes is throttled past 20,000 items). Elevated by the full-ticket-level
  decision.
- **Q10 Users — desk only or wider?** Item-level permissions do **not** delegate; "show only
  mine" should be a single indexed `Owner`/`Author` filter, not per-item unique permissions.
*(Q12 and Q14 were answered on 2026-08-03 — see the Answered section above.)*
- **Q13 Solution-aware?** If the app moves dev → test → prod it needs **environment variables**,
  not hardcoded connections/list references.
- **Q15 Is Azure DevOps available, and can this app live in a Dataverse solution? (2026-08-03)**
  This is the only route that would retire the clipboard: **Power Platform Git integration** stores
  canvas source as `.pa.yaml` and supports *minor* edits made directly in the repo, restored on
  pull — a genuine two-way channel, and the only supported one. It needs **Azure DevOps** (the
  GitHub canvas integration is retired) and a solution. Packaging a `.msapp` by hand is a dead end
  and is not the alternative — see `docs/msapp-and-git-integration.md`. Not blocking: the code-view
  paste channel is proven and the build ships without this.
