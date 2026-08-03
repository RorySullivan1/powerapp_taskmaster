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
- **Q11 Provisioning route** → **Manual (SharePoint UI)** *(under reconsideration — see Q11-bis).*
  High `_x0020_` internal-name risk; the schema snapshot must capture **true** internal names. No
  automated term-store sync path.

## Answered on 2026-08-03 (see `.claude/memory/INDEX.md` → Decisions)

- **Q12 Power Automate availability** → **YES, available.** Unblocks three things that were
  waiting on it: the scheduled Graph-termStore flow that populates `taskmaster_terms` (C10), the
  **flow-as-list-provisioner** route (Q11-bis, whose recommendation was explicitly conditional on
  this), and the extract flow (Q7). Note the app itself needs **no** flow at runtime — that was the
  point of the C10 cache decision.
- **Q14 FX rates** → **do not convert in the app at all.** `transaction_notional_usd` is dropped;
  Power BI converts against an FX dimension keyed on currency + trade date. Reasoning and the
  consequences (no cross-currency figure anywhere in the app; Power BI now owes the blended
  notional) are in `.claude/context/schema.md` → C5.
- **Power BI licence gate** → **soft gate.** Unlicensed users see Reports **greyed but reachable**,
  landing on the empty-state card plus the three licence-free KPI rings. Reports is never hidden —
  a hidden feature is one nobody knows to request a licence for. `gHasPowerBiLicence` stays `false`
  (everyone treated as unlicensed) until a real signal is supplied; nav and the Reports screen both
  read that one line.

## Q11-bis — reconsider provisioning: flow-as-list-provisioner (2026-08-02)

Reviewing April Dunnam's templates surfaced a **third route** that wasn't on the table when Q11
was decided (`docs/powerapp-patterns-distillation.md` §D, T18): ship provisioning as a **Power
Automate flow** that creates the 8 lists + columns from a site URL — typically "Send an HTTP
request to SharePoint" actions, or the SharePoint create-list/create-column actions.

| Route | Sets clean internal names? | Repeatable (dev→test→prod)? | Term-store sync? | Needs |
|---|---|---|---|---|
| **Manual UI** *(current pick)* | Only if hand-disciplined; **high `_x0020_` risk** | **No** — click every column by hand, 8 lists | No | Nothing extra |
| **Flow-as-provisioner** *(new candidate)* | **Yes** — internal name set explicitly at creation | **Yes** — re-runnable, one input (site URL) | Possible via HTTP calls | **Power Automate (Q12)** + work-machine tenant access |
| PnP / CSOM | Yes | Yes | **Yes** (native) | PnP tooling + auth (out of this repo's reach) |
| Graph | Yes | Yes | No (term store excluded) | Graph app reg + auth |

**Recommendation:** if **Power Automate is available (Q12)**, switch Q11 to the **flow-as-
provisioner** route — it removes the `_x0020_` risk *and* gives repeatable, environment-portable
provisioning (which also helps Q13 solution-awareness), for far less effort than clicking 8 lists
by hand. Keep **manual UI as the fallback** only if Power Automate is not available. This does
**not** solve term-store taxonomy sync natively (still needs PnP/CSOM or HTTP calls), so the
`tmIndices`/`tmLookups` taxonomy remains a separate open item regardless.

**UNBLOCKED 2026-08-03 — Q12 answered YES.** The recommendation above was explicitly conditional
on Power Automate being available, and it is, so **flow-as-provisioner is now the recommended
route** and supersedes the manual-UI pick in Q11. Manual UI remains the fallback. Still to do:
author the provisioning flow (9 lists incl. `taskmaster_terms`, internal names set explicitly at
creation, indexes applied while each list is small). Term-store taxonomy sync is a separate flow —
the same Graph termStore walk that populates `taskmaster_terms`.

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
*(Q12 and Q14 were answered on 2026-08-03 — see the Answered section above.)*
- **Q13 Solution-aware?** If the app moves dev → test → prod it needs **environment variables**,
  not hardcoded connections/list references.
