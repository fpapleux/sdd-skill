# Phase: `analyze`

Check the change across its artifacts (spec, design, tasks) before the plan
gate. Read-only: `SDD analyze` writes nothing, and neither does this phase.

1. Run `SDD analyze`. Add `--change <id>` for a change other than the active
   one (the active change is not switched), and `--json` for check's keys
   with the findings merged into `errors` and `warnings`.
2. Read the report. It is check's plan-stage report headed
   `analyze <id> (assurance: <level>)`, with the cross-artifact findings
   added to its errors and warnings, then
   `scenarios: <h> happy, <n> negative, <b> boundary` and `result: OK|FAIL`.
   Exit 1 means at least one error. What it adds:
   - **Design trace** (standard, `designed` or later): an error for a
     requirement ID that `design.md` names and that exists nowhere; a warning
     for a requirement of the change the design never names.
   - **Failure modes** (standard, `designed` or later): an error for each
     malformed entry, a scenario reference that doesn't count, or a repeated
     FM number; no entry at all is an error at `production` and above, a
     warning below.
   - **Contracts** (standard, plan stage on; `SDD check` reports them too):
     an interface with no `### <name>` entry, a nameless line or entry, a
     repeated entry; a warning for an entry no interface lists.
   - **Clauses** (any size): a warning for each clause of a statement
     (split at `;`) whose distinctive words no scenario mentions.
   - **Balance** (any size, above `prototype`): a warning when happy
     scenarios outnumber negative and boundary ones together.
3. **Route each error** to the phase that fixes it:
   - design errors (`design.md names …`, `Failure modes: …`,
     `design.md has no failure modes`, contract errors) → `sdd design`;
   - a failure mode that `… needs an amendment (sdd amend)` → raise it with
     the operator; if they want it, `sdd amend`;
   - plan errors (no tasks, a scenario no task plans, tier, evidence or
     mutation errors) → `sdd tasks`;
   - any other error in the approved spec → `sdd amend`.
4. **Report the warnings** in one line each. They never block. The clause
   and balance warnings are heuristics: judge each one, and add a scenario
   only when a behavior really is untested. Don't reword the spec to silence
   them.
5. Report the result line, the errors grouped by the phase that fixes them,
   and the warnings. Next: the phase for the first error or, when the result
   is OK, **Gate: plan** (`method/phases/tasks.md` step 5). `SDD approve plan`
   runs the same analysis and refuses while it reports an error.
