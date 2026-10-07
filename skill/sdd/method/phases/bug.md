# Phase: `bug "<symptom>"`

Fix a defect so it can't silently come back: reproduce it, trace it to the
spec, prove the fix with a regression test, and keep that test in the living
spec. Roles: **Spec Author** for the defect record and requirements, and
**Planner** for the tasks. Then come the normal `implement` → `verify` →
`archive` phases.

1. **Reproduce first.** Run the case the operator describes, and note the
   exact steps and the real output. If you can't reproduce it, stop and ask
   for details. Don't fix what you can't see.
2. **Trace it to the spec.** Search `specs/capabilities/` for the behavior:
   - **Code defect:** a requirement covers it, and the code disagrees. Then
     `Violates: REQ-…`. Restate that requirement as `[MODIFIED]` with its text
     unchanged, and add a **regression scenario `R1`** built from the
     reproduction.
   - **Spec gap:** no requirement covers it. Then `Violates: spec gap`. The
     expected behavior is a product decision: if the operator hasn't stated
     it, ask (A or B?). Write a new requirement, or a `[MODIFIED]` one that
     extends an existing rule, carrying `R1`.
   - **Not a defect:** the code does what the spec says, but that isn't what's
     wanted. That is a change request: say so, and use `sdd quick` with a
     `[MODIFIED]` requirement.
3. Run `SDD new <slug> --title "<title>" --type defect --capability
   <name>=<PREFIX>`, then fill `## Defect`:
   - Symptom: in the operator's words;
   - Reproduce, Current behavior, Expected behavior;
   - Violates;
   - Root cause: now if you already know it. It is required before
     verification passes.
4. **Requirements.** Give `R1` the category of the failure (validation, state,
   dependency…). At `internal` and above, the usual coverage walk applies to
   every new or modified requirement.
5. **Tasks.** T1 is the regression test. **Its red run must reproduce the
   bug**: the same wrong output you recorded under Current behavior. Then
   come the fix and any other scenarios.
6. Run `SDD check` until it reports `result: OK`. Then follow **Gate: plan**
   exactly as in `method/phases/quick.md` step 9, and stop.

Archiving puts `R1` into the living spec, and its test stays in the suite.
