# BUILD BOOK — one linear pass to build the app in Studio

A single, ordered, tick-as-you-go checklist. Everything you need to build each unit is **on this
page** — component contracts are inlined so you're not flipping between files while you type.

- **Companion docs:** `HANDOFF.md` (how the transfer works + current state), `paste-log.md` (I keep
  it from your reports), `src/authored/components/BUILD-SHEET.md` (generated source of truth for the
  contracts — **if anything here disagrees with BUILD-SHEET, BUILD-SHEET wins**).
- **Golden rule:** paste one unit at a time onto a blank target, then tell me two things — **did it
  land?** and **what suffix did Studio add?** (`galProjects` → `galProjects_1`). Rename back before
  moving on; screens reference controls by name.

## What crosses which way (validated this session)

| Piece | How it gets in | Proven? |
|---|---|---|
| Screens (`scr*.pa.yaml`) | Code view → **Paste code** | ✅ `scrAdmin` landed; the pac-packed shell app also opened |
| `App.Formulas` | **Formula bar** (App has no code view) | route confirmed |
| Component **body** | Code view → paste `bodies/<name>.children.pa.yaml` | ✅ components landed |
| Component **contract** (custom properties) | **Typed by hand in Studio** — no paste exists | the only hand-build |
| Data binding | provision lists → add as data sources → paste data screens | blocked until lists exist |

> **The `.msapp` route is closed for components.** `pac` refuses to author component custom
> properties (`PA3004: … use Power Apps Studio to edit component definitions`). Packing only helps
> for data-independent *screens*. Contracts are Studio-only — that's why they're typed below.

## Pre-flight (once)

- [ ] Get the files on the work machine (clone/pull, or GitHub → **Raw** → copy). Copy files
      **whole**; don't retype.
- [ ] `python tools/validate_pa_yaml.py` → expect **22/22 valid**. Re-copy from `main` right before
      each paste (a stale local copy is invisible from my side).
- [ ] Studio: create the canvas app (**tablet** layout), turn on the **Power Fx formula bar**
      (Settings → General), allow clipboard for `make.powerapps.com`.

---

# PHASE A — needs nothing provisioned (do this now)

## A0 · Smoke-test the channel (5 min)

- [ ] Create a blank screen, rename **`scrReference`**, paste `src/authored/scrReference.pa.yaml`
      via right-click → **Paste code**.
- [ ] **Report: did it paste?** If not, send the error and stop — everything uses the same dialect.
      *(The pac shell `.msapp` already opened, so this should land.)*

## A1 · Create all 11 screens (names are exact — `NavMenu` references them)

- [ ] `scrHome`  · `scrReports` · `scrProjects` · `scrReference` · `scrAdmin`  *(nav menu)*
- [ ] `scrProject` · `scrTask`  *(detail — reached by Navigate)*
- [ ] `scrProjectEdit` · `scrTaskEdit` · `scrTransactionEdit` · `scrIssueEdit`  *(create/edit)*

Leave them empty for now except `scrReference` (done) and `scrAdmin` (paste `scrAdmin.pa.yaml` now —
also a pure shell).

- [ ] Paste `src/authored/scrAdmin.pa.yaml`.

## A1b · (Optional) Stand up a fully navigable app *now* — skeleton screens

A composed screen (`scrHome`/`scrReports`/`scrProjects`) can't paste until its components exist
**and** its lists are provisioned. To get a navigable 5-screen app immediately — before either —
paste the **skeleton variants** instead. They're component-free and data-free: header + nav +
a titled placeholder, needing only `App.Formulas` (do Stage A3 first, or accept an unstyled nav
until it lands).

- [ ] `src/authored/variants/scrHome.skeleton.pa.yaml`  → onto `scrHome`
- [ ] `src/authored/variants/scrReports.skeleton.pa.yaml`  → onto `scrReports`
- [ ] `src/authored/variants/scrProjects.skeleton.pa.yaml`  → onto `scrProjects`

Now all five nav screens navigate to each other. Later, when you've built the components (A2) and
provisioned the lists (Phase B), **replace** each skeleton by pasting the full `scr*.pa.yaml` over
a fresh blank screen. Skeletons are a scaffold, not the destination — they carry no data or KPIs.

## A2 · Build the components you need

**THREE phases per component, not two** — the contract and the body depend on each other:

1. **Create every custom property** (Input/Output/Event/Action, exact type). Set Input `Default`s.
   For anything marked ⚠️ below, enter the **placeholder** — its real formula names a control the
   body hasn't created yet, and typing it now gives a name-isn't-valid error.
2. **Paste** `bodies/<name>.children.pa.yaml` into the component canvas. (The body references the
   properties by name, which is why phase 1 comes first.)
3. **Go back and set the real formula** on every ⚠️ property.

`BUILD-SHEET.md` marks the ⚠️ rows per component and gives each placeholder.

> **Check the property KIND before you change a formula.** An **Output**'s formula runs inside the
> component and can reference its child controls freely. An **Input**'s `Default` runs in the
> *consumer's* scope and cannot see them — so creating an output as an input gives a name-scope
> error pointing at the child control, which looks like a formula problem and isn't. Every ⚠️ row
> below is an **Output**.

> Watch items: **`cmpConfirmDialog`'s input is `IsOpen`, not `Visible`** (a `Visible` custom prop
> collides with the built-in). **`HtmlViewer@2.1.0` is now confirmed** — `cmpStatusPill`'s body
> pasted with it, and `cmpToast`'s timer is **`Timer`** (no `Classic/` prefix, no version suffix).
> **Every control token in the kit is now confirmed** — the validator emits no token warnings.

### `cmpSelection`  *(build first — 7 screens use it)*  · body: 1 control
- [ ] `Items` — Input · Table · Default `=Table({ Id: 1, Label: "Option A" }, { Id: 2, Label: "Option B" }, { Id: 3, Label: "Option C" })`
- [ ] `DefaultId` — Input · Number · Default `=1`
- [ ] `Selected` — **Output** · Record · ⚠️ **phase 3** — placeholder `=First(cmpSelection.Items)`; after the body, set `=If(IsBlank(galSel.Selected), First(cmpSelection.Items), galSel.Selected)`
- [ ] `OnChange` — Event
- [ ] Component props: `Height=40` · `Width=360` · `Fill=RGBA(0,0,0,0)`
- [ ] Paste `bodies/cmpSelection.children.pa.yaml`

### `cmpSectionHeader`  · body: 4 controls
- [ ] `Title` — Input · Text · `="Section"`
- [ ] `Subtitle` — Input · Text · `=""`
- [ ] `ActionLabel` — Input · Text · `="New"`
- [ ] `ShowAction` — Input · Boolean · `=false`
- [ ] `OnAction` — Event
- [ ] Component props: `Height=60` · `Width=640` · `Fill=RGBA(0,0,0,0)`
- [ ] Paste `bodies/cmpSectionHeader.children.pa.yaml`

### `cmpStatusCard`  · body: 7 controls
- [ ] `Title` — Input · Text · `="Metric"`
- [ ] `Value` — Input · Text · `="0"`
- [ ] `Caption` — Input · Text · `=""`
- [ ] `Trend` — Input · Number · `=0`
- [ ] `Accent` — Input · Color · `=RGBA(0, 90, 158, 1)`
- [ ] `OnSelect` — Event
- [ ] Component props: `Height=120` · `Width=240` · `Fill=RGBA(0,0,0,0)`
- [ ] Paste `bodies/cmpStatusCard.children.pa.yaml`

### `cmpKpiRing`  · body: 1 control
- [ ] `Percent` — Input · Number · `=0`
- [ ] `Label` — Input · Text · `=""`
- [ ] `AccentHex` — Input · Text · `="#005A9E"`
- [ ] `TrackHex` — Input · Text · `="#E1E5EB"`
- [ ] Component props: `Height=120` · `Width=120` · `Fill=RGBA(0,0,0,0)`
- [ ] Paste `bodies/cmpKpiRing.children.pa.yaml`

### `cmpToast`  · body: 4 controls
- [ ] `Message` — Input · Text · `=""`
- [ ] `Tone` — Input · Text · `="Info"`
- [ ] `Duration` — Input · Number · `=3000`
- [ ] `Show` — Action · ⚠️ **phase 3** — create with placeholder `=true`; after the body, set `=Set(_show, true); Reset(tmrToast); true`
- [ ] `OnDismiss` — Event
- [ ] Component props: `Height=56` · `Width=340` · `Fill=RGBA(0,0,0,0)`
- [ ] Paste `bodies/cmpToast.children.pa.yaml`  *(Timer token unverified — report if rejected)*

### `cmpConfirmDialog`  · body: 7 controls
- [ ] `IsOpen` — Input · Boolean · `=false`  *(NOT `Visible`)*
- [ ] `Title` — Input · Text · `="Are you sure?"`
- [ ] `Message` — Input · Text · `=""`
- [ ] `ConfirmLabel` — Input · Text · `="Confirm"`
- [ ] `CancelLabel` — Input · Text · `="Cancel"`
- [ ] `Destructive` — Input · Boolean · `=false`
- [ ] `OnConfirm` — Event · `OnCancel` — Event
- [ ] Component props: `Height=720` · `Width=1366` · `Fill=RGBA(0,0,0,0)`
- [ ] Paste `bodies/cmpConfirmDialog.children.pa.yaml`

### `cmpTermPicker`  *(build carefully — it feeds a required Managed-Metadata column, C10)*  · body: 9 controls
- [ ] `Terms` — Input · Table · `=Table( { Label: "", Path: "" } )`
- [ ] `Caption` — Input · Text · `="Term"`
- [ ] `PathDelimiter` — Input · Text · `=";"`
- [ ] `TermPath` — Output · Text · ⚠️ **phase 3** — placeholder `=""`; after the body, `=lblPick.Text`
- [ ] `TermLabel` — **Output** · Text · ⚠️ **phase 3** — placeholder `=""`; after the body, `=Coalesce( LookUp(cmpTermPicker.Terms, Path = lblPick.Text, Label), "" )`
- [ ] `IsComplete` — **Output** · Boolean · ⚠️ **phase 3** — placeholder `=false`; after the body, `=Len(lblPick.Text) > 0 && CountRows( Filter( cmpTermPicker.Terms, StartsWith(Path, lblPick.Text & cmpTermPicker.PathDelimiter) ) ) = 0`
- [ ] `OnChange` — Event
- [ ] Component props: `Height=190` · `Width=620` · `Fill=RGBA(0,0,0,0)`
- [ ] Paste `bodies/cmpTermPicker.children.pa.yaml`
- [ ] Read the two load-bearing decisions (the "— select —" sentinel row, and chain validation) at
      the top of `src/authored/components/cmpTermPicker.pa.yaml`.

### Skip until composed
`cmpUiKit`, `cmpStatusPill`, `cmpChoicePill`, `cmpEditableGrid` are **not yet placed on any screen**.
Build them from `BUILD-SHEET.md` when you wire the galleries that use them. `cmpUiKit` has **no
body** — it's four `OutputFunction`s typed entirely from the sheet.

## A3 · App.Formulas

- [ ] Paste `src/patches/App.Formulas.pa.fx` into the **App.Formulas formula bar** (not code view).
- [ ] **Report:** accepted? If `gUserEmail` or the screen references error, that's the useful signal.
      *(Must be before the data screens — they reference `StageWeights`/`ClaimPrefix` defined here.)*

---

# PHASE B — needs SharePoint (provision first)

## B1 · Provision the 8 lists — `schema/schema.yaml` is the golden source
- [ ] Each column's `name:` **is** the internal name and freezes at creation — create with that exact
      name, friendly display name after. Apply `indexed: true` while the list is small.
- [ ] Prefer the **Power Automate provisioning flow** (explicit internal names, re-runnable) over
      hand-clicking (which risks `_x0020_` names). Hand-UI is the fallback — watch every name.
- [ ] **Do NOT create `transaction_notional_usd`** — commented out in the golden source (Q14).
- [ ] Bind each Managed-Metadata column to its **term set** (the app reads the vocabulary through it;
      no separate terms list).

## B2 · Wire data into the app
- [ ] Add each list as a **data source**.
- [ ] Add the **Office 365 Users** connection (Data → Add data) — the edit screens call
      `Office365Users.SearchUser`; an unrecognised name is a *paste* failure, so do this first.

## B3 · Paste the 9 data-bound screens **in this order** (target must exist before its navigator)
- [ ] a. `scrIssueEdit.pa.yaml`   *(leaf)*
- [ ] b. `scrTransactionEdit.pa.yaml`   *(leaf)*
- [ ] c. `scrTaskEdit.pa.yaml`   *(leaf)*
- [ ] d. `scrProjectEdit.pa.yaml`
- [ ] e. `scrTask.pa.yaml`
- [ ] f. `scrProject.pa.yaml`
- [ ] g. `scrProjects.pa.yaml`
- [ ] h. `scrHome.pa.yaml`
- [ ] i. `scrReports.pa.yaml`

*(`scrProjectEdit`↔`scrProject` navigate to each other — one is pasted while the other is still
empty; that's fine, it only has to exist.)*

## B4 · Settings + verify
- [ ] **Settings → General → Data row limit → 2000.**
- [ ] Nav highlights the active screen and moves between all five.
- [ ] Home shows counts (0 on empty lists is fine — it means the queries ran).
- [ ] **Delegation check:** set the row limit to **1** temporarily — every figure should stay
      *structurally* right; anything that collapses has a non-delegable clause. Set it back to 2000.
- [ ] Reports shows the licence card + three rings (`gHasPowerBiLicence=false` by decision — greyed
      but reachable soft gate, not a bug).
- [ ] **Create a project end-to-end:** Details → Classification (both pickers must reach a leaf
      before Save enables) → stage a task, a transaction, an issue → Save. All three appear on the
      project's tabs; the completion ring reflects the staged task stages.
- [ ] **Person write:** the project manager shows a real person in SharePoint, not a broken chip.
      If broken, `ClaimPrefix` + the expanded-user record are the suspects (community-confirmed).
- [ ] **Currency:** transactions tab totals **per currency**, no blended figure anywhere (Q14).

---

## After each paste — the two things I need back
1. **Did it land?** yes / no (+ verbatim error if no).
2. **What suffix did Studio add?** Rename back immediately and tell me — a stray `_1` breaks
   name references silently. I'll record it in `paste-log.md`.
