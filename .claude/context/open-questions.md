# Open questions

Unresolved decisions that will shape the schema, the app, or the provisioning route. Answered
ones are recorded (with their reasoning) in the `session-memory` Decisions ledger, not here —
this doc holds only what is **still open**. Resolve a question → move it to memory as a
decision and delete it here.

## Answered on 2026-07-26 (see `.claude/memory/INDEX.md` → Decisions)

- **Q1 Ticket-level rows** → **Yes, full ticket-level as the primary store.** `tmTickets`
  holds every trade row and drives figures. Consequence: max delegation/threshold exposure →
  indexing mandatory, every query delegable.
- **Q2 Power BI licensing** → **Not everyone is licensed.** Dashboard can't carry core nav;
  native licence-independent navigation + a real empty state. (Sub-items below still open.)
- **Q11 Provisioning route** → **Manual (SharePoint UI).** High `_x0020_` internal-name risk;
  the schema snapshot must capture **true** internal names. No automated term-store sync path.

## Blocking-adjacent (elevated by this build)

- **Q2b Power BI workspace / refresh / embedded-vs-linked.** Which workspace hosts the report,
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
- **Q12 Power Automate availability.** Needed for the extract flow, optional write-time rollup
  counters, and any term-store sync. With manual provisioning and no PnP/CSOM, this is the only
  automation lever in scope.
- **Q13 Solution-aware?** If the app moves dev → test → prod it needs **environment variables**,
  not hardcoded connections/list references.
