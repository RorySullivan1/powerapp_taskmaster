# 2026-08-19 02:58 — claudeBrain canvas-app port (outbound #2)

**Goal:** Review this repo's `.claude/` asset set and open a PR of the relevant additions onto
`RorySullivan1/claudeBrain`.

**Result:** [claudeBrain#36](https://github.com/RorySullivan1/claudeBrain/pull/36), branch
`claude/powerapp-canvas-asset-port`. 18 files, +2281.

## The flow is still OUTWARD — and now there is a second data point

The 2026-08-15 port (`e179bef`) carried *corrections* to eight files claudeBrain already had.
This one carries a *capability it does not have*: authoring a canvas app as repo source. Nothing
was imported. Confirm before any future "sync from upstream" — claudeBrain's Power Platform
copies remain downstream of this repo.

## What landed there

- **7 skills** → `example-project/.claude/skills/`: the four `powerapp-canvas-*`,
  `studio-transfer`, `power-apps-svg`, `power-apps-editable-table`.
- **2 agents**: `powerapp-canvas-developer`, `pre-paste-review`.
- **1 brief**: `context/air-gap.md`, paired with `studio-transfer` — pitched as the worked
  instance of the brief↔skill split `context-vs-skill` teaches.
- **4 corrections**: the optional-filter no-op predicate (`power-fx-development`), the
  conditional-required-column rule (`sharepoint-list-architecture`), `EXEMPT_DIRS` in
  `pre_read_guard.py`, and a stale "planned `context-vs-skill`" in `skill-authoring` (×2).

## The decision that took the thinking: Power BI

**Our "Power BI is OUT OF SCOPE" edits are project-local and must NOT be ported.** claudeBrain
still ships `power-bi-dax` and `power-query-m`; importing our scope rewrites would make the
factory contradict its own catalog. So:

- `power-apps-svg` — **rewritten** at three points to defer *outward* reporting to the BI skills
  while keeping the in-app claim. Not dropped: the skill is the whole point of the port.
- `graph-api-integration`, `power-fx-review`, `power-apps-components` — the diffs vs claudeBrain
  were **only** the scope rewrite (plus one local validator note). **Dropped entirely.**

This will recur on every future port. The rule: diff, then ask of each hunk *"is this true for a
generic consumer, or only because this project ruled Power BI out?"*

## Also deliberately dropped

- **`pre_write_column_guard.py`** — inseparable from `schema/schema.yaml`, which
  `example-project/` has no equivalent of. It would ship dead.
- **Meta-skill edits** (`skill-authoring`, `workflow-authoring`, `context-vs-skill`,
  `agent-finder`, `skill-distiller/scripts`) — these only swap worked examples from VBA to
  Power Fx. Correct here, wrong in the factory, whose examples must point at *its*
  `example-project/`. The one exception was the stale "planned" reference, a real bug.
- **`power-fx-development/delegation.md`** — claudeBrain's copy is **better**, not older: the
  port generalised our "Settled in this repo, 2026-08-12" heading into "A Monitor-verified
  result". Do not push ours back over it.

## Flagged to the reviewer, not decided

The ported skills reference `tools/validate_pa_yaml.py`, `tools/studio-enums.json`,
`schema/schema.yaml`, `docs/build-history.md` — none exist in `example-project/`. Left as-is
because the existing example skills also speak as "this repo" and a consumer adapts on copy, but
the PR asks whether they'd rather be genericised. **If the answer comes back "genericise", that
is the follow-up.**

## Mechanics worth not re-deriving

- claudeBrain's canonical copies of operational assets live in `example-project/.claude/`; the
  factory `.claude/` **symlinks** to them (`build-hooks.py`, `catalog.py`, `post_bash_filter.py`,
  `pre_read_guard.py`, `version_guard.py`, and five skill dirs). Editing the example copy is
  enough — do not touch the symlink.
- `catalog.py` and `build-hooks.py --check` must be run in **both** trees, each with
  `CLAUDE_PROJECT_DIR=$PWD`.
- claudeBrain has **no PR template** and no `.github/`.

## Verification

Frontmatter `name:` == folder on all 7; every cross-skill reference in the ported files resolves
to an asset that exists there; both catalogs regenerated (9 new rows); `build-hooks --check`
green in both trees (15 and 13 fragments); `pre_read_guard.py` smoke-tested on all three paths
(exempt → silent, non-exempt → caps, garbage → fails open).
