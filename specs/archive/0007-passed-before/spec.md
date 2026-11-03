---
id: 0007-passed-before
title: Tests that passed before the run count as regressions
type: feature
size: mini
assurance: production
status: archived
capabilities: evidence=EVD
created: 2026-10-30
spec_hash: 19129bf6139a
---

# 0007-passed-before — Tests that passed before the run count as regressions

## Intent
<!-- Spec Author: why this change, for whom, and the outcome. Use the operator's
words. No technology choices. 2–5 lines. -->

The operator's rule is that "a regression is a test that passed before the
task and fails after it". Since 0.19.0, `sort-failures` sorts by test name
only, so a test outside the change that passed before and fails now is
reported as "outside" and left to the agent's judgment. For the operator, who
runs large programs with SDD. The outcome: given the tests that passed before
the run, the script reports every such test as a regression, the same way in
every run.

## Scope
- In: `sort-failures` takes, as well as the failing tests, the list of tests that passed before the run, one name per line, read like the failing file (blank lines skipped, surrounding spaces removed, duplicates once). The list is a file the agent writes from its full-suite run before the run's first task, given to sort-failures as an option, the way the failing file is given; the script owns no new file (Q1).
- In: a failing test that is on the list is a regression, whether it is outside the change or the scenario of a task not done yet (0005 Q4, operator, 2026-10-28). Its line says it passed before the run, and it counts in the regression total and the exit code like any regression.
- In: a failing test that isn't on the list is sorted as today: regression, expected or outside.
- Changes existing behavior: with the list, a test outside the change that passed before and fails now was "outside" → it is a regression; the scenario of a task not done yet that passed before and fails now was "expected" → it is a regression.
- Existing changes (project rule 5): without the list, sort-failures behaves exactly as in 0.19.0.
- In (method, project rule 1): before a run's first task, the agent records the tests that pass, and gives that list at every sort.
- Out: running the tests or reading a runner's report (the known gap stays: the script reads the names the agent gives it).
- Out: a list kept across runs or changes, or updated during a run.
- Out: the v2 `baseline` phase, which drafts specs from existing code; this change doesn't use that name, so the phase keeps it.

## Requirements
<!-- REQ-EVD-005 is left as it is: without the option it alone decides every
line, and its scenarios prove the 0.19.0 behavior (project rule 5). -->

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

## Known gaps
- sort-failures doesn't check the list, beyond warning when it names no test: that its tests passed, or that it was recorded before the run's first task. It reads the names the agent gives it.
- A test renamed during the run is not on the list under its new name, so REQ-EVD-005 alone sorts it.
- A test that passed before and fails because the change deliberately alters the behavior it checks is a regression until the Implementer updates it; the list can't mark an intended change.
- Without --passed-before, sort-failures sorts by name only, as in 0.19.0, and doesn't warn that no list was given.
- REQ-EVD-005's text doesn't mention `--passed-before`; when the option is given, REQ-EVD-006 decides the lines it changes, and REQ-EVD-005 stays as it is.
- The method's part (recording the list before the run's first task and giving it at every sort) is design work under project rule 1, verified by review and a dogfood run.

## Design notes
- Files: `skill/sdd/scripts/sdd.py` (`cmd_sort_failures`, one new helper `read_names`, the `sort-failures` subparser), `tests/test_sdd.py` (new class `PassedBeforeTests`; `SortFailuresTests` is not edited) and the method files under "Method changes".
- **`read_names(file) -> list[str]`**: the read-and-clean code now inline in `cmd_sort_failures` (read text, `cannot read <file>: ...` on `OSError` or `UnicodeDecodeError`, strip, skip blanks, keep first of duplicates), moved out unchanged. It reads the failing file as before and, when given, the `--passed-before` file, so both are read the same way (REQ-EVD-006 N2, N3) and 0.19.0 refusals keep their text (project rule 5).
- **The option**: `p.add_argument("--passed-before")` on the `sort-failures` subparser, default `None`; argparse alone gives the exit 2 and its "expected one argument" message for a missing value (N4). Without the option, `passed = set()` and every line is printed as in 0.19.0.
- **Order in `cmd_sort_failures`**: the change check, then `names = read_names(args.file)`, as in 0.19.0 (N5); on the next line `passed = set(read_names(args.passed_before)) if args.passed_before is not None else set()` (an unreadable list raises `SddError` before any line is printed, N2); then the sort.
- **One lookup**: the three existing branches set `kind` and `detail` (the text REQ-EVD-005 puts in the parentheses, empty for outside) in place of printing. After them, one line `if name in passed:` sets `kind` to `"regression"` and sets `detail` on the line `detail = detail + ", passed before the run" if detail else "passed before the run"`, whatever branch found it (S1, S2, N1, B4). Then one `counts[kind] += 1` and one `print(f"{kind}: {name} ({detail})" if detail else f"{kind}: {name}")`, so 0.19.0 lines keep their text. Names on the list that don't fail are never looked at (B2).
- **The warning**: after the loop, `if args.passed_before is not None and not passed:` prints `warning: <list> names no test that passed before the run`, then the `sorted:` line; the return value is unchanged (B1).
- **Method changes** (design work, project rule 1), in `skill/sdd/` of the development checkout, attached to T8 as `also:` lines: `method/phases/implement.md` (before the run's first task, write the names of the tests that pass in the full suite to a file, give it as `--passed-before` at every sort; a regression from the list is handled like any regression); `method/roles/implementer.md` (the checkpoint row: a regression includes a test on the list, and only an outside test not on the list is judged); `method/overview.md` (the script row gains `[--passed-before <list>]`).
- Test strategy: integration through `sdd.main()` with the `Repo` helper and `snapshot()` in a temporary folder, no subprocess and no test doubles. `PassedBeforeTests` builds the same change as `SortFailuresTests` (`SORT_TASKS`, archive folders so the change is 0007) and writes failed.txt and passed.txt with `self.repo.write`; each test compares the snapshot of the folder before and after.
- Test command: `python3 -m unittest tests.test_sdd`
- Test one: `python3 -m unittest tests.test_sdd.{name}`
- Test component: `python3 -m unittest tests.test_sdd -k REQ_{prefix}_`
- Checkpoints: the one capability here, EVD, gives one component checkpoint, run by the Implementer when the last task ends.

## Tasks
<!-- Order exceptions. Where a scenario passes before its rule exists, it comes
after the task that creates the rule, so its red run is real:
- REQ-EVD-006: T1 (S1, S2) writes both tests first, takes one red run and
  builds the option, `read_names` and the design's single lookup, count and
  print. The tasks after it may already pass and record `red: pre-existing
  (after T1)`: T2 (N1), since the lookup covers the not-done line; T3, T4 and
  T5 (N2, N5, N3), since T1 reads the list through `read_names`, after the
  failing file; T6 (N4), which fails before T1, where argparse rejects the
  unknown option with "unrecognized arguments", and passes once T1 adds the
  option; and T8 (B2 to B4), since B2 and B3 need only the lookup and B4 is the
  not-done line with "no task". T7 (B1) fails first: the warning is new. -->

- [x] T1 REQ-EVD-006.S1 REQ-EVD-006.S2 A test that passed before and fails is a regression, outside the change or in a done task
  - tier: strong
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_S1_and_REQ_EVD_006_S2_a_test_that_passed_before_and_fails_is_a_regression
  - red: AssertionError: Lists differ: ['usage: sdd.py [-h] [--root ROOT]', ...] != ['regression: test_legacy_total (passed bef[167 chars]nge'] (sdd.py: error: unrecognized arguments: --passed-before)
  - green: Ran 1 test in 0.084s OK

- [x] T2 REQ-EVD-006.N1 A not-done task's scenario that passed before is a regression
  - tier: mid
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N1_a_not_done_tasks_scenario_that_passed_before_is_a_regression
  - red: pre-existing (after T1) — T1's single lookup already covers the not-done line
  - green: Ran 1 test in 0.1s OK

- [x] T3 REQ-EVD-006.N2 An unreadable list is refused and nothing else is printed
  - tier: light
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N2_an_unreadable_list_is_refused_and_nothing_else_is_printed
  - red: pre-existing (after T1) — T1 reads the list through read_names, which refuses before any line is printed
  - green: Ran 1 test in 0.1s OK

- [x] T4 REQ-EVD-006.N5 An unreadable failing file is refused before the list is read
  - tier: light
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N5_an_unreadable_failing_file_is_refused_before_the_list_is_read
  - red: pre-existing (after T1) — T1 reads the failing file before the list
  - green: Ran 1 test in 0.1s OK

- [x] T5 REQ-EVD-006.N3 The list skips blank lines and trims names
  - tier: light
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N3_the_list_skips_blank_lines_and_trims_names
  - red: pre-existing (after T1) — T1 reads the list through read_names, which strips and skips blanks
  - green: Ran 1 test in 0.1s OK

- [x] T6 REQ-EVD-006.N4 The option without a value is an argparse error
  - tier: light
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N4_the_option_without_a_value_is_an_argparse_error
  - red: pre-existing (after T1) — T1 added the option, so argparse now reports the missing value
  - green: Ran 1 test in 0.1s OK

- [x] T7 REQ-EVD-006.B1 A list that names no test warns before the sorted line
  - tier: light
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B1_a_list_that_names_no_test_warns_before_the_sorted_line
  - red: AssertionError: Lists differ: warning line missing before 'sorted: 0 regression, 1 expected, 1 outside the change'
  - green: Ran 1 test in 0.1s OK

- [x] T8 REQ-EVD-006.B2 REQ-EVD-006.B3 REQ-EVD-006.B4 Only equal failing names count, and a scenario no task plans keeps "no task"
  - tier: light
  - also: method/phases/implement.md: record the passing tests to a file before the run's first task and give it as `--passed-before` at every sort; a regression from the list is handled like any regression
  - also: method/roles/implementer.md: the checkpoint row's Regression includes a test on the list; Outside is judged only for a test not on the list
  - also: method/overview.md: the sort-failures script row gains `[--passed-before <list>]`
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B2_and_REQ_EVD_006_B3_and_REQ_EVD_006_B4_only_equal_failing_names_count_and_no_task_is_kept
  - red: pre-existing (after T1) — T1's lookup is by equal name and keeps REQ-EVD-005's no-task text
  - green: Ran 1 test in 0.1s OK

- [x] T9 REQ-EVD-006.S2 The test that proves S2 carries its full ID (Verification F1): T1's test name has "S1_and_S2", which check --stage verify doesn't read as REQ-EVD-006.S2; name it as 0006 does (e.g. test_REQ_EVD_006_S1_and_REQ_EVD_006_S2_…) and keep T1's test line pointing at it
  - tier: light
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_S1_and_REQ_EVD_006_S2_a_test_that_passed_before_and_fails_is_a_regression
  - red: result: FAIL · REQ-EVD-006.S2: no test names this scenario (e.g. test_REQ_EVD_006_S2)
  - green: Ran 1 test in 0.087s OK

- [x] T10 REQ-EVD-006.B3 REQ-EVD-006.B4 The test that proves B3 and B4 carries their full IDs (Verification F1): T8's test name has "B2_B3_and_B4"; name it test_REQ_EVD_006_B2_and_REQ_EVD_006_B3_and_REQ_EVD_006_B4_… and keep T8's test line pointing at it
  - tier: light
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B2_and_REQ_EVD_006_B3_and_REQ_EVD_006_B4_only_equal_failing_names_count_and_no_task_is_kept
  - red: result: FAIL · REQ-EVD-006.B3: no test names this scenario (e.g. test_REQ_EVD_006_B3) · REQ-EVD-006.B4: no test names this scenario (e.g. test_REQ_EVD_006_B4)
  - green: Ran 1 test in 0.080s OK

- [x] T11 REQ-EVD-006.N1 The method says a not-done task's test on the list is a regression (Verification F2)
  - tier: light
  - also: method/phases/implement.md: "A failing test of a task not done yet is expected … it never stops the run" and "`expected` (no ticked task plans it)" also exclude a test on the list
  - also: method/roles/implementer.md: the checkpoint row's "Expected (its task isn't done yet)" excludes a test on the `--passed-before` list
  - test: tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N1_a_not_done_tasks_scenario_that_passed_before_is_a_regression
  - red: pre-existing (after T2) — the code already sorts a listed not-done test as a regression (T2); T11 changes only the method text in its also: lines, from "is **expected**: count it and go on" to "is **expected** unless it is on the `--passed-before` list … A test on that list is a **regression**"
  - green: Ran 1 test in 0.058s OK

## Mutations
<!-- Planned for the Implementer, who adds each entry once its task is green
(the find text doesn't exist yet; project rule 4). Each is a one-line
find/replace in skill/sdd/scripts/sdd.py whose find text occurs once there
(REQ-EVD-003):
-->

- M1 REQ-EVD-006.S1 skill/sdd/scripts/sdd.py
  - find: `if name in passed:`
  - replace: `if False:`
- M2 REQ-EVD-006.B3 skill/sdd/scripts/sdd.py
  - find: `if name in passed:`
  - replace: `if name.lower() in {p.lower() for p in passed}:`
- M3 REQ-EVD-006.S2 skill/sdd/scripts/sdd.py
  - find: `if name in passed:`
  - replace: `if name in passed and kind != "regression":`
- M4 REQ-EVD-006.N1 skill/sdd/scripts/sdd.py
  - find: `if name in passed:`
  - replace: `if name in passed and kind != "expected":`
- M5 REQ-EVD-006.N2 skill/sdd/scripts/sdd.py
  - find: `raise SddError(f"cannot read {file}: {exc.strerror if isinstance(exc, OSError) else exc}")`
  - replace: `return []`
- M6 REQ-EVD-006.S1 skill/sdd/scripts/sdd.py
  - find: `counts[kind] += 1`
  - replace: `counts[kind] += name not in passed`
- M7 REQ-EVD-006.N3 skill/sdd/scripts/sdd.py
  - find: `line.strip() for line`
  - replace: `line for line`
- M8 REQ-EVD-006.N4 skill/sdd/scripts/sdd.py
  - find: `p.add_argument("--passed-before")`
  - replace: `p.add_argument("--passed-before", nargs="?")`
- M9 REQ-EVD-006.B1 skill/sdd/scripts/sdd.py
  - find: `args.passed_before is not None and not passed`
  - replace: `False`
- M10 REQ-EVD-006.N5 skill/sdd/scripts/sdd.py
  - find: `names = read_names(args.file)`
  - replace: `read_names(args.passed_before) if args.passed_before else None; names = read_names(args.file)`
- M11 REQ-EVD-006.S1 skill/sdd/scripts/sdd.py
  - find: `detail + ", passed before the run" if detail else "passed before the run"`
  - replace: `detail + ", passed before the run"`
- M12 REQ-EVD-006.S1 skill/sdd/scripts/sdd.py
  - find: `({detail})" if detail else f"{kind}: {name}")`
  - replace: `({detail})")`

## Verification
<!-- Verifier: commands run, results, coverage, findings, verdict. -->
- Date: 2026-11-03 · Verifier: subagent (strong)
- Tests: `python3 -m unittest tests.test_sdd` → Ran 562 tests, OK
- Check: `sdd.py check --stage verify` → result: FAIL, 3 errors: "REQ-EVD-006.S2: no test names this scenario", the same for REQ-EVD-006.B3 and REQ-EVD-006.B4 → finding F1. Warnings: the six pre-existing tasks (audited below) and the missing Verifier line, which this record answers.
- Replay: `sdd.py replay --base 416850f` → replay: 8 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` → mutate: 12 caught, 0 survived or invalid
- Coverage: not available (no coverage tool installed)
- Attribution: the working tree also holds change 0006 (defect_gate/blocking_defects, the Defect* test classes, specs/capabilities/defects). 0007's share of `git diff 416850f`: in sdd.py, `read_names`, `cmd_sort_failures` and the one `--passed-before` parser line; in tests/test_sdd.py, the class PassedBeforeTests only. The test diff only adds lines; SortFailuresTests is not edited.
- Pre-existing audit: with the base sdd.py (416850f) and today's tests in a scratch copy (removed), all eight PassedBeforeTests fail on their assertions (usage error "unrecognized arguments: --passed-before", exit 2), so each `(after T1)` task's test fails without T1's code. T6 (N4) checked directly: at the base the output is "sdd.py: error: unrecognized arguments: --passed-before", which doesn't hold "argument --passed-before: expected one argument", so its claim is sound. Each reason holds by reading the code: one `if name in passed:` after all three branches (T2, T8), set membership by equal name and the "no task" detail kept (T8), `read_names` used for the list after `names = read_names(args.file)` and raising before any print (T3, T4), strip and skip blanks in `read_names` (T5). All six are sound.
- REQ-EVD-005 without the option: `passed` is empty and no warning is printed; the three branches give the same `kind` and text as 0.19.0, and `read_names` is the old inline code moved unchanged (same `cannot read` message). The ten test_REQ_EVD_005_* tests are untouched and pass.
- Method edits (design work, project rule 1): overview.md (script row with `[--passed-before <list>]`), implement.md (record the list before the first task, give it at every sort, don't update it; a regression from the list is handled like any regression) and implementer.md (Regression includes a test on the list; Outside only when not on the list) match Scope and the Method changes note, except F2.
- Known gaps: all six are true of the code and complete; I found no behavior the code has that the spec doesn't state.

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-EVD-006.S1 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_S1_and_S2_a_test_that_passed_before_and_fails_is_a_regression | pass | yes |
| REQ-EVD-006.S2 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_S1_and_S2_a_test_that_passed_before_and_fails_is_a_regression | pass | yes (asserted, but the name lacks the full ID: F1) |
| REQ-EVD-006.N1 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N1_a_not_done_tasks_scenario_that_passed_before_is_a_regression | pass | yes |
| REQ-EVD-006.N2 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N2_an_unreadable_list_is_refused_and_nothing_else_is_printed | pass | yes |
| REQ-EVD-006.N5 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N5_an_unreadable_failing_file_is_refused_before_the_list_is_read | pass | yes |
| REQ-EVD-006.N3 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N3_the_list_skips_blank_lines_and_trims_names | pass | yes |
| REQ-EVD-006.N4 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N4_the_option_without_a_value_is_an_argparse_error | pass | yes |
| REQ-EVD-006.B1 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B1_a_list_that_names_no_test_warns_before_the_sorted_line | pass | yes |
| REQ-EVD-006.B2 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B2_B3_and_B4_only_equal_failing_names_count_and_no_task_is_kept | pass | yes |
| REQ-EVD-006.B3 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B2_B3_and_B4_only_equal_failing_names_count_and_no_task_is_kept | pass | yes (asserted, but the name lacks the full ID: F1) |
| REQ-EVD-006.B4 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B2_B3_and_B4_only_equal_failing_names_count_and_no_task_is_kept | pass | yes (asserted, but the name lacks the full ID: F1) |

Findings:
- F1 (untested, by the check) REQ-EVD-006.S2, B3, B4: the grouped test names abbreviate the later IDs ("S1_and_S2", "B2_B3_and_B4"), so no test file carries REQ_EVD_006_S2, _B3 or _B4 (format.md, Test naming) and `check --stage verify` fails. The assertions themselves are complete. → tasks T9 and T10.
- F2 (method text) REQ-EVD-006.N1: implement.md still says a failing test of a task not done yet "is expected … it never stops the run" and defines `expected` as "no ticked task plans it", and implementer.md's row says "Expected (its task isn't done yet): count it and go on". With the list, such a test that passed before is a regression (N1, Scope bullet 2), so the method contradicts the behavior it documents. → task T11.

Verdict: GAPS — 2 findings (T9, T10 and T11 added; no spec gap)

### Round 2

- Date: 2026-11-03 · Verifier: subagent (strong)
- Tests: `python3 -m unittest tests.test_sdd` → Ran 562 tests, OK
- Check: `sdd.py check --stage verify` → result: OK; coverage line lists S1, S2, N1-N5, B1-B4. Warnings: the seven pre-existing tasks (T2-T6, T8, T11).
- Replay: `sdd.py replay --base 416850f` → replay: 11 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` → mutate: 12 caught, 0 survived or invalid
- Coverage: not available (no coverage tool installed)
- F1 closed: the two tests are now `test_REQ_EVD_006_S1_and_REQ_EVD_006_S2_…` and `test_REQ_EVD_006_B2_and_REQ_EVD_006_B3_and_REQ_EVD_006_B4_…`; the old names occur nowhere in tests/, skill/ or specs/ outside round 1's record and T10's title. Their bodies still assert every part of S1, S2, B2, B3 and B4 as round 1 found. T1/T9 and T8/T10 point at the renamed tests, which replay runs; `mutate` finds each mutation's task test (M4 through T2's N1 test, caught).
- F2 partly closed: implement.md now says a not-done task's test is expected "unless it is on the `--passed-before` list" and a listed test is a regression "even when its task isn't done yet"; `expected` reads "no ticked task plans it, and it is not on the list"; implementer.md's row excludes a listed test from Expected. Both agree with N1, Scope bullet 2 and overview.md's script row, and with the rest of implement.md (step 6 stops on an unexplained regression; step 7 records failures that aren't expected).
- T11 evidence: honest. Its test line is N1's real test, recorded `pre-existing (after T2)`, which holds (the code is T1/T2's; replay confirms T11 now). The quoted before and after text matches `git diff 416850f` of implement.md, and both `also:` lines are delivered.
- Unchanged since round 1 and not re-audited: sdd.py, the other six PassedBeforeTests, the Known gaps.

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-EVD-006.S1 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_S1_and_REQ_EVD_006_S2_a_test_that_passed_before_and_fails_is_a_regression | pass | yes |
| REQ-EVD-006.S2 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_S1_and_REQ_EVD_006_S2_a_test_that_passed_before_and_fails_is_a_regression | pass | yes |
| REQ-EVD-006.N1 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N1_a_not_done_tasks_scenario_that_passed_before_is_a_regression | pass | yes (the method text still disagrees in SKILL.md: F3) |
| REQ-EVD-006.N2 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N2_an_unreadable_list_is_refused_and_nothing_else_is_printed | pass | yes |
| REQ-EVD-006.N5 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N5_an_unreadable_failing_file_is_refused_before_the_list_is_read | pass | yes |
| REQ-EVD-006.N3 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N3_the_list_skips_blank_lines_and_trims_names | pass | yes |
| REQ-EVD-006.N4 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_N4_the_option_without_a_value_is_an_argparse_error | pass | yes |
| REQ-EVD-006.B1 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B1_a_list_that_names_no_test_warns_before_the_sorted_line | pass | yes |
| REQ-EVD-006.B2 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B2_and_REQ_EVD_006_B3_and_REQ_EVD_006_B4_only_equal_failing_names_count_and_no_task_is_kept | pass | yes |
| REQ-EVD-006.B3 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B2_and_REQ_EVD_006_B3_and_REQ_EVD_006_B4_only_equal_failing_names_count_and_no_task_is_kept | pass | yes |
| REQ-EVD-006.B4 | tests/test_sdd.py::PassedBeforeTests.test_REQ_EVD_006_B2_and_REQ_EVD_006_B3_and_REQ_EVD_006_B4_only_equal_failing_names_count_and_no_task_is_kept | pass | yes |

Findings:
- F3 (method text, the rest of F2) REQ-EVD-006.N1: skill/sdd/SKILL.md, "When something breaks", still says "A failing test of a task not done yet is expected, not a break." With the list, such a test is a regression (N1, Scope bullet 2), which the same paragraph calls a break; 0005's method review counted SKILL.md ("break = regression") as part of this method. The Method changes note doesn't name SKILL.md. A one-clause edit closes it (e.g. "…is expected, not a break, unless it is on the `--passed-before` list"). This is the second round with a gap on N1's method text, so per the Verifier role no third task is added: reported to the operator, who decides whether it becomes a task here or goes with another change. Not findings: README.md (lines on sort-failures and its known gap) and RELEASE_NOTES go with the archive commit, by 0005's precedent.

Verdict: GAPS — 1 finding (F3, SKILL.md still calls a listed not-done test expected; reported to the operator, no task added; no spec gap)

- F3 → rejected by the operator (operator, 2026-11-03, Claude Code chat): "that is a general claude.md instruction to prevent agents from running loops trying to fix stuff that never gets out. That is a valid line and I don't know how/why it would contradict anything that SDD implements." The SKILL.md sentence covers tests of tasks not built yet during a run. A test on the `--passed-before` list passed before the run, which a not-done task's test practically never does. When one does, sort-failures reports it as a regression and the agent follows that line. F3 is closed.
- Re-judged: the tests pass, the check is OK, every scenario is `yes`, replay and mutate are clean, and no finding is open.

Verdict: PASS

## Open questions
<!-- Mark unknowns where they occur as [NEEDS CLARIFICATION: question] and list them here. -->
- Q1 Where does the list of tests that passed before the run come from? → A: a file the agent writes from its full-suite run before the first task, given to sort-failures as an option; the script owns no new file (operator, 2026-10-30, Claude Code chat)

## Clarifications
<!-- Spec Critic: one round per review, started with `sdd.py round`. Format:
method/format.md. Required before the gate at production and above. -->

### Round 1 — 2026-11-02 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-EVD-006 | issues | F1, F2, F3, F4, F5, F6, F7 |

<!-- Findings: - F1 [type] REQ-…: <problem> → fixed: … | accepted: … | rejected: <reason> | Q1
Questions (at most 5): - Q1 <question> A) … B) … — recommended: …
  - Answer: pending -->

- F1 [ambiguity] REQ-EVD-006: the statement gives two forms with a task (`<task> done`, `<task> not done`) and one for an outside name, but none for a name on the list whose scenario no task plans, where REQ-EVD-005 prints `(<scenario>, no task)` (its B3). The design note implies `(REQ-DUR-001.S2, no task, passed before the run)`. Say it once, as a rule: the regression line keeps what REQ-EVD-005 puts in the parentheses, followed by `, passed before the run`; an outside name gets `(passed before the run)`. Add a boundary row: a scenario REQ-DUR-001.S2 that no task plans, failed.txt and passed.txt listing test_REQ_DUR_001_S2_x → "regression: test_REQ_DUR_001_S2_x (REQ-DUR-001.S2, no task, passed before the run)", 1 regression, exit 1. That rule also carries over REQ-EVD-005's first-ID choice for a name with several IDs and its one line per distinct failing name, so those need no new row. → fixed: the statement gives one rule (REQ-EVD-005's parentheses text, then `, passed before the run`; `(passed before the run)` for an outside name); B4 added for a scenario no task plans; T9 plans it
- F2 [ambiguity] REQ-EVD-006: when the list can't be read, the statement says to print "only an error naming it". It doesn't say what happens when REQ-EVD-005 also refuses (no active change, an unknown --change, an unreadable failing file). The code checks the change and reads the failing file before anything else, and the design reads the list after that, so with both files missing the error names the failing file and not the list. State that REQ-EVD-005's refusals come first and the list is read only after them. Add a row: failed.txt and passed.txt both missing → exit 1, the error names failed.txt, no "sorted:" line. → fixed: the statement puts REQ-EVD-005's refusals first and reads the list after them; N5 added (both files missing, the error names failed.txt); T5 plans it
- F3 [untestable] REQ-EVD-006.N3: the data hides the rule it claims to prove. passed.txt also holds an unpadded "test_legacy_total", so the failing name matches even when nothing is stripped, and M7 ("line.strip() becomes line") survives `mutate`, which runs only T5's test. Blank lines and duplicates in the list can't be seen in the output either, because only membership counts: a blank entry never equals a failing name, and a second copy changes nothing. So the dedup half of M7 can't be caught by any REQ-EVD-006 scenario. Fix: N3's passed.txt holds only "  test_legacy_total  " and a blank line. Drop "counts duplicates once" from N3's claim and from T5's title, and drop the dedup half of M7; REQ-EVD-005 N2 already proves dedup in the shared `read_names`. → fixed: N3's passed.txt holds only the padded name and a blank line; "counts duplicates once" dropped from N3's claim and the task title and test name; M7's dedup half dropped
- F4 [contradiction] REQ-EVD-006.N4 and T6: the order-exceptions comment says N4 "passes even before T1", yet it records `red: pre-existing (after T1)`. In format.md that tag means the claim holds only after T1, and replay then skips the base run, so the evidence claims a dependency that isn't there. The cause is N4's Then ("argparse's error names --passed-before"), which "unrecognized arguments: --passed-before" already meets before the option exists; as written, the test can't tell whether the option exists. N4 is still worth keeping, because it is the only scenario showing that a missing value is refused and not ignored. Fix: the Then says the error is argparse's "argument --passed-before: expected one argument" (the same text since Python 3.8). That fails before T1, so `pre-existing (after T1)` becomes true, and the comment's sentence about T6 changes to match. Give failed.txt concrete content (test_legacy_total). Add a planned mutation M8 REQ-EVD-006.N4: `p.add_argument("--passed-before")` becomes `p.add_argument("--passed-before", nargs="?")`; the missing value is then read as no list, a "sorted:" line is printed with exit 0, and N4 catches it. → fixed: N4's Then requires argparse's "argument --passed-before: expected one argument"; failed.txt lists test_legacy_total; the order comment says N4 fails before T1 and passes after it; M8 planned
- F5 [untestable] Mutations: M5's first variant (read the list after the sort) is not a one-line find/replace. Its second variant (`except` becomes a pass) is in the shared `read_names` and fails by crashing, not on N2's assertions. Plan one line that N2's own test catches, for example `read_names` returning an empty list on a read error. M4 assumes a separate `if name in passed` in the not-done branch, while M1 assumes one lookup and the design note says one lookup "whatever branch found it"; with one lookup, M4 is M1 again. Make the design note and M1/M4 name distinct lines. Each find text must occur exactly once in sdd.py (REQ-EVD-003); `line.strip()` occurs twice in today's read code. → fixed: the design names one lookup line `if name in passed:`, one count line and one print; every mutation is a one-line find/replace on a find text that occurs once; M4 is now a distinct not-done mutation; M5 makes `read_names` return [] on a read error, caught by N2's exit code; M7 finds `line.strip() for line`
- F6 [scope] REQ-EVD-006: Scope "In (method, project rule 1)" (record the passing tests before the run's first task and give the list at every sort) has no design note and no task. 0005 attached its method edits to tasks as `also:` lines. Today method/phases/implement.md (the sort-failures step), method/roles/implementer.md (the checkpoint row, whose "Regression (it passed before the task…)" and "Outside … judge it" wording changes) and method/overview.md (the script-table row, `[--passed-before <list>]`) still describe sorting by name only. Add a "Method changes" design note and `also:` lines on the last task. → fixed: a "Method changes" design note, and `also:` lines on T9 for method/phases/implement.md, method/roles/implementer.md (checkpoint row) and method/overview.md (script row)
- F7 [coverage] REQ-EVD-006.B1: an empty list is silently treated as no list. At production that is the likeliest wrong list: the agent's full-suite run crashed or its names weren't extracted. Every test that passed before then falls back to the 0.19.0 sorting this change exists to close, and nothing shows it. Known gap 1 says the script doesn't check the list, but an empty list costs nothing to notice. → Q1 → fixed: per Q1 B, the statement prints the warning just before the `sorted:` line with the exit code unchanged; B1 (a list of one blank line) asserts the warning, its position and exit 0; T8 plans it; M9 planned
- Q1 When the --passed-before list names no test (empty or only blank lines), what should sort-failures do? A) sort as without the list, silently (B1 as written) B) sort as without the list, exit code unchanged, but print `warning: <list> names no test that passed before the run` before the "sorted:" line — recommended: B (a project with no tests yet gets a harmless line; a crashed recording no longer passes unnoticed)
  - Answer: B — sort the same way with the exit code unchanged, and print "warning: <list> names no test that passed before the run" before the sorted: line (operator, 2026-11-02, Claude Code chat)

### Round 2 — 2026-11-02 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-EVD-006 | issues | F1, F2, F3 |

<!-- Findings: - F1 [type] REQ-…: <problem> → fixed: … | accepted: … | rejected: <reason> | Q1
Questions (at most 5): - Q1 <question> A) … B) … — recommended: …
  - Answer: pending -->

- F1 [conflict] REQ-EVD-006: REQ-EVD-005 stays in specs/capabilities/evidence/spec.md unchanged and untagged, and its trigger ("When `sdd.py sort-failures <file>` is run") still holds when `--passed-before` is given. It requires `outside: <name>` for a name that carries no scenario ID, counts as r only names a ticked task plans, and exits "1 when r is above 0 and 0 otherwise". REQ-EVD-006 S1 requires `regression: test_legacy_total (passed before the run)`, a regression count of 1 and exit 1 for that same name. The precedence is stated only inside REQ-EVD-006 ("in place of the line REQ-EVD-005 gives it") and in the Requirements HTML comment, which the living spec drops. Read alone, REQ-EVD-005 is false whenever the option is given. → Q1 → fixed: per Q1 B, a Known gap says REQ-EVD-005's text doesn't mention the option and REQ-EVD-006 decides the lines it changes when it is given; REQ-EVD-005 is unchanged
- F2 [contradiction] Tasks: the order-exceptions comment has T1 build "the list lookup (for outside names only at first)" so that T2 and T3 fail first. The design note instead describes one lookup line `if name in passed:` after the three branches, "whatever branch found it", with one `counts[kind] += 1` and one print. T1 would write code narrower than the design only so that later reds are real. format.md (Tasks) covers this case by grouping: when the same minimal code satisfies several happy or boundary examples of one rule, write all their tests first and take one red run. The design's single lookup is that minimal code for S1, S2 and B4. A second effect: the Mutations comment adds each entry "once its task is green", but M1 and M6 (anchored S1, so T1) find `if name in passed:` and `counts[kind] += 1`, which under the comment's plan exist only once T3 has merged the branches. A `mutate` run between T1 and T3 would report them invalid. Fix: T1 plans REQ-EVD-006.S1 REQ-EVD-006.S2, writes both tests first, takes one red run and implements the design's lookup, count and print. T3 (N1, a failure path in its own task) and T9 become `red: pre-existing (after T1)`. Rewrite the order-exceptions comment to match. M1 to M6 then find text that exists when T1 is green. → fixed: T1 plans S1 and S2 with one red run and builds the design's single lookup, count and print; N1 (now T2) and B2 to B4 (now T8) are `pre-existing (after T1)`; tasks renumbered T1-T8; the order comment rewritten; M1 to M8 find text that exists once T1 is green
- F3 [coverage] Mutations: project rule 4 says every new sdd.py rule is broken on purpose once. Two rules REQ-EVD-006 adds have no planned mutation. (a) The order (N5): the list is read only after REQ-EVD-005's refusals. A one-line mutation exists. The failing-file read (e.g. `names = read_names(args.file)`) becomes `read_names(args.passed_before) if args.passed_before else None; names = read_names(args.file)`. With both files missing, the error then names passed.txt, and N5 (T5) catches it. (b) The detail join: `", "` comes before `passed before the run` only when the detail isn't empty, and the parentheses are printed only when the detail isn't empty. Making the separator unconditional prints `regression: test_legacy_total (, passed before the run)`, and S1 (T1) catches it. Printing `({detail})` unconditionally prints `outside: test_other_total ()`, which S1 also catches. Today the design note doesn't fix the code text of the join or the print. Name those lines there, and plan M10 REQ-EVD-006.N5 and M11 REQ-EVD-006.S1 (and optionally M12 for the print) on find texts that occur once in sdd.py. → fixed: the design note names the read lines, the detail line and the print; M10 (read order, caught by N5), M11 (separator, caught by S1) and M12 (print, caught by S1) planned
- Q1 F1: how should the living spec show that `--passed-before` changes what REQ-EVD-005 prints? A) restate REQ-EVD-005 as `[MODIFIED]` in this change. Its statement opens "Where `--passed-before` isn't given", and its ten scenarios stay the same, each planned by a task with `red: pre-existing` on the existing test_REQ_EVD_005_* tests (about ten more tasks, so the size cap is at stake). B) leave REQ-EVD-005 as it is and accept the overlap. Add a Known gap saying REQ-EVD-005's text doesn't mention the option and REQ-EVD-006 decides every line it changes when the option is given. — recommended: B (REQ-EVD-006 already states the precedence and the unchanged `sorted:` line and exit code, both requirements sit next to each other in the evidence capability, and A costs about ten pre-existing tasks for one clause in a mini change)
  - Answer: B — keep REQ-EVD-005 as it is and add a Known gap: when --passed-before is given, REQ-EVD-006 decides the lines it changes (operator, 2026-11-02, Claude Code chat)

## Amendments
<!-- Spec changes after approval, one line each, then `sdd.py approve amend`:
- A1 2026-10-07: <reason> → <what changed> -->

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
| plan | 2026-11-03 | Operator in Claude Code chat, 2026-11-03: "approved" (reply to "Approve this spec and plan?" for 0007-passed-before after Critic rounds 1 and 2) |
