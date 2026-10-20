# Open questions

The app is built, and **the GitHub issues are the backlog of record**: anything to build, fix or
run lives there, grouped under epics. This doc holds only the questions that aren't work items
yet, because their answer depends on the platform rather than on the code. Answered questions
go to the `session-memory` Decisions ledger, with their reasoning, and are deleted here.

The pre-build list, with the old `tm*` list names, is kept verbatim in
`docs/notes/open-questions-prebuild.md`. Don't use it as current.

## Open (not blocking)

- **Q13 Solution-aware?** If the app moves dev → test → prod, it needs **environment
  variables** for its list references instead of hardcoded connections.
- **Q15 Is Azure DevOps available, and can this app live in a Dataverse solution?** This is
  the only route that would retire the clipboard. **Power Platform Git integration** stores
  canvas source as `.pa.yaml` and restores minor repo edits on pull, which makes it a genuine
  two-way channel and the only supported one. It needs **Azure DevOps** (the GitHub canvas
  integration is retired) and a solution. Packaging a `.msapp` by hand is a dead end, not the
  alternative; see `docs/msapp-and-git-integration.md`. The code-view paste channel works, so
  nothing waits on this.
