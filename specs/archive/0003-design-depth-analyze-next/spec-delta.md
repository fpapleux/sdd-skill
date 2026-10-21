<!-- Spec Author: what changes in behavior. New requirements are untagged;
existing ones are restated in full as [MODIFIED] or listed as [REMOVED] with a
Reason line. Grammar: method/format.md. Locked at the spec gate. -->

## Requirements

### REQ-ANL-001 Analyze reports cross-artifact findings
When the operator runs `sdd.py analyze`, sdd.py shall analyze the active change, or the one `--change` names, and print check's plan-stage report headed `analyze <id> (assurance: <level>)`, with the cross-artifact findings added to its errors and warnings blocks and a `scenarios: <h> happy, <n> negative, <b> boundary` line immediately before the result line (after the open-questions line, when there is one), and exit 1 when any error is printed and 0 otherwise, without changing any file.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | the otherwise clean standard change 0003-x at designed and production, with 1 happy and 1 negative scenario, a task for each and a design naming its requirement | analyze | exit 0 · the output starts "analyze 0003-x (assurance: production)", its second-to-last line is "scenarios: 1 happy, 1 negative, 0 boundary" and its last line is "result: OK" |
| S2 | happy | the S1 change, with a second requirement that the design never names | analyze --json | exit 0 · the JSON has check's keys, "ok": true, and the REQ-ANL-002 warning in "warnings" |
| S3 | happy | another in-flight change 0004-other that is not active | analyze --change 0004-other | that change is analyzed · the active change is unchanged |
| N1 | validation | no change 9999-none | analyze --change 9999-none | exit 1 · the error names 9999-none · no file is changed |
| N2 | validation | any change | analyze --bogus | exit 2 with argparse's message · no file is changed |
| N3 | state | a repository without specs/ | analyze | exit 1 · the error says SDD is not initialized · no file is created |
| N4 | state | no active change | analyze | exit 1 · the error says there is no active change · no file is changed |
| N5 | state | a change where scenario S1 has no task | analyze | exit 1 · the errors block has the same "no task plans this scenario" error as check --stage plan · "result: FAIL" · no file is changed |
| N6 | validation | the S1 change, with a design naming REQ-ANL-009 | analyze --json | exit 1 · "ok": false · the REQ-ANL-002 error is in "errors" · no file is changed |
| B1 | boundary | a draft with requirements and no tasks | analyze | exit 1 · the errors block has the "no tasks yet" error · no file is changed |
| B2 | boundary | an otherwise clean mini draft with tasks, which has no design.md | analyze | exit 0 · no design finding is printed |
| B3 | boundary | an otherwise clean mini change at planned and production, with no design.md | analyze | exit 0 · no design finding is printed, and no "no failure modes" error · no file is changed |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ANL-002 The design traces to the requirements
When a standard change is at designed or later (a blocked change counts at the status it was blocked from, an abandoned one never), analyze shall report an error for each requirement ID that design.md names, outside comments and fenced code blocks, in hyphen form (one error per distinct ID), and that exists neither in the change nor in the living spec, and a warning for each requirement of the change, other than a removed one, that design.md never names; a scenario reference or a failure-mode outcome names its requirement.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | in a standard change at designed, an otherwise clean designed change with REQ-ANL-001 and REQ-ANL-002, and a design naming both | analyze | no design-trace finding · exit 0 |
| N1 | validation | in a standard change at designed, a design that names REQ-ANL-009, which exists nowhere | analyze | exit 1 · the error says the design names REQ-ANL-009, which doesn't exist · no file is changed |
| N2 | validation | in an otherwise clean standard change at designed with a task for every scenario, a design that names REQ-ANL-001 but not REQ-ANL-002 | analyze | exit 0 · a warning says REQ-ANL-002 is not named in the design · no file is changed |
| N3 | state | a change at spec-approved whose design.md names no requirement | analyze | no design-trace finding, because the design isn't written yet · no file is changed |
| N4 | state | a change blocked from designed, with a design naming REQ-ANL-009 | analyze | exit 1 · the same error as for a designed change · no file is changed |
| N5 | state | an abandoned change whose design names REQ-ANL-009 | analyze | no design-trace finding · no file is changed |
| N6 | validation | in a standard change at designed, a failure-mode outcome naming REQ-ANL-009.N1 and no REQ-ANL-009 | analyze | exactly one error for REQ-ANL-009, from this requirement · no file is changed |
| B1 | boundary | in a standard change at designed, a removed requirement REQ-ANL-003 that the design doesn't name | analyze | no warning for REQ-ANL-003 · no file is changed |
| B2 | boundary | in a standard change at designed, a design naming REQ-ORC-001, which is only in the living spec | analyze | no error for REQ-ORC-001 · no file is changed |
| B3 | boundary | in a standard change at designed, a design whose only mention of REQ-ANL-002 is inside an HTML comment | analyze | the warning that REQ-ANL-002 is not named is printed (comments don't count) · no file is changed |
| B4 | boundary | in a standard change at designed, a design whose only mention of REQ-ANL-002 is the test name test_REQ_ANL_002_S1 | analyze | the warning that REQ-ANL-002 is not named is printed (the underscore form doesn't count) · no file is changed |
| B5 | boundary | in a standard change at designed, a design whose only mention of REQ-ANL-002 is the reference REQ-ANL-002.S1 | analyze | no warning for REQ-ANL-002 · no file is changed |
| B6 | boundary | in a standard change at designed, a design whose only mention of REQ-ANL-009 is inside a fenced code block | analyze | no error for REQ-ANL-009 · no file is changed |
| B7 | boundary | in a standard change at designed, a design naming REQ-ANL-009 twice, once bare and once as REQ-ANL-009.N1 | analyze | exactly one error, for REQ-ANL-009 · no file is changed |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ANL-003 Every failure mode has an outcome
Where a standard change at designed or later (REQ-ANL-002) has a `## Failure modes` section in design.md, analyze shall report an error for each bullet that isn't well formed, for each scenario reference whose requirement exists in the change or the living spec but which names no scenario that counts, and for a repeated FM number. A scenario reference counts when it is in the change or in a living-spec requirement the change neither modifies nor removes. A bullet is a line starting `- ` or `* ` at any indent, outside HTML comments and fenced code blocks; other lines are ignored; an entry is one line, with non-empty text before its arrow, and FM numbers compare as integers. A well-formed bullet is `- FM<n> <text> → <outcome>` (FM<n> followed by a space, `:` or `—`), split at the last arrow, where an outcome is scenario references separated by commas or `N/A` in any case, then `:` or `—` and a reason of at least three words; or a single `- None` (case-sensitive), with `:` or `—` and the same kind of reason, standing alone.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | an otherwise clean standard change at designed, FM1 "queue is full" → REQ-ANL-001.N1, and FM2 "no cache is added" → N/A: the design adds no cache | analyze | no failure-mode finding · exit 0 |
| S2 | happy | an otherwise clean standard change at designed whose section holds only "- None — the design adds no new component" | analyze | no failure-mode finding · exit 0 |
| S3 | happy | an otherwise clean standard change at designed, FM1 → REQ-ORC-001.N1, a scenario of the living spec | analyze | no failure-mode finding · exit 0 |
| S4 | happy | an otherwise clean standard change at designed, with "- FM1: the queue is full → REQ-ANL-001.N1" | analyze | no failure-mode finding · exit 0 |
| N1 | validation | in a standard change at designed, "- FM1 the queue is full" with no arrow | analyze | exit 1 · the error says FM1 has no outcome · no file is changed |
| N2 | validation | in a standard change at designed, "- FM1 the queue is full → REQ-ANL-001.N9", where REQ-ANL-001 exists and N9 doesn't | analyze | exit 1 · the error says FM1 names REQ-ANL-001.N9, which doesn't exist, and that a mode the spec doesn't cover needs an amendment · no file is changed |
| N3 | validation | in a standard change at designed, "- FM1 the queue is full → N/A: later" | analyze | exit 1 · the error says FM1's N/A needs a real reason (at least 3 words) · no file is changed |
| N4 | validation | in a standard change at designed, "- None — none" | analyze | exit 1 · the error says the None line needs a reason of at least 3 words · no file is changed |
| N5 | state | in a standard change at designed, two bullets both numbered FM1 | analyze | exit 1 · the error says FM1 is repeated · no file is changed |
| N6 | validation | in a standard change at designed, the bullet "- the queue may fill up" | analyze | exit 1 · the error says it is neither a failure-mode entry nor a None line · no file is changed |
| N7 | state | in a standard change at designed, a None line next to the entry FM1 | analyze | exit 1 · the error says a None line can't sit next to entries · no file is changed |
| N8 | validation | in a standard change at designed, "- FM1 the queue is full → REQ-ANL-001.N1 (the producer is refused)" | analyze | exit 1 · the error says FM1's outcome is neither scenario references nor N/A · no file is changed |
| N9 | state | a change at spec-approved with a malformed bullet in the section | analyze | no failure-mode finding, because the design isn't written yet · no file is changed |
| N10 | validation | in a standard change at designed, an entry wrapped over two lines, "- FM1 the queue is full" then "  → REQ-ANL-001.N1" | analyze | exit 1 · the error says FM1 has no outcome (an entry is one line) · no file is changed |
| N11 | state | in a standard change at designed, the entries FM1 and FM01 | analyze | exit 1 · the error says FM1 is repeated · no file is changed |
| N12 | validation | in a standard change at designed, a change whose restated REQ-ORC-001 [MODIFIED] drops N4, and "- FM1 the queue is full → REQ-ORC-001.N4" | analyze | exit 1 · the error says FM1 names REQ-ORC-001.N4, which doesn't exist · no file is changed |
| N13 | validation | in a standard change at designed, a second "- None — the design adds nothing" line in the section | analyze | exit 1 · the same error as for a None line next to entries · no file is changed |
| N14 | validation | in a standard change at designed, "- FM1 the queue is full → N/A the design adds nothing" (no separator) | analyze | exit 1 · the error says FM1's outcome is neither scenario references nor N/A · no file is changed |
| N15 | validation | in a standard change at designed, the bullet "- None" alone | analyze | exit 1 · the error says the None line needs a reason of at least 3 words · no file is changed |
| N16 | validation | in a standard change at designed, "- FM1 → REQ-ANL-001.N1" with no text before its arrow | analyze | exit 1 · the error says FM1 has no text before its arrow · no file is changed |
| N17 | validation | in a standard change at designed, "- None the design adds nothing" with no separator | analyze | exit 1 · the error says the None line needs ":" or "—" before its reason · no file is changed |
| B1 | boundary | in an otherwise clean standard change at designed with a task for every scenario, "- FM1 the queue is full → REQ-ANL-001.N1, REQ-ANL-001.N2", both existing | analyze | no failure-mode finding · exit 0 |
| B2 | boundary | in a standard change at designed, a change that removes REQ-ORC-002, and "- FM1 the queue is full → REQ-ORC-002.S1" | analyze | exit 1 · the error says FM1 names REQ-ORC-002.S1, which doesn't exist · no file is changed |
| B3 | boundary | in an otherwise clean standard change at designed with a task for every scenario, "- FM1 the queue is full → N/A: no queue added" (exactly 3 words) | analyze | no failure-mode finding · exit 0 |
| B4 | boundary | in a standard change at designed, a prose line and an indented sub-bullet "  - see the queue notes" in the section | analyze | the prose line is ignored · the sub-bullet gets the "neither an entry nor a None line" error · no file is changed |
| B5 | boundary | in a standard change at designed, an entry written inside a fenced code block in the section | analyze | no finding for it · no file is changed |
| B6 | boundary | in a standard change at designed, an entry written only inside an HTML comment | analyze | no REQ-ANL-003 finding for it · no file is changed |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ANL-004 A production design lists its failure modes
Where a standard change is at designed or later (REQ-ANL-002), analyze shall report as an error at production and above, and as a warning below, that design.md has no entry under `## Failure modes`, an entry being a bullet (as REQ-ANL-003 defines it) whose first word is exactly `FM<n>` or `None` (case-sensitive), followed by a space, `:`, `—` or the end of the line, well formed or not.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | in a standard change at designed, an otherwise clean production change whose design has one failure-mode entry | analyze | no failure-mode-section finding · exit 0 |
| S2 | happy | in a standard change at designed, an otherwise clean production change whose section holds only a None line | analyze | no failure-mode-section finding · exit 0 |
| N1 | validation | in a standard change at designed, a production change whose design has no Failure modes section | analyze | exit 1 · the error says design.md has no failure modes and to list them or write "- None — <reason>" · no file is changed |
| N2 | state | a production change at spec-approved with no Failure modes section | analyze | no failure-mode-section finding · no file is changed |
| N3 | validation | in a standard change at designed, a production change whose section holds only "- the queue may fill up" | analyze | exit 1 · the same error as for a missing section, besides REQ-ANL-003's · no file is changed |
| B1 | boundary | in a standard change at designed, an otherwise clean internal change whose design has no Failure modes section | analyze | exit 0 · a warning gives the same message · no file is changed |
| B2 | boundary | in a standard change at designed, a production change whose Failure modes section is present but has no bullets | analyze | exit 1 · the same error as for a missing section · no file is changed |
| B3 | boundary | in a standard change at designed, a production change whose section holds only "- Nonetheless the queue may fill up" | analyze | exit 1 · the same error as for a missing section, besides REQ-ANL-003's (it is not an entry) · no file is changed |
| B4 | boundary | in a standard change at designed, a production change whose only entry is inside an HTML comment | analyze | exit 1 · the same error as for a missing section · no file is changed |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ANL-005 Every listed interface has a contract entry
Where a standard change's design.md has `- interface: <name>` lines or a `## Contracts` section (key in any case, outside comments, fenced code blocks and `## Contracts`), check at the plan stage and later shall report an error for each distinct interface with no `### <name>` entry under `## Contracts`, for a line with no name, for a `### ` entry with no name, and for a repeated entry, and a warning for each entry no interface lists; names are trimmed of spaces and surrounding backticks and matched exactly.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | an otherwise clean change with "- interface: sdd.py analyze" and a "### sdd.py analyze" entry under Contracts | check --stage plan | no contract finding · exit 0 |
| S2 | happy | an otherwise clean change with "- interface: `sdd.py analyze`" and the entry "### sdd.py analyze" | check --stage plan | no contract finding · exit 0 |
| S3 | happy | an otherwise clean change with no interface line and no Contracts section | check --stage plan | no contract finding · exit 0 |
| N1 | validation | "- interface: sdd.py analyze" and no Contracts section | check --stage plan | exit 1 · the error says the interface "sdd.py analyze" has no contract entry · no file is changed |
| N2 | validation | "- interface:" with no name | check --stage plan | exit 1 · the error says an interface line has no name · no file is changed |
| N3 | state | two "### sdd.py analyze" entries under Contracts | check --stage plan | exit 1 · the error says the contract entry is repeated · no file is changed |
| N4 | state | an interface with no entry, checked at the spec stage | check --stage spec | no contract finding · no file is changed |
| N5 | validation | a "### " heading with no name under Contracts | check --stage plan | exit 1 · the error says a contract entry has no name · no file is changed |
| N6 | validation | "- interface: sdd.py analyze" only inside a fenced code block, and no entry | check --stage plan | no contract finding · no file is changed |
| B1 | boundary | two interfaces listed and an entry for only the first | check --stage plan | exit 1 · one error, for the second interface only · no file is changed |
| B2 | boundary | in an otherwise clean change with a task for every scenario, a "### sdd.py next" entry that no interface line lists | check --stage plan | exit 0 · a warning says the entry has no interface · no file is changed |
| B3 | boundary | in an otherwise clean change with a task for every scenario, the same interface listed on two lines, with one entry | check --stage plan | no contract finding · exit 0 |
| B4 | boundary | an interface with no entry, checked at the implement stage | check --stage implement | exit 1 · the same missing-entry error · no file is changed |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ANL-006 Analyze flags requirement clauses no scenario exercises
Where a requirement's statement has two or more clauses separated by semicolons, analyze shall warn about each clause whose distinctive words appear in none of the requirement's scenarios, with the exit code unchanged; empty clauses are dropped before counting; a word is a run of five or more ASCII letters, distinctive when no other clause of the statement has it (compared without case), and matched without case, bounded by non-letters, in the Given, When and Then cells only.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | in an otherwise clean change with a task for every scenario, "X shall print a header; Y shall write a ledger", and scenarios whose text mentions "header" and "LEDGER" | analyze | no clause warning · exit 0 |
| N1 | validation | in an otherwise clean change with a task for every scenario, "X shall print a header; Y shall write a ledger; Z shall restore a snapshot", and scenarios that mention "header" and "ledger" but not "restore" or "snapshot" | analyze | exit 0 · one warning names the requirement and the clause "Z shall restore a snapshot" (trimmed, without a final period) · no file is changed |
| N2 | validation | in an otherwise clean change with a task for every scenario, the same statement, and scenarios that mention "header" only | analyze | exit 0 · two warnings, one per clause · no file is changed |
| N3 | state | the same statement under a removed requirement | analyze | no clause warning · no file is changed |
| N4 | validation | in an otherwise clean change with a task for every scenario, a clause whose only distinctive word is "validation", and a scenario with the category validation but no such word in its cells | analyze | exit 0 · a warning for that clause (the category cell doesn't count) · no file is changed |
| N5 | validation | in an otherwise clean change with a task for every scenario, a clause whose only distinctive word is "ledger", and a scenario mentioning only "ledgers" | analyze | exit 0 · a warning for that clause (whole words only) · no file is changed |
| B1 | boundary | a statement with one clause and no semicolon | analyze | no clause warning · no file is changed |
| B2 | boundary | a clause whose words are all shorter than five letters or shared with another clause | analyze | that clause is skipped, with no warning · no file is changed |
| B3 | boundary | the two-clause statement "X shall print a header; Y shall write a ledger;" ending with a semicolon, and scenarios mentioning both words | analyze | the empty clause after it is dropped, with no warning · no file is changed |
| B4 | boundary | the three-clause statement of N1, and scenarios that mention "header", "ledger" and "restore" | analyze | no warning for Z's clause (one distinctive word is enough) · no file is changed |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ANL-007 Analyze flags a happy-heavy change
Where the assurance is above prototype, analyze shall warn when a change has more happy scenarios than non-happy ones, every scenario that isn't happy counting, boundary included, naming both counts, with the exit code unchanged.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | in an otherwise clean change with a task for every scenario, 2 happy and 5 non-happy scenarios at production | analyze | no balance warning · exit 0 |
| N1 | validation | in an otherwise clean change with a task for every scenario, 3 happy and 2 non-happy scenarios at production | analyze | exit 0 · a warning says 3 happy scenarios outweigh 2 non-happy ones · no file is changed |
| N2 | state | 3 happy and 2 non-happy scenarios at prototype | analyze | no balance warning · no file is changed |
| B1 | boundary | 2 happy and 2 non-happy scenarios at production | analyze | no balance warning · no file is changed |
| B2 | boundary | no requirements at all, at production | analyze | no balance warning · no file is changed |
| B3 | boundary | 3 happy, 1 negative and 2 boundary scenarios at production | analyze | no balance warning (boundary counts as non-happy) · no file is changed |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ANL-008 The plan gate needs a clean analysis
When the operator approves the plan, sdd.py shall refuse while analyze reports an error, print analyze's report followed by `error: plan approval refused: fix the analyze errors first`, and record no approval.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a designed standard change whose analyze has no error, only a warning, and no open question | approve plan | exit 0 · the plan approval is recorded · the status becomes planned |
| N1 | validation | a design naming REQ-ANL-009, which doesn't exist | approve plan | exit 1 · analyze's report with the error, then "error: plan approval refused: fix the analyze errors first" · no approval row · the status is unchanged |
| N2 | validation | a production design with no Failure modes entry | approve plan | exit 1 · the failure-mode error is printed · no approval row · the status is unchanged |
| N3 | state | a mini draft at internal with a clean check and no open question | approve plan | exit 0 · the plan approval is recorded (mini has no design findings) |
| B1 | boundary | an error that check also reports | approve plan | exit 1 · the error is printed once · no approval row · the status is unchanged |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ORC-004 Next lists the steps to the next gate
When the operator runs `sdd.py next`, sdd.py shall print the remaining steps of the active change, or of the one `--change` names, in order, one `<n>. sdd <phase>` line each, up to the next operator gate, then a `gate:` line naming it, and exit 0 without changing any file; `sdd clarify` is a step, at draft or clarifying (standard) or draft (mini), while a Critic round is required at the change's size and level and the latest round hasn't audited every requirement, or while any finding, question or clarification marker (the bracketed NEEDS CLARIFICATION tag) is open (at any level); a mini change stops after `sdd verify`, and at verified or verifying with a PASS verdict prints no step and the review gate; a change at verifying with a GAPS or unknown verdict prints no step and a gate for the operator's decision; a pending amendment prints `1. sdd amend` and its gate line while no new Amendments entry is logged, and only its gate line once one is; and a change prints only the first of these that applies, with no gate line unless it is the amendment's: abandoned, a changed constitution, a pending amendment, blocked; a status that is not one of the change's size's statuses is an error with exit 1.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a clean standard draft at production with requirements and no Critic round | next | "1. sdd clarify" · "gate: the operator approves the spec (sdd approve spec)" · exit 0 |
| S2 | happy | a standard change at spec-approved | next | "1. sdd design" · "2. sdd tasks" · "3. sdd analyze" · "gate: the operator approves the plan (sdd approve plan)" |
| S3 | happy | a clean standard change at designed with tasks | next | "1. sdd analyze" · the plan gate line |
| S4 | happy | a standard change at planned with 2 of 5 tasks ticked | next | "1. sdd implement" · "2. sdd verify" · "gate: the operator approves the results (sdd approve results)" |
| S5 | happy | a standard change at verified | next | "1. sdd archive" · "gate: none" |
| S6 | happy | a mini change at planned | next | "1. sdd implement" · "2. sdd verify" · "gate: the operator reviews the verification, then sdd archive" |
| S7 | happy | a standard change at verifying with no verdict | next | "1. sdd verify" · the results gate line |
| S8 | happy | a standard change at verifying whose latest verdict is PASS | next | no step line · the results gate line |
| S9 | happy | a clean mini draft at production with tasks and a complete Critic round | next | no step line · the plan gate line |
| S10 | happy | a standard change at clarifying whose round has "?" verdicts | next | "1. sdd clarify" · the spec gate line |
| S11 | happy | a mini change at verified | next | no step line · "gate: the operator reviews the verification, then sdd archive" |
| S12 | happy | a mini change at verifying with a PASS verdict | next | the same as S11 |
| S13 | happy | a standard or mini change at verifying whose latest verdict is GAPS | next | no step line · "gate: the operator decides on the gaps (amend or accept), then sdd verify" |
| N1 | state | a change at status blocked | next | exit 0 · exactly "blocked: resolve the blocker, then sdd status" · no gate line · no file is changed |
| N2 | state | an abandoned change, targeted with --change | next | exit 0 · exactly "nothing to run: the change is abandoned" · no gate line · no file is changed |
| N3 | state | an approved spec edited since approval, with no new Amendments entry | next | exit 0 · "1. sdd amend" · "gate: the operator approves the amendment (sdd approve amend)" · no file is changed |
| N11 | state | the same edit, with its Amendments entry logged | next | exit 0 · exactly "gate: the operator approves the amendment (sdd approve amend)" · no step line · no file is changed |
| N12 | state | a blocked change whose constitution changed since approval | next | exit 0 · exactly the constitution line · no file is changed |
| N13 | state | a blocked change whose approved spec was edited since approval, with no new Amendments entry | next | "1. sdd amend" · the amendment gate line · no file is changed |
| N14 | state | an abandoned change whose constitution changed | next | exit 0 · exactly "nothing to run: the change is abandoned" · no file is changed |
| N15 | validation | a change whose front-matter status is "drafty" | next | exit 1 · the error says it cannot list steps because the status "drafty" is unknown · no file is changed |
| N4 | state | no active change | next | exit 1 · the error says there is no active change · no file is changed |
| N5 | state | a repository without specs/ | next | exit 1 · the error says SDD is not initialized · no file is created |
| N6 | validation | no change 9999-none, or an archived change's ID | next --change 9999-none | exit 1 · the error names the ID · no file is changed |
| N7 | state | a standard draft at production whose latest round audits every requirement, with one unanswered question that no finding waits on | next | "1. sdd clarify" · the spec gate line |
| N8 | state | a change whose constitution changed since approval | next | exit 0 · exactly "the constitution changed since approval: review it, then sdd approve (constitution)" · no step line · no gate line · no file is changed |
| N9 | state | a standard change at planned with a requirement added by an amendment, after a round that predates it | next | "1. sdd implement" and the later steps · no "sdd clarify" line · no file is changed |
| N10 | state | a standard draft at prototype with an open clarification marker | next | "1. sdd clarify" · the spec gate line · no file is changed |
| B1 | boundary | a standard change at implementing with all tasks ticked | next | "1. sdd verify" · the results gate line |
| B2 | boundary | a clean standard draft at prototype with requirements | next | no "sdd clarify" line · the spec gate line |
| B3 | boundary | a clean standard draft at production whose latest Critic round covers every requirement with no open finding or question | next | no "sdd clarify" line · the spec gate line |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ORC-005 Next puts the step that fixes a problem first
While a draft or clarifying change has no requirements or a spec error (one that `check --stage spec` reports outside the Clarifications section), `sdd.py next` shall list `sdd specify` first; while a mini draft or a standard change at designed has no tasks or a plan error (one that only the plan stage adds, other than a REQ-ANL-002 to REQ-ANL-005 error), it shall list `sdd tasks`, and at designed, while check or analyze reports an error from REQ-ANL-002 to REQ-ANL-005, `sdd design` before it; each is followed by the steps a clean change has, and a warning never adds a step.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a standard draft at production with no requirements | next | "1. sdd specify" · "2. sdd clarify" · the spec gate line |
| S2 | happy | a standard change at designed with no tasks | next | "1. sdd tasks" · "2. sdd analyze" · the plan gate line |
| S3 | happy | a standard change at designed, with tasks and a design-trace error from analyze | next | "1. sdd design" · "2. sdd analyze" · the plan gate line |
| S4 | happy | a mini draft at production with no requirements | next | "1. sdd specify" · "2. sdd tasks" · "3. sdd clarify" · the plan gate line |
| N1 | validation | a standard draft with a missing-coverage check error and a complete round | next | "1. sdd specify" · the spec gate line · no file is changed |
| N2 | validation | a mini draft with requirements, no tasks, a complete round | next | "1. sdd tasks" · the plan gate line · no file is changed |
| N3 | state | a standard change at designed with a design-trace error and no tasks | next | "1. sdd design" · "2. sdd tasks" · "3. sdd analyze" · the plan gate line |
| N4 | state | a standard change at planned with a check error | next | "1. sdd implement" and the later steps, with no fixing step · no file is changed |
| N5 | validation | a standard draft whose round has "?" verdicts and no other error | next | "1. sdd clarify" with no "sdd specify" line · the spec gate line · no file is changed |
| N6 | validation | a standard change at designed with tasks and a contract error from REQ-ANL-005 | next | "1. sdd design" · "2. sdd analyze" · the plan gate line · no "sdd tasks" line · no file is changed |
| N7 | validation | a mini draft at production with tasks, a complete round and a "no task plans this scenario" error | next | "1. sdd tasks" · the plan gate line · no "sdd specify" line · no file is changed |
| N8 | state | a standard change at designed whose tasks omit one scenario, so that check --stage plan reports "no task plans this scenario" | next | "1. sdd tasks" · "2. sdd analyze" · the plan gate line · no file is changed |
| B1 | boundary | a standard change at designed with tasks and only warnings | next | "1. sdd analyze" · the plan gate line (no fixing step) |
| B2 | boundary | a standard change at designed with tasks and a failure-mode error from analyze | next | "1. sdd design" · "2. sdd analyze" · the plan gate line |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ORC-006 Status points to analyze before the plan gate
When a standard change is at designed, has tasks and check reports no error, status shall show `next: sdd analyze, then ask for plan approval`, in the text and in `--json`, and otherwise leave its next line unchanged.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a clean standard change at designed with tasks | status | the output ends "next: sdd analyze, then ask for plan approval" |
| S2 | happy | the same change | status --json | "next" is "sdd analyze, then ask for plan approval" |
| N1 | state | a standard change at designed with no tasks | status | "next: sdd tasks" as before · no file is changed |
| N2 | validation | a standard change at designed with a check error | status | the "fix the check errors" next line as before · no file is changed |
| B1 | boundary | a standard change at planned | status | "next: sdd implement" as before · no file is changed |
| B2 | boundary | a standard change at designed with tasks and only warnings | status | the new next line · no file is changed |

- N/A dependency: only local files in the repository are read; no program or service is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

## Known gaps
<!-- Behavior deliberately not handled, one line each. Required at prototype
(write "- None" if there are none). -->
- Clause coverage (REQ-ANL-006) is a word-overlap heuristic: it can miss an uncovered clause and flag a covered one, and it never fails a check.
- A contract entry's content (inputs, outputs, errors) isn't validated, only its presence and well-formedness; its depth is revisited after v1.
- analyze doesn't judge contradictions between requirements, design and tasks, or constitution violations beyond check's own; the Spec Critic and the Architect's review do.
- The quality of a failure mode's wording or an N/A reason isn't judged, only that one is given and is at least three words.
- Interface, failure-mode and contract entries are recognized only in their exact line formats.
- Design-to-requirement and failure-mode findings apply to standard changes only; a mini change keeps its design notes unchecked.
- `next` prints steps and runs nothing, and the steps are advice: a step's result is not proof that it ran.
- `next` can end on a spec gate that refuses when a Critic-round error (a `?` verdict where no round is required, more than 5 questions, an unknown finding type) isn't one that adds a clarify step.
- A tier-line or task-parse error counts as a spec error, so `next` lists `sdd specify` for it at a mini draft instead of `sdd tasks`, and lists no fixing step at designed.
- A change already past the plan gate sees the design-trace and failure-mode findings only in analyze, which no later gate runs; contract findings are check findings from the plan stage on, and no change in specs/ has interface lines today. A change still at designed must add a Failure modes section before plan approval.
- The Architect's failure-mode review, as a read-only strong subagent, and the `design`, `analyze` and `next` method files are design work under project rule 1, verified by review and a dogfood run.
- Several parts of the failure-mode and interface grammar have no scenario of their own: the em dash as a separator, the `*` bullet marker, the split at the last arrow, `N/A` and `interface` in any case, a None reason of exactly two words, and `~~~` fences.
- The REQ-ANL-004 error is tested at production and internal only; it also applies at critical, which the code does and no scenario shows.
- REQ-ORC-004.S13 is tested for a standard change only; a mini change with a GAPS verdict, and a verdict word other than PASS or GAPS (which also gets the gaps gate), have no test.
- No scenario shows that a word shared by several clauses doesn't cover a clause (REQ-ANL-006).
- `design_findings` falls back to the project's level when the report's level isn't valid; no scenario reaches that defensive line.
