#!/usr/bin/env python3
"""Split each canvas component into the two things Studio actually accepts.

WHY THIS EXISTS
A component definition is not one thing, it is two:

  1. its CONTRACT  — custom properties, and the component-level formulas that
     back the Output / OutputFunction / Action ones. There is no paste gesture
     for these. Custom properties are created in the component's property pane,
     one at a time, and nothing in the YAML can shortcut that.
  2. its BODY      — the child controls. These are ordinary controls in exactly
     the dialect the screens use, and the screens paste.

Pasting a whole `ComponentDefinitions:` document asks Studio to accept (1) and
(2) at once through a channel that only carries (2). This script separates them:

  src/authored/components/bodies/<name>.children.pa.yaml   <- paste this
  src/authored/components/BUILD-SHEET.md                    <- type this

The .pa.yaml files under components/ remain the source of record; both outputs
are GENERATED. Edit the component, then re-run:

    python tools/split_components.py
"""
from __future__ import annotations
import pathlib, sys
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "components" if (ROOT / "components").exists() else ROOT / "src" / "authored" / "components"
BODIES = SRC / "bodies"

# Which screens instantiate which component — so nobody builds more than they need.
USED_BY = {
    "cmpSectionHeader":  ["scrProjects", "scrHome", "scrReports"],
    "cmpStatusCard":     ["scrHome"],
    "cmpKpiRing":        ["scrHome", "scrReports", "scrProject"],
    "cmpToast":          ["scrHome"],
    "cmpConfirmDialog":  ["scrHome"],
    "cmpSelection":      ["scrProjects", "scrProject", "scrTask",
                          "scrProjectEdit", "scrTaskEdit",
                          "scrTransactionEdit", "scrIssueEdit"],
    "cmpTermPicker":     ["scrProjectEdit", "scrTaskEdit"],
    "cmpUiKit":          ["(not yet instantiated)"],
    "cmpStatusPill":     ["(not yet instantiated)"],
    "cmpChoicePill":     ["(not yet instantiated)"],
    "cmpEditableGrid":   ["(not yet instantiated)"],
}

# Custom-property kinds whose FORMULA lives in the component's Properties map
# rather than on the property itself (pa-yaml v3.0 rule — a Default on these is
# what got the first component batch rejected).
FORMULA_IN_PROPERTIES = {"Output", "OutputFunction", "Action"}

# A backing formula that names a control (or collection) from the BODY cannot be
# entered until the body has been pasted — the name doesn't exist yet. So the
# build is three phases, not two, and this is what detects which properties are
# affected. Placeholders below are type-correct and body-free, so the property
# can be created and saved in phase 1 and finished in phase 3.
PLACEHOLDER_BY_TYPE = {
    "Text": '=""', "Number": "=0", "Boolean": "=false",
    "Record": "=Blank()", "Table": "=Table()",
}
PLACEHOLDER_OVERRIDE = {
    ("cmpSelection", "Selected"):      "=First(cmpSelection.Items)",
    ("cmpEditableGrid", "EditedItems"): "=cmpEditableGrid.Items",
}


def body_names(children) -> set:
    """Control names declared anywhere in the body."""
    found = set()
    def rec(n):
        if isinstance(n, dict):
            for k, v in n.items():
                if isinstance(v, dict) and "Control" in v:
                    found.add(k)
                rec(v)
        elif isinstance(n, list):
            for v in n:
                rec(v)
    rec(children)
    return found


def deferred_refs(formula: str, names: set) -> list:
    """Body controls / component collections this formula depends on."""
    import re as _re
    f = str(formula or "")
    hits = sorted(n for n in names if _re.search(rf"\b{_re.escape(n)}\b", f))
    hits += sorted(set(_re.findall(r"\bcol[A-Z]\w*", f)) - set(hits))
    return hits


def clean(o):
    """Drop comments, keep multi-line formulas as block scalars.

    A paste payload should be exactly what Studio needs and nothing else — the
    authoring commentary belongs in the source file, not in the clipboard.
    """
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    if isinstance(o, str) and "\n" in o:
        return LiteralScalarString(o)
    return o


def scalar(v) -> str:
    """Render a formula for a markdown table cell, single line."""
    if v is None:
        return ""
    s = str(v).strip()
    s = " ".join(part.strip() for part in s.splitlines())
    return s.replace("|", "\\|")


def _dump(yaml, obj) -> str:
    import io
    b = io.StringIO()
    yaml.dump(obj, b)
    return b.getvalue()


def main() -> int:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096

    files = sorted(SRC.glob("*.pa.yaml"))
    if not files:
        print(f"no component files under {SRC}")
        return 1

    BODIES.mkdir(exist_ok=True)
    sheet: list[str] = []
    sheet.append("""# Component build sheet — GENERATED, do not edit

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

""")

    for f in files:
        doc = yaml.load(f.read_text(encoding="utf-8"))
        defs = doc.get("ComponentDefinitions", {})
        for name, body in defs.items():
            props = body.get("Properties", {}) or {}
            cprops = body.get("CustomProperties", {}) or {}
            children = body.get("Children", []) or []
            kids = body_names(children)

            # ---- body file ----
            if children:
                out = BODIES / f"{name}.children.pa.yaml"
                header = (
                    f"# {name} — BODY ONLY. GENERATED by tools/split_components.py; do not edit.\n"
                    f"# Source of record: ../{f.name}\n"
                    f"#\n"
                    f"# Paste this into the component's canvas via code view, AFTER creating its\n"
                    f"# custom properties (BUILD-SHEET.md). The controls below reference those\n"
                    f"# properties by name, so a missing one fails the paste.\n"
                    f"#\n"
                    f"# This is a bare control sequence — the same shape a screen's Children: holds,\n"
                    f"# and the same shape Studio produces when you copy selected controls.\n"
                )
                import io, yaml as _pyyaml
                buf = io.StringIO()
                # Round-trip through a plain load to strip comments, then re-dump.
                yaml.dump(clean(_pyyaml.safe_load(_dump(yaml, children))), buf)
                out.write_text(header + buf.getvalue(), encoding="utf-8")

            # ---- build sheet section ----
            sheet.append(f"\n---\n\n## `{name}`\n")
            if body.get("Description"):
                sheet.append(f"\n{body['Description']}\n")
            sheet.append(f"\n**Used by:** {', '.join(USED_BY.get(name, ['?']))}  ")
            sheet.append(f"\n**Access app scope:** `{body.get('AccessAppScope', False)}`  ")
            sheet.append(
                f"\n**Body:** "
                + (f"`bodies/{name}.children.pa.yaml` ({len(children)} control(s)) — paste last"
                   if children else
                   "**none — this component has no controls.** It is built entirely from the "
                   "table below; there is nothing to paste.")
                + "\n"
            )

            if cprops:
                sheet.append("\n### Custom properties — create these first\n\n")
                sheet.append("| # | Name | Kind | Type | Default / formula | Where the formula goes |\n")
                sheet.append("|---|---|---|---|---|---|\n")
                for i, (pname, p) in enumerate(cprops.items(), 1):
                    kind = p.get("PropertyKind", "")
                    dtype = p.get("DataType", p.get("ReturnType", ""))
                    if kind in FORMULA_IN_PROPERTIES:
                        formula = props.get(pname)
                        needs = deferred_refs(formula, kids)
                        if needs:
                            ph = PLACEHOLDER_OVERRIDE.get((name, pname)) or \
                                 PLACEHOLDER_BY_TYPE.get(dtype, '=""')
                            where = (f"⚠️ **PHASE 3 — after the body.** Uses `{', '.join(needs)}`, "
                                     f"which the body creates. Create the property now with the "
                                     f"placeholder `{ph}`, then set the real formula once the body is in.")
                        else:
                            where = "component **Properties** (below)"
                        val = scalar(formula) if formula is not None else "—"
                    else:
                        where = "the property's **Default**"
                        val = scalar(p.get("Default"))
                    params = p.get("Parameters")
                    if params:
                        # Each entry is a single-key map: {<param-name>: {DataType, ...}}
                        # (pa-yaml v3.0 — Parameters is a sequence, not a mapping).
                        def _param_desc(q):
                            (pname, pdef), = dict(q).items()
                            pdef = pdef or {}
                            opt = " (optional)" if pdef.get("IsOptional") else ""
                            return f"`{pname}`: {pdef.get('DataType','')}{opt}"
                        plist = ", ".join(_param_desc(q) for q in params)
                        val = (val + f"<br>**Parameters:** {plist}") if val else f"**Parameters:** {plist}"
                    sheet.append(
                        f"| {i} | `{pname}` | {kind} | {dtype} | `{val}` | {where} |\n"
                    )

            # component-level Properties that are NOT backing a custom property
            own = {k: v for k, v in props.items() if k not in cprops}
            if own:
                sheet.append("\n### Component properties — set these on the component itself\n\n")
                sheet.append("| Property | Formula |\n|---|---|\n")
                for k, v in own.items():
                    sheet.append(f"| `{k}` | `{scalar(v)}` |\n")

            backing = {k: v for k, v in props.items() if k in cprops}
            if backing:
                sheet.append("\n### Formulas backing the output properties\n\n")
                sheet.append(
                    "These are the ones that must NOT be entered as a `Default` — that is "
                    "exactly what got the first batch rejected. Create the property, then set "
                    "its formula here.\n\n"
                )
                sheet.append("| Output property | Formula |\n|---|---|\n")
                for k, v in backing.items():
                    sheet.append(f"| `{k}` | `{scalar(v)}` |\n")

    (SRC / "BUILD-SHEET.md").write_text("".join(sheet), encoding="utf-8")
    print(f"wrote {SRC / 'BUILD-SHEET.md'}")
    print(f"wrote {len(list(BODIES.glob('*.pa.yaml')))} body file(s) to {BODIES}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
