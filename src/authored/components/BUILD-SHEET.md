# Component build sheet — GENERATED, do not edit

Regenerate with `python tools/split_components.py`. The `.pa.yaml` files beside
this one are the source of record.

## Why a component takes THREE phases

A component definition is two different things, and Studio accepts them through
two different channels:

| Part | What it is | How it gets in |
|---|---|---|
| **Contract** | custom properties + the component-level formulas backing the Output / OutputFunction / Action ones | **Typed** into the component's property pane. There is no paste gesture for this |
| **Body** | the child controls | **Pasted** via code view, exactly like a screen — `bodies/<name>.children.pa.yaml` |

But the two are **mutually dependent**, so typing everything up front doesn't work:

- the **body** references custom properties by name (`cmpSelection.Items`) — so the
  properties must exist *before* the paste;
- some **backing formulas** reference controls the body creates (`galSel.Selected`) —
  so those cannot be entered *until after* the paste. Typing one early gives you a
  name-isn't-valid error on a control that doesn't exist yet.

Hence three phases:

| Phase | Do this |
|---|---|
| **1** | Create every custom property — name, kind, type, and the `Default` for Inputs. For any row marked ⚠️ below, enter the **placeholder** formula, not the real one |
| **2** | Paste `bodies/<name>.children.pa.yaml` into the component's canvas |
| **3** | Go back and set the real backing formula on every ⚠️ row |

Rows without ⚠️ can be finished in phase 1 — they don't touch the body.

## Build order

Build only what the screens you want actually need. `cmpSelection` is the one to
do first — seven screens use it, and four of them are the editors.


---

## `cmpAppBar`

App header with a fly-out navigation rail. Reports the chosen entry; the screen navigates.

**Used by:** scrHome, scrReports, scrProjects, scrReference, scrAdmin, + the 3 skeleton variants  
**Access app scope:** `False`  
**Body:** `bodies/cmpAppBar.children.pa.yaml` (10 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `Items` | Input | Table | `=Table( { Key: 1, Title: "Home",      Icon: Icon.Home,      NeedsLicence: false }, { Key: 2, Title: "Reports",   Icon: Icon.Table,     NeedsLicence: true  }, { Key: 3, Title: "Projects",  Icon: Icon.Documents, NeedsLicence: false }, { Key: 4, Title: "Reference", Icon: Icon.Bookmark,  NeedsLicence: false }, { Key: 5, Title: "Admin",     Icon: Icon.Settings,  NeedsLicence: false } )` | the property's **Default** |
| 2 | `ActiveKey` | Input | Number | `=1` | the property's **Default** |
| 3 | `HasLicence` | Input | Boolean | `=false` | the property's **Default** |
| 4 | `AppTitle` | Input | Text | `="EQD Taskmaster"` | the property's **Default** |
| 5 | `ScreenTitle` | Input | Text | `=""` | the property's **Default** |
| 6 | `IsOpen` | Input | Boolean | `=false` | the property's **Default** |
| 7 | `SelectedKey` | Output | Number | `=galNav.Selected.Key` | ⚠️ **PHASE 3 — after the body.** Uses `galNav`, which the body creates. Create the property now with the placeholder `=0`, then set the real formula once the body is in. |
| 8 | `OnNavigate` | Event | Boolean | `` | the property's **Default** |
| 9 | `OnToggle` | Event | Boolean | `` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Width` | `=1366` |
| `Height` | `=64` |
| `Fill` | `=RGBA(0, 0, 0, 0)` |

### Formulas backing the output properties

These are the ones that must NOT be entered as a `Default` — that is exactly what got the first batch rejected. Create the property, then set its formula here.

| Output property | Formula |
|---|---|
| `SelectedKey` | `=galNav.Selected.Key` |

---

## `cmpChoicePill`

Clickable filter chip — filled when Selected, outlined otherwise; raises OnSelect.

**Used by:** (not yet instantiated)  
**Access app scope:** `False`  
**Body:** `bodies/cmpChoicePill.children.pa.yaml` (2 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `Label` | Input | Text | `="All"` | the property's **Default** |
| 2 | `Selected` | Input | Boolean | `=false` | the property's **Default** |
| 3 | `OnSelect` | Event | Boolean | `` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Height` | `=32` |
| `Width` | `=110` |
| `Fill` | `=RGBA(0, 0, 0, 0)` |

---

## `cmpConfirmDialog`

Modal confirm — scrim + card + Cancel/Confirm; app-controlled Visible; OnConfirm/OnCancel.

**Used by:** scrHome  
**Access app scope:** `False`  
**Body:** `bodies/cmpConfirmDialog.children.pa.yaml` (7 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `IsOpen` | Input | Boolean | `=false` | the property's **Default** |
| 2 | `Title` | Input | Text | `="Are you sure?"` | the property's **Default** |
| 3 | `Message` | Input | Text | `=""` | the property's **Default** |
| 4 | `ConfirmLabel` | Input | Text | `="Confirm"` | the property's **Default** |
| 5 | `CancelLabel` | Input | Text | `="Cancel"` | the property's **Default** |
| 6 | `Destructive` | Input | Boolean | `=false` | the property's **Default** |
| 7 | `OnConfirm` | Event | Boolean | `` | the property's **Default** |
| 8 | `OnCancel` | Event | Boolean | `` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Height` | `=720` |
| `Width` | `=1366` |
| `Fill` | `=RGBA(0, 0, 0, 0)` |

---

## `cmpEditableGrid`

Editable grid — staging collection, add/delete rows, single bulk-save via OnCommit.

**Used by:** (not yet instantiated)  
**Access app scope:** `False`  
**Body:** `bodies/cmpEditableGrid.children.pa.yaml` (6 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `Items` | Input | Table | `=Table({ Id: 0, Col1: "", Col2: "", Col3: "" })` | the property's **Default** |
| 2 | `EditedItems` | Output | Table | `=colGrid` | ⚠️ **PHASE 3 — after the body.** Uses `colGrid`, which the body creates. Create the property now with the placeholder `=cmpEditableGrid.Items`, then set the real formula once the body is in. |
| 3 | `RowCount` | Output | Number | `=CountRows(colGrid)` | ⚠️ **PHASE 3 — after the body.** Uses `colGrid`, which the body creates. Create the property now with the placeholder `=0`, then set the real formula once the body is in. |
| 4 | `AddRow` | Action | Boolean | `=Collect(colGrid, { Id: 0, Col1: "", Col2: "", Col3: "" }); true` | ⚠️ **PHASE 3 — after the body.** Uses `colGrid`, which the body creates. Create the property now with the placeholder `=false`, then set the real formula once the body is in. |
| 5 | `OnCommit` | Event | Boolean | `` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Height` | `=360` |
| `Width` | `=640` |
| `Fill` | `=RGBA(255, 255, 255, 1)` |
| `OnReset` | `=ClearCollect(colGrid, cmpEditableGrid.Items)` |

### Formulas backing the output properties

These are the ones that must NOT be entered as a `Default` — that is exactly what got the first batch rejected. Create the property, then set its formula here.

| Output property | Formula |
|---|---|
| `EditedItems` | `=colGrid` |
| `RowCount` | `=CountRows(colGrid)` |
| `AddRow` | `=Collect(colGrid, { Id: 0, Col1: "", Col2: "", Col3: "" }); true` |

---

## `cmpKpiRing`

SVG percent ring (Image data URI) — Percent, centre Label, AccentHex/TrackHex.

**Used by:** scrHome, scrReports, scrProject  
**Access app scope:** `False`  
**Body:** `bodies/cmpKpiRing.children.pa.yaml` (1 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `Percent` | Input | Number | `=0` | the property's **Default** |
| 2 | `Label` | Input | Text | `=""` | the property's **Default** |
| 3 | `AccentHex` | Input | Text | `="#005A9E"` | the property's **Default** |
| 4 | `TrackHex` | Input | Text | `="#E1E5EB"` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Height` | `=120` |
| `Width` | `=120` |
| `Fill` | `=RGBA(0, 0, 0, 0)` |

---

## `cmpSectionHeader`

Section header — Title, optional Subtitle, optional right-aligned action button.

**Used by:** scrProjects, scrHome, scrReports  
**Access app scope:** `False`  
**Body:** `bodies/cmpSectionHeader.children.pa.yaml` (4 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `Title` | Input | Text | `="Section"` | the property's **Default** |
| 2 | `Subtitle` | Input | Text | `=""` | the property's **Default** |
| 3 | `ActionLabel` | Input | Text | `="New"` | the property's **Default** |
| 4 | `ShowAction` | Input | Boolean | `=false` | the property's **Default** |
| 5 | `OnAction` | Event | Boolean | `` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Height` | `=60` |
| `Width` | `=640` |
| `Fill` | `=RGBA(0, 0, 0, 0)` |

---

## `cmpSelection`

Single-select strip over an Items table; outputs Selected record, raises OnChange.

**Used by:** scrProjects, scrProject, scrTask, scrProjectEdit, scrTaskEdit, scrTransactionEdit, scrIssueEdit  
**Access app scope:** `False`  
**Body:** `bodies/cmpSelection.children.pa.yaml` (1 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `Items` | Input | Table | `=Table({ Id: 1, Label: "Option A" }, { Id: 2, Label: "Option B" }, { Id: 3, Label: "Option C" })` | the property's **Default** |
| 2 | `DefaultId` | Input | Number | `=1` | the property's **Default** |
| 3 | `Selected` | Output | Record | `=If(IsBlank(galSel.Selected), First(cmpSelection.Items), galSel.Selected)` | ⚠️ **PHASE 3 — after the body.** Uses `galSel`, which the body creates. Create the property now with the placeholder `=First(cmpSelection.Items)`, then set the real formula once the body is in. |
| 4 | `OnChange` | Event | Boolean | `` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Height` | `=40` |
| `Width` | `=360` |
| `Fill` | `=RGBA(0, 0, 0, 0)` |

### Formulas backing the output properties

These are the ones that must NOT be entered as a `Default` — that is exactly what got the first batch rejected. Create the property, then set its formula here.

| Output property | Formula |
|---|---|
| `Selected` | `=If(IsBlank(galSel.Selected), First(cmpSelection.Items), galSel.Selected)` |

---

## `cmpStatusCard`

Tappable KPI card — Title, Value, Caption, Trend, Accent; raises OnSelect.

**Used by:** scrHome  
**Access app scope:** `False`  
**Body:** `bodies/cmpStatusCard.children.pa.yaml` (7 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `Title` | Input | Text | `="Metric"` | the property's **Default** |
| 2 | `Value` | Input | Text | `="0"` | the property's **Default** |
| 3 | `Caption` | Input | Text | `=""` | the property's **Default** |
| 4 | `Trend` | Input | Number | `=0` | the property's **Default** |
| 5 | `Accent` | Input | Color | `=RGBA(0, 90, 158, 1)` | the property's **Default** |
| 6 | `OnSelect` | Event | Boolean | `` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Height` | `=120` |
| `Width` | `=240` |
| `Fill` | `=RGBA(0, 0, 0, 0)` |

---

## `cmpStatusPill`

Rounded colour-coded status badge (screen-level). Inputs Label + Tone.

**Used by:** (not yet instantiated)  
**Access app scope:** `False`  
**Body:** `bodies/cmpStatusPill.children.pa.yaml` (1 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `Label` | Input | Text | `="Open"` | the property's **Default** |
| 2 | `Tone` | Input | Text | `="auto"` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Height` | `=28` |
| `Width` | `=120` |
| `Fill` | `=RGBA(0, 0, 0, 0)` |

---

## `cmpTermPicker`

Cascading managed-metadata term picker driven by the term Path; outputs the leaf term's path and label.

**Used by:** scrProjectEdit, scrTaskEdit  
**Access app scope:** `False`  
**Body:** `bodies/cmpTermPicker.children.pa.yaml` (9 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `Terms` | Input | Table | `=Table( { Label: "", Path: "" } )` | the property's **Default** |
| 2 | `Caption` | Input | Text | `="Term"` | the property's **Default** |
| 3 | `PathDelimiter` | Input | Text | `=";"` | the property's **Default** |
| 4 | `TermPath` | Output | Text | `=lblPick.Text` | ⚠️ **PHASE 3 — after the body.** Uses `lblPick`, which the body creates. Create the property now with the placeholder `=""`, then set the real formula once the body is in. |
| 5 | `TermLabel` | Output | Text | `=Coalesce( LookUp(cmpTermPicker.Terms, Path = lblPick.Text, Label), "" )` | ⚠️ **PHASE 3 — after the body.** Uses `lblPick`, which the body creates. Create the property now with the placeholder `=""`, then set the real formula once the body is in. |
| 6 | `IsComplete` | Output | Boolean | `=Len(lblPick.Text) > 0 && CountRows( Filter( cmpTermPicker.Terms, StartsWith(Path, lblPick.Text & cmpTermPicker.PathDelimiter) ) ) = 0` | ⚠️ **PHASE 3 — after the body.** Uses `lblPick`, which the body creates. Create the property now with the placeholder `=false`, then set the real formula once the body is in. |
| 7 | `OnChange` | Event | Boolean | `` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Height` | `=190` |
| `Width` | `=620` |
| `Fill` | `=RGBA(255, 255, 255, 1)` |

### Formulas backing the output properties

These are the ones that must NOT be entered as a `Default` — that is exactly what got the first batch rejected. Create the property, then set its formula here.

| Output property | Formula |
|---|---|
| `TermPath` | `=lblPick.Text` |
| `TermLabel` | `=Coalesce( LookUp(cmpTermPicker.Terms, Path = lblPick.Text, Label), "" )` |
| `IsComplete` | `=Len(lblPick.Text) > 0 && CountRows( Filter( cmpTermPicker.Terms, StartsWith(Path, lblPick.Text & cmpTermPicker.PathDelimiter) ) ) = 0` |

---

## `cmpToast`

Self-dismissing toast. The screen sets IsOpen; an internal Timer raises OnDismiss after Duration.

**Used by:** scrHome  
**Access app scope:** `False`  
**Body:** `bodies/cmpToast.children.pa.yaml` (4 control(s)) — paste last

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `IsOpen` | Input | Boolean | `=false` | the property's **Default** |
| 2 | `Message` | Input | Text | `=""` | the property's **Default** |
| 3 | `Tone` | Input | Text | `="Info"` | the property's **Default** |
| 4 | `Duration` | Input | Number | `=3000` | the property's **Default** |
| 5 | `OnDismiss` | Event | Boolean | `` | the property's **Default** |

### Component properties — set these on the component itself

| Property | Formula |
|---|---|
| `Height` | `=56` |
| `Width` | `=340` |
| `Fill` | `=RGBA(0, 0, 0, 0)` |

---

## `cmpUiKit`

Pure HtmlText-builder functions for gallery-safe pills, chips and person avatars.

**Used by:** (not yet instantiated)  
**Access app scope:** `False`  
**Body:** **none — this component has no controls.** It is built entirely from the table below; there is nothing to paste.

### Custom properties — create these first

| # | Name | Kind | Type | Default / formula | Where the formula goes |
|---|---|---|---|---|---|
| 1 | `StatusPillHtml` | OutputFunction | Text | `=With( { s: Trim(label) }, With( { t: If( tone <> "auto", tone, Switch( true, s in ["done", "complete", "completed", "closed", "approved", "active", "on track"], "Success", s in ["blocked", "overdue", "rejected", "failed", "error", "breach"], "Danger", s in ["at risk", "pending", "review", "waiting", "on hold", "hold"], "Warning", s in ["in progress", "open", "new", "todo", "to do"], "Info", "Neutral" ) ) }, With( { c: Switch(t, "Success","#31825D", "Warning","#D69828", "Danger","#C53A3A", "Info","#005A9E", "#6E7882") }, "<span style='display:inline-block;background:" & c & ";color:#fff;padding:2px 10px;border-radius:11px;font:600 12px Segoe UI,Arial,sans-serif'>" & EncodeHTML(s) & "</span>" ) ) )<br>**Parameters:** `label`: Text, `tone`: Text (optional)` | component **Properties** (below) |
| 2 | `ChoicePillHtml` | OutputFunction | Text | `=If( selected, "<span style='display:inline-block;background:#005A9E;color:#fff;padding:3px 12px;border-radius:13px;font:600 12px Segoe UI,Arial,sans-serif'>" & EncodeHTML(label) & "</span>", "<span style='display:inline-block;background:#fff;color:#005A9E;padding:2px 11px;border:1px solid #005A9E;border-radius:13px;font:600 12px Segoe UI,Arial,sans-serif'>" & EncodeHTML(label) & "</span>" )<br>**Parameters:** `label`: Text, `selected`: Boolean (optional)` | component **Properties** (below) |
| 3 | `Initials` | OutputFunction | Text | `=With( { parts: Filter(Split(Trim(name), " "), Len(Result) > 0) }, Upper( Left( First(parts).Result, 1 ) & If( CountRows(parts) > 1, Left( Last(parts).Result, 1 ), "" ) ) )<br>**Parameters:** `name`: Text` | component **Properties** (below) |
| 4 | `PersonChipHtml` | OutputFunction | Text | `=If( IsBlank(Trim(name)), "<span style='color:#6E7882;font:italic 12px Segoe UI,Arial,sans-serif'>Unassigned</span>", With( { ini: Upper( Left(First(Filter(Split(Trim(name)," "),Len(Result)>0)).Result,1) & If(CountRows(Filter(Split(Trim(name)," "),Len(Result)>0))>1, Left(Last(Filter(Split(Trim(name)," "),Len(Result)>0)).Result,1), "") ) }, "<span style='display:inline-flex;align-items:center;gap:6px;font:12px Segoe UI,Arial,sans-serif;color:#20262D'>" & "<span style='display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:11px;background:#005A9E;color:#fff;font-size:10px;font-weight:600'>" & EncodeHTML(ini) & "</span>" & EncodeHTML(name) & "</span>" ) )<br>**Parameters:** `name`: Text` | component **Properties** (below) |

### Formulas backing the output properties

These are the ones that must NOT be entered as a `Default` — that is exactly what got the first batch rejected. Create the property, then set its formula here.

| Output property | Formula |
|---|---|
| `StatusPillHtml` | `=With( { s: Trim(label) }, With( { t: If( tone <> "auto", tone, Switch( true, s in ["done", "complete", "completed", "closed", "approved", "active", "on track"], "Success", s in ["blocked", "overdue", "rejected", "failed", "error", "breach"], "Danger", s in ["at risk", "pending", "review", "waiting", "on hold", "hold"], "Warning", s in ["in progress", "open", "new", "todo", "to do"], "Info", "Neutral" ) ) }, With( { c: Switch(t, "Success","#31825D", "Warning","#D69828", "Danger","#C53A3A", "Info","#005A9E", "#6E7882") }, "<span style='display:inline-block;background:" & c & ";color:#fff;padding:2px 10px;border-radius:11px;font:600 12px Segoe UI,Arial,sans-serif'>" & EncodeHTML(s) & "</span>" ) ) )` |
| `ChoicePillHtml` | `=If( selected, "<span style='display:inline-block;background:#005A9E;color:#fff;padding:3px 12px;border-radius:13px;font:600 12px Segoe UI,Arial,sans-serif'>" & EncodeHTML(label) & "</span>", "<span style='display:inline-block;background:#fff;color:#005A9E;padding:2px 11px;border:1px solid #005A9E;border-radius:13px;font:600 12px Segoe UI,Arial,sans-serif'>" & EncodeHTML(label) & "</span>" )` |
| `Initials` | `=With( { parts: Filter(Split(Trim(name), " "), Len(Result) > 0) }, Upper( Left( First(parts).Result, 1 ) & If( CountRows(parts) > 1, Left( Last(parts).Result, 1 ), "" ) ) )` |
| `PersonChipHtml` | `=If( IsBlank(Trim(name)), "<span style='color:#6E7882;font:italic 12px Segoe UI,Arial,sans-serif'>Unassigned</span>", With( { ini: Upper( Left(First(Filter(Split(Trim(name)," "),Len(Result)>0)).Result,1) & If(CountRows(Filter(Split(Trim(name)," "),Len(Result)>0))>1, Left(Last(Filter(Split(Trim(name)," "),Len(Result)>0)).Result,1), "") ) }, "<span style='display:inline-flex;align-items:center;gap:6px;font:12px Segoe UI,Arial,sans-serif;color:#20262D'>" & "<span style='display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:11px;background:#005A9E;color:#fff;font-size:10px;font-weight:600'>" & EncodeHTML(ini) & "</span>" & EncodeHTML(name) & "</span>" ) )` |
