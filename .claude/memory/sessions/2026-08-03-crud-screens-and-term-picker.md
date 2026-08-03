# 2026-08-03 — schema intake → data layer → validator → C10 → the CRUD screens

Covers the stretch from the photographed schema through to the four create/edit screens and
the cascading managed-metadata picker. Decisions are in `INDEX.md`; this is the reasoning.

## 1. Schema intake and the golden-source inversion

Seven lists arrived as phone photos. Two things came out of transcribing them:

- **The repo defines the backend, SharePoint applies it.** `schema/schema.yaml` became the
  golden source rather than a snapshot of what someone had already built. That mirrors the
  one-way gap exactly: internal names freeze at creation, and there is no channel to read
  the real ones back, so the only safe model is "decide here, then create to match".
- **`.claude/context/schema.md` never repeats a column.** It holds shape, join costs and
  consequences and points at the YAML for names. Two copies of a column list is a drift bug
  waiting to happen.

Consequences C1–C10 were raised as `open_recommendations` and settled one at a time. The
ones that changed the app rather than the schema:

- **C1** multi-person → a single indexed `*_supporter`. "Show me my work" is now a delegable
  `lead.Email = me || supporter.Email = me`; multi-person has no delegable filter at all.
- **C3** `project_perc_completion` had no writer. It is now a weighted mean of child task
  stages, written **app-side** — the app patches the parent whenever a task is saved. Cost,
  stated rather than hidden: a stage edited directly in SharePoint leaves it stale.
- **C5** cross-currency totals were meaningless, so `transaction_notional_usd` normalised at
  write time. That obligation landed on the transaction form in this session (see §5).
- **C9** the three lifecycle Choices were optional, so blank rows fell out of every
  enumerated filter — a silent undercount. Made required with defaults.

## 2. The component paste failure, and the only check we have

Studio rejected the components with *"expecting 'SequenceStart' not 'MappingStart'"*. There
is no return channel to inspect, so the fix came from Microsoft's official **pa-yaml v3.0
schema**: `Parameters` must be a sequence (ours were mappings), and `Default` is not allowed
on Output / OutputFunction / Action properties — their formula belongs in the component's
`Properties:` map.

That produced `tools/validate_pa_yaml.py` against a vendored copy of the schema. It is the
**only** pre-paste check that exists on this side of the gap, and it has caught real errors
since — including plain-YAML breakage from `=Set(g, { Id: 0 })` style one-liners, where the
`: ` inside the Power Fx record is a YAML mapping indicator. Anything containing `: ` is now
authored as a block scalar.

## 3. C10 — managed metadata, and why the cache won

`project_region` and `project_type` are **required** Managed Metadata, so without an MM write
path no project can be created from the app at all. The user's proposal was: detect nesting as
the user selects, generate another dropdown per level until the depth is met, and push the
last term's GUID into the column. Research (`docs/managed-metadata-picker.md`) confirmed both
halves, with one important asymmetry:

| | Status |
|---|---|
| Reading the hierarchy — Graph termStore `children` endpoints, GA Aug 2021 | **First-party confirmed.** Nesting detection falls out of the API. `TermStore.Read.All`, **delegated only** — app-only is not supported |
| Writing the column value — `SPListExpandedTaxonomy` + `WssId: -1` | **Community-confirmed only.** The single riskiest construct in the app |

The old note "Graph doesn't support managed metadata" turned out to be narrower than it read:
it applies to the *list column value*, not the term store. Read terms with Graph, write the
column with the SharePoint connector.

Then the architecture choice — live Graph per level, or a cached list. **Cache, decided.**
`taskmaster_terms` is now a real list in the golden source (flat, one row per term, with a
parent pointer), and the cascade is ordinary delegable `Filter`s on the indexed
`term_parent_guid`. The deciding argument was not performance: a per-level flow call makes
every create form depend on a flow being healthy at runtime, and a runtime dependency is the
one thing that cannot be debugged across this gap. With the cache, a dead refresh degrades to
a stale vocabulary; the form still works.

This also **narrows Q12** rather than resolving it. The app is authored and pastes with no
flow at all; what still needs Power Automate is *populating* the list — and a small vocabulary
can be hand-seeded in the meantime.

## 4. `cmpTermPicker` — two decisions that are load-bearing

Four progressively-revealed vertical galleries, one per level. A level appears when its Items
have more than the sentinel row, which is the nesting detection. Depth is discovered from the
data; the number of *placed* levels is fixed at four because a canvas app cannot instantiate
controls at runtime and nested galleries are not supported.

**The sentinel row.** A gallery's `Selected` returns its first row until the user touches it.
Without a `"— select —"` row whose guid is `""`, the picker would auto-select a whole path the
user never chose — into a *required* column. `Coalesce` treats `""` as blank, which is why the
sentinel's guid is an empty string rather than a marker value.

**Chain validation.** If the user changes level 1 after picking level 2, whether the level-2
gallery clears its selection is exactly the sort of runtime detail this gap cannot verify. So
a level's value counts only if that row is genuinely a child of the level above. A stale
deeper pick fails the test and is discarded rather than written. The whole resolution runs
once on a hidden label (`lblPick`) and all four outputs read it — a control property is the
grounded way to compute once and read four times, since a custom property referencing another
custom property of the same component is unverified.

`IsComplete` counts children rather than trusting the cached `term_is_leaf` flag: the flag is
only as good as the last refresh; the child rows are the same data the cascade already walks.

## 5. The four edit screens

Full pattern in `src/authored/_EDIT-NOTES.md`. The parts worth remembering:

- **Seed globals in `OnVisible`, write from the globals.** Same defence as `scrTask`: a
  component's internal selection cannot be reset from outside, so the write must not depend
  on what the screen is displaying.
- **No ComboBox, no DatePicker.** Neither token is grounded. Lookups and people are search
  box + overlay gallery (declared last, so positional z-order floats them); dates are typed
  and parsed with `DateValue()`, with an echo label so a bad parse is visible rather than
  silently stored as `Blank()`.
- **Guarded optional patches.** Power Fx cannot conditionally omit a field from a record
  literal, and `{Value: ""}` is not a legal Choice write. Each optional field gets its own
  `Patch`, which also isolates the two community-confirmed shapes (expanded user, expanded
  taxonomy) so neither can take the rest of the record down.
- **The success gate.** `Errors()` returns a table, and `FirstError` only exists inside
  `IfError`'s fallback. So the fallback stashes `FirstError.Message` into a `g*Err` variable
  and everything that says "saved" sits behind `Len(g*Err) = 0`. Every `IfError` argument is
  a single statement — no `;` chains inside a function argument.
- **People need a connector.** `Office365Users.SearchUser` is first-party and returns exactly
  `DisplayName` / `Mail`. The cost is a Studio prerequisite: the connection must be added
  *before* the edit screens are pasted, or the paste fails on an unrecognised name. That is
  now a numbered step in HANDOFF.
- **C5 landed here.** The transaction form writes `transaction_notional_usd` in the same
  statement as the native notional, using a static `FxToUsd` table in `App.Formulas`, and
  echoes the USD figure live so the rate is not hidden from whoever books the trade. The
  rates are placeholders and will go stale — raised as **Q14**. The form refuses to save a
  notional whose currency has no rate rather than quietly multiplying by 1.

## 6. `scrProjectEdit` — creating children with the parent

The user asked for the project screen to add tasks, transactions and issues *while creating
the project*. Every child carries a **required** Lookup to `taskmaster_projects`, and a
Lookup needs an ID that only exists after the insert — so children are staged locally and
written once the parent's `Patch` returns a record.

The interesting part is failure. The parent is already saved by then, so nothing can be
rolled back, and pretending otherwise would silently drop the user's work. Instead:
successes are removed from staging, failures stay and are listed with their error, and the
screen **flips to Edit mode against the project it just created**. That flip is load-bearing:
pressing Save again retries only what failed and cannot create a second project.

`IfError(value, fallback, default)` classifies each row in one pass — the third argument is
what comes back when nothing errored.

Owners for staged children come from a two-option strip (Manager / Me), resolved at *staging*
time so a later change of project manager cannot silently reassign rows already added. Five
tabs, because a canvas screen does not scroll.

## Where this leaves things

Authored and validating (22/22), **nothing landed**. The real gates are external: the lists
are not provisioned, `taskmaster_terms` has no rows, and the two community-confirmed write
shapes have never been executed against this tenant. The cheapest way to retire most of that
risk is one project saved with one region — if that MM write lands, the riskiest construct in
the app is proven for the price of a single paste.
