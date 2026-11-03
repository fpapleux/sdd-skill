---
capability: defects
prefix: DEF
---

# Capability: defects

<!-- Living spec: the current, approved behavior of this capability.
Maintained by `sdd.py archive`. Do not edit by hand. -->

## Known gaps
<!-- Behavior deliberately not handled yet, carried from archived changes. -->
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
- A defect blocks only the change its Change cell names, as written: a defect recorded under another change, a mistyped ID or an archived change blocks nothing. (0006-blocking-defects)
- Closing a blocking defect or deciding it later or wont-fix clears the block on the agent's evidence; close doesn't check that the defect's test now passes. (0006-blocking-defects)
- status and next count the open defects but don't name the blocking ones; check at the verify stage and the three gates do. (0006-blocking-defects)

## Change history
- 0005-scoped-test-runs — Scoped test runs and a defect log (2026-10-28): added REQ-DEF-001, added REQ-DEF-002, added REQ-DEF-003, added REQ-DEF-004, added REQ-DEF-006
- 0006-blocking-defects — Open defects block the verify gates (2026-11-02): added REQ-DEF-007, added REQ-DEF-008, added REQ-DEF-009

## Requirements

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

### REQ-DEF-007 A blocking defect refuses the verify gates
When `sdd.py approve results` (standard), `sdd.py advance verified` (from verifying or back from blocked) or `sdd.py archive` is run on a change that has a blocking defect, a row of a valid specs/defects.md whose Change cell is the change's ID and which is open, critical or major, and undecided or decided fix-now, sdd.py shall exit 1, print for each blocking defect, in the log's order, `D<n> (<severity>, <decision>) is open: close it, or decide later or wont-fix, first`, and change no file; this is the only refusal shown, checked right after the gate's argument, size and status checks and before the verify check, the verdict and archive's destination check; a minor or closed defect, one decided later or wont-fix, and one whose Change cell names another change never block, and no other approve or advance is refused because of the defects.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a standard change 0007-x in verifying, verify check OK, "Verdict: PASS", a log with D1 open, critical, later and D2 open, major, wont-fix, both of 0007-x | approve results | exit 0 · status verified · one results row · specs/defects.md is byte-for-byte unchanged |
| S2 | happy | a mini change 0007-x in verifying, verify check OK, "Verdict: PASS", a log with D1 closed, critical, fix-now, of 0007-x | advance verified | exit 0 · status verified (a closed defect never blocks) |
| S3 | happy | a verified mini change 0007-x and the S1 log | archive | exit 0 · the change is in specs/archive/0007-x |
| N1 | state | the S1 change and a log with D1 open, critical, fix-now, of 0007-x | approve results | exit 1 · the output has "D1 (critical, fix-now) is open: close it, or decide later or wont-fix, first" · status stays verifying · no results row · specs/defects.md is byte-for-byte unchanged |
| N2 | state | the S2 change and a log with D1 open, major, undecided, of 0007-x | advance verified | exit 1 · the output has "D1 (major, undecided) is open: close it, or decide later or wont-fix, first" · status stays verifying · spec.md is byte-for-byte unchanged |
| N3 | state | a verified mini change 0007-x and a log with D1, added after verified, open, critical, undecided, of 0007-x | archive | exit 1 · the output has "D1 (critical, undecided) is open: …" · status stays verified · the change stays in specs/changes · spec.md is byte-for-byte unchanged · no capability spec is written · specs/defects.md is byte-for-byte unchanged |
| N4 | state | a verified standard change 0007-x whose verify check fails (its test file no longer names a scenario) and a log with D1 open, critical, fix-now, D2 open, minor, undecided and D3 open, major, fix-now, all of 0007-x | archive | exit 1 · the output is only the D1 and D3 lines: D1, then "D3 (major, fix-now) is open: …" (no "verify check fails") · it doesn't name D2 · status stays verified · the change stays in specs/changes · spec.md is byte-for-byte unchanged · no capability spec is written · specs/defects.md is byte-for-byte unchanged |
| N5 | state | the N1 setup, then defect decide D1 later --evidence "After the demo" | approve results | exit 0 · status verified (deciding later clears the block) |
| N6 | state | the N1 setup, with T1 left unticked (the verify check fails) and the latest line "Verdict: GAPS — F1" | approve results | exit 1 · the output is only the D1 refusal "D1 (critical, fix-now) is open: …" (no "verify check fails", no "GAPS") · status stays verifying · no results row |
| N7 | state | a mini change 0007-x blocked from verified (blocked_from: verified), with T1 left unticked (the verify check fails), the latest line "Verdict: GAPS — F1", a log with D1 open, critical, undecided, of 0007-x | advance verified | exit 1 · the output is only the D1 refusal "D1 (critical, undecided) is open: …" (no "verify check fails", no "GAPS") · status stays blocked · spec.md is byte-for-byte unchanged |
| B1 | boundary | the S2 change and no specs/defects.md | advance verified | exit 0 · status verified · no specs/defects.md is created |
| B2 | boundary | the S1 change and a log with D1 open, minor, undecided and D2 open, minor, fix-now, both of 0007-x | approve results | exit 0 · status verified (minor never blocks) |
| B3 | boundary | the S1 change and a log with D1 open, critical, fix-now, of 0008-y | approve results | exit 0 · status verified (another change's defect doesn't block) |
| B4 | boundary | a mini draft 0007-x ready for plan approval and a log with D1 open, critical, undecided, of 0007-x | approve plan, then advance implementing | exit 0 each time · status implementing (the plan gate and other moves aren't refused because of defects) |
| B5 | boundary | the N2 setup | advance implementing | exit 0 · status implementing (the way back to fix a defect isn't refused) |

- N/A validation: the gates take no new argument; a log whose rows aren't valid is covered by REQ-DEF-008
- N/A dependency: a missing log is B1; a log that can't be read as rows is covered by REQ-DEF-008
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-DEF-008 An invalid defect log refuses the verify gates
If specs/defects.md isn't valid (REQ-DEF-006) when `sdd.py approve results`, `sdd.py advance verified` or `sdd.py archive` is run, then sdd.py shall exit 1, print the problem as REQ-DEF-006 names it (specs/defects.md, the line number and the problem) and change no file, even when no row names the change; as in REQ-DEF-007, this is the only refusal shown, checked right after the gate's argument, size and status checks; no other approve or advance is refused because of the log.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| N1 | dependency | the REQ-DEF-007.S1 change and a log whose row D1, on line 5, has the severity blocker | approve results | exit 1 · the output is only that problem, naming specs/defects.md, line 5 and "blocker" · status stays verifying · no results row · specs/defects.md is byte-for-byte unchanged |
| N2 | dependency | the REQ-DEF-007.S2 change and the N1 log | advance verified | exit 1 · the N1 problem · status stays verifying · spec.md is byte-for-byte unchanged |
| N3 | dependency | a verified mini change 0007-x and a log with two rows D1, both of 0008-y | archive | exit 1 · the output says D1 is repeated · status stays verified · the change stays in specs/changes · spec.md is byte-for-byte unchanged · no capability spec is written · specs/defects.md is byte-for-byte unchanged |
| B1 | boundary | the REQ-DEF-007.B4 draft and the N1 log | approve plan | exit 0 · status planned (an invalid log refuses only the verify gates) |
| B2 | boundary | the REQ-DEF-007.S2 change and the N1 log | advance implementing | exit 0 · status implementing (no other advance is refused because of an invalid log) |

### REQ-DEF-009 check lists the blocking defects at the verify stage
When `sdd.py check` runs at the verify stage (`--stage verify`, or without `--stage` on a change in verifying or verified), sdd.py shall report each blocking defect of the change (REQ-DEF-007) as an error with the REQ-DEF-007 text, in the log's order, and exit 1; at the other stages it reports none of them, and the open defects line and `defects` key of REQ-DEF-004 are unchanged.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a mini change 0007-x in verifying, otherwise clean, a log with D1 open, critical, later, D2 open, minor, undecided and D3 closed, critical, fix-now, of 0007-x, and D4 open, critical, fix-now, of 0008-y | check --stage verify | exit 0 · no error names a defect · "open defects: 3 (2 critical, 1 undecided)" · no file is changed |
| N1 | state | the S1 change and a log with D1 open, critical, fix-now and D2 open, major, undecided, of 0007-x | check --stage verify | exit 1 · the errors "D1 (critical, fix-now) is open: close it, or decide later or wont-fix, first" and "D2 (major, undecided) is open: …", in that order · check --json's errors hold each of the two lines exactly once · no file is changed |
| B1 | boundary | the N1 setup | check, without --stage | exit 1 · the N1 errors (the stage is verify) · no file is changed |
| B2 | boundary | the N1 log, naming an otherwise clean standard change 0007-x at designed | check --stage plan | exit 0 · no error names a defect · "open defects: 2 (1 critical, 1 undecided)" · no file is changed |

- N/A validation: check takes no new argument; a log whose rows aren't valid is covered by REQ-DEF-006
- N/A dependency: a missing log gives no defect error (REQ-DEF-004.B1); an invalid one is REQ-DEF-006.N2
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules
