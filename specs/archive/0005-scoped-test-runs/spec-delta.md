<!-- Spec Author: what changes in behavior. New requirements are untagged;
existing ones are restated in full as [MODIFIED] or listed as [REMOVED] with a
Reason line. Grammar: method/format.md. Locked at the spec gate. -->

## Requirements

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

### REQ-DEF-001 Add a defect to the log
When `sdd.py defect add --test <name> --severity <critical|major|minor>` is run, sdd.py shall add to `specs/defects.md` the row `D<n>`, `open`, the severity, `undecided`, the capability, the change, the test name (a `|` in it written `\|`) and two empty cells (Evidence, Close evidence), and print `D<n> added (<severity>, <PREFIX>)`; n is one more than the highest defect number in the log (1 when it has none); the capability is `--capability <PREFIX>` when given, else the first requirement prefix the test name carries (`REQ`, `-` or `_`, the prefix, `-` or `_`, digits, in any case; taken in capitals), and must be, as written, a prefix of the living spec or of the change's front matter; the change is the active one or the one `--change` names, at any status. A missing or blank file is written as exactly the lines `# Defects`, an empty line, the header `| ID | Status | Severity | Decision | Capability | Change | Test | Evidence | Close evidence |`, the separator (`| --- ` for each of the nine columns, then `|`) and the row, ending with a newline; a file with lines but no table line gets an empty line, the header, the separator and the row appended; any other log gets the row appended as its last line. A row is written as `| ` and its cells joined by ` | `, then ` |`, so an empty cell is two spaces between pipes.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | no specs/defects.md, the active change 0007-x declaring duration=DUR | defect add --test test_REQ_DUR_001_S1_parses --severity critical | exit 0 · specs/defects.md is exactly "# Defects", an empty line, the header, the separator and the row "\| D1 \| open \| critical \| undecided \| DUR \| 0007-x \| test_REQ_DUR_001_S1_parses \|  \|  \|", ending with a newline · "D1 added (critical, DUR)" |
| S2 | happy | a log with D1 open and D2 closed | defect add --test test_REQ_DUR_001_N1_x --severity minor | exit 0 · a row D3 is appended (a closed number is never reused) · rows D1 and D2 are unchanged |
| S3 | happy | the S1 setup and a living capability cli=CLI | defect add --test test_legacy_total --severity major --capability CLI | exit 0 · the row has capability CLI |
| N1 | validation | the S1 setup | defect add --test test_x --severity blocker | exit 2 · argparse's error lists critical, major and minor · no specs/defects.md is created |
| N2 | validation | the S1 setup | defect add --test test_legacy_total --severity major | exit 1 · the error says the test name carries no requirement ID and asks for --capability · no specs/defects.md is created |
| N4 | validation | the S1 setup | defect add --test "" --severity minor | exit 1 · the error says the test name is empty · no specs/defects.md is created |
| N5 | state | a log with D1 open for test_REQ_DUR_001_S1_parses | defect add --test test_REQ_DUR_001_S1_parses --severity major | exit 1 · the error names D1 · the log is byte-for-byte unchanged |
| N6 | state | no active change | defect add --test test_REQ_DUR_001_S1_parses --severity minor | exit 1 · the error says there is no active change · no specs/defects.md is created |
| B1 | boundary | a log with D1 closed for test_REQ_DUR_001_S1_parses | defect add --test test_REQ_DUR_001_S1_parses --severity minor | exit 0 · a row D2 is appended (only an open defect blocks a second one) |
| B2 | boundary | the S1 setup | defect add --test "test_REQ_DUR_001_S1[a\|b]" --severity minor | exit 0 · the test cell writes the pipe as a backslash and a pipe · the row still has nine cells (check reports no defect-log problem) |
| B3 | boundary | the S3 setup | defect add --test "REQ-CLI-001.S1 then req_dur_001_s2" --severity minor | exit 0 · the row has capability CLI (the first ID counts) |
| N7 | validation | the S1 setup, no capability with prefix ZZZ | defect add --test test_legacy_total --severity minor --capability dur, then defect add --test test_REQ_ZZZ_001_S1 --severity minor | exit 1 each time · the errors name "dur", then ZZZ · no specs/defects.md is created |
| N8 | validation | the S1 setup, no change 9999-none | defect add --test test_REQ_DUR_001_S1_parses --severity minor --change 9999-none | exit 1 · the error names 9999-none · no specs/defects.md is created |
| B4 | boundary | the S3 setup | defect add --test test_REQ_DUR_001_S1_parses --severity minor --capability CLI | exit 0 · the row has capability CLI (--capability wins over the name) |
| B5 | boundary | a specs/defects.md holding only the line "# Defects" | defect add --test test_REQ_DUR_001_S1_parses --severity minor | exit 0 · the file is "# Defects", an empty line, the header, the separator and the row D1 |
| B6 | boundary | the S1 setup with 0007-x at verified | defect add --test test_REQ_DUR_001_S1_parses --severity minor | exit 0 · the row's change is 0007-x (any status may record a defect) |

- N/A dependency: a log that can't be read as rows is covered by REQ-DEF-006
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

### REQ-DEF-002 Record the operator's decision on a defect
When `sdd.py defect decide D<n> <fix-now|later|wont-fix> --evidence "<text>"` is run on an open defect, sdd.py shall write the decision in that row's Decision cell and the operator's words, with line breaks as spaces and a `|` written `\|`, in its Evidence cell, replacing earlier ones, print `D<n>: <decision>`, and leave every other line of the log unchanged; it rewrites only the cells it changes (each written with one space either side), and the rest of the row stays as written; a missing or empty (blank) `--evidence` is refused with exit 1.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a log with D1 open, critical and undecided | defect decide D1 fix-now --evidence "Fix it before the release" | exit 0 · D1's decision is fix-now and its Evidence cell "Fix it before the release" · "D1: fix-now" · every other line is unchanged |
| N6 | validation | the S1 log | defect decide D1 fix-now, without --evidence, then with --evidence "   " | exit 1 each time · the error says the decision needs the operator's words (--evidence) · the log is byte-for-byte unchanged |
| S2 | happy | a log with D1 open and decided later | defect decide D1 fix-now --evidence "Fix it now" | exit 0 · D1's decision is fix-now |
| N1 | validation | the S1 log | defect decide D1 soon --evidence "x" | exit 2 · argparse's error lists fix-now, later and wont-fix · the log is byte-for-byte unchanged |
| N2 | validation | a log with D1 only | defect decide D9 later --evidence "x" | exit 1 · the error names D9 · the log is byte-for-byte unchanged |
| N3 | validation | the S1 log | defect decide d1 later --evidence "x" | exit 1 · the error names "d1" and the form D<n> · the log is byte-for-byte unchanged |
| N4 | state | a log with D1 closed | defect decide D1 later --evidence "x" | exit 1 · the error says D1 is closed · the log is byte-for-byte unchanged |
| N5 | dependency | no specs/defects.md | defect decide D1 later --evidence "x" | exit 1 · the error says no defect is logged · no specs/defects.md is created |
| B2 | boundary | a log with D1 open, decided fix-now with the evidence "Fix it" | defect decide D1 fix-now --evidence "Fix it" | exit 0 · the log is byte-for-byte unchanged |
| B3 | boundary | the S1 log | defect decide D1 later --evidence "Not now \| after the demo" | exit 0 · the Evidence cell writes the pipe as a backslash and a pipe · the row still has nine cells |
| B4 | boundary | the S1 log | defect decide D1 later with evidence "Not now" and "after the demo" on two lines | exit 0 · the Evidence cell is "Not now after the demo" · the row stays one line |

- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-DEF-003 Close a decided defect
When `sdd.py defect close D<n> --evidence "<text>"` is run on an open defect that has a decision, sdd.py shall write `closed` in its Status cell and the text (what fixed it, or why it is closed; line breaks as spaces, a `|` written `\|`) in its Close evidence cell, keep the row, print `D<n> closed`, and leave every other line of the log unchanged; it rewrites only the cells it changes (each written with one space either side), and the rest of the row stays as written; a missing or blank `--evidence` is refused with exit 1.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a log with D1 open, critical and decided fix-now | defect close D1 --evidence "T4 green: 1 passed" | exit 0 · D1's status is closed, its Close evidence "T4 green: 1 passed", its other cells unchanged · "D1 closed" · every other line is unchanged |
| N6 | validation | the S1 log | defect close D1, without --evidence, then with --evidence "  " | exit 1 each time · the error says closing needs --evidence · the log is byte-for-byte unchanged |
| S2 | happy | a log with D2 open and decided wont-fix | defect close D2 --evidence "Accepted as is by the operator" | exit 0 · D2's status is closed |
| N1 | state | a log with D1 open and undecided | defect close D1 --evidence "Fixed" | exit 1 · the error says the operator decides first (sdd.py defect decide) · the log is byte-for-byte unchanged |
| N2 | state | a log with D1 closed | defect close D1 --evidence "Fixed" | exit 1 · the error says D1 is already closed · the log is byte-for-byte unchanged |
| B1 | boundary | a log with D1 open and decided later | defect close D1 --evidence "Fixed" | exit 0 · D1's status is closed (a later defect is closed once it is fixed) |

- N/A dependency: a missing log is refused by the same lookup as REQ-DEF-002.N5, an invalid one by REQ-DEF-006
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-DEF-004 Status and check count the open defects
The status and check commands shall count the open defects of a valid specs/defects.md (an invalid one: REQ-DEF-006), with how many of them are critical and how many undecided: in text, the line `open defects: <n> (<c> critical, <u> undecided)` when n is above 0 and no such line otherwise; in `--json`, the key `defects` with `{"open": <n>, "critical": <c>, "undecided": <u>}`, zeros included; the count alone never changes an exit code.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a log with D1 open, critical and undecided, D2 open, minor and later, D3 closed and critical | status | "open defects: 2 (1 critical, 1 undecided)" · status --json has "defects": {"open": 2, "critical": 1, "undecided": 1} |
| S2 | happy | the S1 log and an otherwise clean change at designed | check | exit 0 · the S1 line · check --json has the same "defects" value |
| N1 | state | the S1 log and no active change | status | the S1 line (the log belongs to the project, not to a change) · no file is changed |
| B1 | boundary | no specs/defects.md | status | no "open defects" line · status --json has "defects": {"open": 0, "critical": 0, "undecided": 0} · no specs/defects.md is created |
| B2 | boundary | a log whose defects are all closed | check | no "open defects" line · check --json has zeros · no file is changed |
| B3 | boundary | the S1 log and an otherwise clean standard draft | check --stage spec | exit 0 (open defects alone don't fail a check) · the S1 line · no file is changed |

- N/A validation: status and check take no new argument; the log's rows are validated by REQ-DEF-006
- N/A dependency: a log that can't be read as rows is covered by REQ-DEF-006
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-DEF-006 A defect log that isn't valid rows is refused
If specs/defects.md has, outside HTML comments, table lines (lines starting with `|`) of which the first doesn't have, cell by cell after trimming spaces, the cells of the REQ-DEF-001 header, or the second is missing or isn't a separator row (every cell dashes, with optional colons at either end), or a later one that doesn't have nine cells, an ID D<n>, a status open or closed, a severity critical, major or minor and a decision undecided, fix-now, later or wont-fix, or that repeats an earlier row's ID, then the defect commands shall print an error naming specs/defects.md, the line number and the problem, exit 1 and leave the file unchanged; check shall report the same problem as an error at the verify stage and as a warning at the other stages; and status shall print it as `defect log: <problem>` and exit 0; neither shows an open defects line, and their `--json` has `"defects": null`.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| N1 | dependency | a log whose row D1, on line 5, has the severity blocker | defect add --test test_REQ_DUR_001_S1_x --severity minor | exit 1 · the error names specs/defects.md, line 5 and "blocker" · the log is byte-for-byte unchanged |
| N2 | dependency | the N1 log and a change at verifying, otherwise clean | check --stage verify | exit 1 · the N1 problem as an error · no file is changed |
| N3 | dependency | the N1 log and an otherwise clean change at designed | check --stage plan | exit 0 · the N1 problem as a warning · no "open defects" line · check --json has "defects": null · no file is changed |
| N4 | dependency | the N1 log | status | exit 0 · "defect log: specs/defects.md line 5: …blocker…" · status --json has "defects": null · no file is changed |
| N5 | dependency | a log with two rows D1 | defect decide D1 later --evidence "x" | exit 1 · the error says D1 is repeated · the log is byte-for-byte unchanged |
| N6 | dependency | a log whose row D1 has eight cells | defect close D1 --evidence "Fixed" | exit 1 · the error names the line number · the log is byte-for-byte unchanged |
| N7 | dependency | a log whose header has eight columns, without Close evidence | defect add --test test_REQ_DUR_001_S1_x --severity minor | exit 1 · the error names line 3 and the header · the log is byte-for-byte unchanged |
| N8 | dependency | a log whose second table line, on line 4, is "\| -- \| ab \| -- \| -- \| -- \| -- \| -- \| -- \| -- \|" | defect add --test test_REQ_DUR_001_S1_x --severity minor | exit 1 · the error names specs/defects.md, line 4 and the separator row · the log is byte-for-byte unchanged |
| N9 | dependency | a log whose row on line 5 has the ID E1 | defect decide D1 later --evidence "x" | exit 1 · the error names specs/defects.md, line 5 and "E1" · the log is byte-for-byte unchanged |
| N10 | dependency | a log whose header, on line 3, is its only table line | defect add --test test_REQ_DUR_001_S1_x --severity minor | exit 1 · the error names specs/defects.md, line 3 and the missing separator row · the log is byte-for-byte unchanged |
| B1 | boundary | a valid log with a blank line and an HTML comment between its rows | defect add --test test_REQ_DUR_001_S2_x --severity minor | exit 0 · the next row is appended · the earlier lines are unchanged |
| B2 | boundary | a log whose test cell holds an escaped pipe | check | no defect-log problem · no file is changed |
| B3 | boundary | a valid log whose header is padded ("\| ID  \| Status  \| …") and whose separator is "\| :--- \| ------ \| …" | defect add --test test_REQ_DUR_001_S2_x --severity minor | exit 0 · the next row is appended · the header and separator lines are unchanged |

## Known gaps
- sort-failures reads the names the agent gives it; it doesn't run tests or read a runner's report.
- A failing test outside the change is sorted outside, even when it passed before the run; telling it apart needs a baseline (follow-up change).
- The component command is not checked to select a capability's tests: a command that selects none passes.
- The defect log is plain text: a hand edit that keeps the row format is not detected, and decisions and close evidence are recorded by the agent, not verified, like approval rows.
- Deleting specs/defects.md restarts the numbering at D1.
- A defect's severity can't be changed after it is added; the operator's view of it goes in the decision.
- The same failure seen in several tests gives several defects; one test has at most one open defect.
- Two defect commands run at the same moment can write the same ID (concurrency is not required at production).
- next-req counts requirement IDs written with hyphens in specs/defects.md test names, so it can skip a number.
- The method's part (implement ranges, the three test levels, the stop conditions, the triage report, what a capability is) is design work under project rule 1, verified by review and a dogfood run.
