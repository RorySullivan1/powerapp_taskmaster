// ============================================================================
// App.Formulas  —  the core-shell foundation (theme + nav table + identity)
// ============================================================================
// TRANSFER PATH: FORMULA BAR ONLY. The App object has NO code view (studio-
// transfer, "two hard limitations"). Paste this body into the App.Formulas
// formula bar by hand — never through Paste code.
//
// PASTE ORDER (matters — and it CHANGED once the screens gained data):
//   1. Create ELEVEN blank screens, named exactly:
//        scrHome / scrReports / scrProjects / scrReference / scrAdmin
//        scrProject / scrTask                                  <- detail screens
//        scrProjectEdit / scrTaskEdit / scrTransactionEdit / scrIssueEdit
//                                                              <- create / edit screens
//      (NavMenu below holds live Screen references, so the names must exist. The
//       detail and edit screens are NOT in NavMenu — they are reached by Navigate.)
//   2. Paste THIS file into the App.Formulas formula bar.
//   3. Only then paste the screen controls (src/authored/scr*.pa.yaml).
// Step 2 must precede step 3 because scrHome/scrReports OnVisible now reference
// StageWeights, and the edit screens reference ClaimPrefix, both defined here.
// The old "paste App.Formulas last" order would fail validation on those screens.
//
// CONNECTION PREREQUISITE (edit screens only): the four scr*Edit screens call
// Office365Users.SearchUser for their people pickers. Add the **Office 365 Users**
// connection in Studio (Data -> Add data -> Office 365 Users) BEFORE pasting them,
// or the paste fails on an unrecognised name. See HANDOFF.md.
//
// Data-independent: no tmXxx column tokens — nothing here binds to SharePoint,
// so it is paste-ready before any list is provisioned (screen-map Phase 1).
// Theme is a static token set now; screen-map's intent is to feed it from
// tmLookups later — keep every colour/size behind Theme.* so that swap is local.
// ============================================================================

// --- Identity ---------------------------------------------------------------
// Lowercased to match the Person-column Claims convention (schema.md).
// NOTE: this named formula INLINES into the server-side predicates on scrHome /
// scrReports (task_lead.Email = gUserEmail). User() inside a Filter has
// historically tripped the delegation analyser. If either Filter shows a blue
// underline on first paste, the grounded fallback is to delete this line and
// instead put  Set(gUserEmail, Lower(User().Email))  in App.OnStart.
gUserEmail = Lower(User().Email);

// --- Theme ------------------------------------------------------------------
// One record, referenced as Theme.Color.* / Theme.Size.* / Theme.Space.*.
// The single styling channel for the whole app (distillation T7/T16).
Theme = {
    Color: {
        Primary:      RGBA(0,  90, 158, 1),   // EQD desk blue
        PrimaryDark:  RGBA(0,  60, 110, 1),
        Accent:       RGBA(102, 182, 227, 1),
        Bg:           RGBA(245, 247, 250, 1),  // app canvas
        Surface:      RGBA(255, 255, 255, 1),  // cards / nav panel
        Border:       RGBA(225, 229, 235, 1),
        TextPrimary:  RGBA(32,  38,  45,  1),
        TextMuted:    RGBA(110, 120, 130, 1),
        OnPrimary:    RGBA(255, 255, 255, 1),  // text on Primary fill
        Success:      RGBA(49,  130, 93,  1),
        Warning:      RGBA(214, 152, 40,  1),
        Danger:       RGBA(197, 58,  58,  1)
    },
    Size: { H1: 28, H2: 20, H3: 16, Body: 14, Small: 12 },
    Space: { Gutter: 24, Gap: 16, HeaderH: 64, NavW: 240, RowH: 52 },
    Font: Font.'Segoe UI'
};

// --- Navigation model (native, licence-independent — Q2 decision) -----------
// Screen references passed AS DATA (pattern T6). Every screen binds one nav
// gallery to NavMenu; the gallery's OnSelect does Navigate(ThisItem.Screen).
// NeedsLicence flags the Power BI-gated entry so the shell can grey/hide it for
// unlicensed users without the dashboard ever carrying navigation.
NavMenu = Table(
    { Key: 1, Title: "Home",      Icon: Icon.Home,     Screen: scrHome,      NeedsLicence: false },
    { Key: 2, Title: "Reports",   Icon: Icon.Table,    Screen: scrReports,   NeedsLicence: true  },
    { Key: 3, Title: "Projects",  Icon: Icon.Documents,Screen: scrProjects,  NeedsLicence: false },
    { Key: 4, Title: "Reference", Icon: Icon.Bookmark, Screen: scrReference, NeedsLicence: false },
    { Key: 5, Title: "Admin",     Icon: Icon.Settings, Screen: scrAdmin,     NeedsLicence: false }
);

// --- Power BI licence gate (Q2) ---------------------------------------------
// DECIDED 2026-08-03 — SOFT GATE. An unlicensed user sees the Reports entry
// GREYED, can still open it, and lands on the empty-state card plus the three
// licence-free KPI rings. Reports is never hidden: a hidden feature is one nobody
// knows to ask for a licence for, and the rings are useful on their own.
//
// There is no in-app Power BI licence API, so this stays FALSE — everyone is
// treated as unlicensed until a real signal is supplied. That is the safe default
// for a soft gate: the worst case is a licensed user seeing the fallback rings
// and one extra click, not an unlicensed user hitting a broken embed.
//
// To supply a signal later, replace this line only — nav and the Reports screen
// both read it, so nothing else changes. A lookup/config allow-list column or an
// Entra group check are the two obvious sources.
gHasPowerBiLicence = false;   // soft gate; see above before changing

// --- Task-stage weights (C3: project completion is a WEIGHTED rollup) --------
// Golden source for these numbers: schema/schema.yaml -> rollups:
//   project_perc_completion. Keep the two in step — this table is the app-side
//   copy that the write-back below reads.
//
// A named formula is a VALUE, so the weights live here; the write-back is a
// side effect and therefore lives in a behaviour property (snippet below).
StageWeights = Table(
    { Stage: "Not Started",  Weight: 0   },
    { Stage: "Planning",     Weight: 10  },
    { Stage: "Drafting",     Weight: 35  },
    { Stage: "Under Review", Weight: 60  },
    { Stage: "Finalizing",   Weight: 85  },
    { Stage: "Complete",     Weight: 100 }
    // "Archived" is deliberately ABSENT — archived tasks are excluded from both
    // numerator and denominator, so a shelved task can't drag a project down.
);

// --- Person-column claims prefix --------------------------------------------
// A SharePoint Person column is patched as an expanded-user record whose Claims
// string is this prefix plus the LOWERCASED user principal name. One definition
// so the four edit screens cannot drift from each other:
//
//   { '@odata.type': "#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser",
//     Claims: ClaimPrefix & Lower(<mail>), DisplayName: ..., Email: ...,
//     Department: "", JobTitle: "", Picture: "" }
//
// COMMUNITY-CONFIRMED shape, not first-party — same risk class as the managed-
// metadata write (docs/managed-metadata-picker.md §2). If a Person write fails on
// first paste, this line and the record shape around it are the first suspects.
ClaimPrefix = "i:0#.f|membership|";

// --- NO FX TABLE HERE, DELIBERATELY (Q14 decided 2026-08-03) ----------------
// An `FxToUsd` table briefly lived here so the transaction form could normalise
// transaction_notional_usd at write time. It has been REMOVED: currency
// conversion now happens in the REPORT layer, against a proper FX dimension in
// Power BI, and the app writes only the native `transaction_notional` +
// `transaction_currency`.
//
// Why this is the better place for it: a write-time rate freezes whatever number
// happened to be in the app on the day of the trade, and nothing downstream can
// ever correct it. Report-time conversion can be restated, back-dated and audited.
//
// CONSEQUENCE, and it is a real one: **the app can no longer show a
// cross-currency total anywhere.** Any figure that mixes currencies must either
// be shown per-currency or deferred to Power BI — see scrProject's transactions
// tab, which now totals per currency and says so. Do not reintroduce a rate table
// to "just add a total".
// --- Write-back: recompute one project's % (app-side writer, C3) -------------
// IMPLEMENTED in src/authored/scrTask.pa.yaml -> btnSave.OnSelect. That is the
// live copy; this block is the reference for any OTHER place a stage can change
// (a kanban drag, the editable grid's save). Substitute the project's ID for <pid>.
//
//   With(
//       { scored:
//           AddColumns(
//               // Delegable: FK = on an indexed Lookup, plus an Or-of-equals over
//               // the six non-archived stages. Enumerating them is how Archived is
//               // excluded server-side — `<> "Archived"` is a Text <> and would NOT
//               // delegate. Tasks with a blank stage match nothing and are omitted.
//               Filter( taskmaster_tasks,
//                       task_project_id.Id = <pid>
//                    && ( task_stage.Value = "Not Started"  || task_stage.Value = "Planning"
//                      || task_stage.Value = "Drafting"     || task_stage.Value = "Under Review"
//                      || task_stage.Value = "Finalizing"   || task_stage.Value = "Complete" ) ),
//               "wgt", Coalesce(LookUp(StageWeights, Stage = task_stage.Value, Weight), 0) ) },
//       Patch( taskmaster_projects,
//              LookUp(taskmaster_projects, ID = <pid>),
//              { project_perc_completion:
//                    If( CountRows(scored) = 0, 0, RoundDown(Average(scored, wgt), 0) ) } )
//   )
//
// Notes:
//  * Average/CountRows here run LOCALLY over the already-filtered page — correct
//    because the Filter narrows to one project first. Only exact if a project
//    holds fewer tasks than the data row limit (set it to 2000).
//  * App-side writer means the value is only as fresh as the app: a stage edited
//    directly in SharePoint leaves project_perc_completion stale until the next
//    in-app change to that project.
