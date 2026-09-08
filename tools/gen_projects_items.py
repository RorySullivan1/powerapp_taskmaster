#!/usr/bin/env python3
"""Generate galProjects.Items for src/Screens/scrProjects.pa.yaml.

THIS FORMULA IS MACHINE-GENERATED. It is hundreds of lines of near-identical
delegable branches, and the whole point of every one of them is that it folds
into a single server query. Hand-editing one branch is how the arms drift apart
and how a filter silently stops folding, so change THIS FILE and regenerate.

    python3 tools/gen_projects_items.py --check     # does the screen match?
    python3 tools/gen_projects_items.py --write     # regenerate it in place

WHY THERE ARE SO MANY BRANCHES. Five binary dimensions — search, show-completed,
only-mine, coverage, priority — and four of them multiply, because an "off"
state has to be a BRANCH rather than a match-everything predicate:
`StartsWith(col, "")` is rejected outright by SharePoint, a Text `<>` does not
delegate, and there is no delegable tautology on a Choice column. That is 32
filter combinations. Every alternative that looks smaller stops folding —
`Sort(If(...))`, a sort key built from an expression, a predicate assembled from
a variable — and a query that stops folding runs over one fetched page and
leaves the rest of a 2,000+ row list unsorted or unfiltered, in silence.

TWO SORT SHAPES, and the choice is a real trade rather than a preference:

  dynamic  32 branches, and what scrProjects ships. One
           `SortByColumns(src, gPrjSortCol, gPrjSortOrd)` per branch, so
           gPrjSortCol IS A COLUMN NAME and must be the SharePoint INTERNAL
           name. A VARIABLE column name DOES delegate — confirmed in Studio on
           the live list (user, 2026-09-08). MS Learn does not document it, so
           that observation is the only evidence there is; if it ever stops
           holding, the symptom is a sort that looks right on the first page and
           leaves the rest of the list in its old order.

  switch   96 branches. A Switch over three arms, each sorting on a LITERAL
           identifier, which is the shape the screen already shipped and is
           certainly delegable. Three times the size, no open question.

Both are generated from the same branch builder, so switching between them is
one flag and costs nothing but a paste.

THE INTERNAL-NAME TRAP, and it is the reason `switch` exists at all: a column
name passed as a STRING is matched against the SharePoint INTERNAL name, while a
Power Fx IDENTIFIER resolves by DISPLAY name. `project_name`'s internal name is
`Title` — it is the built-in Title column, renamed — so `SortByColumns(src,
"project_name", ...)` does not resolve. Every name in COLUMNS below is the
INTERNAL one, and each is recorded in schema/schema.yaml as `internal_name:`.
Add a sort column here only after confirming its internal name in SharePoint
(list settings, click the column, the URL ends `&Field=<internal name>`).
"""
import argparse, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCREEN = ROOT / "src" / "Screens" / "scrProjects.pa.yaml"

# display identifier -> SharePoint INTERNAL name. Order is the Switch arm order.
COLUMNS = [("project_date_target",     "project_date_target"),
           ("project_perc_completion", "project_perc_completion"),
           ("project_name",            "Title")]

COV  = "project_coverage.Value = cboPrjCoverage.Selected.Value"
PRI  = "project_priority.Value = cboPrjPriority.Selected.Value"
MINE = ["( project_manager.Email = gUserEmail", "|| project_supporter.Email = gUserEmail )"]
SRCH = "StartsWith( project_name, Trim(txtProjSearch.Text) )"
ALLC = 'Coalesce(cboPrjCoverage.Selected.Value, "All coverage") = "All coverage"'
ALLP = 'Coalesce(cboPrjPriority.Selected.Value, "All priorities") = "All priorities"'


def _branch(ind, src, sort_arg, preds, last):
    """One delegable branch: a Filter (or the bare source) wrapped in a sort."""
    fn, E, F, P = sort_arg[0], " "*(ind+8), " "*(ind+12), " "*(ind+20)
    tail = sort_arg[1]
    if not preds:
        out = [E + "%s( %s, %s )" % (fn, src, tail)]
    else:
        out = [E + "%s(" % fn, F + "Filter( %s," % src]
        for i, pr in enumerate(preds):
            for j, ln in enumerate(pr if isinstance(pr, list) else [pr]):
                if j:   out.append(" "*(ind+20-len(ln.split()[0])) + ln)
                elif i: out.append(" "*(ind+17) + "&& " + ln)
                else:   out.append(P + ln)
        out[-1] += " ),"
        out.append(F + tail + " )")
    out[-1] += " )" if last else ","
    return out


def _group(ind, sort_arg, search):
    """The 32 filter combinations, as one If().

    Flags are tested most-significant first and ONLY where true, so an arm is
    reached only once every earlier arm has failed — which is what keeps the
    shorter conditions unambiguous. Bits: showComplete, mine, coverageAll,
    priorityAll. Predicate order inside Filter: coverage, priority, mine, search.
    """
    body = []
    for n in range(15, -1, -1):
        sc, mine, covall, priall = [(n >> (3-k)) & 1 for k in range(4)]
        preds = ([COV] if not covall else []) + ([PRI] if not priall else []) \
              + ([MINE] if mine else []) + ([SRCH] if search else [])
        if n:
            toggles = " && ".join([t for t, on in (("tglShowComplete.Value", sc),
                                                   ("tglOnlyMine.Value", mine)) if on])
            parts = ([toggles] if toggles else []) + ([ALLC] if covall else []) \
                  + ([ALLP] if priall else [])
            for i, part in enumerate(parts):
                pre = " "*(ind+8) if i == 0 else " "*(ind+5) + "&& "
                body.append(pre + part + ("," if i == len(parts)-1 else ""))
        body += _branch(ind, "ActiveProjects" if sc else "OpenProjects",
                        sort_arg, preds, n == 0)
    return [" "*(ind+4) + "If( " + body[0].strip()] + body[1:]


def _block(ind, sort_arg):
    out = [" "*ind + "If( Len( Trim(txtProjSearch.Text) ) = 0,"]
    out += _group(ind, sort_arg, False); out[-1] += ","
    out += _group(ind, sort_arg, True);  out[-1] += " )"
    return out


def items(mode):
    if mode == "dynamic":
        lines = [" "*14 + "="] ; lines = []
        body = _block(14, ("SortByColumns", "gPrjSortCol, gPrjSortOrd"))
        body[0] = " "*14 + "=" + body[0].strip()
        lines = body
    else:
        lines = [" "*14 + "=Switch( gPrjSortCol,"]
        for ident, internal in COLUMNS[:-1]:
            lines += [" "*19 + '"%s",' % internal] + _block(19, ("Sort", "%s, gPrjSortOrd" % ident))
            lines[-1] += ","
        lines += _block(19, ("Sort", "%s, gPrjSortOrd" % COLUMNS[-1][0]))
        lines[-1] += " )"
    return "            Items: |\n" + "\n".join(lines) + "\n"


def _slice(text):
    a = text.index("            Items: |\n")
    b = text.index("            # EXPLICIT single column.")
    return a, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dynamic", "switch"], default="dynamic")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    text = SCREEN.read_text()
    a, b = _slice(text)
    gen = items(args.mode)
    if args.check:
        same = re.sub(r"\s+", "", text[a:b]) == re.sub(r"\s+", "", gen)
        print(("MATCHES" if same else "DIFFERS FROM") + " --mode %s" % args.mode)
        return 0 if same else 1
    if args.write:
        SCREEN.write_text(text[:a] + gen + text[b:])
        print("wrote --mode %s: %d branches" % (args.mode, gen.count("gPrjSortOrd")))
        return 0
    sys.stdout.write(gen)
    return 0


if __name__ == "__main__":
    sys.exit(main())
