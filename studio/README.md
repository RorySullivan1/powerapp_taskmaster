# studio/ — INERT under the one-way air gap

> **These folders assumed a two-way gap that does not exist.** The air gap is **one-way**
> (repo → Studio): nothing is ever pulled out of Studio, so there is no pulled state, no
> baseline, and no mirror to maintain here. **The repo itself is the authoritative source.**
> Kept only as inert scaffolding — do not treat anything here as a baseline, and do not wait on
> a "pull" to populate it.

Originally intended (now moot):
- `pulled/` — would have held code-view YAML copied from Studio. **Nothing arrives here** —
  Studio's output can't reach the repo. Ground the paste dialect from the `/example` `.msapp`,
  MS Learn, or the `microsoft/PowerApps-Tooling` schema instead.
- `pulled-src/` — would have held a read-only `.pa.yaml` export for whole-app reasoning. Same
  problem: the work machine's exports never come back. (`/example` is the public sample we mine.)
- `snapshots/` — transient scratch. **Gitignored.** Also unused.

See the `studio-transfer` skill (one-way principles) and `CLAUDE.md` "The air gap". The
`/pull-reconcile` command is **deprecated** for the same reason.
