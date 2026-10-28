# Phase: `implement [T-id | T<a>-T<b> | next | all]`

Deliver tasks test-first. Role: **Implementer**
(`method/roles/implementer.md`).

1. **Precondition.** The active change must be `planned` or `implementing`.
   If it is `draft`, refuse: the plan isn't approved yet, so offer
   `sdd approve`. If it is `planned`, run `SDD advance implementing`.
2. **Select tasks.** `T3` means that task. `T1-T45` means the unticked tasks
   from T1 to T45, in plan order. `next` (the default) means the first
   unticked task. `all` means every unticked task in order. The operator
   authorizes the selection once: the run goes on to its last task without
   asking again, unless a stop condition (step 6) occurs.
3. For each task, run the TDD loop from the role file and record its evidence
   in the task's `test:` / `red:` / `green:` lines. Tick the box only after
   green.
4. After each task, run `SDD check`. It must show no error about that task.
5. **Run the tests at three levels.**
   - **Task:** the task's own test, with the design's `Test one:` command, at
     red and at green. During development this is the only test you run.
   - **Component:** the tests of one capability, with the design's
     `Test component:` command, `{prefix}` replaced by the capability's
     requirement prefix. Run it at the end of that capability's tasks in the
     run: when the next task has another requirement prefix, or when the run
     ends inside it. One checkpoint per prefix. If the design has no
     `Test component:` line, skip the component checkpoints and say so in
     the report.
   - **Full:** the design's `Test command:`, once, before the run closes.

   A **regression** is a test that passed before the task and fails after
   it. A failing test of a task not done yet is **expected**: count it and
   go on; it never stops the run. At each checkpoint and at the end, write
   the failing test names to a file, one per line, and run
   `SDD sort-failures <file>`. It sorts them into `regression` (a ticked
   task plans the scenario), `expected` (no ticked task plans it) and
   `outside` (not a scenario of this change). Judge an outside failure from
   your own runs: if it passed before the task, it is a regression.
6. **Stop and ask the operator** only when:
   - the task's own test still fails, or can't be made to fail for the right
     reason, after two planned fixes;
   - a regression appears that the task can't explain;
   - the spec is ambiguous or wrong for what you found, including work that
     needs something outside the Design notes, such as a new dependency or
     another module.

   Explain the problem and propose the smallest fix. If the fix changes the
   spec, run the `amend` phase (`method/phases/amend.md`). The spec is locked,
   so a quiet edit makes `SDD check` fail.
7. **Before the run closes,** run the full suite and sort its failures.
   - Record each failure that isn't expected with
     `SDD defect add --test <name> --severity <critical|major|minor>`, with
     the severity you suggest. Add `--capability <PREFIX>` when the name
     carries no requirement ID.
   - Give the operator a triage report: each defect with its ID, test,
     capability and suggested severity. Ask for a decision on each: fix now,
     later or won't fix. Only the operator decides.
   - Record each decision with
     `SDD defect decide D<n> <fix-now|later|wont-fix> --evidence "<the operator's words>"`.
     A fix-now defect becomes a `bug` change (`sdd bug`) or a task of this
     change; a later one stays open in the log.
   - When a defect is fixed, or the operator accepts it as is, close it with
     `SDD defect close D<n> --evidence "<what fixed it, or why it is closed>"`.
8. Report the tasks done (each with its red → green line), each component
   checkpoint and its result (or that they were skipped), the full-suite
   result with the `sorted:` counts, and the defects recorded with their
   decisions. Next: `sdd verify` when every task is ticked, else
   `sdd implement` with the tasks left.
