#!/usr/bin/env python3
"""PreToolUse(Write|Edit) guard: refuse a SharePoint column token that is not in the schema.

`CLAUDE.md`'s output contract says every field token must resolve to a `name:` in
`schema/schema.yaml`. That has been prose the model can drift past, and the cost of
drifting is not a failed test — there are none — it is a failed manual paste on a work
machine, reported back across a one-way gap as "it didn't work". This hook makes the
rule enforced instead of aspirational.

WHAT IT CHECKS
    Writes and edits to files under `src/` only. That is where the output contract
    applies; `tests/` probes are deliberately self-contained and `docs/` is prose.

HOW IT DECIDES, and why it is narrow on purpose
    It only judges snake_case tokens whose PREFIX is already a prefix of some real
    column (`task_`, `project_`, `issue_`, …). That namespace is, in this repo,
    exclusively SharePoint columns — globals and collections are camelCase (`gTkStage`,
    `colTkProducts`) and never match. So a typo in a real column is caught, while
    ordinary Power Fx is never even considered.

    Comments are stripped first. Screens legitimately discuss RETIRED columns by name
    (`task_output_approval`, the pre-2026-08-09 lookup) and blocking a comment would be
    the guard misfiring on the one thing the repo asks for: an explanation of why the
    code is the way it is.

HOW IT FAILS
    Fail-OPEN on anything unexpected — unreadable schema, unparsable input, no tokens,
    any exception at all → exit 0, write proceeds, silently. A guard that blocks work it
    does not understand is worse than no guard. It fails CLOSED only on a positive
    identification: a token in the columns' own namespace that no column matches.

    If it is ever wrong, it names the token it objected to, so the fix is obvious and
    the escape is to correct the token, rename the identifier out of the column
    namespace, or delete this hook's fragment and rebuild.
"""
import difflib
import json
import os
import re
import sys
from pathlib import Path

# A snake_case identifier: a lowercase word, an underscore, then more.
TOKEN = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")

# Tokens that live in the column namespace but are not columns.
ALLOW = {
    # SharePoint's own encoded-space form, and connector/OData shapes.
    "odata_type",
    # Power Fx / connector identifiers that happen to be snake_case.
    "search_term",
}


def columns_and_prefixes(schema_path: Path):
    """Every column name in the golden source, plus the prefix namespace they occupy."""
    text = schema_path.read_text(encoding="utf-8")
    # Parse the `name:` keys directly rather than with a YAML loader: the file carries
    # commented-out lists (retired ones) whose columns are still referenced in comments,
    # and a text scan keeps this hook free of a PyYAML dependency at hook time.
    names = set(re.findall(r"\bname:\s*([a-z][a-z0-9_]*)", text))
    # LIST names count as valid tokens too. Screens name the list itself constantly —
    # `Filter(taskmaster_issues, ...)`, `lookup: { list: asset_library }` — and those
    # share the columns' prefix namespace, so without this every data source in the app
    # reads as an invented column. Any snake_case key at two-space indent qualifies;
    # over-including here only makes the guard quieter, which is the safe direction for
    # something that blocks.
    names |= set(re.findall(r"(?m)^  ([a-z][a-z0-9_]*):\s*$", text))
    prefixes = {n.split("_", 1)[0] for n in names if "_" in n}
    return names, prefixes


def strip_comments(text: str) -> str:
    out = []
    for line in text.split("\n"):
        s = line.lstrip()
        if s.startswith("#") or s.startswith("//"):
            continue
        # Trailing Power Fx comment, but never a URL's `//`.
        line = re.sub(r"(?<!:)//.*$", "", line)
        # Trailing YAML comment.
        line = re.sub(r"\s#\s.*$", "", line)
        out.append(line)
    return "\n".join(out)


def offenders(content: str, names: set, prefixes: set) -> list:
    bad = {}
    for tok in TOKEN.findall(strip_comments(content)):
        if tok in names or tok in ALLOW:
            continue
        if tok.split("_", 1)[0] not in prefixes:
            continue        # not in the columns' namespace — none of this hook's business
        if tok not in bad:
            near = difflib.get_close_matches(tok, sorted(names), n=1, cutoff=0.75)
            bad[tok] = near[0] if near else None
    return sorted(bad.items())


def main() -> int:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        if data.get("tool_name") not in ("Write", "Edit"):
            return 0
        ti = data.get("tool_input") or {}
        fp = ti.get("file_path")
        if not fp:
            return 0

        root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
        try:
            parts = Path(fp).resolve().relative_to(root.resolve()).parts
        except (OSError, ValueError):
            return 0
        if not parts or parts[0] != "src":
            return 0

        content = ti.get("content") or ti.get("new_string") or ""
        if not content.strip():
            return 0

        schema = root / "schema" / "schema.yaml"
        if not schema.is_file():
            return 0
        names, prefixes = columns_and_prefixes(schema)
        if not names:
            return 0

        bad = offenders(content, names, prefixes)
        if not bad:
            return 0
    except Exception:
        return 0        # fail OPEN — never block on something this hook cannot parse

    lines = [
        "Blocked: this write names SharePoint columns that are not in "
        "schema/schema.yaml, the golden source.",
        "",
    ]
    for tok, near in bad:
        lines.append(f"  {tok}" + (f"   — did you mean {near}?" if near else "   — no close match"))
    lines += [
        "",
        "A column that does not exist is not a test failure here; it is a paste that "
        "fails on a work machine and comes back as \"it didn't work\".",
        "Fix the token, or add the column to schema/schema.yaml first — the repo "
        "defines the schema and SharePoint is provisioned to match it.",
    ]
    print("\n".join(lines), file=sys.stderr)
    return 2        # non-zero vetoes the tool call


if __name__ == "__main__":
    raise SystemExit(main())
