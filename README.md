# powerapp_taskmaster

Source for the **EQD Taskmaster** canvas Power App — a work-management app over SharePoint
lists, reported on in Power BI.

This repo is the authoritative source. The running app lives in Power Apps Studio; changes are
authored here and carried across by hand. Nothing is read back, so these files are the truth.

## Layout

```
src/
  App.pa.yaml              the App object — named formulas (Theme, NavMenu, …)
  Screens/                 one file per screen (11)
  Components/              one file per component (12), definition and controls together
schema/
  schema.yaml              GOLDEN SOURCE for the SharePoint backend
tools/
  validate_pa_yaml.py      run before any hand-off
  pa.schema.v3.0.yaml      Microsoft's pa-yaml v3.0 schema, vendored
  studio-enums.json        grounded control tokens and the 180-value Icon enum
docs/                      design notes, and build-history.md (closed record)
```

Everything under `src/` is [pa-yaml v3.0](https://github.com/microsoft/PowerApps-Tooling),
the same dialect Power Apps Studio's code view emits.

## Validate

```bash
pip install -r tools/requirements.txt
python3 tools/validate_pa_yaml.py
```

Two passes. The **schema** pass checks structure against Microsoft's official schema. The
**token** pass checks what the schema deliberately leaves open — the schema declares `Control:`
as "anything" and `Variant:` as any non-empty string, so a made-up control name validates
perfectly and still cannot work. Every control token, gallery variant and `Icon.*` value is
checked against an allow-list of tokens confirmed against real Studio output.

## The one rule that matters

**Never invent a column name.** Every SharePoint field token must resolve to a `name:` in
`schema/schema.yaml`. The schema defines the lists; SharePoint is provisioned to match it, not
the other way round.
