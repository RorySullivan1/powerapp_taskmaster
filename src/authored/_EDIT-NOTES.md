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
| `scrProject` → transactions row, issues row | edit that child |
| `scrTask` → "All fields…" | full edit of the current task |

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

## 2. Normalised picker records

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

No `ComboBox` or `DatePicker` token is grounded, so there are no dropdowns. Instead:

- **Lookup / person** → a search `TextInput` (`DelayOutput: true`) plus a results `Gallery`
  that is `Visible` only at 2+ characters with nothing yet chosen. Z-order is positional in
  this dialect, so declaring the gallery at the **end** of `Children:` floats it above the
  fields it covers — which is what makes it behave like a dropdown.
- **Dates** → a text box parsed with `DateValue()`, plus an echo label that renders the parse
  (`12 Aug 2026`, or `⚠ not a date`). A mis-typed date cannot be silently stored as `Blank()`
  without the user seeing it.
- **Choice** → `cmpSelection` strips. Optional Choices carry a real `"(none)"` option,
  because `{Value: ""}` is not a legal write and an optional column has to be clearable.

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
  Claims: ClaimPrefix & Lower(mail), DisplayName: name, Email: mail,
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

Five tabs (Details · Classification · Tasks · Transactions · Issues) because a canvas screen
does not scroll.

Staged children take their owner from a two-option strip — **Manager** or **Me** — resolved
at *staging* time, not at save time, so a later change of project manager cannot silently
reassign rows the user already added. A full people picker per staged row would be four more
overlay galleries on an already dense screen, and reassigning is one click on the child
afterwards.

## Known limits, stated rather than hidden

- **`task_output_asset` is not editable.** `asset_library` has no schema, so there is nothing
  to bind to. The task editor says so on screen instead of offering a control that can't work.
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
- **Dates are typed, not picked.** Locale governs how `DateValue()` reads `dd/mm/yyyy`; the
  echo label is the check. A grounded `DatePicker` token would replace this whole pattern.
- **A stale component strip can display a value the form will not write.** Point 1 makes the
  write correct, not the display. If that becomes confusing in use, it is a real thing to fix
  — but it is the safe direction of the two.
