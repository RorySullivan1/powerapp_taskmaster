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

6. Create and name the remaining four screens **exactly**: `scrHome`, `scrReports`,
   `scrProjects`, `scrAdmin`. (Names must exist before `App.Formulas`, which holds live screen
   references.) Paste `scrAdmin.fx.yaml` now; leave the other three empty for Stage 4.
7. **Build the components by hand** — see `src/authored/components/_COMPONENTS-NOTES.md`.
   Canvas components are **not** code-view-pasteable; each is recreated in the component editor
   from its contract table. This is the slowest part of the whole job.

   Build only what the screens you want actually need:

   | Component | Needed by |
   |---|---|
   | `cmpSectionHeader`, `cmpStatusCard`, `cmpKpiRing`, `cmpToast`, `cmpConfirmDialog` | `scrHome` |
   | `cmpSectionHeader`, `cmpKpiRing` | `scrReports` |
   | `cmpSectionHeader`, `cmpSelection` | `scrProjects` |
   | `cmpUiKit`, `cmpStatusPill`, `cmpChoicePill`, `cmpEditableGrid` | not yet composed — skip |

   Note `cmpConfirmDialog`'s input is **`IsOpen`**, not `Visible` — a custom property named
   `Visible` collides with the built-in one.

## Stage 3 — App.Formulas

8. Paste `src/patches/App.Formulas.pa.fx` into the **App.Formulas formula bar**. Not code view —
   the App object has none.

   **This is now before the screens, not after.** The data-bound screens reference `StageWeights`,
   which is defined here.

→ **Report back:** did it accept? If `gUserEmail` or the screen references error, that's the
useful signal.

## Stage 4 — provision the lists, then the data screens

9. **Provision the eight lists from `schema/schema.yaml`.** That file is the golden source: each
   column's `name:` **is** the internal name and freezes at creation. Create the column with that
   exact name, then set a friendly display name if you want one. Apply `indexed: true` while each
   list is small — indexes can't be added past 20,000 items.
10. In the app, **add each list as a data source**.
11. Paste the three data-bound screens: `scrHome.fx.yaml`, `scrProjects.fx.yaml`,
    `scrReports.fx.yaml`.

    These **cannot** paste before step 10 — Studio won't bind to a list that doesn't exist.

## Stage 5 — settings and verification

12. **Settings → General → Data row limit → 2000.**
13. Walk the checks:
    - Nav highlights the active screen and moves between all five.
    - Home shows counts (0 is fine on empty lists — it means the queries ran).
    - **Delegation check:** temporarily set the data row limit to **1**. Every figure should still
      be *structurally* right; anything that collapses has a non-delegable clause. Set it back.
    - Reports shows the licence card and the three rings for an unlicensed user.

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
| Lists provisioned | **No** — every list is `provisioned: pending` in `schema/schema.yaml` |
| Components built | **No** |
| App.Formulas landed | **No** |
| Screens landed | **No** — `paste-log.md` is empty |

Schema decisions are **complete** (C1, C3, C4, C5, C8, C9 applied; C6 by design). The one
structural gap is **`asset_library`** — its schema was never supplied, so `task_output_asset` has
no target. Everything else is ready to provision.
