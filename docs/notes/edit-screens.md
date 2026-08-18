# Edit screens — the shared pattern, and why each part of it exists

Covers `scrProjectEdit`, `scrTaskEdit`, `scrTransactionEdit`, `scrIssueEdit` and the
`cmpTermPicker` component. Read this once; the screen headers then only carry what is
specific to them.

Everything here is shaped by one constraint: **the gap is one-way.** A wrong construct
comes back as "it didn't work", and a *silently* wrong one doesn't come back at all — it
becomes a bad row in SharePoint that Power BI reports as fact. So the recurring bias is
toward being loudly wrong over quietly wrong.

---

## Entering an edit screen

```powerapps
Set( gEditMode, "New" | "Edit" );
Set( gEditProject | gEditTask | gEditTransaction | gEditIssue, <record> );   // "Edit" only
Navigate( scr<Thing>Edit, ScreenTransition.Cover )
```

`gSelProject`, if set, pre-attaches a **new** child to that project. `scrProjects` clears it
before opening a new project, because a stale selection would silently parent the next new
item to whatever the user last opened.

| From | Action |
|---|---|
| `scrProjects` → section header "New project" | new project |
| `scrProject` → "Edit project" | edit this project |
| `scrProject` → "New task / transaction / issue" (follows the active tab) | new child, pre-attached |
| `scrProject` → tasks row, transactions row, issues row | edit that child |

All three child rows behave identically: set `gEditMode` to `"Edit"`, set the child's edit
global, navigate to the editor. There is no intermediate detail screen for any of them.
`scrTask` used to be one for tasks and was deleted 2026-08-10 — see
`.claude/memory/INDEX.md` for why a second writer for one row is a defect, not a shortcut.

## 1. Seed globals in `OnVisible`, write from the globals

Never write from a control's or a component's live state.

A `cmpSelection` strip owns its pick inside an internal gallery, and `Reset()` cannot reach
into a component from outside. After editing record A and opening record B the strip may
still be showing A's pick — and `Selected` falls back to `First(Items)` when it isn't.
Whether navigation clears it is exactly the kind of runtime detail this gap cannot verify,
and the failure mode is a wrong value written to a **required** Choice column.

Re-seeding a global in `OnVisible` and patching from that global makes the write correct
regardless of what the screen happens to be displaying. Text inputs get `Reset()` in the
same `OnVisible` so their `Default` re-reads.

## 1a. Column ARITY must match the schema, or the screen errors on load

**Applies to Person *and* Managed Metadata columns**, and both have already bitten:
`project_requestor` was provisioned multi-Person, `project_region` and `project_coverage`
multi-value MM. Symptom is identical in every case — a multi column returns a **table**, so
`Coalesce(<table>, "…")` fails because Coalesce takes its type from the first argument.

The MM read and write both assume single:

```powerapps
Coalesce( gEditProject.project_region.Value, "not set" )                        // read
project_region: LookUp( Choices([@taskmaster_projects].project_region), Path = … )  // write
```

`Choices()` itself is unaffected — it returns the term set, so the picker keeps working and only
the current-value label and the save break. That makes a multi MM column quieter than a multi
Person column, not safer.

### The Person case in detail

`schema/schema.yaml` marks every Person column `multi: false`, and the app depends on it in two
places:

```powerapps
Coalesce( gEditProject.project_requestor.DisplayName, "" )        // read, in OnVisible
project_requestor: { '@odata.type': "…SPListExpandedUser", … }    // write, in the Patch
```

If the SharePoint column is provisioned with **Allow multiple selections = Yes**, the connector
returns a **table**, so `col.DisplayName` is a single-column table and `Coalesce(<table>, "")`
fails — Coalesce takes its type from the first argument, and `""` is not a table. The write breaks
too: a single expanded-user record is not a table. Seen live on `project_requestor`, 2026-08-04,
while `project_manager` and `project_supporter` — the same formula, one column apart — were fine.

**The fix is in SharePoint, not here**: the repo is the golden source and it says single. Turn
*Allow multiple selections* off on that column. If a column genuinely needs to be multi, change
`multi:` in `schema.yaml` first, then both the read (`First(col).DisplayName`) and the write (a
table of expanded-user records) have to change for that column — it is not a formula tweak.

Every picker global has exactly **one** record schema:

| Kind | Schema | "nothing picked" | test |
|---|---|---|---|
| Person | `{ DisplayName, Mail }` | `{ DisplayName: "", Mail: "" }` | `Len(g.Mail) = 0` |
| Lookup | `{ Id, Value }` | `{ Id: 0, Value: "" }` | `g.Id <= 0` |

A global assigned two different record shapes is a type conflict — which is why a person
picked from `Office365Users.SearchUser` is reduced to those two fields rather than stored
whole. The empty record, not `Blank()`, is the null state: a global whose type was inferred
from `Blank()` and later assigned a record is asking for trouble across a gap with no
round-trip.

## 3. Overlay picker galleries are declared last

Choice fields use `ModernCombobox@1.0.0` (`.Selected.Value`, with `SelectMultiple: =false`).
Lookups and people are still search-plus-results, because they query a data source rather than a
fixed list:

- **People search uses `SearchUserV2`, not `SearchUser`.** The V1 docs claim `searchTerm` covers
  display name, given name, surname, mail, mail nickname and UPN, but in practice V1 matched only
  the address — people could not be found by name. MS's own current worked example uses V2, which
  returns a wrapper, so the Items formula ends in `.value`:

  ```powerapps
  Office365Users.SearchUserV2({ searchTerm: txtPrManagerSearch.Text, top: 8 }).value
  ```

  All 8 people pickers use this form. The row already leads with `DisplayName`.

- **Lookup / person** → a search `TextInput` (`DelayOutput: true`) plus a results `Gallery`
  that is `Visible` only at 2+ characters with nothing yet chosen. Z-order is positional in
  this dialect, so declaring the gallery at the **end** of `Children:` floats it above the
  fields it covers — which is what makes it behave like a dropdown.

  **Two rules that came out of the first render (2026-08-04), because the original layout was
  unusable:**

  1. **One picker open at a time.** Each search box does `OnChange: =Set(gXPicker, "<key>")`
     and each results gallery requires `gXPicker = "<key>"` on top of its own conditions.
     Without this, several dropdowns can be open at once and — since they sit 66px apart but
     are 132px tall — the later-declared one covers the lower half of the earlier one, so
     **some rows simply cannot be clicked**.
  2. **The results gallery sits BESIDE its search box, not under it** — `X = input.X +
     input.Width + 8`, same `Y`, width 280. Stacked pickers are 66px apart, so a 132px
     dropdown opening downwards covers the next *two* search boxes and locks the user out of
     them until they clear the current search. Opening sideways covers only the chip label and
     empty space.

  **Both rules are ABSOLUTE-LAYOUT workarounds, and `scrProjectEdit` no longer needs either.**
  Inside an auto-layout container a hidden child takes no space, so the results gallery is a
  *sibling* of its row, declared immediately after it, full width, `Height: =132`, visible only
  at 2+ typed characters with nothing yet picked. It expands the column and collapses again —
  no z-order, no covering, no one-at-a-time gate, and nothing can ever sit on a row the user
  needs to click. **Prefer this on any screen already built on containers**; rules 1 and 2 stand
  for the screens still laid out absolutely.

  Two things the gallery must NOT be gated on, both found live on 2026-08-05:
  - **the modal's own `g*Open` flag** — that leaves it permanently open, and if it shares its
    chip's X/Y it hides the pick entirely while querying `SearchUserV2` with an empty term;
  - **nothing at all on clear** — clearing a pick must `Reset()` the search box too, or the
    stale term re-opens the gallery the instant the chip is cleared.

  The pick itself collapses to a flat `Classic/Button` reading `Name  ✕`
  (`DisplayMode.Disabled` when empty), which is one control instead of a label plus a separate
  clear icon, and gives the clear action a real hit target.
- **Dates** → `ModernDatePicker@1.0.0`, read as `.SelectedDate` (Blank when unset). The old
  pattern — a text box parsed with `DateValue()` plus an echo label rendering `12 Aug 2026` or
  `⚠ not a date` — is **retired across all four edit screens**: a picker cannot produce an
  unparseable date, so there is nothing left to echo and nothing left to parse. Dates now travel
  as real date values from control to collection to `Patch`.
- **Numbers** → `ModernNumberInput@1.0.0`, read as `.Value` (a number). Same reasoning: the two
  notional fields no longer go through `Value()` and no longer need an `IsError` guard.
- **Choice** → `cmpSelection` strips, **but only while the labels are short**. Optional Choices
  carry a real `"(none)"` option, because `{Value: ""}` is not a legal write and an optional column
  has to be clearable. The strip's label size is the `FontSize` input (default **11**), and a
  component cannot read `gTheme.Size.*`, so tune it on the instance.
  **A strip lays every option across ONE row** (`WrapCount = CountRows(Items)`), so each chip gets
  `Width / N` — which is why long values need a `ModernCombobox` instead. Both stage
  (`cboTkStage`, 2026-08-07) and issue status (`cboIssStatus`, 2026-08-12, when its values became
  `"Closed - Unresolved"` and friends) left the strip for exactly that reason. Health, type and
  impact are still strips and should stay strips.
  **If you swap a strip for a combo box, PIN BOTH CHILDREN** (`FillPortions: =0` +
  `LayoutMinHeight`). Auto-layout children are flexible by default, so the declared heights are
  otherwise ignored and the space splits evenly — a strip squashes gracefully, a combo box does not.

## 4. Required fields in one Patch; optional ones after, guarded

Power Fx cannot conditionally omit a field from a record literal. So:

```powerapps
// set it when chosen; clear it only when editing (nothing to clear on a new record)
If( gChoice <> "(none)",
    IfError( Set( gOpt, Patch(list, saved, { col: { Value: gChoice } }) ),
             Set( gWarn, gWarn & "the col didn't stick: " & FirstError.Message & "   " ) ),
    gEditMode = "Edit",
    IfError( Set( gOpt, Patch(list, saved, { col: Blank() }) ),
             Set( gWarn, gWarn & "the col didn't clear: " & FirstError.Message & "   " ) ) )
```

The `Set` wrappers are **not** decoration — see §5a. `gOpt` is never read; it exists only so both
`IfError` arguments have the same type.

More round trips, but a failure is attributable to one field instead of taking the whole
form down — and the two risky shapes (**expanded user**, **expanded taxonomy**) get their
own `Patch` each, so neither can lose the rest of the record.

## 5. Success is never assumed

`Errors()` returns a **table**, so `IsError(Errors(…))` is always false and would never gate
anything. `FirstError` only exists inside `IfError`'s fallback. Hence:

```powerapps
Set( gErr, "" );
IfError( Set( gSaved, Patch(…) ), Set( gErr, FirstError.Message ) );
If( Len(gErr) > 0, Notify("Couldn't save: " & gErr, NotificationType.Error) );
If( Len(gErr) = 0, …everything that says it worked… )
```

Each `IfError` argument is a **single statement** — no `;` chains inside a function argument.

## 5a. Every `IfError` argument must be the SAME TYPE

This is the rule that bit hardest. MS Learn: *"IfError returns the value of one of its arguments.
The types of all values that might be returned by IfError must be compatible"* — followed by a note
that **currently ALL arguments must be compatible**, not merely the ones that could be returned.

So the idiom the docs themselves print,

```powerapps
IfError( Patch(list, rec, {…}), Notify("didn't save") )       // REJECTED
```

fails in Studio with **"expecting a record"**: `Patch` returns a record, `Notify` a boolean. The
same applies to `IfError(Patch(…), Set(…))` and to a three-arm `IfError(Patch(…), Collect(a,…),
Collect(b,…))` where the two `Collect`s target differently-shaped tables.

The fix is uniform — **make every arm a `Set`**:

```powerapps
IfError( Set( gTmp, Patch(list, rec, {…}) ),
         Set( gErr, FirstError.Message ) );
If( Len(gErr) > 0, Notify("Couldn't save: " & gErr, NotificationType.Error) )
```

`FirstError` is only in scope *inside* the replacement, which is why the message is stashed in a
variable and notified afterwards. Warnings from the optional-column pass accumulate into one
`gXWarn` string and produce a single banner instead of up to ten.

Where a `Set` would be unsafe — inside `ForAll`, whose iteration order is not guaranteed — force
the arms to text instead: `IfError( Text(Patch(…).ID), FirstError.Message, "" )`. An empty result
means the row was written. That is how `scrProjectEdit` records per-row outcomes for staged
children.

Not affected: `IfError(Text(…), "⚠ not a date")` and `IfError(DateValue(…), Blank())` — text/text
and date/blank are already compatible. The validator flags only a genuine mix of behaviour
functions.

## 6. Complex column writes — give the connector its own shape wherever you can

**Managed metadata** is written by handing back the record `Choices()` produced, found by the
path the picker resolved:

```powerapps
project_region: LookUp( Choices([@taskmaster_projects].project_region), Path = gPrRegionPath )
```

No hand-built `SPListExpandedTaxonomy` literal is authored anywhere in this repo. That literal
was community-reported only, and depended on getting `WssId: -1` and the exact field names
right; passing back the connector's own record removes the whole class of risk. Fallback, if
this ever fails: `docs/managed-metadata-picker.md` §5.

**Person** still has no equivalent — there is no `Choices()` for a Person column — so it is the
one hand-built shape left, and therefore the highest-risk write in the app:

```powerapps
{ '@odata.type': "#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser",
  Claims: gClaimPrefix & Lower(mail), DisplayName: name, Email: mail,
  Department: "", JobTitle: "", Picture: "" }
```

It stays isolated in its own guarded `Patch` for that reason.

## 7. Managed metadata on edit: untouched unless re-picked

What the connector returns for an **existing** MM value isn't in the picker's path form, so on
an **edit** the pickers start empty and the column is left alone unless the user actively picks
a new leaf; the current label is shown beside the picker so nothing looks lost. On a **new**
project, `project_region` and `project_type` are required by the list, so both must reach a leaf
before Save enables — and they go in with the insert, not afterwards.

`cmpTermPicker.IsComplete` is the leaf test: it counts terms sitting below the pick, from the
same data the cascade walks, so it cannot disagree with what is on screen.

The picker reads the term store **directly** — `ShowColumns(Choices([@list].mmColumn), Label,
Path)`. There is no terms list. `Path` already carries the full hierarchy, so the cascade is
prefix matching and the term store stays the only copy of the vocabulary.

---

## `scrProjectEdit` — creating children with the parent

A task, transaction or issue carries a **required** Lookup to `taskmaster_projects`, and a
Lookup needs an ID that only exists after the insert. So children are staged locally
(`colNewTasks` / `colNewTransactions` / `colNewIssues`, keyed by a local `sid`) and written
only once the project's `Patch` has returned a record.

The parent is already saved by the time a child can fail, so a failure cannot be rolled
back. Rather than pretend otherwise:

1. successful children are **removed** from staging;
2. failures **stay** in staging and are listed on screen with their error;
3. the screen flips to `gEditMode = "Edit"` against the project it just created.

Step 3 is load-bearing: pressing Save again then retries only what failed and **cannot
create a second project**.

`IfError(value, fallback, default)` is what records per-row success — the third argument is
returned when nothing errored, so one pass classifies every row.

**No tabs.** The screen is ONE scrolling auto-layout column (`frmPrScroll`) with a headed
section per former tab: Details · People · Classification · Tasks · Transactions · Issues. The
old claim that "a canvas screen does not scroll" is wrong — `LayoutOverflowY:
=LayoutOverflow.Scroll` on a `GroupContainer` scrolls, and it is strictly better than tabs here
because the container also makes every child immune to the X/Y freeze.

**Staged children get a full people picker**, inside the modal that stages them — not the old
two-option **Manager / Me** strip. A task lead, sales owner or assignee can be anyone in the
directory, resolved at *staging* time so a later change of project manager cannot silently
reassign rows the user already added. The modals are what made this affordable: the pickers live
in a card that is only rendered while its `g*Open` flag is true, so they cost nothing on the
form itself.

## Known limits, stated rather than hidden

- **`task_output_asset` is not editable.** `asset_library` has no schema, so there is nothing
  to bind to. The task editor says so on screen instead of offering a control that can't work.
- **The Output section carries a conditional requirement the list cannot.** With the section on,
  an audience is required to save at all, and a non-`Internal Only` audience additionally needs an
  approval id to reach stage `Completed`. Enforced only in `lblTkMissing` — see
  *Constraints SharePoint cannot hold* in `.claude/context/schema.md`.
- **No cross-currency figure exists in the app** (Q14). The transaction form writes the native
  notional and its currency only; conversion happens in Power BI against an FX dimension keyed on
  currency + trade date. `scrProject`'s transactions tab totals per currency and says so. Do not
  reintroduce a rate table to "just add a total" — a write-time rate freezes a number nothing
  downstream can correct.
- **`Choices()` on an MM column is capped at 20 terms** by the connector, not configurable. If a
  vocabulary outgrows it, terms silently go missing from the picker; the fix is to feed that one
  instance from a Power Automate call in the same `{Label, Path}` shape — the component doesn't
  change. The `Path` delimiter (`;`) is also not first-party documented, so it is a component
  input and the picker prints a raw path on screen to settle it at first paste.
- **A date picker with no `DefaultDate` silently wipes the stored date on an edit.** The control
  opens blank, and a `Patch` writing `dtp.SelectedDate` unconditionally then overwrites the real
  value with `Blank()`. No error, no warning — found live on `scrProjectEdit`'s
  `project_date_start` / `project_date_target`, 2026-08-05. **Every date picker on an edit path
  needs `DefaultDate` seeded from the edit record AND a `Reset()` in `OnVisible`.** (This
  supersedes the old "dates are typed, not picked" limit — `DateValue()` parsing was retired
  across all four edit screens on 2026-08-04.)
- **A hardcoded combobox `Items` array drifts from the list exactly like an invented column name
  does**, and the validator does not look inside array literals. `scrProjectEdit` shipped
  "In Progress"/"Resolved" for `issue_status` and "Medium" for `issue_impact`, none of which are
  members of those columns. Check every `Items: =[…]` against the Choice column's `values:` in
  `schema/schema.yaml` before hand-off.
- **A stale component strip can display a value the form will not write.** Point 1 makes the
  write correct, not the display. If that becomes confusing in use, it is a real thing to fix
  — but it is the safe direction of the two.
