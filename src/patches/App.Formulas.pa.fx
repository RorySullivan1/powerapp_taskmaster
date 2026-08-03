// ============================================================================
// App.Formulas  —  the core-shell foundation (theme + nav table + identity)
// ============================================================================
// TRANSFER PATH: FORMULA BAR ONLY. The App object has NO code view (studio-
// transfer, "two hard limitations"). Paste this body into the App.Formulas
// formula bar by hand — never through Paste code.
//
// PASTE ORDER (matters): the five screens must EXIST and be NAMED
//   scrHome / scrReports / scrProjects / scrReference / scrAdmin
// before this pastes, because NavMenu holds live Screen references. Create the
// screen shells first (src/authored/scr*.fx.yaml), then paste this last.
//
// Data-independent: no tmXxx column tokens — nothing here binds to SharePoint,
// so it is paste-ready before any list is provisioned (screen-map Phase 1).
// Theme is a static token set now; screen-map's intent is to feed it from
// tmLookups later — keep every colour/size behind Theme.* so that swap is local.
// ============================================================================

// --- Identity ---------------------------------------------------------------
// Lowercased to match the Person-column Claims convention (schema.md).
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
// TODO (design choice — shapes the shell's UX): define how an unlicensed user
// sees the Reports entry. This flag drives nav-item Visible/DisplayMode AND the
// Reports screen's empty-state vs. embed. Two defensible options:
//   (a) hard-gate  = false  -> hide Reports entirely (cleanest, but hides a feature)
//   (b) soft-gate  = based on a real signal -> show greyed, with the empty-state card
// There is no in-app Power BI licence API, so this must be sourced deliberately
// (e.g. a tmLookups/allow-list flag, or an env/user-group check). Set it here so
// every consumer (nav + Reports screen) reads one source of truth.
gHasPowerBiLicence = false;   // <-- replace with the chosen signal

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

// --- Write-back: recompute one project's % (app-side writer, C3) -------------
// PASTE THIS INTO A BEHAVIOUR PROPERTY, not here. Run it wherever a task's
// stage can change: the task form's OnSuccess, a kanban drop, the editable
// grid's save. Substitute the project's ID for <pid>.
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
