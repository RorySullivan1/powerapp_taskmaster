#!/usr/bin/env python3
"""Emit src/App.pa.yaml's OnStart or Formulas body ready for the Studio FORMULA BAR.

The App object has no code view, so both properties cross the gap through the
formula bar by hand. Two things about that channel bite:

  1. THE LEADING `=` IS A pa-yaml MARKER, NOT PART OF THE FORMULA. The formula
     bar renders its own `=` outside the editable area, so pasting ours yields
     `==` and an error that reads like a syntax fault in the first statement.

  2. `//` RUNS TO END OF LINE. If the paste loses its newlines - which is what
     a COLLAPSED formula bar does to multi-line text - the first comment
     swallows the entire rest of the property. Our body opens with a comment,
     so the result is that NOTHING is set: no gTheme, no gNavMenu, no
     gStageWeights. Every screen then reads blank for every colour and every
     gTheme.Space.* dimension, which renders as squished and black.

`--bare` stops that being possible by removing the comments. The reasoning
stays in the repo, which is the authoritative source; Studio only needs the
code. Use it when the full paste has failed, or pre-emptively.

    python3 tools/formula_bar_body.py onstart --bare   # App.OnStart, code only
    python3 tools/formula_bar_body.py formulas --bare  # App.Formulas, code only
"""
import pathlib
import re
import sys

SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "App.pa.yaml"

# The App object has TWO formula-bar properties now. OnStart carries the constants
# (Theme and friends); Formulas keeps only the data-source filters, which must stay
# lazy to delegate. Both cross the gap the same way and both need the same care.
BLOCKS = {"formulas": "    Formulas: |-\n", "onstart": "    OnStart: |-\n"}


def strip_line_comment(line: str) -> str:
    """Drop a // comment, ignoring // inside a string literal."""
    out, in_str, i = [], False, 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            in_str = not in_str
        if not in_str and ch == "/" and i + 1 < len(line) and line[i + 1] == "/":
            break
        out.append(ch)
        i += 1
    return "".join(out).rstrip()


def main() -> int:
    bare = "--bare" in sys.argv
    which = next((a for a in sys.argv[1:] if a in BLOCKS), "onstart")
    marker = BLOCKS[which]
    text = SRC.read_text()
    if marker not in text:
        print(f"App.{which} block not found", file=sys.stderr)
        return 1

    body = text.split(marker, 1)[1]
    lines = []
    for raw in body.split("\n"):
        if raw.strip() and not raw.startswith("      "):
            break                      # dedented out of the block scalar
        lines.append(raw[6:] if raw.startswith("      ") else raw)

    # Drop the lone `=` marker - the formula bar supplies its own.
    while lines and lines[0].strip() in ("", "="):
        lines.pop(0)

    if bare:
        kept = [strip_line_comment(l) for l in lines]
        lines = [l for l in kept if l.strip()]

    out = "\n".join(lines).rstrip() + "\n"

    if which == "onstart":
        names = re.findall(r"Set\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*,", out)
        label = "globals Set"
    else:
        names = re.findall(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=", out, re.M)
        label = "named formulas"
    print(out)
    print(f"--- {len(names)} {label}: {', '.join(names)}", file=sys.stderr)
    print(f"--- App.{which}: {len(out.splitlines())} lines, "
          f"{'no comments' if bare else 'with comments'}", file=sys.stderr)
    if not bare and any("//" in l for l in lines):
        print("--- NOTE: contains // comments. EXPAND the formula bar before pasting, or the\n"
              "    newlines collapse and the first comment swallows everything after it.\n"
              "    Re-run with --bare if the paste fails.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
