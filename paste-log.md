# Paste log

Every crossing of the air gap, newest first. A row exists only once a human has pasted the unit
into Studio and confirmed the outcome. Nothing is "in the app" without a row here.
See the `studio-transfer` skill for the lifecycle and the rename-and-log rule.

| Date | Direction | Target screen | Intended name | Studio suffix | Channel | Source file | Outcome | Notes |
|------|-----------|---------------|---------------|---------------|---------|-------------|---------|-------|
| 2026-08-03 | repo → Studio | components (retry) | — | *(not reported)* | Code view | `src/authored/components/*.pa.yaml` | **PARTLY LANDED** | Corrects the entry below and the repo's standing assumption: **components ARE code-view-pasteable** — the notes claimed they had to be rebuilt by hand in the component editor, which was wrong. User reports several landed after the schema fix; individual names not reported, so this row covers the batch. Consequence: component control tokens are a real paste payload, so `HtmlViewer@2.1.0` and `Classic/Timer@2.1.0` are now genuine risks rather than documentation. |
| 2026-08-03 | repo → Studio | scrAdmin | scrAdmin | *(not reported)* | Code view | `src/authored/scrAdmin.fx.yaml` | **LANDED** | First successful crossing. Confirms the modern structured `.pa.yaml` screen dialect and the grounded control tokens. Theme unstyled as expected — `App.Formulas` not yet pasted, so `Theme.*` is undefined. |
| 2026-08-03 | repo → Studio | components (batch) | — | — | Component editor | `src/authored/components/*.pa.yaml` | **REJECTED** | YAML structural error: *"expected SequenceStart, got MappingStart"*. Cause found against Microsoft's official pa-yaml v3.0 schema: `Parameters` must be a **sequence**, and `Output`/`OutputFunction`/`Action` properties may not carry `Default`. All 10 components corrected and now validate. |
