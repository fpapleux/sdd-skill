# Phase: `implement [T-id | next | all]`

Deliver tasks test-first. Role: **Implementer**
(`method/roles/implementer.md`).

1. **Precondition.** The active change must be `planned` or `implementing`.
   If it is `draft`, refuse: the plan isn't approved yet, so offer
   `sdd approve`. If it is `planned`, run `SDD advance implementing`.
2. **Select tasks.** `T3` means that task. `next` (the default) means the
   first unticked task. `all` means every unticked task in order, stopping at
   the first problem.
3. For each task, run the TDD loop from the role file and record its evidence
   in the task's `test:` / `red:` / `green:` lines. Tick the box only after
   green.
4. After each task, run `SDD check`. It must show no error about that task.
5. **Stop and ask the operator** when:
   - the spec is ambiguous or wrong for what you found;
   - the work needs something outside the Design notes, such as a new
     dependency or another module;
   - a test can't be made to fail for the right reason.

   Explain the problem and propose the smallest fix. If the fix changes the
   spec, run the `amend` phase (`method/phases/amend.md`). The spec is locked,
   so a quiet edit makes `SDD check` fail.
6. When every task is ticked, run the full test command. Report the tasks
   done (each with its red → green line) and the full-suite result. Next:
   `sdd verify`.
