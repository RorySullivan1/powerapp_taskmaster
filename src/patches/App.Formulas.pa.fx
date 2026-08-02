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
