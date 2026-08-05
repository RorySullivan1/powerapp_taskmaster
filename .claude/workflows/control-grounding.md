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

## 5. Record it, once
- `tools/studio-enums.json` — the token, its properties, its output, its provenance
- `tools/validate_pa_yaml.py` — the allow-list, with a dated comment
- `.claude/memory/INDEX.md` — if it corrects a previous belief

A token grounded once must never need grounding twice.
