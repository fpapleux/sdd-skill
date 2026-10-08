# Phase: `amend "<reason>"`

Change the approved spec while work is under way. The operator decides. Roles:
**Spec Author** for the spec edit and **Planner** for the tasks.

Use it when implementation or verification shows the spec is wrong,
incomplete or ambiguous, or when the operator changes their mind. The Verifier
also uses it when the operator accepts a spec gap as a known gap.

The approved spec is **locked**: `SDD approve plan` stores a fingerprint of
Intent, Defect, Scope, Requirements and Known gaps. Any later edit to those
sections makes `SDD check` fail until the amendment is approved. Tasks and
Design notes stay editable.

1. **Precondition.** The active change is `planned`, `implementing` or
   `verifying`. A `draft` has no approval yet: just edit it.
2. **Stop the current task.** Don't work around the problem in code.
3. **Edit the spec, minimally**, following the Spec Author rules: requirement
   text, scenarios, N/A lines, Known gaps, Scope.
4. **Adjust the tasks** (Planner rules). Add tasks for new scenarios. If a
   ticked task's scenario changed, untick it and redo it test-first.
5. **Log it** under `## Amendments`:
   `- A<n> <date>: <reason> → <what changed>`.
6. Run `SDD check`. It reports "the spec changed since it was approved", which
   is expected until approval. It must show **no other** errors.
7. **Gate: amendment.** Show the operator:
   - the reason;
   - a before → after view of each changed item (use `git diff -- specs/`
     when available);
   - the new or reopened tasks.

   Ask "Approve this amendment?" and **stop**.
8. **Approved:** run `SDD approve amend --evidence "<their words, where,
   date>"`. The spec is locked again. Next: `sdd implement`.
   **Refused:** undo your spec edits. `SDD check` confirms the undo is exact,
   because the lock error disappears. Then continue or stop, as the operator
   decides.
