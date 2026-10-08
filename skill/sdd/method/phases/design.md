# Phase: `design` (standard changes)

Decide **how** the approved spec will be built. Role: **Architect**
(`method/roles/architect.md`).

1. **Precondition.** The active change is `standard` and `spec-approved`. A
   `mini` change keeps its design in the `## Design notes` of `spec.md`, so
   point to `sdd tasks`. A `draft` change needs spec approval first.
2. Write `design.md`: Approach, Components and interfaces, and Test strategy
   with a real `- Test command:` line.
3. **Anything the spec doesn't cover is a question, not a design decision.**
   If you find behavior the spec lacks (an error case, a limit, a timeout),
   don't design it in quietly. Raise it with the operator. If they want it,
   it goes through `sdd amend` (the spec is locked).
4. Run `SDD check` and fix every error.
5. Run `SDD advance designed`. The script refuses if there's no test command.
6. Report the approach in 3–5 bullets, the components touched, and the test
   strategy. Next: `sdd tasks`.
