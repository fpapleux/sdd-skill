# Phase: `tasks`

Plan the work test-first, then bring the change to its gate. Role:
**Planner** (`method/roles/planner.md`).

1. Preconditions:
   - `mini`: the change is `draft` with requirements, and
     `SDD check --stage spec` passes. Otherwise, point to `sdd specify`.
   - `standard`: the change is `designed`. If it is `spec-approved`, point to
     `sdd design`. If it is `draft`, it needs spec approval.
2. Write the tasks: `## Tasks` in `spec.md` (mini, together with `## Design
   notes`) or `tasks.md` (standard; the design is already in `design.md`).
3. Run `SDD check` (plan stage) until it reports `result: OK`.
4. If open questions remain, ask them first. Approval is refused while any
   `[NEEDS CLARIFICATION]` marker is left.
5. **Gate: plan.** Show the review digest, then ask and **stop**:
   - `mini`: "Approve this spec and plan?"
   - `standard`: "Approve this plan?" The spec was approved at the spec gate,
     so the digest focuses on the design and the tasks.
