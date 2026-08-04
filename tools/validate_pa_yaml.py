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
import sys, re, pathlib, yaml
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
}
# Gallery Variant tokens are NOT "Vertical"/"Horizontal" — that was a guess this
# repo carried for weeks. Studio's own generated YAML names them
# `BrowseLayout_<Orientation>_<Template>_ver5.0`. The vertical one below was read
# straight off a Studio code-view screenshot; the others are corroborated from
# published .pa.yaml in the wild.
KNOWN_VARIANTS = {
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
            out.append(f"{path}: unknown gallery Variant {var!r} — expected one of {sorted(KNOWN_VARIANTS)}")

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
    src = ROOT / "src" / "authored"
    return sorted([*src.glob("*.pa.yaml"),
                   *(src / "components").glob("*.pa.yaml")])

def rel(p: pathlib.Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)

def main() -> int:
    validator = Draft7Validator(yaml.safe_load(SCHEMA.read_text(encoding="utf-8")))
    files = targets(sys.argv[1:])
    if not files:
        print("no files to validate"); return 0

    bad = 0
    for f in files:
        try:
            doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            print(f"FAIL {rel(f)}\n  YAML parse error: {e}\n"); bad += 1; continue
        if doc is None:
            print(f"SKIP {rel(f)} (empty)"); continue

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

    total = len(files)
    print(f"\n{total - bad}/{total} valid" + ("" if not bad else f"  —  {bad} FAILING"))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
