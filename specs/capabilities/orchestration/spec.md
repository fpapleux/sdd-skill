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

## Change history
- 0002-subagent-fanout — Subagent fan-out: prime orchestrator, role tiers, scripted verification evidence (2026-10-18): added REQ-ORC-001, added REQ-ORC-002, added REQ-ORC-003

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
