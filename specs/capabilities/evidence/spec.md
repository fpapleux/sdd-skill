---
capability: evidence
prefix: EVD
---

# Capability: evidence

<!-- Living spec: the current, approved behavior of this capability.
Maintained by `sdd.py archive`. Do not edit by hand. -->

## Known gaps
<!-- Behavior deliberately not handled yet, carried from archived changes. -->
- The runner and tier in review records are written by the agent and not verified, like approval rows. (0002-subagent-fanout)
- Read-only subagents are an instruction, not enforced by the host (Q3): no agent files are installed. (0002-subagent-fanout)
- Replay and mutate have no time limit: a test that hangs makes them hang. (0002-subagent-fanout)
- A mutation is a single-line find and replace; changes spanning lines can't be planned. (0002-subagent-fanout)
- Replay and mutate read only the per-test command's exit code: 0 is a pass, anything else a failure. (0002-subagent-fanout)
- A task's test line is run as one test; a task proven by several tests is replayed through its test line only. (0002-subagent-fanout)
- A replay or mutate run that is killed can leave a scratch copy in the system's temporary folder. (0002-subagent-fanout)
- Replay's current-tree pass runs the tests in the working tree itself: files a test writes there are the test's doing, and replay doesn't undo them. (0002-subagent-fanout)
- A task that depends on an earlier task is checked only in the working tree: its red run at that intermediate state is not replayed. (0002-subagent-fanout)
- sort-failures reads the names the agent gives it; it doesn't run tests or read a runner's report. (0005-scoped-test-runs)
- A failing test outside the change is sorted outside, even when it passed before the run; telling it apart needs a baseline (follow-up change). (0005-scoped-test-runs)
- The component command is not checked to select a capability's tests: a command that selects none passes. (0005-scoped-test-runs)
- The defect log is plain text: a hand edit that keeps the row format is not detected, and decisions and close evidence are recorded by the agent, not verified, like approval rows. (0005-scoped-test-runs)
- Deleting specs/defects.md restarts the numbering at D1. (0005-scoped-test-runs)
- A defect's severity can't be changed after it is added; the operator's view of it goes in the decision. (0005-scoped-test-runs)
- The same failure seen in several tests gives several defects; one test has at most one open defect. (0005-scoped-test-runs)
- Two defect commands run at the same moment can write the same ID (concurrency is not required at production). (0005-scoped-test-runs)
- next-req counts requirement IDs written with hyphens in specs/defects.md test names, so it can skip a number. (0005-scoped-test-runs)
- The method's part (implement ranges, the three test levels, the stop conditions, the triage report, what a capability is) is design work under project rule 1, verified by review and a dogfood run. (0005-scoped-test-runs)
- sort-failures doesn't check the list, beyond warning when it names no test: that its tests passed, or that it was recorded before the run's first task. It reads the names the agent gives it. (0007-passed-before)
- A test renamed during the run is not on the list under its new name, so REQ-EVD-005 alone sorts it. (0007-passed-before)
- A test that passed before and fails because the change deliberately alters the behavior it checks is a regression until the Implementer updates it; the list can't mark an intended change. (0007-passed-before)
- Without --passed-before, sort-failures sorts by name only, as in 0.19.0, and doesn't warn that no list was given. (0007-passed-before)
- REQ-EVD-005's text doesn't mention `--passed-before`; when the option is given, REQ-EVD-006 decides the lines it changes, and REQ-EVD-005 stays as it is. (0007-passed-before)
- The method's part (recording the list before the run's first task and giving it at every sort) is design work under project rule 1, verified by review and a dogfood run. (0007-passed-before)
- A capability declared with two prefixes gets one component checkpoint per prefix, each running part of its tests, not one checkpoint for the capability (0005 Q4). (0008-run-plan)
- A task whose scenario references carry two prefixes is grouped by its first reference only; its other prefix gets no checkpoint from it. (0008-run-plan)
- run-plan prints the `Test component:` command as written: a command without `{prefix}` or with a quote that doesn't close is reported by check at the plan stage (REQ-EVD-004), not by run-plan. (0008-run-plan)
- run-plan runs no step, ticks no task and records no evidence; `sdd.py test` runs the steps (REQ-EVD-007), and ticking a task stays the agent's. (0008-run-plan)
- A run that spans several changes, and components other than capabilities (such as architectural layers), are not planned. (0008-run-plan)
- The plan lists the test steps only: `advance implementing` at planned and the check after each task stay in implement.md (round 1 Q1); the sorts are in the `test` report (REQ-EVD-007). (0008-run-plan)
- check at the plan stage and `advance designed` read `Test command:` as its first mention anywhere in the change, and replay and mutate read `Test one:` as its first list line anywhere in the change, not from the design's list line that run-plan reads, so a prose mention or a list line outside the design can stand in for the design's line and the command replay runs can differ from the one run-plan prints; this defect is outside this change, and the operator decides on a separate defect change. (0008-run-plan)
- That `implement` follows the printed plan is method work under project rule 1, verified by review and a dogfood run. (0008-run-plan)
- A test run that never ends is not stopped: sdd.py waits for the command to end. (0008-run-plan)
- A step reuses only the last run (Q4), so steps that alternate (a task, its component, the full suite) rarely reuse one; earlier runs stay as run-of files that git ignores, on the machine that ran them. A change planned before this rule has no baseline.txt, so its runs sort as REQ-EVD-005 did, with the warning. (0008-run-plan)
- A baseline is refused once a task is ticked, but a code edit made before the first tick, outside a task, is not detected: the baseline then holds the edited code's results. (0008-run-plan)
- A red line that holds only after an earlier task's code (`(after T<n>)`) and a `red: pre-existing` line are still written by hand; `test --red` writes neither. (0008-run-plan)
- A runner that can't write JUnit XML gets the exit code and the last 20 lines only: no per-test outcome, no sorting, no red or green line. A project's own adapter that writes the report (as this repository's unittest one, in the design) is the way round it. (0008-run-plan)
- Reuse compares file content, not what the tests read: a change to a file git ignores, an environment variable or a service the tests call doesn't stop a reuse; --rerun runs the step anyway. (0008-run-plan)
- That implement and verify run their test steps through `sdd.py test`, and read its report instead of the output, is method work under project rule 1, verified by review and a dogfood run. (0008-run-plan)
- Only the project folder's absolute path is written as `.`: other local paths in a runner's output (the home folder, a virtual environment, a temporary folder) are kept as they are in the committed last-run.log, and a project rule against local paths in committed files is checked by the operator. (0008-run-plan)
- A red or green line typed by hand in the form sdd.py writes, with "(sdd test <time>)", is not told apart from one sdd.py wrote: the mark isn't checked against a recorded run. (0008-run-plan)
- Two `sdd.py test` runs at the same moment can overwrite each other's report and last run (concurrency is not required at production). (0008-run-plan)
- Duplicate test names in one report are counted as the report lists them, and a name that both passed and failed counts as failed. (0008-run-plan)
- A runner's output is kept whole, with no size cap, and a large last-run.log is committed. (0008-run-plan)
- Files a runner writes that git doesn't ignore (caches, coverage data) change the digest, so no run is reused after them. (0008-run-plan)
- A test line holding `{name}` or `{file}`, or several `::`, is filled as replay fills it (REQ-EVD-001), for the defect change on the loose readers. (0008-run-plan)
- No platform is named: Windows paths in commands and a missing `python3` are not handled. (0008-run-plan)
- A test name with surrounding spaces or a newline doesn't survive baseline.txt, so it isn't matched to the baseline. (0008-run-plan)
- A range with nothing left to run still prints "component checkpoints skipped" when the design has no Test component line (verification F2). (0008-run-plan)
- No test catches the reused suffix on a result line with no report, a submodule in the digest, the skip of a tracked file deleted in the working tree, or write_evidence keeping CRLF line endings and ending its block at a heading (verification F4). (0008-run-plan)
- A file the runner creates gets the umask default mode; only an existing file's mode is kept (verification F3). (0008-run-plan)

## Change history
- 0002-subagent-fanout — Subagent fan-out: prime orchestrator, role tiers, scripted verification evidence (2026-10-18): added REQ-EVD-001, added REQ-EVD-002, added REQ-EVD-003
- 0005-scoped-test-runs — Scoped test runs and a defect log (2026-10-28): added REQ-EVD-004, added REQ-EVD-005
- 0007-passed-before — Tests that passed before the run count as regressions (2026-11-03): added REQ-EVD-006
- 0008-run-plan — A scripted plan of a run's steps and checkpoints (2026-11-25): added REQ-EVD-007, added REQ-EVD-008, added REQ-EVD-009, added REQ-EVD-010, added REQ-EVD-011

## Requirements

### REQ-EVD-001 Replay the tests against the base revision
When `sdd.py replay --base <rev>` is run, sdd.py shall run each ticked task's
test through the design's per-test command, once in a scratch copy of the base
revision over which every current test file is laid and once in the current
working tree, and shall print each command it runs and each task as confirmed
or as a mismatch, exiting 1 if any task is a mismatch. A task is a mismatch
when it has no test line, when its test fails in the working tree, when it
claims a red run and its test passes at the base, or when it claims
pre-existing behavior and its test fails at the base. A task whose red line
contains "(after T<n>)", naming a task listed before it, depends on that task:
its test runs only in the working tree, and it is reported "confirmed now
(depends on T<n>)" when the test passes, or as a mismatch when it fails. The
per-test command is
the design's `Test one:` line, in which `{test}` stands for the task's test
line and `{file}` and `{name}` for its parts before and after `::`; it runs
from the root of the copy or of the working tree. The current test files are
the files format.md counts as test files, tracked or untracked and not ignored
by git. The working tree is unchanged when `git status --porcelain` and the
content of its tracked and untracked, not ignored, files are the same before
and after the run.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a ticked red task whose test fails at the base revision and passes now | replay --base <base> | exit 0 · T1 is reported confirmed · the working tree is unchanged · no scratch copy is left |
| S2 | happy | a ticked pre-existing task whose test passes at the base revision and now | replay --base <base> | exit 0 · T1 is reported confirmed |
| N1 | state | a ticked red task whose test passes at the base revision | replay --base <base> | exit 1 · T1 is reported as a mismatch: red claimed, but the test passes at the base · the working tree is unchanged |
| N2 | state | a ticked pre-existing task whose test fails at the base revision | replay --base <base> | exit 1 · T1 is reported as a mismatch: pre-existing claimed, but the test fails at the base · the working tree is unchanged |
| N3 | state | a ticked task whose test fails in the current working tree | replay --base <base> | exit 1 · T1 is reported as a mismatch: the test fails now · the working tree is unchanged |
| N4 | validation | a design without a `Test one:` line | replay --base <base> | exit 1 · the error names the "Test one:" line · no test is run |
| N5 | validation | a base revision "nosuchrev" that git doesn't know | replay --base nosuchrev | exit 1 · the error names "nosuchrev" · no test is run |
| N6 | dependency | a project folder that is not a git repository | replay --base HEAD | exit 1 · the error says replay needs a git repository · no test is run |
| N7 | dependency | a `Test one:` command that doesn't exist, e.g. "no-such-runner {test}" | replay --base <base> | exit 1 · every ticked task is reported as a mismatch because its test fails now · the working tree is unchanged |
| N8 | validation | a ticked task with an empty test line | replay --base <base> | exit 1 · T1 is reported as a mismatch: no test to run · no command is run for T1 · the working tree is unchanged |
| N9 | validation | "Test one: `runner {file} {name}`" and the test line "tests/t_x.py", without "::" | replay --base <base> | exit 1 · T1 is reported as a mismatch: the test line has no "::" · no command is run for T1 |
| N10 | validation | a change with ticked tasks | replay, without --base | exit 2 · argparse's error names --base · no test is run |
| B1 | boundary | one ticked task and one unticked task | replay --base <base> | the unticked task is reported as skipped and its test is not run |
| B2 | boundary | a change with no ticked task | replay --base <base> | exit 0 · the output says there is nothing to replay |
| B3 | boundary | "Test one: `runner {file} {name}`" and the test line "tests/t_x.py::Cases.test_a" | replay --base <base> | the output shows the command "runner tests/t_x.py Cases.test_a" · the working tree is unchanged |
| B4 | boundary | a ticked pre-existing task whose test reads tests/fixtures/f.json, a fixture that is untracked and not ignored | replay --base <base> | exit 0 · T1 is reported confirmed (the fixture is laid over the base copy) · the working tree is unchanged |
| S3 | happy | a ticked task T2 whose red line is "pre-existing (after T1) — T1's code already does it", whose test fails at the base and passes now | replay --base <base> | exit 0 · T2 is reported "confirmed now (depends on T1)" · T2's test is not run at the base |
| S4 | happy | a ticked task T2 whose red line is "AssertionError (after T1): warning shown", whose test passes at the base and now | replay --base <base> | exit 0 · T2 is reported "confirmed now (depends on T1)" · T2's test is not run at the base |
| N11 | state | a ticked task T2 whose red line contains "(after T1)" and whose test fails now | replay --base <base> | exit 1 · T2 is reported as a mismatch: the test fails now · the working tree is unchanged |
| B5 | boundary | a ticked task T1 whose red line is "pre-existing (after T2) — see T2", naming a later task, and whose test fails at the base | replay --base <base> | exit 1 · T1 is reported as a mismatch: pre-existing claimed, but the test fails at the base |
| B6 | boundary | a ticked task T2 whose red line is "AssertionError: 'T1 skipped' not found", mentioning T1 without "(after", and whose test passes at the base and now | replay --base <base> | exit 1 · T2 is reported as a mismatch: red claimed, but the test passes at the base |

- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-EVD-002 The change lists its planned mutations
sdd.py shall read a `## Mutations` section, in tasks.md for a standard change
and in spec.md for a mini one and not counted toward the size cap, in which
each entry is a line `- M<n> <scenario> <file>` followed by `  - find:` and
`  - replace:` lines whose text is everything between the line's first and
last backtick, and check shall report as an error an entry with a missing
field, a duplicate ID, a scenario that isn't one of this change's, a file path
that is absolute or leads outside the project, or a replace text equal to its
find text.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a Mutations entry "- M1 REQ-DUR-001.N1 src/dur.py" with "  - find: `return 0`" and "  - replace: `return 1`" | check | exit 0 · no mutation error |
| N1 | validation | entry M1 without a replace line | check | exit 1 · the error names M1 and "replace" · no file is changed |
| N2 | validation | entry M1 naming the scenario REQ-DUR-001.N9, which isn't a scenario of this change | check | exit 1 · the error names M1 and REQ-DUR-001.N9 · no file is changed |
| N3 | validation | entry M1 without a file | check | exit 1 · the error names M1 and "file" · no file is changed |
| N4 | state | two entries with the ID M1 | check | exit 1 · the error says M1 is a duplicate · no file is changed |
| N5 | validation | entry M1 with the file "../x.py" | check | exit 1 · the error names M1 and "../x.py" · no file is changed |
| N6 | validation | entry M1 with the absolute file "/src/dur.py" | check | exit 1 · the error names M1 and "/src/dur.py" · no file is changed |
| N7 | validation | entry M1 with "  - find: return 0", without backticks | check | exit 1 · the error names M1 and "find" · no file is changed |
| B1 | boundary | a change with no Mutations section | check | exit 0 · no mutation error |
| B2 | boundary | entry M1 whose replace text equals its find text | check | exit 1 · the error says M1 changes nothing · no file is changed |
| B3 | boundary | entry M1 with "  - replace: ``", an empty replace | check | exit 0 · no mutation error (the find text is deleted) |
| B4 | boundary | a standard change with a 30-line Mutations section in tasks.md | status | the spec line count is the same as without the section · no file is changed |

- N/A dependency: only the change's own files are read; whether the named file exists is checked by mutate (REQ-EVD-003)
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-EVD-003 Run the planned mutations
When `sdd.py mutate` is run, sdd.py shall, for each mutation, run the tests of
the tasks that plan its scenario through the design's per-test command, first
in a scratch copy of the working tree and then in a scratch copy where the
find text, which must occur exactly once in the file, is replaced; it shall
print the mutation as caught when every test passes before and at least one
fails after, survived when every test passes both times, and invalid
otherwise, and exit 1 if any mutation survived or is invalid. A scratch copy
holds the tracked files and the untracked files git doesn't ignore; mutate
needs a git repository and never writes outside its scratch copies.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a mutation that breaks the rule its scenario's test checks | mutate | exit 0 · M1 is reported caught · the working tree is unchanged · no scratch copy is left |
| N1 | state | a mutation that the scenario's test doesn't notice | mutate | exit 1 · M1 is reported survived · the working tree is unchanged |
| N2 | state | a mutation whose scenario's test already fails without it | mutate | exit 1 · M1 is reported invalid: the test fails without the mutation · the working tree is unchanged |
| N3 | validation | a find text that doesn't occur in the file | mutate | exit 1 · M1 is reported invalid: the find text is not in the file · no test is run for M1 |
| N4 | validation | a find text that occurs twice in the file | mutate | exit 1 · M1 is reported invalid: the find text occurs 2 times · no test is run for M1 |
| N5 | validation | a design without a `Test one:` line | mutate | exit 1 · the error names the "Test one:" line · no test is run |
| N6 | dependency | a mutation naming a file that doesn't exist | mutate | exit 1 · M1 is reported invalid: the file doesn't exist · no test is run for M1 |
| N7 | dependency | a mutation whose scenario is planned by a task with no test line | mutate | exit 1 · M1 is reported invalid: no test to run · no test is run for M1 |
| N8 | dependency | a project folder that is not a git repository | mutate | exit 1 · the error says mutate needs a git repository · no test is run |
| N9 | validation | a mutation whose scenario no task plans | mutate | exit 1 · M1 is reported invalid: no test to run · no test is run for M1 |
| B1 | boundary | a change with no Mutations section | mutate | exit 0 · the output says no mutations are planned |
| B2 | boundary | two mutations, one caught and one survived | mutate | exit 1 · both are reported, M1 caught and M2 survived |
| B3 | boundary | a find text "`    return total`" with four leading spaces, which occurs once with them and twice without | mutate | exit 0 · M1 is reported caught (the leading spaces are kept) · the working tree is unchanged |
| B4 | boundary | a mutation whose scenario two tasks plan, failing the first task's test and passing the second's | mutate | exit 0 · M1 is reported caught |

- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-EVD-004 The design names a component test command
Where the design (design.md of a standard change, the Design notes of a mini one) has a list line (`-` or `*`) `Test component: <command>`, as `Test one:` is written, sdd.py shall take its text, without surrounding backticks, as the component command, in which every `{prefix}` stands for a capability's requirement prefix; check at the plan stage and later shall report as an error a component command without `{prefix}`, one whose quotes don't close, or a second `Test component:` line, and shall warn, without failing, when the design has no component command or an empty one, saying that the component checkpoints will be skipped.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | an otherwise clean change at designed whose design has "- Test component: `python3 -m unittest tests.test_x -k REQ_{prefix}_`" | check --stage plan | exit 0 · no warning or error mentions "Test component" |
| N1 | validation | the S1 change with "- Test component: `python3 -m unittest`" | check --stage plan | exit 1 · the error names "Test component" and "{prefix}" · no file is changed |
| N2 | validation | the S1 change with "- Test component: `runner -k 'REQ_{prefix}`" | check --stage plan | exit 1 · the error names "Test component" and says a quote is not closed · no file is changed |
| N3 | state | the S1 change with two "Test component:" lines | check --stage plan | exit 1 · the error says the design has more than one "Test component:" line · no file is changed |
| B1 | boundary | the S1 change without a "Test component:" line | check --stage plan | exit 0 · a warning says there is no "Test component:" line and component checkpoints will be skipped · no file is changed |
| B2 | boundary | the S1 change with an empty "- Test component:" line | check --stage plan | exit 0 · the B1 warning · no file is changed |
| B3 | boundary | a standard draft with requirements, no tasks and no design | check --stage spec | no warning or error mentions "Test component" |
| B5 | boundary | the S1 change with "Test component: `runner -k REQ_{prefix}_`" written without a list marker | check --stage plan | the B1 warning (only a list line counts) · no file is changed |
| B6 | boundary | an otherwise clean mini draft with tasks whose Design notes have "- Test component: `runner -k REQ_{prefix}_`" | check --stage plan | exit 0 · no warning or error mentions "Test component" · no file is changed |

- N/A dependency: only the change's own files are read; no command is run
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-EVD-005 Sort failing tests into regressions, expected failures and the rest
When `sdd.py sort-failures <file>` is run for the active change or the one `--change` names, with a file of failing test names, one per line (blank lines skipped, surrounding spaces removed), sdd.py shall print one line per distinct name, in file order: `regression: <name> (<scenario>, <task> done)` when the name carries a scenario ID of the change (in the forms check --stage verify recognizes, such as REQ-DUR-001.S1 or test_REQ_DUR_001_S1, in any case) that a ticked task plans; `expected: <name> (<scenario>, <task> not done)` when it carries a scenario ID of the change and no ticked task plans any of them; and `outside: <name>` otherwise; the scenario printed is the first ID in the name that decides the line (for a regression, the first that a ticked task plans), and the task is the first in plan order that plans it (a ticked one for a regression), or `no task`; then `sorted: <r> regression, <e> expected, <o> outside the change`, exiting 1 when r is above 0 and 0 otherwise, and changing no file.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a change with T1 ticked planning REQ-DUR-001.S1, T2 unticked planning REQ-DUR-001.N1, and failed.txt listing test_REQ_DUR_001_S1_parses and test_REQ_DUR_001_N1_rejects | sort-failures failed.txt | "regression: test_REQ_DUR_001_S1_parses (REQ-DUR-001.S1, T1 done)" · "expected: test_REQ_DUR_001_N1_rejects (REQ-DUR-001.N1, T2 not done)" · "sorted: 1 regression, 1 expected, 0 outside the change" · exit 1 · no file is changed |
| S2 | happy | the S1 change, which has no scenario S10, and failed.txt listing test_REQ_DUR_001_N1_rejects, test_legacy_total and test_REQ_DUR_001_S10_x | sort-failures failed.txt | the "expected:" line · "outside: test_legacy_total" · "outside: test_REQ_DUR_001_S10_x" · "sorted: 0 regression, 1 expected, 2 outside the change" · exit 0 · no file is changed |
| N1 | dependency | the S1 change and no file missing.txt | sort-failures missing.txt | exit 1 · the error names missing.txt · no "sorted:" line · no file is created |
| N2 | validation | failed.txt with "  test_REQ_DUR_001_N1_rejects  ", a blank line and the same name again | sort-failures failed.txt | one "expected: test_REQ_DUR_001_N1_rejects (REQ-DUR-001.N1, T2 not done)" line · "sorted: 0 regression, 1 expected, 0 outside the change" · no file is changed |
| N3 | state | no active change, and failed.txt | sort-failures failed.txt | exit 1 · the error says there is no active change · no "sorted:" line · no file is changed |
| N4 | validation | no change 9999-none, and failed.txt | sort-failures failed.txt --change 9999-none | exit 1 · the error names 9999-none · no "sorted:" line · no file is changed |
| B1 | boundary | an empty failed.txt | sort-failures failed.txt | exactly "sorted: 0 regression, 0 expected, 0 outside the change" · exit 0 · no file is changed |
| B2 | boundary | failed.txt listing test_REQ_DUR_001_N1_and_REQ_DUR_001_S1, carrying N1 (unticked T2) then S1 (ticked T1) | sort-failures failed.txt | "regression: test_REQ_DUR_001_N1_and_REQ_DUR_001_S1 (REQ-DUR-001.S1, T1 done)" · exit 1 · no file is changed |
| B3 | boundary | a scenario REQ-DUR-001.S2 that no task plans, and failed.txt listing test_REQ_DUR_001_S2_x | sort-failures failed.txt | "expected: test_REQ_DUR_001_S2_x (REQ-DUR-001.S2, no task)" · exit 0 · no file is changed |
| B4 | boundary | the S1 change and failed.txt listing "Req-Dur-001.N1 rejects letters" | sort-failures failed.txt | "expected: Req-Dur-001.N1 rejects letters (REQ-DUR-001.N1, T2 not done)" (the hyphen form, in any case) · exit 0 · no file is changed |

- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-EVD-006 Tests that passed before the run count as regressions
Where `sdd.py sort-failures <file>` is run with `--passed-before <list>`, a file of the test names that passed before the run, one per line, read like the failing file (blank lines skipped, surrounding spaces removed), sdd.py shall first make REQ-EVD-005's own refusals (no active change, an unknown `--change`, an unreadable failing file) and read the list only after them, and when the list can't be read, print only an error naming it and exit 1. For each failing name that equals a name on the list, it shall print, in place of the line REQ-EVD-005 gives it, `regression: <name> (<text>, passed before the run)`, where `<text>` is what REQ-EVD-005 puts in that line's parentheses, or `regression: <name> (passed before the run)` for a name REQ-EVD-005 sorts outside, and count the name once, as a regression, in the unchanged `sorted:` line and exit code of REQ-EVD-005. It shall sort every other name by REQ-EVD-005. When the list names no test, it shall print `warning: <list> names no test that passed before the run` as the line just before the `sorted:` line, with the exit code unchanged. It shall change no file.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | the REQ-EVD-005 S1 change (T1 ticked planning REQ-DUR-001.S1, T2 unticked planning REQ-DUR-001.N1), failed.txt listing test_legacy_total, test_other_total and test_REQ_DUR_001_N1_rejects, and passed.txt listing test_legacy_total | sort-failures failed.txt --passed-before passed.txt | "regression: test_legacy_total (passed before the run)" · "outside: test_other_total" · "expected: test_REQ_DUR_001_N1_rejects (REQ-DUR-001.N1, T2 not done)" · "sorted: 1 regression, 1 expected, 1 outside the change" · exit 1 · no file is changed |
| S2 | happy | the S1 change, and failed.txt and passed.txt both listing test_REQ_DUR_001_S1_parses | sort-failures failed.txt --passed-before passed.txt | exactly "regression: test_REQ_DUR_001_S1_parses (REQ-DUR-001.S1, T1 done, passed before the run)" and "sorted: 1 regression, 0 expected, 0 outside the change" · exit 1 · no file is changed |
| N1 | state | the S1 change, and failed.txt and passed.txt both listing test_REQ_DUR_001_N1_rejects, the scenario of unticked T2 | sort-failures failed.txt --passed-before passed.txt | exactly "regression: test_REQ_DUR_001_N1_rejects (REQ-DUR-001.N1, T2 not done, passed before the run)" and "sorted: 1 regression, 0 expected, 0 outside the change" · exit 1 · no file is changed |
| N2 | dependency | the S1 change, failed.txt listing test_legacy_total, and no file missing.txt | sort-failures failed.txt --passed-before missing.txt | exit 1 · the error names missing.txt · nothing else is printed (no "outside:" or "sorted:" line) · no file is created |
| N5 | dependency | the S1 change, and no file failed.txt or passed.txt | sort-failures failed.txt --passed-before passed.txt | exit 1 · the error names failed.txt, not passed.txt (REQ-EVD-005's refusal comes first) · no "sorted:" line · no file is created |
| N3 | validation | the S1 change, failed.txt listing test_legacy_total, and passed.txt holding only "  test_legacy_total  " and a blank line | sort-failures failed.txt --passed-before passed.txt | exactly "regression: test_legacy_total (passed before the run)" and "sorted: 1 regression, 0 expected, 0 outside the change" · exit 1 · no file is changed |
| N4 | validation | the S1 change and failed.txt listing test_legacy_total | sort-failures failed.txt --passed-before, without a value | exit 2 · the error is argparse's "argument --passed-before: expected one argument" · no "sorted:" line · no file is changed |
| B1 | boundary | the S1 change, failed.txt listing test_legacy_total and test_REQ_DUR_001_N1_rejects, and passed.txt holding only a blank line (it names no test) | sort-failures failed.txt --passed-before passed.txt | exactly "outside: test_legacy_total" · "expected: test_REQ_DUR_001_N1_rejects (REQ-DUR-001.N1, T2 not done)" · "warning: passed.txt names no test that passed before the run" · "sorted: 0 regression, 1 expected, 1 outside the change", in that order · exit 0, as without the list · no file is changed |
| B2 | boundary | the S1 change, failed.txt listing test_legacy_total, and passed.txt listing test_REQ_DUR_001_S1_parses and test_other_total, which don't fail | sort-failures failed.txt --passed-before passed.txt | exactly "outside: test_legacy_total" and "sorted: 0 regression, 0 expected, 1 outside the change" · exit 0 · no line names a test that didn't fail · no file is changed |
| B3 | boundary | the S1 change, failed.txt listing test_legacy_total, and passed.txt listing "Test_Legacy_Total" and "test_legacy" | sort-failures failed.txt --passed-before passed.txt | "outside: test_legacy_total" (a name is on the list only when it is equal, case included) · "sorted: 0 regression, 0 expected, 1 outside the change" · exit 0 · no file is changed |
| B4 | boundary | the S1 change with a scenario REQ-DUR-001.S2 that no task plans, and failed.txt and passed.txt both listing test_REQ_DUR_001_S2_x | sort-failures failed.txt --passed-before passed.txt | exactly "regression: test_REQ_DUR_001_S2_x (REQ-DUR-001.S2, no task, passed before the run)" and "sorted: 1 regression, 0 expected, 0 outside the change" · exit 1 · no file is changed |

- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-EVD-007 Run a test step and report its exceptions
When the operator runs `sdd.py test <step>` for the active change, or the one `--change` names, at planned, implementing or verifying, where the step is `T<n>` (the task's own test), `component <PREFIX>` (the capability's tests) or `full` (the full suite), sdd.py shall run the step's command as `run-plan` prints it (REQ-ORC-009, REQ-ORC-010), as its words with no shell, from the folder that holds specs/, and wait for it to end; once the command has started, sdd.py renames the previous last run's files, if any, from `specs/.sdd/runs/last-run.json` and `last-run.log` to `run-of-<its time>.json` and `.log`, the time written with `-` for `:` (`run-of-2026-11-16T09-00-00Z`) and `-2`, `-3`… added when that name is taken, which the folder's `.gitignore` (holding `run-of-*`, written when missing) keeps out of git; then it writes the run's record (the time, the change, the commit, the step, the command, its exit code, each test's outcome and the digest of REQ-EVD-009) to `last-run.json` and the command's full output to `last-run.log`, which git tracks, writing each occurrence of the project folder's absolute path as `.` in both files and in the report; a time is UTC to the second, as `2026-11-16T09:00:00Z`. sdd.py shall print the report: `test <step>: <command>`; then `result: <p> passed, <f> failed, <e> errors, <k> skipped (<n> tests) in <s>s`, s being the wall-clock seconds with one decimal; then, for each test that failed or errored, `failed: <name>` or `error: <name>`, followed by at most 5 lines, each indented by two spaces, taken from its failure or error element's `message` attribute and then its text, or `  (no message)` when both are empty; then the lines of REQ-EVD-005 for those names, sorted against the change's baseline as REQ-EVD-006 does when it has one (REQ-EVD-008), and otherwise with `warning: no baseline recorded; a test that passed before the change is sorted as outside` before the `sorted:` line; then `warning: the command exited <code> but the report shows no failure` when the command exits other than 0 and no test failed or errored; and last `log: specs/.sdd/runs/last-run.log`. Each test's outcome is read from the JUnit XML report at the path the design's `Test report:` list line names, read like `Test one:` (REQ-ORC-009), which sdd.py deletes before the run so a report left by an earlier run is never read; a test's name is its `classname`, a dot and its `name`, or its `name` alone when it has no `classname`. When the design has no `Test report:` line, or an empty one, or the run leaves no report there that can be read as JUnit XML, sdd.py shall print, in place of the result, test, sort and exit-code warning lines, `result: exit <code>, no test report: each test's outcome is unknown`, then the last 20 lines of the output, each indented by two spaces. When `last-run.json` can't be read as a run record, sdd.py shall rename it and its log to `run-of-unreadable-<now>.json` and `.log`, print `warning: last-run.json could not be read; kept as run-of-unreadable-<now>.json` and run the step. When the command can't be started, sdd.py shall print an error that names it and exit 1, recording no run and renaming nothing. sdd.py exits 1 when a regression is sorted, when the exit-code warning is printed, or, with no test report, when the command exits other than 0; otherwise 0.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a change 0001-x at implementing whose design has "- Test command: `python3 fake.py all`" and "- Test report: `out/junit.xml`", where fake.py writes out/junit.xml with t.test_a passed, t.test_REQ_DUR_001_N1_x failed with message "AssertionError: 1 != 2", and t.test_b skipped, and exits 1; T1 (REQ-DUR-001.N1) is unticked; no baseline.txt; no specs/.sdd/runs/ | test full | the lines "test full: python3 fake.py all", "result: 1 passed, 1 failed, 0 errors, 1 skipped (3 tests) in <s>s", "failed: t.test_REQ_DUR_001_N1_x", "  AssertionError: 1 != 2", "expected: t.test_REQ_DUR_001_N1_x (REQ-DUR-001.N1, T1 not done)", the warning on no baseline, "sorted: 0 regression, 1 expected, 0 outside the change", "log: specs/.sdd/runs/last-run.log" · no exit-code warning · exit 0 · last-run.log holds fake.py's whole output · last-run.json records the run · specs/.sdd/runs/.gitignore holds "run-of-*" · git status lists last-run.json and last-run.log as files to commit · sdd.py changes no file outside specs/.sdd/runs/ except deleting out/junit.xml before the run |
| S2 | happy | the S1 change with "- Test component: `python3 fake.py -k REQ_{prefix}_`" | test component DUR | the first line is "test component DUR: python3 fake.py -k REQ_DUR_" · the S1 result and sort lines · exit 0 |
| S3 | happy | the S1 change with "- Test one: `python3 fake.py {name}`" and T1's test line "t.py::test_REQ_DUR_001_N1_x" | test T1 | the first line is "test T1: python3 fake.py test_REQ_DUR_001_N1_x" · exit 0 · T1's red and green lines are unchanged |
| S4 | happy | the S1 change with T1 ticked, and fake.py's failure unchanged | test full | "regression: t.test_REQ_DUR_001_N1_x (REQ-DUR-001.N1, T1 done)" · "sorted: 1 regression, 0 expected, 0 outside the change" · exit 1 |
| N1 | dependency | the S1 change with no "Test report:" line, and fake.py printing 30 lines and exiting 3 | test full | "result: exit 3, no test report: each test's outcome is unknown" · the last 20 output lines, indented · the "log:" line · no "failed:" or "sorted:" line · exit 1 |
| N7 | dependency | the S1 change with an empty "- Test report:" line, and fake.py exiting 0 | test full | "result: exit 0, no test report: each test's outcome is unknown" · exit 0 |
| N2 | dependency | the S1 change, a stale out/junit.xml from an earlier run, and fake.py now writing no report and exiting 0 | test full | "result: exit 0, no test report: each test's outcome is unknown" (the stale file is not read) · exit 0 · out/junit.xml does not exist after the run |
| N3 | dependency | the S1 change with fake.py writing "<testsuite" (malformed XML) to out/junit.xml and exiting 1 | test full | "result: exit 1, no test report: each test's outcome is unknown" · exit 1 · the run is recorded in last-run.json |
| N4 | dependency | the S1 change with "- Test command: `no-such-runner all`" and a last run recorded at 2026-11-16T09:00:00Z | test full | exit 1 · the error names no-such-runner and says it can't be started · no "result:" line · last-run.json and last-run.log are unchanged, not renamed · no run is recorded |
| N5 | dependency | the S1 change with last-run.json holding "<<<<<<< HEAD" | test full | "warning: last-run.json could not be read; kept as run-of-unreadable-<now>.json" · the files are renamed to run-of-unreadable-<now>.json and .log · the S1 report · last-run.json records the new run · exit 0 |
| N6 | dependency | the S1 change with fake.py writing a report where every test passed, then exiting 2 | test full | "result: 3 passed, 0 failed, 0 errors, 0 skipped (3 tests) in <s>s" · "warning: the command exited 2 but the report shows no failure" · exit 1 |
| B1 | boundary | the S1 change, the failure's message attribute "AssertionError: 1 != 2" and its text 7 more lines | test full | exactly 5 indented lines follow "failed: t.test_REQ_DUR_001_N1_x", the first "  AssertionError: 1 != 2" · exit 0 |
| B2 | boundary | the S1 change, fake.py writing a testcase name="test_c" with no classname, errored with message "ImportError: x" | test full | "error: test_c" · "  ImportError: x" · "outside: test_c" · exit 0 |
| B3 | boundary | the S1 change, fake.py writing a report with no testcase and exiting 0 | test full | "result: 0 passed, 0 failed, 0 errors, 0 skipped (0 tests) in <s>s" · "sorted: 0 regression, 0 expected, 0 outside the change" · exit 0 |
| B4 | boundary | the S1 change at verifying | test full | the S1 report · exit 0 · the status stays verifying |
| B5 | boundary | the S1 change after a test full run recorded at 2026-11-16T09:00:00Z, then t.py changed | test component DUR | the earlier files are now specs/.sdd/runs/run-of-2026-11-16T09-00-00Z.json and .log, ignored by git · last-run.json and last-run.log hold the component run · exit 0 |
| B6 | boundary | the B5 setup with run-of-2026-11-16T09-00-00Z.json already present | test component DUR | the earlier files are now run-of-2026-11-16T09-00-00Z-2.json and .log · the file already present is unchanged · exit 0 |
| B7 | boundary | the S1 change, the failure element with no message attribute and no text | test full | "failed: t.test_REQ_DUR_001_N1_x" then "  (no message)" · exit 0 |
| B8 | boundary | the S1 change, fake.py printing the project folder's absolute path followed by "/t.py" in its output and in the failure's message | test full | the indented message line and last-run.log show "./t.py" · neither file nor the report holds the absolute path · exit 0 |

- N/A validation: covered by REQ-EVD-011, which refuses a bad step and a bad design line
- N/A state: covered by REQ-EVD-011, which refuses the other statuses and a missing change
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-EVD-008 Record the tests that pass before the change, once
When the operator runs `sdd.py test baseline` for a change at planned or implementing that has no ticked task, no baseline.txt and a `Test report:` line, sdd.py shall run the full suite as `test full` does (REQ-EVD-007) and print its report with the first line `test baseline: <test command>` and no baseline warning, then write the change's baseline to `baseline.txt` in the change's folder (its first line `# baseline <time> <commit>`, the commit being `none` outside a git repository or before its first commit, then the names of the tests that passed, one per line), which git tracks and archive moves with the change, and print `baseline: <p> tests passed, recorded <time>`; every later `test` run of the change sorts against that baseline, which is never rerun or changed; when the full suite's run is reused (REQ-EVD-009), the reused run counts as the baseline's run and baseline.txt carries its time. When its run leaves no test report, sdd.py shall print the report of REQ-EVD-007, then an error that a baseline needs a test report, write no baseline.txt and exit 1. Its own refusals (a baseline.txt already there, a ticked task, a status other than planned or implementing, no `Test report:` line) come after the step in REQ-EVD-011's order, in that order, before anything is run.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | the REQ-EVD-007.S1 change at planned with fake.py writing t.test_a and t.test_legacy passed and t.test_REQ_DUR_001_N1_x failed | test baseline | the report with the first line "test baseline: python3 fake.py all" and no "warning: no baseline" line · "baseline: 2 tests passed, recorded <time>" · baseline.txt in the change's folder holds the "# baseline <time> <commit>" line, then t.test_a and t.test_legacy · exit 0 · the status stays planned |
| S2 | happy | the S1 baseline recorded, T1 now ticked, and fake.py now failing t.test_legacy | test full | "regression: t.test_legacy (passed before the run)" · exit 1 · baseline.txt is unchanged |
| N1 | state | the S1 change whose baseline.txt starts "# baseline 2026-11-16T09:00:00Z abc1234" | test baseline | exit 1 · the error says the baseline was recorded at 2026-11-16T09:00:00Z and is never rerun · nothing is run · no file is changed |
| N2 | state | the S1 change with T1 ticked and no baseline.txt | test baseline | exit 1 · the error says a task is ticked, so the code has already changed · nothing is run · no file is changed |
| N3 | state | the S1 change at verifying with no ticked task | test baseline | exit 1 · the error names verifying and says a baseline needs planned or implementing · nothing is run · no file is changed |
| N4 | dependency | the S1 change with no "Test report:" line | test baseline | exit 1 · the error says a baseline needs a "Test report:" line · nothing is run · no file is changed |
| N5 | dependency | the S1 change, fake.py writing no report | test baseline | the no-report result line · then the error that a baseline needs a test report · no baseline.txt · exit 1 |
| B2 | boundary | the S1 change outside a git repository | test baseline | baseline.txt's first line is "# baseline <time> none" · exit 0 |
| B3 | boundary | the S1 change whose last run is a test baseline of this change at 2026-11-16T09:00:00Z with a report, nothing changed since, and no baseline.txt | test baseline | fake.py is not run · baseline.txt's first line starts "# baseline 2026-11-16T09:00:00Z" · exit 0 |
| B1 | boundary | the S1 change with fake.py writing only failed tests | test baseline | "baseline: 0 tests passed, recorded <time>" · exit 0 · a later test full prints no "warning: no baseline" line |

- N/A validation: test baseline takes no argument; the step form is refused by REQ-EVD-011
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-EVD-009 Reuse the last run on unchanged code
When `sdd.py test <step>` is run and `last-run.json` records a run of the same change, the same step (`baseline` and `full` are different steps) and the same command, on the same commit and with the same digest (SHA-256 over the path and the content of each file that git tracks or doesn't ignore, outside `specs/`, in path order), sdd.py shall run nothing and print that run's report, changing no file except the red or green line or baseline.txt that `--red`, `--green` or `baseline` write from the reused run, with its time (REQ-EVD-008, REQ-EVD-010), with ` (reused from <time>)` added to its `result:` line, its sort lines computed again against the change's current tasks and baseline, and its `log:` line naming last-run.log; `--rerun` runs the step anyway, and outside a git repository, or before its first commit, every step is run.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | the REQ-EVD-007.S1 change whose last run is a test full recorded at 2026-11-16T09:00:00Z, nothing changed since | test full | fake.py is not run · "result: 1 passed, 1 failed, 0 errors, 1 skipped (3 tests) in <s>s (reused from 2026-11-16T09:00:00Z)" · "log: specs/.sdd/runs/last-run.log" · exit 0 · no file is changed |
| S2 | happy | the S1 setup, then T1 ticked in tasks.md (a file under specs/) | test full | fake.py is not run · the reused report sorts "regression: t.test_REQ_DUR_001_N1_x (REQ-DUR-001.N1, T1 done)" · exit 1 |
| S3 | happy | the S1 setup | test full --rerun | fake.py is run · the result line has no "reused" · exit 0 |
| B1 | boundary | the S1 setup, then one byte of t.py changed | test full | fake.py is run · no "reused" |
| B2 | boundary | the S1 setup, then a new untracked file src/new.py that git doesn't ignore | test full | fake.py is run · no "reused" |
| B3 | boundary | the S1 setup, then a new file in a folder git ignores | test full | fake.py is not run · "reused from 2026-11-16T09:00:00Z" |
| B4 | boundary | the S1 setup, then a commit that changes no file content | test full | fake.py is run (the commit differs) · no "reused" |
| B5 | boundary | the S1 setup, then a test component DUR run, then nothing changed | test full | fake.py is run (the last run is another step; earlier runs are not reused) · no "reused" |
| B6 | boundary | the S1 setup, then a tracked file t2.py deleted | test full | fake.py is run · no "reused" |
| B7 | boundary | the S1 setup with the last run recorded for another change 0002-y | test full | fake.py is run · no "reused" |
| B8 | boundary | the S1 setup, then the design's Test command changed to "`python3 fake2.py all`" | test full | fake2.py is run · fake.py is not run · no "reused" |
| N1 | dependency | the S1 change in a folder that is not a git repository, with a last run | test full | fake.py is run · no "reused" · exit 0 |
| N2 | dependency | the S1 change in a git repository with no commit yet, with a last run | test full | fake.py is run · no "reused" · exit 0 |

- N/A validation: covered by REQ-EVD-011, which refuses a bad step
- N/A state: a reused run is sorted against the change's current tasks, as S2 shows
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-EVD-010 Write a task's red and green lines from its run
Where `sdd.py test T<n>` is run with `--red` or `--green` for an unticked task with a test line, sdd.py shall run the task's test (REQ-EVD-007) and find in the report the test whose name equals the part of the test line after its last `::` (the whole line when it has none) or ends with a dot and that part; with `--red`, when that test failed, sdd.py shall write the task's `red:` line as `red: failed: <the first line of its message> (sdd test <time>)`, or `red: failed (sdd test <time>)` when it has no message or that line holds a comment marker (`<!` then two hyphens, or two hyphens then `>`) or `(after T`; with `--green`, when it passed, the `green:` line as `green: passed (sdd test <time>)`; replacing what the line held, or, when the task has no such line, inserting it right after the task's `test:` line, and changing nothing else in the file; when the task's test run is reused (REQ-EVD-009), the reused run counts and the line carries its time. Otherwise it shall write nothing to tasks.md and exit 1 with an error that says what the run showed: with `--red`, that the test passed (and that a behavior that already existed is recorded by hand as `red: pre-existing — <why>`), errored (it must fail on an assertion, not on an error), was skipped, or is not in the report; with `--green`, that it failed, errored, was skipped or is not in the report; that two tests match, naming both; that the task has two `red:` or two `green:` lines, naming both, before anything is run; or that the run has no test report. `--green` for a task whose red line is empty is refused before anything is run, with an error that says to record red first (`--red`, or `red: pre-existing — <why>` by hand).

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | the REQ-EVD-007.S3 change, T1's red line empty, fake.py failing t.test_REQ_DUR_001_N1_x with "AssertionError: 1 != 2" | test T1 --red | T1's line is "  - red: failed: AssertionError: 1 != 2 (sdd test <time>)" · the rest of tasks.md is unchanged · check accepts the red line · exit 0 |
| S2 | happy | the S1 change after S1, fake.py now passing the test | test T1 --green | T1's line is "  - green: passed (sdd test <time>)" · the red line is unchanged · T1 stays unticked · exit 0 |
| N1 | validation | the S1 change, fake.py passing the test | test T1 --red | exit 1 · the error says the test passes and names "red: pre-existing" · tasks.md is unchanged |
| N2 | validation | the S1 change, the test errored with "ImportError: x" | test T1 --red | exit 1 · the error says it errored, not failed on an assertion · tasks.md is unchanged |
| N3 | validation | the S1 change, the report has no test named test_REQ_DUR_001_N1_x | test T1 --red | exit 1 · the error names test_REQ_DUR_001_N1_x and says it is not in the report · tasks.md is unchanged |
| N4 | validation | the S1 change after S1, the test still failing | test T1 --green | exit 1 · the error says the test fails · tasks.md is unchanged |
| N5 | dependency | the S1 change with no "Test report:" line | test T1 --red | exit 1 · the error says the run has no test report · tasks.md is unchanged |
| N6 | state | the S1 change with T1 ticked | test T1 --red | exit 1 · the error says T1 is ticked · nothing is run · no file is changed |
| N7 | validation | the S1 change with T1's red line empty | test T1 --green | exit 1 · the error says to record red first and names --red and "red: pre-existing" · nothing is run · no file is changed |
| N8 | validation | the S1 change, the report holding t.test_REQ_DUR_001_N1_x and u.test_REQ_DUR_001_N1_x, both failing | test T1 --red | exit 1 · the error names both tests · tasks.md is unchanged |
| B1 | boundary | the S1 change with T1's test line "test_REQ_DUR_001_N1_x" (no "::") and a red line already holding "AssertionError: old" | test T1 --red | T1's line is "  - red: failed: AssertionError: 1 != 2 (sdd test <time>)" (the old text replaced) · exit 0 |
| B2 | boundary | the S1 change, the failure with no message and no text | test T1 --red | T1's line is "  - red: failed (sdd test <time>)" · check accepts it · exit 0 |
| B4 | boundary | the S1 change whose T1 has a test: line and no red: or green: line | test T1 --red | a line "  - red: failed: AssertionError: 1 != 2 (sdd test <time>)" is inserted right after T1's test: line · nothing else in tasks.md changes · exit 0 |
| B5 | boundary | the S1 change whose last run is test T1 at 2026-11-16T09:00:00Z, nothing changed since, T1's red line empty | test T1 --red | the runner is not run · T1's line is "  - red: failed: AssertionError: 1 != 2 (sdd test 2026-11-16T09:00:00Z)" · exit 0 |
| N9 | validation | the S1 change, the test skipped | test T1 --red | exit 1 · the error says the test was skipped · tasks.md is unchanged |
| N10 | validation | the S1 change whose T1 has two red: lines | test T1 --red | exit 1 · the error names both lines · nothing is run · no file is changed |
| B6 | boundary | the S1 change, the failure message "expected", a comment opener (`<!` then two hyphens), then " x" | test T1 --red | T1's line is "  - red: failed (sdd test <time>)" · exit 0 |
| B7 | boundary | the S1 change with tasks.md at mode 0644 | test T1 --red | the S1 red line · tasks.md keeps mode 0644 · exit 0 |
| B3 | boundary | the S1 change, the report also holding t.other_test_REQ_DUR_001_N1_x, which passes | test T1 --red | t.other_test_REQ_DUR_001_N1_x doesn't match (its name doesn't end with "." and the part) · the S1 red line · exit 0 |

- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-EVD-011 The test runner refuses what it cannot run
If `sdd.py test` is run in a repository without specs/, or with no active change and no `--change`, or a `--change` that names no change, or for a change at a status other than planned, implementing or verifying, or is given a step other than `T<n>`, `component <PREFIX>`, `full` or `baseline`, a task that isn't in the plan, a prefix the change doesn't declare, `--red` or `--green` with a step other than `T<n>`, or both together, or the step's design line (`Test one:` for a task, `Test component:` for a component, `Test command:` for full and baseline) is missing, empty or has a quote that doesn't close, or the `Test report:` path is absolute, leads outside the project folder (its folders' symlinks followed), or names a file git tracks or a folder, or a task step's task has no test line (empty or a placeholder, as REQ-ORC-009 reads it), or a test line with no `::` while `Test one:` uses `{file}` or `{name}`, or the change's baseline.txt doesn't start with a `# baseline <time> <commit>` line, then sdd.py shall print an error that names the first problem in that order and exit 1, running no command and changing no file.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| N1 | state | a repository without specs/ | test full | exit 1 · the error says SDD is not initialized · nothing is run · no file is created |
| N2 | state | no active change | test full | exit 1 · the error says there is no active change · nothing is run · no file is changed |
| N3 | validation | no change 9999-none | test full --change 9999-none | exit 1 · the error names 9999-none · nothing is run · no file is changed |
| N4 | state | the REQ-EVD-007.S1 change at draft | test full | exit 1 · the error names draft and lists planned, implementing and verifying · nothing is run · no file is changed |
| N5 | validation | the REQ-EVD-007.S1 change | test everything | exit 1 · the error names "everything" and lists T<n>, component <PREFIX>, full and baseline · nothing is run · no file is changed |
| N6 | validation | the REQ-EVD-007.S1 change, which has no T9 | test T9 | exit 1 · the error names T9 · nothing is run · no file is changed |
| N7 | validation | the REQ-EVD-007.S2 change, which declares DUR only | test component CLI | exit 1 · the error names CLI and the declared prefix DUR · nothing is run · no file is changed |
| N8 | validation | the REQ-EVD-007.S1 change | test full --red | exit 1 · the error says --red needs a task step · nothing is run · no file is changed |
| N9 | validation | the REQ-EVD-007.S3 change | test T1 --red --green | exit 1 · the error says --red and --green can't be given together · nothing is run · no file is changed |
| N10 | validation | the REQ-EVD-007.S1 change with no "Test component:" line | test component DUR | exit 1 · the error names "Test component:" · nothing is run · no file is changed |
| N11 | validation | the REQ-EVD-007.S1 change with "- Test command: `python3 'fake.py`" | test full | exit 1 · the error names "Test command:" and says a quote is not closed · nothing is run · no file is changed |
| N12 | validation | the REQ-EVD-007.S3 change with T1's test line empty | test T1 | exit 1 · the error says T1 has no test line · nothing is run · no file is changed |
| N13 | validation | the REQ-EVD-007.S1 change at draft, given step "everything" | test everything | exit 1 · the error names the status draft, not the step (the status comes first) · nothing is run · no file is changed |
| N14 | validation | the REQ-EVD-007.S1 change with "- Test report: `../junit.xml`", and a file ../junit.xml | test full | exit 1 · the error names "Test report:" and says the path leads outside the project · ../junit.xml still exists · nothing is run · no file is changed |
| N15 | validation | the REQ-EVD-007.S1 change with "- Test report: `/tmp/junit.xml`" | test full | exit 1 · the error names "Test report:" and says the path is absolute · nothing is run · no file is changed |
| N19 | validation | the REQ-EVD-007.S1 change with "- Test report: `t.py`", a file git tracks | test full | exit 1 · the error names "Test report:" and says git tracks t.py · t.py still exists · nothing is run · no file is changed |
| N20 | validation | the REQ-EVD-007.S1 change with "- Test report: `out`", a folder | test full | exit 1 · the error says "Test report:" names a folder · nothing is run · no file is changed |
| N21 | validation | the REQ-EVD-007.S1 change with "- Test report: `link/junit.xml`", link a symlink to a folder outside the project holding junit.xml | test full | exit 1 · the error says the path leads outside the project · that junit.xml still exists · nothing is run · no file is changed |
| N16 | validation | the REQ-EVD-007.S3 change with "- Test one: `python3 fake.py {file} {name}`" and T1's test line "t.py" | test T1 | exit 1 · the error says T1's test line has no "::" · nothing is run · no file is changed |
| N17 | validation | the REQ-EVD-007.S3 change with T1's test line "tbd" | test T1 | exit 1 · the error says T1 has no test line · nothing is run · no file is changed |
| N18 | validation | the REQ-EVD-007.S1 change whose baseline.txt starts "<<<<<<< HEAD" | test full | exit 1 · the error names baseline.txt and the "# baseline <time> <commit>" line it expects · nothing is run · no file is changed |
