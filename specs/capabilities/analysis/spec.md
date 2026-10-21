---
capability: analysis
prefix: ANL
---

# Capability: analysis

<!-- Living spec: the current, approved behavior of this capability.
Maintained by `sdd.py archive`. Do not edit by hand. -->

## Known gaps
<!-- Behavior deliberately not handled yet, carried from archived changes. -->
- Clause coverage (REQ-ANL-006) is a word-overlap heuristic: it can miss an uncovered clause and flag a covered one, and it never fails a check. (0003-design-depth-analyze-next)
- A contract entry's content (inputs, outputs, errors) isn't validated, only its presence and well-formedness; its depth is revisited after v1. (0003-design-depth-analyze-next)
- analyze doesn't judge contradictions between requirements, design and tasks, or constitution violations beyond check's own; the Spec Critic and the Architect's review do. (0003-design-depth-analyze-next)
- The quality of a failure mode's wording or an N/A reason isn't judged, only that one is given and is at least three words. (0003-design-depth-analyze-next)
- Interface, failure-mode and contract entries are recognized only in their exact line formats. (0003-design-depth-analyze-next)
- Design-to-requirement and failure-mode findings apply to standard changes only; a mini change keeps its design notes unchecked. (0003-design-depth-analyze-next)
- `next` prints steps and runs nothing, and the steps are advice: a step's result is not proof that it ran. (0003-design-depth-analyze-next)
- `next` can end on a spec gate that refuses when a Critic-round error (a `?` verdict where no round is required, more than 5 questions, an unknown finding type) isn't one that adds a clarify step. (0003-design-depth-analyze-next)
- A tier-line or task-parse error counts as a spec error, so `next` lists `sdd specify` for it at a mini draft instead of `sdd tasks`, and lists no fixing step at designed. (0003-design-depth-analyze-next)
- A change already past the plan gate sees the design-trace and failure-mode findings only in analyze, which no later gate runs; contract findings are check findings from the plan stage on, and no change in specs/ has interface lines today. A change still at designed must add a Failure modes section before plan approval. (0003-design-depth-analyze-next)
- The Architect's failure-mode review, as a read-only strong subagent, and the `design`, `analyze` and `next` method files are design work under project rule 1, verified by review and a dogfood run. (0003-design-depth-analyze-next)
- Several parts of the failure-mode and interface grammar have no scenario of their own: the em dash as a separator, the `*` bullet marker, the split at the last arrow, `N/A` and `interface` in any case, a None reason of exactly two words, and `~~~` fences. (0003-design-depth-analyze-next)
- The REQ-ANL-004 error is tested at production and internal only; it also applies at critical, which the code does and no scenario shows. (0003-design-depth-analyze-next)
- REQ-ORC-004.S13 is tested for a standard change only; a mini change with a GAPS verdict, and a verdict word other than PASS or GAPS (which also gets the gaps gate), have no test. (0003-design-depth-analyze-next)
- No scenario shows that a word shared by several clauses doesn't cover a clause (REQ-ANL-006). (0003-design-depth-analyze-next)
- `design_findings` falls back to the project's level when the report's level isn't valid; no scenario reaches that defensive line. (0003-design-depth-analyze-next)

## Change history
- 0003-design-depth-analyze-next — Design depth, analyze and next (2026-10-21): added REQ-ANL-001, added REQ-ANL-002, added REQ-ANL-003, added REQ-ANL-004, added REQ-ANL-005, added REQ-ANL-006, added REQ-ANL-007, added REQ-ANL-008

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
