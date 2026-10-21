# Phase: `design` (standard changes)

Decide **how** the approved spec will be built. Role: **Architect**
(`method/roles/architect.md`).

1. **Precondition.** The active change is `standard` and `spec-approved`. A
   `mini` change keeps its design in the `## Design notes` of `spec.md`, so
   point to `sdd tasks`. A `draft` change needs spec approval first.
2. Write `design.md`: Approach, Components and interfaces (an
   `- interface: <name>` line for each new interface), Test strategy with a
   real `- Test command:` line, `## Failure modes` and `## Contracts`. The
   grammar of the last two is in `method/format.md` ("design.md").
3. **Anything the spec doesn't cover is a question, not a design decision.**
   If you find behavior the spec lacks (an error case, a limit, a timeout),
   don't design it in quietly. Raise it with the operator. If they want it,
   it goes through `sdd amend` (the spec is locked).
4. **Failure-mode review.** The prime model spawns a **strong read-only
   subagent** (SKILL.md, Orchestration) that reads `spec-delta.md` and
   `design.md` and returns the failure modes the design misses. Without
   subagents (Codex), run the review in a **fresh session** (a new chat). It
   writes nothing. Answer each mode it returns:
   - an existing scenario covers it → add `- FM<n> <what fails> → <scenarios>`;
   - it can't happen in this design → add `- FM<n> <what fails> → N/A: <reason>`;
   - the spec doesn't cover it → raise it with the operator. If they want it,
     it goes through `sdd amend`, then gets its entry.
5. Run `SDD check` and fix every error.
6. Run `SDD advance designed`. The script refuses if there's no test command.
7. Run `SDD analyze` and fix every design error: the trace, the failure
   modes and the contracts (`method/phases/analyze.md`). Its "no tasks yet"
   errors are for `sdd tasks`.
8. Report the approach in 3–5 bullets, the components touched, the test
   strategy and the failure modes with their outcomes. Next: `sdd tasks`.
