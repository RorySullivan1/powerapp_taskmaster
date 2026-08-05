# Workflow — ground an unknown control, property or enum

Run this the moment you want a token you cannot cite evidence for. It is always cheaper than a
failed paste.

## 1. Look in the repo first
An `.msapp` is a zip, and its `References/Templates.json` holds enum tables as pipe-delimited
runs:

```bash
unzip -o build/*.msapp -d /tmp/app          # ignore the backslash-path warning
grep -oE '[A-Za-z0-9_]+(\|[A-Za-z0-9_]+){20,}' /tmp/app/References/Templates.json
```

This is how the complete 180-value classic `Icon` enum was recovered — from an export that had
been sitting in `build/` the whole time. **"MS Learn doesn't document it" is not the same as
"ungroundable".**

## 2. Ask for a code-view sample
Insert the control in Studio, open code view, send the YAML or a photo.

**Studio prints only NON-DEFAULT properties.** If you need to know a property's name, ask for
it to be set to something non-default first — that is why the container's scroll switch needed
a second photo.

## 3. MS Learn for semantics
The docs describe **output properties** and **enum members** well even when they never name the
control token. That is where `.SelectedDate`, `.Selected.Value` and `.Text` were confirmed.

## 4. Ship a fallback if it stays unknown
Build the thing from proven tokens — three Rectangles instead of an unverified icon. Note in
the file header what the nicer version would be, so it can be swapped once grounded.

## 5. Record it in all four places, once
- `tools/validate_pa_yaml.py` — the allow-list, with a dated comment. **This is the only copy
  that gates a paste**; the rest are what make it findable.
- `tools/studio-enums.json` — the token, its properties, its OUTPUT property, the Studio
  defaults seen in the sample, and its provenance
- `.claude/skills/powerapp-canvas-controls/SKILL.md` — the grounded-token list, the output-
  property table, and a short YAML example if the control's wiring is not obvious. **A skill
  is how the next session finds this**; a token that exists only in the allow-list is grounding
  nobody will look for.
- `paste-log.md` and `.claude/memory/INDEX.md` — the crossing, and the decision if it corrects
  a previous belief.

Then run `python3 tools/validate_pa_yaml.py`. It **audits the three copies against each other**
and prints `NOTE control catalogue is out of step` for any allow-listed token missing from the
enums file or the skill. A warning there means step 5 is unfinished.

Downstream: if the control writes to SharePoint, check whether the COLUMN needs to change too —
a rich text editor emits markup and needs an *Enhanced rich text* column; a toggle cannot
produce `Blank()`, so a Yes/No column can never mean "unanswered". That belongs in
`sharepoint-list-architecture`, not here.

A token grounded once must never need grounding twice.
