---
id: 0005-scoped-test-runs
title: Scoped test runs and a defect log
type: feature
size: standard
assurance: production
status: archived
capabilities: evidence=EVD, defects=DEF
created: 2026-10-28
spec_hash: 8b993c6a3062
---

# 0005-scoped-test-runs — Scoped test runs and a defect log

<!-- A standard change is this folder: proposal.md (this file), spec-delta.md,
design.md, tasks.md and verification.md. sdd.py reads them as one spec.
Gates: spec (locks Intent, Defect, Scope, Requirements, Known gaps) → plan → results. -->

## Intent
An intermediary release, ahead of increment 6, that the operator calls
critical. "As soon as we start building something a little larger, SDD
becomes extremely slow, taking days to create somewhat small changes", because
the whole test suite runs at every step of a single change. In a program of
335 tasks, task 1 covers a tiny part of the scope, yet it runs every test, and
the failures of tests for work not built yet send the run back to the operator.
The operator authorizes a range of tasks at once ("sdd implement tasks 1-45")
and doesn't want to come back to authorize each one. For the operator, who
runs large programs with SDD. The outcome: during development each task runs
only its own test and moves on when it passes; the tests of a component run
at the end of that component's tasks; the whole suite runs once, before the
run closes; and what it finds is recorded as defects, triaged with the
operator, so that critical ones are fixed and the rest are accounted for.

## Scope
- In: three test levels. Task: the task's own test, during development. Component: the tests of one capability, at the end of that capability's tasks in a run (the next task belongs to another capability, or the run ends inside it). Full: the whole suite, once, before the run closes. A capability is the component (operator, 2026-10-28); its tests are the ones whose names carry its requirement prefix.
- In: the design names the command for the component level, next to the existing task and full-suite commands, and `check` validates it.
- In: a regression is a test that passed before the task and fails after it. The agent applies this definition from its own runs during the method; the script's `sort-failures` sorts by name only, so a failing test outside the change is reported as outside and the agent judges it. A failing test for a task not done yet is expected: it is reported as a count and never stops the run. A run stops only when the task's own test still fails after two planned fixes, on a regression the task can't explain, or when the spec is ambiguous or wrong for what was found.
- In: `implement` takes a range of tasks (`T1-T45`) as well as one task, `next` and `all`. The operator authorizes the range once, and the run continues to its end unless a stop condition occurs.
- In: a defect log the script owns, so that every defect is accounted for (operator, 2026-10-28). Each defect has an ID, the failing test, its capability, a severity the agent suggests (critical, major, minor) and the operator's decision (fix now, later, won't fix). Commands add a defect, record the decision and close it; `status` and `check` count the open ones.
- In: at the end of a run, the failures of the full suite are recorded as defects, and a triage report asks the operator for each decision. A "fix now" defect becomes a `bug` change or a task; a "later" one stays open in the log.
- In: the method says what a capability is: a unit of coherent functional purpose (for example checkout, catalog or accounts), small enough to test as one component. The Spec Author proposes the capabilities a change needs, and the operator confirms them at the spec gate.
- Changes existing behavior: "an unrelated test failing" counted as a break, and two failed fixes sent the run back to the operator → only a regression is a break, and a failing test for a task not done yet is expected.
- Changes existing behavior: each task ran "the test, plus the tests around it", which agents took to mean the whole suite → the task's own test only, with the component and full levels at their checkpoints.
- Changes existing behavior: `implement all` stopped "at the first problem" → it stops only on the stop conditions above.
- In: defects are recorded, triaged and accounted for; in this change no defect blocks results approval or archive (Q1, Q5 and R1Q1 superseded: blocking moved to a follow-up change, operator, 2026-10-28).
- In: the script sorts failing tests by name into regression (a scenario of the change planned by a done task), expected (a scenario of the change no done task plans) and outside the change (any other test), from the scenario IDs the names carry, so that every run sorts them the same way (Q2). A failing test outside the change is reported as outside, not as a regression.
- Existing changes: a design without the component command keeps working (project rule 5): `check` warns, the run skips the component checkpoints and says so, and the full suite still runs before the run closes (Q3). Archived specs are unaffected.
- Out: runs that span several changes, and a program level above a change.
- Out: components other than capabilities, such as architectural layers (front end, back end, API).
- Out: replay and mutate cost at verify, including their scratch copies, which leave out ignored files such as installed dependencies (a follow-up change).
- Out: delivery profiles, releases and deploy (increment 6), blocking diff coverage and the adversarial probe (increment 7), and `harden` (increment 8).
- Out: `run-plan`, a scripted plan of a run's steps and checkpoints; the agent finds checkpoints from the task list (follow-up change, operator, 2026-10-28)
- Out: a baseline of tests that passed before, so that a failing test outside the change counts as a regression (follow-up change)
- Out: a defect that blocks results approval and archive (follow-up change)

## Open questions
<!-- Mark unknowns where they occur as [NEEDS CLARIFICATION: question]; log
answers here as "- <question> → <answer> (operator, <date>)". -->
- Q1 Does an open critical defect block the change? → A: results approval and archive refuse while a critical defect the change recorded is open with "fix now"; "later" doesn't block (operator, 2026-10-28) — superseded: moved to a follow-up change (operator, 2026-10-28)
- Q2 Who sorts a failing test into expected, regression or outside the change? → B: the script, from the failing test names and the scenario IDs they carry (operator, 2026-10-28)
- Q3 What happens with a design without the component command? → A: `check` warns, the run skips the component checkpoints and says so, and the full suite still runs before the run closes (operator, 2026-10-28)
- Q4 Is a test listed in the baseline (it passed before) that fails now a regression, even when it is the scenario of a task not done yet? → A: yes, it is a regression (operator, 2026-10-28) — superseded: moved to a follow-up change (operator, 2026-10-28)
- Q5 Does an undecided defect the change recorded block its results approval and archive? → C: "Yes. But only non-minor defects block." An open, undecided critical or major defect blocks; an undecided minor one doesn't; Q1 is unchanged (operator, 2026-10-28) — superseded: moved to a follow-up change (operator, 2026-10-28)
- Q6 Does each decision record the operator's words? → A: yes, `defect decide` requires `--evidence`, kept in an Evidence column; "my words are important because they may add to the context of the decision" (operator, 2026-10-28)
- R1Q1 Should an open major defect decided fix-now block results approval, advance verified and archive? → B: any open critical or major defect the change recorded blocks unless decided later or wont-fix; minor never blocks (operator, 2026-10-28, Critic round 1) — superseded: moved to a follow-up change (operator, 2026-10-28)
- R1Q2 Should `defect close` record why the defect is closed? → B: close requires `--evidence`, kept in the row (operator, 2026-10-28, Critic round 1)
- R1Q3 Where does an invalid defect log fail check? → B: an error at the verify stage and in the defect commands, a warning at the other stages and in status (operator, 2026-10-28, Critic round 1)
- R1Q4 What is the component checkpoint of a capability with two prefixes? → A: one checkpoint per prefix, recorded as a Known gap (operator, 2026-10-28, Critic round 1) — superseded: checkpoints are method work, one per prefix (operator, 2026-10-28)

## Amendments
<!-- Spec changes after the spec gate, one line each, then `sdd.py approve amend`:
- A1 2026-10-08: <reason> → <what changed> -->
- A1 2026-10-28: the Verifier's round 1 (GAPS) found the separator and row-ID rules untested (F1) and a header-only log not refused (F2); the operator decided A for both → REQ-DEF-006: a missing separator row is refused (statement), N8 (bad separator), N9 (bad row ID) and N10 (header with no separator) added; tasks T69–T71

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
| spec | 2026-10-28 | Operator in Claude Code chat, 2026-10-28: "Approve" (spec of 0005-scoped-test-runs after Critic rounds 1-3 and the operator's cut: 7 requirements, 68 scenarios) |
| plan | 2026-10-28 | Operator in Claude Code chat, 2026-10-28: "Approve" (plan of 0005-scoped-test-runs: design.md and 68 tasks; implement all with task-level tests, component checkpoints and the full suite at the end) |
| amend | 2026-10-28 | Operator in Claude Code chat, 2026-10-28: "Approve A1" (amendment A1 of 0005: REQ-DEF-006 refuses a missing separator row; N8, N9, N10 and tasks T69-T71) |
| results | 2026-10-28 | Operator in Claude Code chat, 2026-10-28: "Approve results" (0005-scoped-test-runs, Verifier round 2 PASS: 534 tests OK, replay 71 confirmed, mutate 59 caught) |
