<!-- Spec Author: what changes in behavior. New requirements are untagged;
existing ones are restated in full as [MODIFIED] or listed as [REMOVED] with a
Reason line. Grammar: method/format.md. Locked at the spec gate. -->

## Requirements

### REQ-ORC-009 Run-plan prints the steps of a run
When the operator runs `sdd.py run-plan [<form>]` for the active change, or the one `--change` names, at planned or implementing, sdd.py shall print the plan of the run that `implement <form>` makes and exit 0, running no command and changing no file: the form is `T<n>` (that task), `T<a>-T<b>` (the tasks from T<a> to T<b> in plan order), `next` (the first unticked task; the default) or `all` (every task of the plan); the first line is `plan for <change-id> (<form>): <n> to do, <m> done`, where n and m count the unticked and the ticked tasks of the range; then come `1. record the tests that pass before the run: <test command>`; one line per task of the range, in plan order: `<k>. T<i>: <command>` for an unticked task, where the command is the design's `Test one:` command with `{test}`, `{file}` and `{name}` filled from the task's test line as replay fills them (REQ-EVD-001), its words joined by single spaces and quoted only where a shell needs it, or `<k>. T<i>: no command (the test line has no "::")` when that command uses `{file}` or `{name}` and the test line has no `::`, or `<k>. T<i>: <Test one command> (no test line yet)` when the task's test line is empty, and `- T<i>: done`, unnumbered, for a ticked task, with the component checkpoints of REQ-ORC-010 placed among them; and last `<k>. full suite: <test command>`; the test command is the design's `Test command:` text without surrounding backticks, and k numbers the numbered lines from 1; a range with no unticked task prints only the first line, its done lines and `nothing to run: no task to do in the range`.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a standard change 0001-x at planned whose design has "- Test command: `runner tests`", "- Test one: `runner {file} {name}`" and "- Test component: `runner -k REQ_{prefix}_`", and tasks T1 (REQ-DUR-001.S1, ticked), T2 (REQ-DUR-001.N1, test line "tests/t_x.py::test_b") and T3 (REQ-DUR-001.S2, test line "tests/t_x.py::test_c") | run-plan T1-T3 | exactly "plan for 0001-x (T1-T3): 2 to do, 1 done", "1. record the tests that pass before the run: runner tests", "- T1: done", "2. T2: runner tests/t_x.py test_b", "3. T3: runner tests/t_x.py test_c", "4. component DUR: runner -k REQ_DUR_", "5. full suite: runner tests" · exit 0 · no command is run · no file is changed |
| S2 | happy | the S1 change, with another change 0002-y active | run-plan T2 --change 0001-x | exactly "plan for 0001-x (T2): 1 to do, 0 done", "1. record the tests that pass before the run: runner tests", "2. T2: runner tests/t_x.py test_b", "3. component DUR: runner -k REQ_DUR_", "4. full suite: runner tests" · exit 0 · no file is changed |
| S3 | happy | the S1 change, active | run-plan next | the S2 lines, with the first line "plan for 0001-x (next): 1 to do, 0 done" · exit 0 |
| S4 | happy | the S1 change, active | run-plan all | the S1 lines, with the first line "plan for 0001-x (all): 2 to do, 1 done" · exit 0 |
| B1 | boundary | the S1 change, active | run-plan T2-T2 | the S2 lines, with the first line "plan for 0001-x (T2-T2): 1 to do, 0 done" · exit 0 |
| B2 | boundary | the S1 change, active | run-plan, with no form | the S3 lines (next is the default) · exit 0 |
| B3 | boundary | the S1 change with T2 and T3 ticked too | run-plan all | exactly "plan for 0001-x (all): 0 to do, 3 done", "- T1: done", "- T2: done", "- T3: done", "nothing to run: no task to do in the range" · no numbered line · exit 0 · no file is changed |
| B4 | boundary | the B3 change | run-plan next | exactly "plan for 0001-x (next): 0 to do, 0 done", "nothing to run: no task to do in the range" · exit 0 · no file is changed |
| B5 | boundary | the S1 change with "- Test one: `runner {test}`" and T2's test line "tests/t_x.py" | run-plan T2 | the step "2. T2: runner tests/t_x.py" · exit 0 |
| B6 | boundary | the S1 change with T2's test line "tests/t_x.py" | run-plan T2 | the step `2. T2: no command (the test line has no "::")`, then the component and full-suite lines of S2 · exit 0 |
| B7 | boundary | the S1 change with T2's test line empty | run-plan T2 | the step "2. T2: runner {file} {name} (no test line yet)", then the component and full-suite lines of S2 · exit 0 |
| B8 | boundary | the S1 change at implementing | run-plan T2 | the S2 lines · exit 0 · the status stays implementing |

- N/A validation: covered by REQ-ORC-011, which refuses a bad form, task ID or design line
- N/A state: covered by REQ-ORC-011, which refuses the other statuses and a missing change
- N/A dependency: only the change's own files are read; no command is run
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ORC-010 Run-plan places a component checkpoint after each group
When `sdd.py run-plan` prints a plan with an unticked task, sdd.py shall print a component checkpoint, `<k>. component <PREFIX>: <command>`, where the command is the design's `Test component:` command (REQ-EVD-004) with every `{prefix}` replaced by PREFIX, for each group of unticked tasks of the range that share a requirement prefix with no unticked task of another prefix between them, a task's prefix being the prefix of its first scenario reference; the checkpoint comes right before the next unticked task with another prefix, or after the range's last task; a ticked task, or a task with no scenario reference, is listed but neither joins nor ends a group; and when the design has no `Test component:` command, or an empty one, sdd.py shall print `component checkpoints skipped: the design has no "Test component:" line` right after the first line and no component step, the full suite staying the last step.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a change at planned with the REQ-ORC-009.S1 design and unticked tasks T1 (REQ-DUR-001.S1), T2 (REQ-DUR-001.N1), T3 (REQ-CLI-001.S1) and T4 (REQ-CLI-001.N1), each with a test line | run-plan all | the numbered lines are, in order: 1 the record step, 2 T1, 3 T2, "4. component DUR: runner -k REQ_DUR_", 5 T3, 6 T4, "7. component CLI: runner -k REQ_CLI_", "8. full suite: runner tests" · exit 0 · no file is changed |
| B1 | boundary | the S1 change | run-plan T1-T3 | 2 T1, 3 T2, "4. component DUR: runner -k REQ_DUR_", 5 T3, "6. component CLI: runner -k REQ_CLI_", "7. full suite: runner tests" (the range ends inside the CLI group) · exit 0 |
| B2 | boundary | the S1 design and unticked tasks T1 (REQ-DUR-001.S1), T2 (REQ-CLI-001.S1) and T3 (REQ-DUR-001.N1) | run-plan all | 2 T1, "3. component DUR: …", 4 T2, "5. component CLI: …", 6 T3, "7. component DUR: …", "8. full suite: runner tests" · exit 0 |
| B3 | boundary | the S1 design and unticked tasks T1 (REQ-DUR-001.S1), T2 (no scenario reference), T3 (REQ-DUR-001.N1), T4 (no scenario reference) and T5 (REQ-CLI-001.S1) | run-plan all | 2 T1, 3 T2, 4 T3, 5 T4, "6. component DUR: …", 7 T5, "8. component CLI: …", "9. full suite: runner tests" · no component line between T1 and T4 · exit 0 |
| B4 | boundary | the S1 design and tasks T1 (REQ-DUR-001.S1, unticked), T2 (REQ-CLI-001.S1, ticked) and T3 (REQ-DUR-001.N1, unticked) | run-plan all | the first line ends "2 to do, 1 done" · 2 T1 · "- T2: done" · 3 T3 · "4. component DUR: …" · "5. full suite: runner tests" · no component CLI line · exit 0 |
| B5 | boundary | the S1 change whose design has no "Test component:" line | run-plan all | the second line is `component checkpoints skipped: the design has no "Test component:" line` · no component step · "6. full suite: runner tests" is the last line · exit 0 · no file is changed |

- N/A validation: the component command is checked at the plan stage by REQ-EVD-004
- N/A state: covered by REQ-ORC-011, which refuses the other statuses and a missing change
- N/A dependency: only the change's own files are read; no command is run
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ORC-011 Run-plan refuses what it cannot plan
If `sdd.py run-plan` is given a form other than `T<n>`, `T<a>-T<b>`, `next` or `all`, a range whose T<a> comes after T<b> in the plan, a task ID that isn't in the plan, a change at a status other than planned or implementing, no active change and no `--change`, a `--change` that names no change in `specs/changes/`, a design with no `Test one:` or no `Test command:` command, or one of these two commands with a quote that doesn't close, then sdd.py shall print an error that names the problem and exit 1, printing no plan line and changing no file.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| N1 | validation | the REQ-ORC-009.S1 change, active | run-plan T1- | exit 1 · the error names "T1-" and lists T<n>, T<a>-T<b>, next and all · no plan line is printed · no file is changed |
| N2 | validation | the REQ-ORC-009.S1 change, active | run-plan T3-T1 | exit 1 · the error says T3 comes after T1 in the plan · no plan line is printed · no file is changed |
| N3 | validation | the REQ-ORC-009.S1 change, which has no task T9 | run-plan T2-T9 | exit 1 · the error names T9 · no plan line is printed · no file is changed |
| N4 | state | the REQ-ORC-009.S1 change at draft | run-plan T2 | exit 1 · the error names the status draft and says run-plan needs planned or implementing · no plan line is printed · no file is changed |
| N5 | state | no active change | run-plan T2 | exit 1 · the error says there is no active change · no plan line is printed · no file is changed |
| N6 | validation | no change 9999-none | run-plan T2 --change 9999-none | exit 1 · the error names 9999-none · no plan line is printed · no file is changed |
| N7 | validation | the REQ-ORC-009.S1 change without a "Test one:" line | run-plan T2 | exit 1 · the error names "Test one:" · no plan line is printed · no file is changed |
| N8 | validation | the REQ-ORC-009.S1 change without a "Test command:" line | run-plan T2 | exit 1 · the error names "Test command:" · no plan line is printed · no file is changed |
| N9 | validation | the REQ-ORC-009.S1 change with "- Test one: `runner '{name}`" | run-plan T2 | exit 1 · the error names "Test one:" and says a quote is not closed · no plan line is printed · no file is changed |
| N10 | validation | the REQ-ORC-009.S1 change with "- Test command: `runner 'tests`" | run-plan T2 | exit 1 · the error names "Test command:" and says a quote is not closed · no plan line is printed · no file is changed |

## Known gaps
<!-- Behavior deliberately not handled, one line each. Required at prototype
(write "- None" if there are none). -->
- A capability declared with two prefixes gets one component checkpoint per prefix, each running part of its tests, not one checkpoint for the capability (0005 Q4).
- A task whose scenario references carry two prefixes is grouped by its first reference only; its other prefix gets no checkpoint from it.
- run-plan prints the `Test component:` command as written: a command without `{prefix}` or with a quote that doesn't close is reported by check at the plan stage (REQ-EVD-004), not by run-plan.
- The plan is advice, like `next`: run-plan runs no step, ticks no task and records no evidence, and a step's result is not proof that it ran.
- A run that spans several changes, and components other than capabilities (such as architectural layers), are not planned.
- The record step prints the full-suite command only; the passing tests it yields are kept and given to sort-failures as change 0007 specifies, by the agent.
- That `implement` follows the printed plan is method work under project rule 1, verified by review and a dogfood run.
