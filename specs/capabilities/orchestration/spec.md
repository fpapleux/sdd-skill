---
capability: orchestration
prefix: ORC
---

# Capability: orchestration

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
- A capability declared with two prefixes gets one component checkpoint per prefix, each running part of its tests, not one checkpoint for the capability (0005 Q4). (0008-run-plan)
- A task whose scenario references carry two prefixes is grouped by its first reference only; its other prefix gets no checkpoint from it. (0008-run-plan)
- A run that spans several changes, and components other than capabilities (such as architectural layers), are not planned. (0008-run-plan)
- check at the plan stage and `advance designed` read `Test command:` as its first mention anywhere in the change, and replay and mutate read `Test one:` as its first list line anywhere in the change, not from the design's list line that run-plan reads, so a prose mention or a list line outside the design can stand in for the design's line and the command replay runs can differ from the one run-plan prints; this defect is outside this change, and the operator decides on a separate defect change. (0008-run-plan)
- That `implement` follows the printed plan is method work under project rule 1, verified by review and a dogfood run. (0008-run-plan)
- A test run that never ends is not stopped: sdd.py waits for the command to end. (0008-run-plan)
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
- No platform is named: Windows paths in commands and a missing `python3` are not handled. (0008-run-plan)
- A test name with surrounding spaces or a newline doesn't survive baseline.txt, so it isn't matched to the baseline. (0008-run-plan)
- A range with nothing left to run still prints "component checkpoints skipped" when the design has no Test component line (verification F2). (0008-run-plan)
- No test catches the reused suffix on a result line with no report, a submodule in the digest, the skip of a tracked file deleted in the working tree, or write_evidence keeping CRLF line endings and ending its block at a heading (verification F4). (0008-run-plan)
- A file the runner creates gets the umask default mode; only an existing file's mode is kept (verification F3). (0008-run-plan)

## Change history
- 0002-subagent-fanout — Subagent fan-out: prime orchestrator, role tiers, scripted verification evidence (2026-10-18): added REQ-ORC-001, added REQ-ORC-002, added REQ-ORC-003
- 0003-design-depth-analyze-next — Design depth, analyze and next (2026-10-21): added REQ-ORC-004, added REQ-ORC-005, added REQ-ORC-006
- 0008-run-plan — A scripted plan of a run's steps and checkpoints (2026-11-25): added REQ-ORC-009, added REQ-ORC-010, added REQ-ORC-011

## Requirements

### REQ-ORC-001 Tasks carry a model tier
Where a task has a tier line (`  - tier: …` under the task, like its test
line), sdd.py shall accept only `light`, `mid` or `strong`, or an escalation
chain such as `light → mid → strong` in which each `→` step goes up exactly one
tier and the task counts as the last tier; check at the plan stage shall warn
about each task without a tier, and status (text and `--json`) shall show how
many tasks each tier has, counting tasks without a tier as untiered.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a draft whose three tasks have the tiers light, mid and strong | check, then status | exit 0 · no tier warning · status shows "tiers: 1 light, 1 mid, 1 strong" · status --json has "tiers": {"light": 1, "mid": 1, "strong": 1} |
| S2 | happy | a draft whose task T1 has "tier: light → mid" | check | exit 0 · status counts T1 as mid |
| S3 | happy | a draft whose task T1 has "tier: light → mid → strong" | check | exit 0 · status counts T1 as strong |
| N1 | validation | a task with "tier: cheap" | check | exit 1 · the error names T1 and lists light, mid and strong · no file is changed |
| N2 | validation | a task with "tier: strong → light" | check | exit 1 · the error says each step must go up exactly one tier · no file is changed |
| N3 | validation | a task with "tier: Light" | check | exit 1 · the error lists light, mid and strong (tiers are lowercase) · no file is changed |
| N4 | state | a task with two tier lines | check | exit 1 · the error says T1 has more than one tier · no file is changed |
| N5 | validation | a task with "tier: light → strong" | check | exit 1 · the error says each step must go up exactly one tier · no file is changed |
| N6 | validation | a task with "tier: light -> mid" | check | exit 1 · the error says an escalation is written with "→" · no file is changed |
| B1 | boundary | a task with "tier: mid → mid" | check | exit 1 · the error says each step must go up exactly one tier · no file is changed |
| B2 | boundary | a draft where T1 has no tier line and the rest of the plan is valid | check | exit 0 · a warning names T1 as having no tier · no file is changed |
| B3 | boundary | a draft where T1 has "tier: light" and T2 has no tier line | status | the output shows "tiers: 1 light, 1 untiered" · no file is changed |
| B4 | boundary | a draft with no tasks | status | no tiers line is shown · status --json has no "tiers" key |

- N/A dependency: only the change's own files are read; nothing else is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ORC-002 Critic rounds record a subagent runner
When `sdd.py round` is run with `--subagent <tier>` (light, mid or strong),
sdd.py shall head the new round "Critic: subagent (<tier>)", and check shall
treat a latest round headed, in any case, "Critic: subagent (strong)" or
"Critic: fresh session" as independent at production and above, and warn
about any other latest round.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a standard draft at production with requirements | round --subagent strong | exit 0 · the new round is headed "Critic: subagent (strong)" · status clarifying |
| S2 | happy | a production change whose latest round, otherwise complete, is headed "Critic: subagent (strong)" | check | no warning about the Critic's runner |
| N1 | validation | a standard draft with requirements | round --subagent cheap | exit 2 · argparse's error lists light, mid and strong · no round is added · the files are unchanged |
| N2 | validation | a standard draft with requirements | round --subagent strong --fresh | exit 2 · the error says --subagent is not allowed with --fresh · no round is added · the files are unchanged |
| N3 | state | a standard change that is spec-approved | round --subagent strong | exit 1 · the error points to sdd amend · no round is added · the files are unchanged |
| N4 | validation | a production change whose latest round is hand-headed "Critic: subagent (cheap)" | check | a warning says the latest round's runner is not independent · no file is changed |
| B1 | boundary | a production change with an earlier subagent round and a later round headed "Critic: same session" | check | a warning says the latest round ran in the same session · no file is changed |
| B2 | boundary | a production change whose latest round is headed "Critic: subagent" with no tier | check | a warning says the latest round's runner is not independent · no file is changed |
| B3 | boundary | a production change whose latest round is headed "Critic: subagent (mid)" | check | a warning says the latest round's runner is not independent · no file is changed |
| B4 | boundary | an internal change whose latest round is headed "Critic: subagent (light)" | check | no warning about the Critic's runner |

- N/A dependency: only the change's own files are read and written; nothing else is called
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ORC-003 The Verifier's runner is recorded
While a change at production or above is checked at the verify stage, sdd.py
shall warn unless the latest Verifier line of the Verification section names a
fresh session or a strong subagent. A Verifier line is a line outside HTML
comments and fenced code blocks that contains "Verifier:" in any case; the text
after it must begin, in any case, with "fresh session" or "subagent (strong)".

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a production change in verifying with "- Date: 2026-10-14 · Verifier: subagent (strong)" | check --stage verify | no Verifier warning |
| S2 | happy | a production change in verifying with "- Date: 2026-10-14 · Verifier: fresh session (production)" | check --stage verify | no Verifier warning |
| N1 | validation | a production change in verifying with "Verifier: same session" | check --stage verify | a warning says the Verifier should run in a fresh session or a strong subagent · exit 0 when nothing else fails · no file is changed |
| N2 | validation | a production change in verifying with no line containing "Verifier:" | check --stage verify | the same warning · no file is changed |
| N3 | validation | a production change in verifying with "Verifier: subagent (cheap)" | check --stage verify | the same warning · no file is changed |
| N5 | validation | a production change in verifying with "Verifier: subagent (mid)" | check --stage verify | the same warning · no file is changed |
| N4 | state | a production change in draft, with no Verification yet | check | no Verifier warning |
| B1 | boundary | an internal change in verifying with "Verifier: same session" | check --stage verify | no Verifier warning |
| B2 | boundary | a production change with an earlier "Verifier: fresh session" line and a later "Verifier: same session" line | check --stage verify | the warning is shown (the latest line counts) · no file is changed |
| B3 | boundary | a production change with "Verifier: same session" followed by an HTML comment containing "Verifier: subagent (strong)" | check --stage verify | the warning is shown (a comment is not a Verifier line) · no file is changed |
| B4 | boundary | a production change in verifying with "verifier: Fresh Session" | check --stage verify | no Verifier warning |

- N/A dependency: only the change's own files are read; nothing else is called
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

### REQ-ORC-009 Run-plan prints the steps of a run
When the operator runs `sdd.py run-plan [<form>]` for the active change, or the one `--change` names, at planned or implementing, sdd.py shall print the test steps of the run that `implement <form>` makes and exit 0, running no command and changing no file: the form is `T<n>` (that task), `T<a>-T<b>` (the tasks from T<a> to T<b> in plan order), `next` (the first unticked task; the default) or `all` (every task of the plan); `Test command:` and `Test one:` are each read from the first list line (`-` or `*`) of the design (design.md of a standard change, the Design notes of a mini one) that carries it, as REQ-EVD-004 reads `Test component:`, taken without surrounding backticks, and a mention elsewhere in the change does not count; the first line is `plan for <change-id> (<form>): <n> to do, <m> done`, where n and m count the unticked and the ticked tasks of the range; after it, or after the skipped line of REQ-ORC-010 when there is one, comes the baseline line, read from the change's baseline.txt (REQ-EVD-008): `- baseline: none (the design has no "Test report:" line)`, unnumbered, when the design has no `Test report:` line or an empty one and no baseline.txt, otherwise `1. baseline: <test command>` when the change has no baseline.txt and no ticked task, `- baseline: none (a task is ticked; runs sort without one)`, unnumbered, when it has no baseline.txt and a ticked task, or `- baseline: recorded <time>`, unnumbered, with the time of its first line, when it has one; then one line per task of the range, in plan order; for an unticked task, first `<k>. T<i>: <Test one> (no test line yet)` when the task has no test line (empty or a placeholder, as replay reads it, REQ-EVD-001), where `<Test one>` is the `Test one:` command as written, without backticks; otherwise `<k>. T<i>: no command (the test line has no "::")` when that command uses `{file}` or `{name}` and the test line has no `::`; otherwise `<k>. T<i>: <command>`, where the command is the `Test one:` command split into words as a shell splits them, then each `{test}`, `{file}` and `{name}` filled inside its word from the task's test line as replay fills them (REQ-EVD-001), the words joined by single spaces, a word being single-quoted when it is empty or holds a character other than an ASCII letter, an ASCII digit or one of `@%+=:,./_-`, with a single quote inside it written `'"'"'`; and `- T<i>: done`, unnumbered, for a ticked task, with the component checkpoints of REQ-ORC-010 placed among them; and last `<k>. full suite: <test command>`; the test command is the `Test command:` text as written, without backticks, and k numbers the numbered lines from 1; a range with no unticked task prints only the first line, the baseline line, its done lines and `nothing to run: no task to do in the range`.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a standard change 0001-x at planned whose design has "- Test command: `runner tests`", "- Test one: `runner {file} {name}`" and "- Test component: `runner -k REQ_{prefix}_`", and tasks T1 (REQ-DUR-001.S1, ticked), T2 (REQ-DUR-001.N1, test line "tests/t_x.py::test_b") and T3 (REQ-DUR-001.S2, test line "tests/t_x.py::test_c") | run-plan T1-T3 | exactly "plan for 0001-x (T1-T3): 2 to do, 1 done", "- baseline: none (a task is ticked; runs sort without one)", "- T1: done", "1. T2: runner tests/t_x.py test_b", "2. T3: runner tests/t_x.py test_c", "3. component DUR: runner -k REQ_DUR_", "4. full suite: runner tests" · exit 0 · no command is run · no file is changed |
| S2 | happy | the S1 change, with another change 0002-y active | run-plan T2 --change 0001-x | exactly "plan for 0001-x (T2): 1 to do, 0 done", "- baseline: none (a task is ticked; runs sort without one)" (T1 is ticked), "1. T2: runner tests/t_x.py test_b", "2. component DUR: runner -k REQ_DUR_", "3. full suite: runner tests" · exit 0 · no file is changed |
| S3 | happy | the S1 change, active | run-plan next | the S2 lines, with the first line "plan for 0001-x (next): 1 to do, 0 done" · exit 0 |
| B1 | boundary | the S1 change, active | run-plan T2-T2 | the S2 lines, with the first line "plan for 0001-x (T2-T2): 1 to do, 0 done" · exit 0 |
| B2 | boundary | the S1 change, active | run-plan, with no form | the S3 lines (next is the default) · exit 0 |
| B3 | boundary | the S1 change with T2 and T3 ticked too | run-plan all | exactly "plan for 0001-x (all): 0 to do, 3 done", "- baseline: none (a task is ticked; runs sort without one)", "- T1: done", "- T2: done", "- T3: done", "nothing to run: no task to do in the range" · no numbered line · exit 0 · no file is changed |
| B4 | boundary | the B3 change | run-plan next | exactly "plan for 0001-x (next): 0 to do, 0 done", "- baseline: none (a task is ticked; runs sort without one)", "nothing to run: no task to do in the range" · exit 0 · no file is changed |
| B5 | boundary | the S1 change with "- Test one: `runner {test}`" and T2's test line "tests/it's x.py" | run-plan T2 | the step "1. T2: runner 'tests/it'"'"'s x.py'" · exit 0 |
| B6 | boundary | the S1 change with T2's test line "tests/t_x.py" | run-plan T2 | the step `1. T2: no command (the test line has no "::")`, then the component and full-suite lines of S2 · exit 0 |
| B7 | boundary | the S1 change with T2's test line empty | run-plan T2 | the step "1. T2: runner {file} {name} (no test line yet)", then the component and full-suite lines of S2 · exit 0 |
| B8 | boundary | a mini change 0001-x at implementing, active, whose Design notes have the S1 design lines, with the S1 tasks | run-plan T2 | the S2 lines · exit 0 · the status stays implementing · no file is changed |
| B10 | boundary | the S1 change with all its tasks unticked and no "Test report:" line | run-plan T2 | the second line is `- baseline: none (the design has no "Test report:" line)` · "1. T2: runner tests/t_x.py test_b" · exit 0 |
| B9 | boundary | the S1 change whose baseline.txt starts "# baseline 2026-11-16T09:00:00Z abc1234" | run-plan T2 | exactly "plan for 0001-x (T2): 1 to do, 0 done", "- baseline: recorded 2026-11-16T09:00:00Z", "1. T2: runner tests/t_x.py test_b", "2. component DUR: runner -k REQ_DUR_", "3. full suite: runner tests" · exit 0 · no file is changed |

- N/A validation: covered by REQ-ORC-011, which refuses a bad form, task ID or design line
- N/A state: covered by REQ-ORC-011, which refuses the other statuses and a missing change
- N/A dependency: only the change's own files are read; no command is run
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ORC-010 Run-plan places a component checkpoint after each group
When `sdd.py run-plan` prints a plan with an unticked task, sdd.py shall print a component checkpoint, `<k>. component <PREFIX>: <command>`, where the command is the design's `Test component:` command (REQ-EVD-004) with every `{prefix}` replaced by PREFIX, for each group of unticked tasks of the range that share a requirement prefix with no unticked task of another prefix between them, a task's prefix being the prefix of its first scenario reference; the checkpoint comes right before the next unticked task with another prefix, or after the range's last task; a ticked task, or a task with no scenario reference, is listed but neither joins nor ends a group; and when the design has no `Test component:` command, or an empty one, sdd.py shall print `component checkpoints skipped: the design has no "Test component:" line` right after the first line and no component step, the full suite staying the last step.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a change at planned with the REQ-ORC-009.S1 design and unticked tasks T1 (REQ-DUR-001.S1), T2 (REQ-DUR-001.N1), T3 (REQ-CLI-001.S1) and T4 (REQ-CLI-001.N1), each with a test line | run-plan T1-T3 | the numbered lines are, in order: "1. baseline: runner tests", 2 T1, 3 T2, "4. component DUR: runner -k REQ_DUR_", 5 T3, "6. component CLI: runner -k REQ_CLI_", "7. full suite: runner tests" (the range ends inside the CLI group) · exit 0 · no file is changed |
| B2 | boundary | the S1 design and unticked tasks T1 (REQ-DUR-001.S1), T2 (REQ-CLI-001.S1) and T3 (REQ-DUR-001.N1) | run-plan all | 2 T1, "3. component DUR: …", 4 T2, "5. component CLI: …", 6 T3, "7. component DUR: …", "8. full suite: runner tests" · exit 0 |
| B3 | boundary | the S1 design and unticked tasks T1 (REQ-DUR-001.S1), T2 (no scenario reference), T3 (REQ-DUR-001.N1), T4 (no scenario reference) and T5 (REQ-CLI-001.S1) | run-plan all | 2 T1, 3 T2, 4 T3, 5 T4, "6. component DUR: …", 7 T5, "8. component CLI: …", "9. full suite: runner tests" · no component line between T1 and T4 · exit 0 |
| B4 | boundary | the S1 design and tasks T1 (REQ-DUR-001.S1, unticked), T2 (REQ-CLI-001.S1, ticked) and T3 (REQ-DUR-001.N1, unticked) | run-plan all | the first line ends "2 to do, 1 done" · "- baseline: none (a task is ticked; runs sort without one)" · 1 T1 · "- T2: done" · 2 T3 · "3. component DUR: …" · "4. full suite: runner tests" · no component CLI line · exit 0 |
| B5 | boundary | the S1 change whose design has no "Test component:" line | run-plan all | the second line is `component checkpoints skipped: the design has no "Test component:" line` · the third line is "1. baseline: runner tests" · no component step · "6. full suite: runner tests" is the last line · exit 0 · no file is changed |

- N/A validation: the component command is checked at the plan stage by REQ-EVD-004
- N/A state: covered by REQ-ORC-011, which refuses the other statuses and a missing change
- N/A dependency: only the change's own files are read; no command is run
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-ORC-011 Run-plan refuses what it cannot plan
If `sdd.py run-plan` is run in a repository without specs/, or with no active change and no `--change`, or a `--change` that names no change in `specs/changes/`, or for a change at a status other than planned or implementing, or is given a form other than `T<n>`, `T<a>-T<b>`, `next` or `all`, a task ID that isn't in the plan, a range whose T<a> comes after T<b> in the plan, or the design has no `Test one:` or no `Test command:` list line, or an empty one (the first list line of each counts, REQ-ORC-009), or one of these two commands has a quote that doesn't close, or the change's baseline.txt doesn't start with a `# baseline <time> <commit>` line, then sdd.py shall print an error that names the first problem in that order (specs/, the change, its status, the form, the task IDs, the range, the design lines, then baseline.txt) and exit 1, printing no plan line and changing no file.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| N1 | validation | the REQ-ORC-009.S1 change, active | run-plan T1- | exit 1 · the error names "T1-" and lists T<n>, T<a>-T<b>, next and all · no plan line is printed · no file is changed |
| N2 | validation | the REQ-ORC-009.S1 change, active | run-plan T3-T1 | exit 1 · the error says T3 comes after T1 in the plan · no plan line is printed · no file is changed |
| N3 | validation | the REQ-ORC-009.S1 change, which has no task T9 | run-plan T2-T9 | exit 1 · the error names T9 · no plan line is printed · no file is changed |
| N4 | state | the REQ-ORC-009.S1 change at draft | run-plan T2 | exit 1 · the error names the status draft and says run-plan needs planned or implementing · no plan line is printed · no file is changed |
| N5 | state | no active change | run-plan T2 | exit 1 · the error says there is no active change · no plan line is printed · no file is changed |
| N6 | validation | no change 9999-none | run-plan T2 --change 9999-none | exit 1 · the error names 9999-none · no plan line is printed · no file is changed |
| N7 | validation | the REQ-ORC-009.S1 change without a "Test one:" design line | run-plan T2 | exit 1 · the error names "Test one:" · no plan line is printed · no file is changed |
| N8 | validation | the REQ-ORC-009.S1 change with an empty "- Test command:" design line, whose proposal mentions "Test command:" in its prose | run-plan T2 | exit 1 · the error names "Test command:" · no plan line is printed · no file is changed |
| N9 | validation | the REQ-ORC-009.S1 change with "- Test one: `runner '{name}`" | run-plan T2 | exit 1 · the error names "Test one:" and says a quote is not closed · no plan line is printed · no file is changed |
| N10 | validation | the REQ-ORC-009.S1 change with "- Test command: `runner 'tests`" | run-plan T2 | exit 1 · the error names "Test command:" and says a quote is not closed · no plan line is printed · no file is changed |
| N11 | state | a repository without specs/ | run-plan T2 | exit 1 · the error says SDD is not initialized · no plan line is printed · no file is created |
| N12 | validation | the REQ-ORC-009.S1 change whose baseline.txt starts "<<<<<<< HEAD" | run-plan T2 | exit 1 · the error names baseline.txt and the "# baseline <time> <commit>" line it expects · no plan line is printed · no file is changed |
