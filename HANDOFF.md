# HANDOFF — moving the app from this repo to Studio

**Start here on the work machine.** This is the single ordered entry point for getting everything
in this repo into Power Apps Studio.

## How the transfer works

```
GitHub repo  ──►  work machine  ──►  Power Apps Studio
                                          │
                                          └──►  chat: "it worked" / "it didn't"
```

**One way.** Nothing returns to the repo — no pull, no export, no code-view sample. The only
return channel is you telling me in chat, and it only has to carry a binary result plus, if it
failed, the error text.

**Consequence for the paste log:** you can't write to the repo, so **I maintain `paste-log.md`
for you.** Tell me what landed and I'll commit the entry. An unlogged crossing is a crossing we
can't reconstruct later, so it's worth the one-line report.

## Getting the files onto the work machine

Whichever works there:
- **Clone/pull the repo**, and open the files locally — best, because paths in this doc resolve.
- **Browse GitHub in the work browser** — open the file, click **Raw**, then select-all + copy.
  Raw matters: the rendered view inserts markup that will not paste correctly.
- **Download the repo as a ZIP** from GitHub if git isn't available.

Copy the file **whole** unless a step says otherwise. Don't retype.

## Validate before you carry anything across

```
python tools/validate_pa_yaml.py
```

Checks every authored file against **Microsoft's official `pa-yaml` v3.0 schema** (vendored at
`tools/pa.schema.v3.0.yaml`). This is the only pre-paste check that exists on this side of the gap
— it is what caught the component rejection. Expect `22/22 valid`.

---

# The order

Dependencies are real — each stage assumes the one before it. Stages 1–2 need **nothing
provisioned**, so start there even if SharePoint isn't ready.

## Stage 1 — smoke-test the channel (do this first, costs 5 minutes)

Before building anything, prove that a paste from this repo actually lands in your Studio.

1. Create the canvas app (tablet layout unless you've decided otherwise).
2. Turn on the **Power Fx formula bar**: Settings → Upcoming/General. Without it there is no
   **View code**.
3. Allow clipboard access for `https://make.powerapps.com` when the browser prompts.
4. Create a blank screen, rename it **`scrReference`**.
5. Paste `src/authored/scrReference.fx.yaml` into it via right-click → **Paste code**.

**Why this one:** `scrReference` and `scrAdmin` are pure shells — no components, no data sources,
no `App.Formulas` dependency. They are the only units that can land with nothing else in place, so
they isolate *the channel itself* from every other variable.

→ **Report back: did it paste?** If it didn't, send me the error and stop — everything downstream
uses the same dialect, and there is no point pasting fifteen more units into a channel we know is
rejecting. If it did, we know the dialect is right and the rest is mechanical.

## Stage 2 — the rest of the shells and the components

6. Create and name the remaining **ten** screens **exactly**:

   | Screen | Role |
   |---|---|
   | `scrHome`, `scrReports`, `scrProjects`, `scrAdmin` | in the nav menu |
   | `scrProject`, `scrTask` | detail screens, reached by `Navigate` |
   | `scrProjectEdit`, `scrTaskEdit`, `scrTransactionEdit`, `scrIssueEdit` | create / edit screens, reached by `Navigate` |

   The five nav screens must exist before `App.Formulas`, which holds live screen references. The
   detail and edit screens aren't in the nav menu, but must exist before any screen that navigates
   to them. Paste `scrAdmin.fx.yaml` now; leave the rest empty for Stage 4.
7. **Build the components by hand** — see `src/authored/components/_COMPONENTS-NOTES.md`.
   Canvas components are **not** code-view-pasteable; each is recreated in the component editor
   from its contract table. This is the slowest part of the whole job.

   Build only what the screens you want actually need:

   | Component | Needed by |
   |---|---|
   | `cmpSectionHeader`, `cmpStatusCard`, `cmpKpiRing`, `cmpToast`, `cmpConfirmDialog` | `scrHome` |
   | `cmpSectionHeader`, `cmpKpiRing` | `scrReports` |
   | `cmpSectionHeader`, `cmpSelection` | `scrProjects` |
   | `cmpSelection`, `cmpKpiRing` | `scrProject` |
   | `cmpSelection` | `scrTask` |
   | `cmpSelection` | `scrTransactionEdit`, `scrIssueEdit` |
   | `cmpSelection`, **`cmpTermPicker`** | `scrProjectEdit`, `scrTaskEdit` |
   | `cmpUiKit`, `cmpStatusPill`, `cmpChoicePill`, `cmpEditableGrid` | not yet composed — skip |

   **`cmpTermPicker` is new and is the one to build carefully** — it is how a required Managed
   Metadata column gets a value (C10). Four vertical galleries side by side, each revealing the
   next; the hidden `lblPick` label carries the resolved GUID and all four outputs read it. The
   contract and the two load-bearing decisions (the "— select —" sentinel row, and chain
   validation) are documented at the top of `src/authored/components/cmpTermPicker.pa.yaml`.

   Note `cmpConfirmDialog`'s input is **`IsOpen`**, not `Visible` — a custom property named
   `Visible` collides with the built-in one.

## Stage 3 — App.Formulas

8. Paste `src/patches/App.Formulas.pa.fx` into the **App.Formulas formula bar**. Not code view —
   the App object has none.

   **This is now before the screens, not after.** The data-bound screens reference `StageWeights`,
   and the edit screens reference `ClaimPrefix` and `FxToUsd` — all defined here.

   **Check `FxToUsd` before anyone books a trade.** Those rates are static placeholders. Every
   `transaction_notional_usd` is normalised with them at write time (C5), so a stale rate is a
   wrong number in Power BI that nothing downstream can correct.

→ **Report back:** did it accept? If `gUserEmail` or the screen references error, that's the
useful signal.

## Stage 4 — provision the lists, then the data screens

9. **Provision the nine lists from `schema/schema.yaml`.** That file is the golden source: each
   column's `name:` **is** the internal name and freezes at creation. Create the column with that
   exact name, then set a friendly display name if you want one. Apply `indexed: true` while each
   list is small — indexes can't be added past 20,000 items.
    `taskmaster_terms` is the ninth and is new: it is a flat cache of the term store, and it is
    what makes the required Managed Metadata columns writable from the app (C10). Nothing can
    create a project until it has rows in it — see step 10b.

10. In the app, **add each list as a data source**.

10a. **Add the `Office 365 Users` connection** (Data → Add data → Office 365 Users). The four
    `scr*Edit` screens call `Office365Users.SearchUser` for their people pickers. Do this
    **before** pasting them — an unrecognised name is a paste failure, not a runtime one.

10b. **Populate `taskmaster_terms`.** A scheduled Power Automate flow walking the Graph termStore
    is the intended route (`docs/managed-metadata-picker.md`; blocked on Q12), but for a small
    vocabulary **hand-entering the rows works and unblocks everything**: one row per term, with
    `term_parent_guid` empty at the top level and set to the parent's `term_guid` below it. The
    GUIDs must be the **real** term GUIDs from the term store, because they are what gets written
    into the Managed Metadata column.

    **Cheapest possible de-risking test, worth doing before anything else here:** create one
    project by hand in SharePoint, then use `scrProjectEdit` to save a single region. If the
    Managed Metadata write lands, the riskiest construct in the app is proven. If it errors, send
    me the message — that shape is community-confirmed, not first-party, and the exact error is
    what tells us how to adapt.

11. Paste the nine data-bound screens. **Order matters** — paste a screen before the one that
    navigates to it, so the target exists:

    | # | Screen | Navigates to |
    |---|---|---|
    | a | `scrIssueEdit.fx.yaml` | — (leaf) |
    | b | `scrTransactionEdit.fx.yaml` | — (leaf) |
    | c | `scrTaskEdit.fx.yaml` | — (leaf) |
    | d | `scrProjectEdit.fx.yaml` | `scrProject` |
    | e | `scrTask.fx.yaml` | `scrTaskEdit` |
    | f | `scrProject.fx.yaml` | `scrTask`, `scrProjectEdit`, `scrTaskEdit`, `scrTransactionEdit`, `scrIssueEdit` |
    | g | `scrProjects.fx.yaml` | `scrProject`, `scrProjectEdit` |
    | h | `scrHome.fx.yaml` | `scrProjects` |
    | i | `scrReports.fx.yaml` | — |

    `scrProjectEdit` and `scrProject` navigate to each other, so one of them will be pasted while
    its target is still an empty screen. That is fine — the screen only has to **exist**.

    These **cannot** paste before step 10 — Studio won't bind to a list that doesn't exist.

## Stage 5 — settings and verification

12. **Settings → General → Data row limit → 2000.**
13. Walk the checks:
    - Nav highlights the active screen and moves between all five.
    - Home shows counts (0 is fine on empty lists — it means the queries ran).
    - **Delegation check:** temporarily set the data row limit to **1**. Every figure should still
      be *structurally* right; anything that collapses has a non-delegable clause. Set it back.
    - Reports shows the licence card and the three rings for an unlicensed user.
    - **Create a project end to end**: New project → fill Details → Classification (both pickers
      must reach a leaf before Save enables) → stage a task, a transaction and an issue → Save.
      All three children should appear on the project's tabs, and the completion ring should
      reflect the staged tasks' stages.
    - **Person write**: check the project manager actually shows a person in SharePoint, not a
      broken chip. If it is broken, `ClaimPrefix` and the expanded-user record shape are the
      suspects (both community-confirmed, not first-party).

---

# After each paste — the two things I need back

1. **Did it land?** yes / no. If no, the error text verbatim.
2. **What name did Studio give it?** Paste creates a *new* control and suffixes the name
   (`galProjects` → `galProjects_1`). Rename it back to the intended name immediately, and tell me
   the suffix you saw — screens here reference controls by name (`galProjects.AllItems`,
   `SearchBox.Text`, `cmpToastHome.Show()`), so a stray suffix breaks them silently.

Paste **one unit at a time, onto a blank screen**. A rejection then points at one thing.

---

# Current state

| Stage | Status |
|---|---|
| Channel | **PROVEN** — `scrAdmin` landed 2026-08-03. The screen dialect and control tokens are correct. |
| Lists provisioned | **No** — every list is `provisioned: pending` in `schema/schema.yaml` |
| Components built | **No** — first attempt was rejected; all 10 have since been corrected against Microsoft's official schema and now validate. Retry. |
| App.Formulas landed | **No** (this is why `scrAdmin` rendered unstyled — `Theme.*` is undefined until it lands) |
| Screens landed | `scrAdmin` only |
| CRUD screens | **Authored, not landed** — `scrProjectEdit`, `scrTaskEdit`, `scrTransactionEdit`, `scrIssueEdit` |
| Managed-metadata picker | **Authored, not landed** — `cmpTermPicker`; needs `taskmaster_terms` to have rows |

Schema decisions are **complete** (C1, C3, C4, C5, C8, C9, C10 applied; C6 by design). Two
structural gaps remain, both external to the authored code:

- **`asset_library`** — its schema was never supplied, so `task_output_asset` has no target. The
  task editor says so on screen rather than offering a control that cannot work.
- **`taskmaster_terms` has no populator** — Q12 (Power Automate / custom connector). The app is
  authored and pastes without it; it just has nothing to pick from until the list has rows, and
  the picker says exactly that rather than showing four empty columns.

Everything else is ready to provision.
