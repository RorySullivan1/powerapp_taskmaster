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

## Re-copy before every paste

The `scrAdmin` that reached Studio carried `Variant: CONFIRM_BlankVertical` — a placeholder that
had been fixed in the repo long before. A stale local copy is easy to accumulate and impossible to
spot from this side, so **re-copy the file from current `main` immediately before pasting it**, and
run the validator first:

```
python tools/validate_pa_yaml.py
```

It now checks control tokens and gallery variants against an allow-list and rejects leftover
`CONFIRM_` / `TODO_` placeholders — the official schema constrains neither, which is exactly how
that one got through.

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
5. Paste `src/authored/scrReference.pa.yaml` into it via right-click → **Paste code**.

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
   to them. Paste `scrAdmin.pa.yaml` now; leave the rest empty for Stage 4.
7. **Build the components in two steps** — see `src/authored/components/BUILD-SHEET.md`.

   A component is a **contract** (custom properties) plus a **body** (controls), and Studio takes
   those through different channels. Pasting the whole definition asks one channel to carry both,
   which is the likeliest reason a whole-file paste fails.

   For each component: create it, add every custom property from the build sheet **first**, set the
   component-level formulas, then paste `bodies/<name>.children.pa.yaml` into its canvas. The body
   references the properties by name, so the order isn't optional.

   `cmpUiKit` is the exception — no controls at all, built entirely from the sheet.

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
   next; the hidden `lblPick` label carries the resolved term **path** and the outputs read it.
   It cascades on the term's `Path`, which `Choices()` already supplies, so there is no terms
   list behind it. The contract and the two load-bearing decisions (the "— select —" sentinel
   row, and chain validation) are documented at the top of
   `src/authored/components/cmpTermPicker.pa.yaml`.

   Note `cmpConfirmDialog`'s input is **`IsOpen`**, not `Visible` — a custom property named
   `Visible` collides with the built-in one.

## Stage 3 — App.Formulas

8. Paste `src/patches/App.Formulas.pa.fx` into the **App.Formulas formula bar**. Not code view —
   the App object has none.

   **This is now before the screens, not after.** The data-bound screens reference `StageWeights`
   and the edit screens reference `ClaimPrefix`, both defined here.

   There is deliberately **no FX table** (Q14). The app stores the native notional only; currency
   conversion belongs to Power BI, against an FX dimension keyed on currency and trade date. If you
   find yourself wanting a rate table to "just add a total", read the note in the file first.

→ **Report back:** did it accept? If `gUserEmail` or the screen references error, that's the
useful signal.

## Stage 4 — provision the lists, then the data screens

9. **Provision the eight lists from `schema/schema.yaml`.** That file is the golden source: each
   column's `name:` **is** the internal name and freezes at creation. Create the column with that
   exact name, then set a friendly display name if you want one. Apply `indexed: true` while each
   list is small — indexes can't be added past 20,000 items.

   **Provisioning route: a Power Automate flow, not the UI** (Q11-bis, unblocked now that Q12 is
   answered). Setting the internal name explicitly at creation removes the `_x0020_` risk that
   hand-clicking carries, and it is re-runnable for dev → test → prod. Clicking eight lists by hand
   remains the fallback; if you take it, watch every column name.

   One column to skip: **do not create `transaction_notional_usd`.** It is commented out in the
   golden source (Q14). Nothing writes it, so provisioning it would leave a permanently blank
   Currency field that looks like a real figure.

   Make sure each Managed Metadata column is **bound to its term set** — that binding is what the
   app reads the vocabulary through (C10). There is no separate terms list to create or seed.

10. In the app, **add each list as a data source**.

10a. **Add the `Office 365 Users` connection** (Data → Add data → Office 365 Users). The four
    `scr*Edit` screens call `Office365Users.SearchUser` for their people pickers. Do this
    **before** pasting them — an unrecognised name is a paste failure, not a runtime one.

10b. **Nothing to seed for managed metadata.** The pickers read each column's term set directly
    via `Choices()`, so the term store is the only copy — no cache list, no refresh flow.

    Two things to watch on the first run, both visible on screen:
    - The picker prints a **raw term path** under itself (`first term's path: …`). If the separator
      is not `;`, tell me what it is — it's the `PathDelimiter` input, a one-line fix.
    - `Choices()` on an MM column is **capped at 20 terms** by the connector. If a vocabulary is
      bigger than that and terms go missing from the picker, say so: the fix is to feed that one
      picker from a Power Automate call instead, and the component itself doesn't change.

    **Cheapest possible de-risking test, worth doing before anything else here:** create a project
    with `scrProjectEdit` and set only a region. If the managed-metadata write lands, the least-
    proven construct in the app is proven. If it errors, send me the message — the fallback is a
    hand-built taxonomy record, documented in `docs/managed-metadata-picker.md` §5.

11. Paste the nine data-bound screens. **Order matters** — paste a screen before the one that
    navigates to it, so the target exists:

    | # | Screen | Navigates to |
    |---|---|---|
    | a | `scrIssueEdit.pa.yaml` | — (leaf) |
    | b | `scrTransactionEdit.pa.yaml` | — (leaf) |
    | c | `scrTaskEdit.pa.yaml` | — (leaf) |
    | d | `scrProjectEdit.pa.yaml` | `scrProject` |
    | e | `scrTask.pa.yaml` | `scrTaskEdit` |
    | f | `scrProject.pa.yaml` | `scrTask`, `scrProjectEdit`, `scrTaskEdit`, `scrTransactionEdit`, `scrIssueEdit` |
    | g | `scrProjects.pa.yaml` | `scrProject`, `scrProjectEdit` |
    | h | `scrHome.pa.yaml` | `scrProjects` |
    | i | `scrReports.pa.yaml` | — |

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
    - Reports shows the licence card and the three rings. `gHasPowerBiLicence` is `false` by
      decision, so **everyone** sees that state until a real signal is supplied — the Reports nav
      entry is greyed but still opens. That is the intended soft gate, not a bug.
    - **Create a project end to end**: New project → fill Details → Classification (both pickers
      must reach a leaf before Save enables) → stage a task, a transaction and an issue → Save.
      All three children should appear on the project's tabs, and the completion ring should
      reflect the staged tasks' stages.
    - **Person write**: check the project manager actually shows a person in SharePoint, not a
      broken chip. If it is broken, `ClaimPrefix` and the expanded-user record shape are the
      suspects (both community-confirmed, not first-party).
    - **Currency**: the transactions tab totals **per currency**, not blended. There is no USD
      column and no total across currencies anywhere — that is Q14, working as decided.

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
| Components | **Partly landed** — the first batch was rejected on a dialect error, since fixed; several have since landed (exact names not reported). All 11 validate. |
| App.Formulas landed | **No** (this is why `scrAdmin` rendered unstyled — `Theme.*` is undefined until it lands) |
| Screens landed | `scrAdmin` only |
| CRUD screens | **Authored, not landed** — `scrProjectEdit`, `scrTaskEdit`, `scrTransactionEdit`, `scrIssueEdit` |
| Managed-metadata picker | **Authored, not landed** — `cmpTermPicker`, reading each term set directly via `Choices()`. Nothing to seed |

Schema decisions are **complete** (C1, C3, C4, C8, C9, C10 applied; C5 superseded by Q14; C6 by
design). Q12, Q14 and the Power BI licence gate were all answered on 2026-08-03.

One structural gap remains, and it is external to the authored code: **`asset_library`** — its
schema was never supplied, so `task_output_asset` has no target. The task editor says so on screen
rather than offering a control that cannot work.

Two things Power Automate now owes, both unblocked rather than blocking:

- the **provisioning flow** (eight lists, explicit internal names) — see step 9;
*(A term-store sync flow was on this list and is no longer needed — the app reads the term store
directly.)*

And one thing **Power BI** now owes: an FX dimension and a measure converting `transaction_notional`
at the trade date. Since Q14 the app deliberately stores no USD figure, so until that measure
exists there is no blended notional anywhere. That is the accepted cost of the decision.

Everything else is ready to provision.
