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

## Change history
- 0002-subagent-fanout — Subagent fan-out: prime orchestrator, role tiers, scripted verification evidence (2026-10-18): added REQ-EVD-001, added REQ-EVD-002, added REQ-EVD-003

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
