#!/usr/bin/env python3
"""Undefined-global audit.

A global that is READ but never `Set()` anywhere in the app has no type, so
Studio reports it as unknown and every `gFoo.column` reference against it fails
to resolve. This is invisible in the repo — the YAML is perfectly valid — and
only shows up once a human opens the screen in Studio, which across a one-way
gap costs a round trip to learn.

It happens when a screen is authored with an Edit path before anything can
reach that path: `scrClientEdit` read `gEditClient` for two days while the only
entry point opened it in New mode, so nothing ever assigned it.

App NAMED FORMULAS are declared in App.pa.yaml rather than assigned, so they are
read from there and excluded — `gUserEmail` are
legitimately never `Set`.

  python3 tools/audit_globals.py
"""
import io
import re
import glob
import sys


def audit(root="src"):
    read, written = {}, set()
    for f in glob.glob(f"{root}/**/*.pa.yaml", recursive=True):
        for n, line in enumerate(io.open(f, encoding="utf-8"), 1):
            if line.lstrip().startswith("#"):
                continue
            code = re.sub(r"//.*", "", line)
            for m in re.findall(r"\bSet\(\s*(g[A-Z]\w*)", code):
                written.add(m)
            for m in re.findall(r"\b(g[A-Z]\w*)\b", code):
                read.setdefault(m, []).append((f.split("/")[-1], n))

    app = io.open(f"{root}/App.pa.yaml", encoding="utf-8").read()
    named = set(re.findall(r"^\s{6}(g[A-Z]\w*)\s*=", app, re.M))

    undefined = sorted(set(read) - written - named)
    return undefined, read, named


if __name__ == "__main__":
    undefined, read, named = audit()
    print("App named formulas (declared, never Set — fine): %s" % ", ".join(sorted(named)))
    if not undefined:
        print("OK — every other global that is read is Set somewhere")
        sys.exit(0)
    print("\n%d GLOBAL(S) READ BUT NEVER Set — Studio will show these as unknown:" % len(undefined))
    for g in undefined:
        where = sorted({w for w, _ in read[g]})
        print("   %-22s read in: %s" % (g, ", ".join(where)))
    sys.exit(1)
