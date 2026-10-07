# Phase: `tasks`

Plan the work test-first, then bring the change to its gate. Role:
**Planner** (`method/roles/planner.md`).

1. The active change must be `draft` with requirements, and
   `SDD check --stage spec` must pass. Otherwise, say what's missing and point
   to `sdd specify`.
2. Write `## Design notes` and `## Tasks`.
3. Run `SDD check` (plan stage) until it reports `result: OK`.
4. If open questions remain, ask them first. Approval is refused while any
   `[NEEDS CLARIFICATION]` marker is left.
5. **Gate: plan.** Show the review digest and ask: "Approve this spec and
   plan?" Then **stop**.
