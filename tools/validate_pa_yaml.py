#!/usr/bin/env python3
"""Validate authored *.pa.yaml / *.fx.yaml against Microsoft's official
Power Apps source schema (pa-yaml v3.0).

The air gap is one-way: a malformed file comes back only as "it didn't work".
This is the one check we CAN run before a paste, so run it before every hand-off.

    python tools/validate_pa_yaml.py            # validate everything authored
    python tools/validate_pa_yaml.py <paths>    # validate specific files

Schema vendored from (MS Learn links to this as the current static schema):
https://raw.githubusercontent.com/microsoft/PowerApps-Tooling/refs/heads/master/schemas/pa-yaml/v3.0/pa.schema.yaml
"""
from __future__ import annotations
import sys, pathlib, yaml
from jsonschema import Draft7Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "tools" / "pa.schema.v3.0.yaml"

def targets(argv):
    if argv:
        return [pathlib.Path(a) for a in argv]
    src = ROOT / "src" / "authored"
    return sorted([*src.glob("*.fx.yaml"), *src.glob("*.pa.yaml"),
                   *(src / "components").glob("*.pa.yaml")])

def main() -> int:
    validator = Draft7Validator(yaml.safe_load(SCHEMA.read_text()))
    files = targets(sys.argv[1:])
    if not files:
        print("no files to validate"); return 0

    bad = 0
    for f in files:
        try:
            doc = yaml.safe_load(f.read_text())
        except yaml.YAMLError as e:
            print(f"FAIL {f.relative_to(ROOT)}\n  YAML parse error: {e}\n"); bad += 1; continue
        if doc is None:
            print(f"SKIP {f.relative_to(ROOT)} (empty)"); continue

        errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
        if not errors:
            print(f"ok   {f.relative_to(ROOT)}")
            continue
        bad += 1
        print(f"FAIL {f.relative_to(ROOT)}")
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
