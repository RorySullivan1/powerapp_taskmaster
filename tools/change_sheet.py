#!/usr/bin/env python3
"""Turn authored .pa.yaml into a FORMULA-BAR change sheet.

The code-view paste route is closed (2026-08-05). What still crosses the gap is
a human selecting a control in Studio and typing/pasting ONE property formula at
a time. So the delivery unit is no longer a file — it is a list of

    <control>  .  <property>  =  <formula>

This script produces that list. Two modes:

    python tools/change_sheet.py src/authored/scrTaskEdit.pa.yaml
        Everything in the file — use when a screen is being built or rebuilt.

    python tools/change_sheet.py --since HEAD~1 src/authored/scrTaskEdit.pa.yaml
        ONLY what changed against that git ref. This is the normal mode during
        refinement: change three properties in the repo, hand over three lines.

Why per-property beats re-pasting even where paste works: Studio FREEZES X/Y/
Width/Height formulas into constants whenever it positions a control, and a
paste positions every control. It also renames anything whose name collides.
A property edit does neither — it touches exactly what it says and nothing else.

Options:
    --only NAME       just this control (repeatable)
    --skip-layout     omit X/Y/Width/Height — they freeze anyway, so during a
                      design pass they are usually noise
    --out PATH        write markdown to a file instead of stdout
"""
from __future__ import annotations
import argparse, pathlib, subprocess, sys, yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAYOUT = {"X", "Y", "Width", "Height"}

# pa-yaml stores every formula with a leading '='. Studio's formula bar renders
# that '=' outside the editable area, so it must NOT be part of what gets typed —
# pasting "=Set(x, 1)" yields "==Set(x, 1)" and an error that looks like a syntax
# problem in the formula itself.
def formula(raw) -> str:
    if not isinstance(raw, str):
        return str(raw)
    return raw[1:] if raw.startswith("=") else raw


def collect(doc) -> dict:
    """name -> {token, variant, props, path} for every control in the document.

    Control names are unique within a screen in pa-yaml and are what the human
    sees in Studio's tree, so the name is the right key: it is how they will
    find the control.
    """
    out: dict[str, dict] = {}

    def walk(children, trail):
        if not isinstance(children, list):
            return
        for entry in children:
            if not isinstance(entry, dict):
                continue
            for name, node in entry.items():
                if not isinstance(node, dict):
                    continue
                out[name] = {
                    "token":   node.get("Control"),
                    "variant": node.get("Variant"),
                    "props":   node.get("Properties") or {},
                    "trail":   trail,
                }
                walk(node.get("Children"), trail + [name])

    if isinstance(doc, list):                      # a component body fragment
        walk(doc, [])
        return out
    if not isinstance(doc, dict):
        return out
    for screen, sdef in (doc.get("Screens") or {}).items():
        if isinstance(sdef, dict):
            # A screen's own properties (OnVisible, Fill) are edited the same way.
            out[screen] = {"token": "Screen", "variant": None,
                           "props": sdef.get("Properties") or {}, "trail": []}
            walk(sdef.get("Children"), [screen])
    for comp, cdef in (doc.get("ComponentDefinitions") or {}).items():
        if isinstance(cdef, dict):
            walk(cdef.get("Children"), [comp])
    return out


def at_ref(ref: str, path: pathlib.Path):
    rel = path.resolve().relative_to(ROOT)
    try:
        blob = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None                                 # file did not exist at that ref
    return yaml.safe_load(blob)


def sheet(path: pathlib.Path, since: str | None, only: set[str], skip_layout: bool) -> list[str]:
    now = collect(yaml.safe_load(path.read_text(encoding="utf-8")))
    was = collect(at_ref(since, path)) if since else None

    lines = [f"## {path.relative_to(ROOT) if path.is_absolute() else path}", ""]
    if was is None and since:
        lines.append(f"*New file — did not exist at `{since}`, so everything below is new.*\n")

    body, touched = [], 0
    for name, cur in now.items():
        if only and name not in only:
            continue
        prev = (was or {}).get(name)
        props = cur["props"]

        changed = {}
        for prop, val in props.items():
            if skip_layout and prop in LAYOUT:
                continue
            if was is None or prev is None or prev["props"].get(prop) != val:
                changed[prop] = val
        # A property present before and gone now must be cleared BY HAND — Studio
        # keeps the old formula until someone deletes it, so silence here is wrong.
        removed = [p for p in (prev["props"] if prev else {})
                   if p not in props and not (skip_layout and p in LAYOUT)]

        if not changed and not removed:
            continue
        touched += 1

        where = " › ".join(cur["trail"]) if cur["trail"] else "(screen root)"
        head = f"### `{name}`"
        if prev is None and was is not None:
            head += "  — **NEW CONTROL: insert it in Studio first**"
        body.append(head)
        body.append(f"*{cur['token']}*"
                    + (f" · `Variant: {cur['variant']}`" if cur.get("variant") else "")
                    + f" · in {where}")
        body.append("")
        for prop, val in changed.items():
            body.append(f"**{prop}**")
            body.append("```powerapps")
            body.append(formula(val))
            body.append("```")
        for prop in removed:
            body.append(f"**{prop}** — ⚠️ DELETE this property's formula (it is gone from the source; "
                        f"Studio keeps the old one until you clear it)")
        body.append("")

    if not touched:
        lines.append("*No changes.*\n")
        return lines
    lines.append(f"**{touched} control(s) to touch.** Select each in Studio's tree, then set the "
                 f"properties listed. The `=` is already handled by the formula bar — paste what "
                 f"is in the block, nothing more.\n")
    return lines + body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--since", help="git ref to diff against (e.g. HEAD~1, a tag, a commit)")
    ap.add_argument("--only", action="append", default=[], help="only this control (repeatable)")
    ap.add_argument("--skip-layout", action="store_true", help="omit X/Y/Width/Height")
    ap.add_argument("--out", help="write to this file instead of stdout")
    a = ap.parse_args()

    chunks = ["# Studio change sheet",
              "",
              "Apply in order. Select the control in the tree, pick the property, paste the block.",
              "**Do not drag anything afterwards** — dragging re-freezes X/Y/Width/Height.",
              ""]
    for f in a.files:
        p = pathlib.Path(f).resolve()
        if not p.exists():
            print(f"no such file: {f}", file=sys.stderr); return 2
        chunks += sheet(p, a.since, set(a.only), a.skip_layout)
    text = "\n".join(chunks)

    if a.out:
        pathlib.Path(a.out).write_text(text, encoding="utf-8")
        print(f"wrote {a.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
