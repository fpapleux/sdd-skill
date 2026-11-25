---
id: 0010-impact-targeted-tests
title: An impact assessment chooses the tests a change runs
type: feature
size: standard
assurance: production
status: draft
capabilities: impact=IMP
created: 2026-11-16
---

# 0010-impact-targeted-tests — An impact assessment chooses the tests a change runs

<!-- A standard change is this folder: proposal.md (this file), spec-delta.md,
design.md, tasks.md and verification.md. sdd.py reads them as one spec.
Gates: spec (locks Intent, Defect, Scope, Requirements, Known gaps) → plan → results. -->

## Intent
<!-- Spec Author: why this change, for whom, and the outcome. Use the operator's
words. No technology choices. -->

"At some point, the smallest change takes a day and much of my tokens just
because of the sheer depth of how we test. For instance, I'll make a tiny
change and we're running a test of the test mechanics first even though we
just ran the suite an hour ago." For the operator who builds software with
SDD. Testing should be "not lighter but better targeted": once the spec is
approved, each change assesses its impact (the data, scenarios, UI and flows
it might affect) and from it picks the tests to run. The operator sees a
summary of the assessment and a grouped table of those tests, so they know
what they approve when they approve the plan.

## Scope
- In: after the spec is approved, the change records an impact assessment: each data point, existing scenario, UI and flow the change might affect, with why. A kind with nothing affected says so ("none", and why). For a mini change, whose spec and plan are approved together, the assessment comes before that single gate. [NEEDS CLARIFICATION: Q3 — every change, mini included, or standard only?]
- In: from the assessment, the change records the tests to run: its own scenarios' tests and the existing tests of each affected item, grouped by capability and then by affected item.
- In: at the plan gate, the operator is shown a summary of the assessment and the grouped test table before being asked to approve; the plan approval covers both, and a later edit to either is reported like any change after the gate.
- In: the plan gate refuses a change with no assessment, or whose test table lists a test that doesn't exist or an affected item with no test.
- In: the run uses the table: implement runs only the tests the assessment picked, and never the full suite. The full suite runs only in verify, as a final round that everything still works, and only when the change is large enough. [NEEDS CLARIFICATION: Q4 — what makes a change large enough, and who decides?]
- In: the script prints the summary and the grouped table, so the operator sees the same view at every gate and in a fresh session.
- In (method, project rule 1): the role that writes the assessment, where it sits in the phases (design, tasks, approve digest, implement, verify), and how the Verifier checks it.
- Existing changes (project rule 5): a change planned before this rule keeps today's test levels; archived changes are unaffected.
- Out: working out the impact from the code automatically; the assessment is the agent's judgment, recorded and approved by the operator.
- Out: fewer scenarios, larger tasks, or lighter Critic and Verifier rounds (a separate change).
- Out: coverage measurement.
- Out: running the tests, recording their results and reusing a result on unchanged code: the scripted test runner of change 0008, which this change builds on (operator, 2026-11-16).

## Open questions
<!-- Mark unknowns where they occur as [NEEDS CLARIFICATION: question]; log
answers here as "- <question> → <answer> (operator, <date>)". -->
- Q1 Does the full suite still run once per change? → Only in verify, and only if the change is large enough: "That's what verification should be. A final round to make sure everything still works. Sometimes I change a label on a screen. It's ridiculous to suggest that a full suite needs to run." (operator, 2026-11-16, Claude Code chat)
- Q2 Is a recorded result reused on unchanged code? → moved to change 0008, the scripted test runner: "fold it in and 0010 will be about targeting" (operator, 2026-11-16, Claude Code chat)

## Amendments
<!-- Spec changes after the spec gate, one line each, then `sdd.py approve amend`:
- A1 2026-10-08: <reason> → <what changed> -->

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
