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
    "HtmlViewer@2.1.0":       "unverified", # "HTML text" — name is best-effort
    "Classic/Timer@2.1.0":    "unverified", # "Timer" — name is best-effort
}
KNOWN_VARIANTS = {"Vertical", "Horizontal"}
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
