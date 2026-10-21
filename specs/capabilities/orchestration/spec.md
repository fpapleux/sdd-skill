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

## Change history
- 0002-subagent-fanout — Subagent fan-out: prime orchestrator, role tiers, scripted verification evidence (2026-10-18): added REQ-ORC-001, added REQ-ORC-002, added REQ-ORC-003
- 0003-design-depth-analyze-next — Design depth, analyze and next (2026-10-21): added REQ-ORC-004, added REQ-ORC-005, added REQ-ORC-006

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
