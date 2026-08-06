#!/usr/bin/env python3
"""Validate authored *.pa.yaml against Microsoft's official
Power Apps source schema (pa-yaml v3.0), and against a token allow-list.

The air gap is one-way: a malformed file comes back only as "it didn't work".
This is the one check we CAN run before a paste, so run it before every hand-off.

TWO PASSES, because the schema alone is not enough:

  1. SCHEMA  — structure. Catches things like `Parameters` being a mapping when
     it must be a sequence, which is what got the first component batch rejected.

  2. TOKENS  — values the schema deliberately leaves open. `Variant` is declared
     in the official schema as nothing more than `type: string, minLength: 1`, so
     `Variant: CONFIRM_BlankVertical` — a placeholder this repo genuinely shipped
     into a paste — validates perfectly and still cannot work in Studio. Same for
     `Control:`, which the schema declares as `true` (anything goes).

     Pass 2 exists because of that specific escape. It rejects unknown control
     tokens, unknown variants, and any leftover CONFIRM_/TODO_/TBD_ placeholder.

    python tools/validate_pa_yaml.py            # validate everything authored
    python tools/validate_pa_yaml.py <paths>    # validate specific files

Schema vendored from (MS Learn links to this as the current static schema):
https://raw.githubusercontent.com/microsoft/PowerApps-Tooling/refs/heads/master/schemas/pa-yaml/v3.0/pa.schema.yaml
"""
from __future__ import annotations
import sys, re, json, pathlib, yaml
from jsonschema import Draft7Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "tools" / "pa.schema.v3.0.yaml"

# ---------------------------------------------------------------------------
# Token allow-list. Add to this ONLY with a reason — an unverified token is a
# failed paste that comes back as "it didn't work" with no further detail.
#
#   grounded   = read off a genuine export, or landed in Studio
#   unverified = best-effort name; a paste using it is a live risk
# ---------------------------------------------------------------------------
KNOWN_CONTROLS = {
    "Label@2.5.1":            "grounded",
    "Rectangle@2.3.0":        "grounded",
    "Classic/Icon@2.5.0":     "grounded",
    "Classic/TextInput@2.3.2":"grounded",
    "Classic/Button@2.2.0":   "grounded",
    "Gallery@2.15.0":         "grounded",
    "Image@2.2.3":            "grounded",
    "CanvasComponent":        "grounded",   # component instance, not a control
    "HtmlViewer@2.1.0":       "grounded",   # CONFIRMED 2026-08-03 — cmpStatusPill body pasted
    "Timer":                  "grounded",   # CONFIRMED 2026-08-03 — NOT Classic/Timer
    "ModernTextInput@1.0.0":  "grounded",   # CONFIRMED 2026-08-04 — output is .Text, as classic
    "ModernNumberInput@1.0.0":"grounded",   # CONFIRMED 2026-08-04 — output is .Value (a number)
    "ModernTabList@1.0.0":    "grounded",   # CONFIRMED 2026-08-04 — output is .Selected.Value
    "ModernButton@1.0.0":     "grounded",   # CONFIRMED 2026-08-04 — user-supplied Studio YAML
    # VERSION TRAP, paid for with a failed paste. The @x.y.z in a pa-yaml token is the
    # TEMPLATE version, NOT the product revision Studio shows in its properties pane.
    # `@1.1.1` was authored from a spoken "current version is 1.1.1" and rejected the whole
    # paste. MS Learn's own YAML example for the UPDATED control — same page that documents
    # DelayOutput, typed enums and SelectMultiple defaulting true — emits @1.0.0, which is
    # also what every other modern token in this repo is.
    "ModernCombobox@1.0.0":   "grounded",   # MS Learn modern-control-combobox, 2026-08-06.
                                            # No Reset PROPERTY (classic ListBox has one, this does not);
                                            # SelectMultiple now defaults to true; TriggerOutput replaced
                                            # by DelayOutput; Appearance/ValidationState take typed enums.
    "ModernDatePicker@1.0.0": "grounded",   # CONFIRMED 2026-08-04 — user-supplied Studio YAML
    "Classic/ComboBox@2.4.0": "grounded",   # CONFIRMED 2026-08-04 — classic combo box
    "Classic/DropDown@2.3.1": "grounded",   # CONFIRMED 2026-08-04 — note the capital D in DropDown
    "ListBox@2.2.0":          "grounded",   # CONFIRMED 2026-08-04 — NO Classic/ prefix, like Timer
    "ModernDropdown@1.0.0":   "grounded",   # from MS Learn's own YAML sample, 2026-08-04
    "Form@2.4.4":             "grounded",   # CONFIRMED 2026-08-04 — Variant: Classic, Layout: Vertical
    "TypedDataCard@1.0.7":    "grounded",   # CONFIRMED 2026-08-04 — a Form's data card
    "GroupContainer@1.5.0":   "grounded",   # CONFIRMED 2026-08-04 — auto-layout container,
                                            # read off a Studio code-view photo. Variant: AutoLayout
    "Classic/Toggle@2.1.0":   "grounded",   # CONFIRMED 2026-08-05 — prefixed; a modern Toggle exists
    "RichTextEditor@2.7.0":   "grounded",   # CONFIRMED 2026-08-05 — NO prefix; out is .HtmlText
    "Rating@2.1.0":           "grounded",   # CONFIRMED 2026-08-05 — NO prefix; out is .Value
    "Classic/Slider@2.1.0":   "grounded",   # CONFIRMED 2026-08-05 — prefixed; out is .Value
    "Classic/Radio@2.3.0":    "grounded",   # CONFIRMED 2026-08-05 — prefixed; out is .Selected.Value
    "ModernSlider@1.0.0":     "grounded",   # from MS Learn's own YAML sample, 2026-08-05 —
                                            # same provenance as ModernDropdown@1.0.0
}

# The `Classic/` prefix is not decoration: it appears on exactly those controls whose
# NAME is shared with a modern Fluent control, and is absent where no modern namesake
# exists. Prefixed: Icon, TextInput, Button, ComboBox, DropDown, Toggle, Slider, Radio.
# Bare: Timer, ListBox, RichTextEditor, Rating, Gallery, Image, HtmlViewer, Label, Rectangle.
# Useful for PREDICTING an unseen token — never for asserting one. Ground it, then add it.
# Gallery Variant tokens are NOT "Vertical"/"Horizontal" — that was a guess this
# repo carried for weeks. Studio's own generated YAML names them
# `BrowseLayout_<Orientation>_<Template>_ver5.0`. The vertical one below was read
# straight off a Studio code-view screenshot; the others are corroborated from
# published .pa.yaml in the wild.
KNOWN_VARIANTS = {
    "AutoLayout",        # GroupContainer@1.5.0
    "Classic",           # Form@2.4.4 — CONFIRMED from Studio code view 2026-08-04
    "ClassicTextualEdit",# TypedDataCard@1.0.7 — the text-field card
   # GroupContainer@1.5.0 — CONFIRMED from Studio code view 2026-08-04
    "BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0",   # CONFIRMED from Studio
    "BrowseLayout_Horizontal_TwoTextOneImageVariant_ver5.0",
    "BrowseLayout_Vertical_OneTextVariant_ver5.0",
    "BrowseLayout_Flexible_SocialFeed_ver5.0",
}

# Power Apps 3.24042 (Apr 2024) changed these functions' column-name arguments
# from literal strings to IDENTIFIERS. `Ungroup(t, "v")` now errors with
# "expecting an identifier name"; it must be `Ungroup(t, v)`. Existing apps were
# migrated automatically — but this repo authors from scratch, so nothing
# migrates it for us. Anything written against a pre-2024 example is wrong.
#
# Which ARGUMENT POSITIONS are column names differs per function, and getting
# that wrong makes the check cry wolf: AddColumns' even args are formulas (a
# quoted string there is fine) and Search's second arg is the search text.
# Positions are 0-based over the direct arguments.
COLUMN_ARG_POSITIONS = {
    "ShowColumns":    lambda i: i >= 1,
    "DropColumns":    lambda i: i >= 1,
    "GroupBy":        lambda i: i >= 1,
    "RenameColumns":  lambda i: i >= 1,
    "Ungroup":        lambda i: i == 1,
    "AddColumns":     lambda i: i >= 1 and i % 2 == 1,   # name, formula, name, ...
    "Search":         lambda i: i >= 2,                  # arg 1 is the search text
    "DataSourceInfo": lambda i: i >= 2,
}


def split_args(src: str, open_idx: int):
    """Direct arguments of the call whose '(' is at open_idx — depth-aware."""
    depth, arg, args, in_str = 0, [], [], False
    i = open_idx
    while i < len(src):
        ch = src[i]
        if in_str:
            arg.append(ch)
            if ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
            arg.append(ch)
        elif ch == "(":
            depth += 1
            if depth > 1:
                arg.append(ch)
        elif ch == ")":
            depth -= 1
            if depth == 0:
                args.append("".join(arg).strip())
                return args
            arg.append(ch)
        elif ch == "," and depth == 1:
            args.append("".join(arg).strip())
            arg = []
        else:
            arg.append(ch)
        i += 1
    return None   # unbalanced — leave it to the Power Fx parser

# Behaviour functions that RETURN A VALUE. An Action property declares
# ReturnType: Boolean, but a behaviour formula returns its last expression — so
# ending on one of these means the implementation's type disagrees with the
# contract. Real bug, found in cmpEditableGrid.AddRow (Collect returns a Record).
VALUE_RETURNING_BEHAVIOUR = (
    "Collect", "ClearCollect", "Patch", "Remove", "RemoveIf", "Update", "UpdateIf",
)
PLACEHOLDER = re.compile(r"\b(?:CONFIRM|TODO|TBD|XXX|FIXME)_\w+")

# The 180 classic Icon enum values, recovered from References/Templates.json inside
# a genuine Studio-exported .msapp. See tools/studio-enums.json for provenance.
try:
    ICON_NAMES = set(
        json.loads((pathlib.Path(__file__).parent / "studio-enums.json").read_text())["Icon"]
    )
except Exception:            # reference missing — skip the check rather than fail
    ICON_NAMES = set()


def strip_comments(src: str) -> str:
    """Drop Power Fx `//` line comments — they carry example code that would
    otherwise be parsed as if it were live formula text."""
    out, in_str = [], False
    i = 0
    while i < len(src):
        ch = src[i]
        if in_str:
            out.append(ch)
            if ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
            out.append(ch)
        elif ch == "/" and src[i:i + 2] == "//":
            while i < len(src) and src[i] != "\n":
                i += 1
            continue
        else:
            out.append(ch)
        i += 1
    return "".join(out)


PAIRS = {")": "(", "]": "[", "}": "{"}


def bracket_error(formula: str) -> str | None:
    """Unbalanced (), [] or {} in a formula.

    A formula that does not close cannot work, and Studio reports it as a single
    red control with no clue which paren is missing. It is also the classic
    casualty of an edit that deletes some arms of a long `&`-chain and takes the
    closing parens with them — which is exactly how `lblPrMissing` broke.
    Strings and `//` comments are skipped so their brackets never count.
    """
    src = strip_comments(formula)
    stack, in_str, i = [], False, 0
    while i < len(src):
        ch = src[i]
        if in_str:
            if ch == '"':
                if src[i + 1:i + 2] == '"':   # "" is an escaped quote, not a close
                    i += 1
                else:
                    in_str = False
        elif ch == '"':
            in_str = True
        elif ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != PAIRS[ch]:
                return f"unbalanced brackets — unexpected {ch!r}"
            stack.pop()
        i += 1
    if stack:
        return f"unbalanced brackets — {len(stack)} unclosed {''.join(stack)!r}"
    return None


def walk(node, path=""):
    """Yield (path, dict) for every mapping in the tree."""
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from walk(v, f"{path}/{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}/{i}")


def token_errors(doc) -> list[str]:
    """Pass 2 — the values the schema leaves wide open."""
    out, warned = [], set()
    for path, node in walk(doc):
        ctrl = node.get("Control")
        if isinstance(ctrl, str) and ctrl not in KNOWN_CONTROLS:
            out.append(f"{path}: unknown control token {ctrl!r} — not on the allow-list")
        elif isinstance(ctrl, str) and KNOWN_CONTROLS[ctrl] == "unverified" and ctrl not in warned:
            warned.add(ctrl)
            out.append(f"{path}: NOTE control token {ctrl!r} is UNVERIFIED — a paste using it is a live risk")

        var = node.get("Variant")
        if isinstance(var, str) and var not in KNOWN_VARIANTS:
            out.append(f"{path}: unknown Variant {var!r} — not on the allow-list. Galleries take BrowseLayout_<Orientation>_<Template>_ver5.0; other controls have their own")

    # Action properties: does the implementation actually return what it declares?
    for _, node in walk(doc):
        for cname, cdef in (node.get("ComponentDefinitions") or {}).items():
            props = cdef.get("Properties") or {}
            for pname, p in (cdef.get("CustomProperties") or {}).items():
                if not isinstance(p, dict) or p.get("PropertyKind") != "Action":
                    continue
                if p.get("ReturnType") != "Boolean":
                    continue
                f = str(props.get(pname, "")).strip().rstrip(";").strip()
                last = f.split(";")[-1].strip().lstrip("=").strip()
                if last.startswith(VALUE_RETURNING_BEHAVIOUR):
                    out.append(
                        f"{cname}.{pname}: NOTE Action declares ReturnType: Boolean but its formula "
                        f"ends in {last.split('(')[0]}(), which returns a value — end it with `; true`"
                    )

    # A CanvasComponent instance sized to the screen with no `Visible` sits on
    # top and swallows EVERY click — a transparent fill does not help, the
    # component still hit-tests. Cost a whole preview session on scrHome.
    for path, node in walk(doc):
        for name, body in node.items():
            if not isinstance(body, dict) or body.get("Control") != "CanvasComponent":
                continue
            props = body.get("Properties", {}) or {}
            if "Visible" in props:
                continue
            w, h = str(props.get("Width", "")), str(props.get("Height", ""))
            # A CONDITIONAL size is the other legitimate gate, and the one cmpAppBar
            # uses: `Height: =If(gNavOpen, Parent.Height, Theme.Space.HeaderH)` is
            # full-screen only while the fly-out is open — and then swallowing the
            # click is the point, because the scrim closes the menu with it.
            gated = h.lstrip("=").strip().startswith(("If(", "Switch("))
            if "Parent.Width" in w and "Parent.Height" in h and not gated:
                out.append(
                    f"{path}/{name}: full-screen {body.get('ComponentName')} instance with no "
                    f"`Visible` — it will sit on top and swallow every click on the screen. "
                    f"Gate it on the same flag that opens it, or make its Height conditional"
                )

    # A control's POSITION must not depend on another control's geometry. Studio
    # suffixes a colliding name on paste (SearchBox -> SearchBox_1); if the reference
    # then fails to resolve, the control silently jumps — scrProjects' gallery landed
    # over the filter and search row that way. Anchoring X/Width to a backdrop
    # rectangle is harmless by comparison, so only Y and Height are flagged.
    for path, node in walk(doc):
        for name, body in node.items():
            if not isinstance(body, dict):
                continue
            for prop in ("Y", "Height"):
                f = strip_comments(str((body.get("Properties") or {}).get(prop, "")))
                for ref in re.findall(r"\b([A-Z][A-Za-z0-9_]*|gal[A-Za-z0-9_]*)\.(?:X|Y|Width|Height)\b", f):
                    if ref in ("Parent", "Self", "ThisItem", "App", "Theme"):
                        continue
                    out.append(
                        f"{path}/{name}/{prop}: NOTE positions off `{ref}` — a paste-time rename "
                        f"breaks the chain silently and the control jumps. Prefer Theme arithmetic"
                    )

    # MS Learn documents the Icon property and NEVER enumerates its values, so every
    # icon name here was a guess until the list was recovered from Templates.json
    # inside the example .msapp — a real Studio export, i.e. first-party ground
    # truth. Icon.Back, Icon.Documents and Icon.Table were all invented and would
    # each have failed a paste. Anything off this list must be drawn as an SVG in an
    # Image control instead (the cmpKpiRing pattern).
    for path, node in walk(doc):
        for prop, formula in (node.get("Properties") or {}).items():
            for name in set(re.findall(r"\bIcon\.([A-Za-z0-9_]+)\b", strip_comments(str(formula)))):
                if ICON_NAMES and name not in ICON_NAMES:
                    near = [i for i in ICON_NAMES if name.rstrip("s").lower() in i.lower()][:4]
                    out.append(
                        f"{path}/{prop}: `Icon.{name}` is not one of the {len(ICON_NAMES)} classic "
                        f"icon names" + (f" — did you mean {', '.join('Icon.' + n for n in near)}?" if near else "")
                    )

    # A formula that does not close cannot work. Studio shows it as one red control
    # with no indication of which bracket is missing, and across a one-way gap that
    # comes back as "it's erroring" — so catch it here, where the position is known.
    for path, node in walk(doc):
        for prop, formula in (node.get("Properties") or {}).items():
            if isinstance(formula, str):
                bad = bracket_error(formula)
                if bad:
                    out.append(f"{path}/{prop}: {bad}")
        # A component's CustomProperties[*].Default is a formula too, and it was
        # outside this sweep — an unbalanced one there fails the same paste.
        for cname, cdef in (node.get("ComponentDefinitions") or {}).items():
            for pname, pdef in ((cdef or {}).get("CustomProperties") or {}).items():
                dflt = (pdef or {}).get("Default")
                if isinstance(dflt, str):
                    bad = bracket_error(dflt)
                    if bad:
                        out.append(f"{path}/{cname}/{pname}/Default: {bad}")

    # IfError returns the value of one of its arguments, and MS Learn is explicit
    # that *currently* the types of ALL its arguments must be compatible — not just
    # the ones that could be returned. So the idiom the docs themselves show,
    # `IfError( Patch(…), Notify(…) )`, is rejected: Patch gives a record, Notify a
    # boolean, and Studio says "expecting a record". Wrap the value in a Set so both
    # sides are a Set. This checks the mix of BEHAVIOUR functions only — Text vs a
    # string literal, or DateValue vs Blank(), are fine and not flagged.
    MIXABLE = {"Patch", "Collect", "ClearCollect", "Set", "Notify", "Remove", "RemoveIf"}
    for path, node in walk(doc):
        for prop, formula in (node.get("Properties") or {}).items():
            src = strip_comments(str(formula))
            for m in re.finditer(r"\bIfError\s*\(", src):
                args = split_args(src, m.end() - 1)
                if not args:
                    continue
                kinds = set()
                for a in args:
                    head = re.match(r"([A-Za-z][A-Za-z0-9]*)\s*\(", a.strip())
                    if head and head.group(1) in MIXABLE:
                        kinds.add(head.group(1))
                if len(kinds) > 1:
                    out.append(
                        f"{path}/{prop}: IfError mixes {sorted(kinds)} — all arguments must be "
                        f"type-compatible, so a bare Patch cannot sit against a Notify or Set. "
                        f"Wrap the value: `IfError( Set(gTmp, Patch(…)), Set(gErr, FirstError.Message) )`"
                    )

    # A gallery's own `OnSelect` does NOT reliably fire when the click lands on a
    # child control — the row looks right and does nothing. Confirmed in Studio on
    # the nav rail. The action belongs on a transparent full-template button
    # declared LAST in the row, doing `Select(Parent); <action>`.
    for path, node in walk(doc):
        for name, body in node.items():
            if not isinstance(body, dict):
                continue
            if not str(body.get("Control", "")).startswith("Gallery@"):
                continue
            if "OnSelect" not in (body.get("Properties") or {}):
                continue
            out.append(
                f"{path}/{name}: a gallery's own `OnSelect` does not fire reliably when the "
                f"click lands on a child control — move the action to a transparent "
                f"`Classic/Button@2.2.0` sized to Parent.TemplateWidth/Height, declared LAST "
                f"in Children, doing `Select(Parent); <action>`"
            )

    # A control's `Items` is write-only — you set it, you can't read it. The
    # readable form is `AllItems`. Component custom properties NAMED Items are
    # fine (cmpSelection.Items), so only flag names declared as controls here.
    declared = set()
    for _, node in walk(doc):
        for k, v in node.items():
            if isinstance(v, dict) and "Control" in v:
                declared.add(k)
    if declared:
        for path, node in walk(doc):
            for k, v in node.items():
                if not isinstance(v, str):
                    continue
                for ctrl in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\.Items\b", v):
                    if ctrl in declared:
                        out.append(
                            f"{path}/{k}: reads {ctrl}.Items — a control's Items is set, not read. "
                            f"Use {ctrl}.AllItems, or better, ask the underlying data: a hidden "
                            f"gallery's AllItems is empty, which can latch a Visible formula off"
                        )

    # Column names must be identifiers, not strings (see COLUMN_ARG_POSITIONS).
    for path, node in walk(doc):
        for k, v in node.items():
            if not isinstance(v, str):
                continue
            flat = " ".join(v.split())
            for fn, is_col in COLUMN_ARG_POSITIONS.items():
                for m in re.finditer(rf"\b{fn}\s*\(", flat):
                    args = split_args(flat, flat.index("(", m.start()))
                    if not args:
                        continue
                    bad = [a for i, a in enumerate(args)
                           if is_col(i) and a.startswith('"') and a.endswith('"')]
                    if bad:
                        out.append(
                            f"{path}/{k}: {fn}() takes column names as IDENTIFIERS since "
                            f"Power Apps 3.24042, but got {', '.join(bad)} — drop the quotes "
                            f'(Ungroup(t, v), not Ungroup(t, "v"))'
                        )

    # IsMatch in Power Apps defaults to MatchOptions.Complete, which already wraps
    # the pattern in ^...$. Supplying your own anchors double-anchors it — the trap
    # that got cmpStatusPill rejected. Flag it rather than rely on remembering.
    for path, node in walk(doc):
        for k, v in node.items():
            if isinstance(v, str) and "IsMatch(" in v and ("^" in v or "$" in v):
                out.append(
                    f"{path}/{k}: NOTE IsMatch with a ^ or $ anchor — IsMatch defaults to "
                    f"MatchOptions.Complete in Power Apps, which anchors already. For a fixed "
                    f"word list prefer `value in [\"a\",\"b\"]` (membership, case-insensitive)"
                )

    # Placeholders can hide in any string, not just Control/Variant.
    for path, node in walk(doc):
        for k, v in node.items():
            if isinstance(v, str):
                for m in PLACEHOLDER.findall(v):
                    out.append(f"{path}/{k}: leftover placeholder {m!r} — never paste this")
    return out

def targets(argv):
    if argv:
        return [pathlib.Path(a).resolve() for a in argv]
    # Everything under src/ is source: the App object, the screens, the components.
    return sorted((ROOT / "src").rglob("*.pa.yaml"))

def rel(p: pathlib.Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)

# Built-in control properties an instance may set without the component declaring
# them. Anything else must be a custom property of that component, or the paste
# fails on an unrecognised name — and across a one-way gap that costs a round trip.
INSTANCE_BUILTINS = {
    "X", "Y", "Width", "Height", "Visible", "Fill", "DisplayMode",
    "TabIndex", "Tooltip", "OnReset", "BorderColor", "BorderThickness",
    "AccessibleLabel",
}


def contract_errors(files) -> list[str]:
    """Cross-file check: every property a CanvasComponent instance sets must exist."""
    comps: dict[str, set] = {}
    for f in files:
        try:
            doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        for cname, cdef in ((doc if isinstance(doc, dict) else {}).get("ComponentDefinitions") or {}).items():
            comps[cname] = set((cdef.get("CustomProperties") or {}).keys())
    if not comps:
        return []

    out = []
    for f in files:
        try:
            doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        for path, node in walk(doc):
            for name, body in node.items():
                if not isinstance(body, dict) or body.get("Control") != "CanvasComponent":
                    continue
                cn = body.get("ComponentName")
                if cn not in comps:
                    out.append(f"{rel(f)}: {name} references unknown component {cn!r}")
                    continue
                for prop in (body.get("Properties") or {}):
                    if prop not in INSTANCE_BUILTINS and prop not in comps[cn]:
                        out.append(
                            f"{rel(f)}: {name} ({cn}) sets `{prop}`, which is neither a custom "
                            f"property of {cn} nor a built-in — the paste will fail"
                        )
    return out


# A token grounded in the validator but absent from the machine-readable enums or from the
# controls skill is grounding that Claude will not FIND next session — the knowledge exists
# but nothing routes to it. This audit keeps the three copies in step; it warns rather than
# fails, because the allow-list is what actually gates a paste.
CATALOGUE_EXEMPT = {"CanvasComponent"}   # a component instance, not a control template


def catalogue_gaps() -> list[str]:
    root = pathlib.Path(__file__).resolve().parent.parent
    enums = root / "tools" / "studio-enums.json"
    skill = root / ".claude" / "skills" / "powerapp-canvas-controls" / "SKILL.md"
    out = []
    for f in (enums, skill):
        if not f.exists():
            out.append(f"{rel(f)} is missing — the control catalogue has no second copy")
    enums_txt = enums.read_text(encoding="utf-8") if enums.exists() else ""
    skill_txt = skill.read_text(encoding="utf-8") if skill.exists() else ""
    for tok in KNOWN_CONTROLS:
        if tok in CATALOGUE_EXEMPT:
            continue
        if enums_txt and tok not in enums_txt:
            out.append(f"{tok} is allow-listed but absent from tools/studio-enums.json")
        if skill_txt and tok not in skill_txt:
            out.append(f"{tok} is allow-listed but absent from the powerapp-canvas-controls skill")
    return out


# A duplicate key is the one corruption that passes every other check here.
# PyYAML keeps the LAST of them silently, so a file can carry two copies of a
# control's Control/Properties/Children and still load, validate and report
# "ok" — while everything in the discarded copy is invisible to this script and
# to any edit made against it. That is exactly what happened to scrProjectEdit
# in 445f59d: 132 controls doubled, 360 duplicate keys, 24/24 valid. Studio is
# the only thing downstream that would have caught it, by failing the paste.
def duplicate_keys(text: str) -> list[str]:
    hits: list[str] = []

    class Detect(yaml.SafeLoader):
        pass

    def mapping(loader, node, deep=False):
        out = {}
        for k, v in node.value:
            key = loader.construct_object(k, deep=deep)
            if key in out:
                hits.append(f"line {k.start_mark.line + 1}: duplicate key `{key}`")
            out[key] = loader.construct_object(v, deep=deep)
        return out

    Detect.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try:
        yaml.load(text, Detect)
    except yaml.YAMLError:
        return []          # the parse error is reported by the caller
    return hits


def main() -> int:
    validator = Draft7Validator(yaml.safe_load(SCHEMA.read_text(encoding="utf-8")))
    files = targets(sys.argv[1:])
    if not files:
        print("no files to validate"); return 0

    bad = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        try:
            doc = yaml.safe_load(text)
        except yaml.YAMLError as e:
            print(f"FAIL {rel(f)}\n  YAML parse error: {e}\n"); bad += 1; continue
        if doc is None:
            print(f"SKIP {rel(f)} (empty)"); continue
        dups = duplicate_keys(text)
        if dups:
            bad += 1
            print(f"FAIL {rel(f)}")
            print(f"  {len(dups)} duplicate key(s) — PyYAML keeps the last silently, so")
            print(f"  everything in the discarded copy is invisible to this validator.")
            for d in dups[:12]:
                print(f"    {d}")
            if len(dups) > 12:
                print(f"    ... and {len(dups) - 12} more")
            print()
            continue
        tok = token_errors(doc)
        errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
        hard_tok = [t for t in tok if "NOTE " not in t]
        if not errors and not hard_tok:
            if tok:
                print(f"ok   {rel(f)}")
                for t in tok:
                    print(f"       {t}")
                continue
            print(f"ok   {rel(f)}")
            continue
        bad += 1
        print(f"FAIL {rel(f)}")
        for t in tok:
            print(f"  {t}")
        seen = set()
        for e in errors:
            path = "/".join(str(p) for p in e.absolute_path) or "<root>"
            msg = e.message.split("\n")[0][:200]
            key = (path, msg)
            if key in seen:
                continue
            seen.add(key)
            print(f"  at {path}\n     {msg}")
        print()

    contract = contract_errors(files)
    if contract:
        print("\nFAIL component-instance contracts")
        for c in contract:
            print(f"  {c}")

    gaps = catalogue_gaps()
    if gaps:
        print("\nNOTE control catalogue is out of step (warning, not a paste failure)")
        for g in gaps:
            print(f"  {g}")

    total = len(files)
    print(f"\n{total - bad}/{total} valid" + ("" if not bad else f"  —  {bad} FAILING"))
    if contract:
        print(f"{len(contract)} component-instance contract error(s) — a paste WILL fail on these")
    return 1 if (bad or contract) else 0

if __name__ == "__main__":
    sys.exit(main())
