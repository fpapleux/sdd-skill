---
id: 0008-run-plan
title: A scripted plan of a run's steps and checkpoints
type: feature
size: standard
assurance: production
status: draft
capabilities: orchestration=ORC
created: 2026-10-30
---

# 0008-run-plan — A scripted plan of a run's steps and checkpoints

<!-- A standard change is this folder: proposal.md (this file), spec-delta.md,
design.md, tasks.md and verification.md. sdd.py reads them as one spec.
Gates: spec (locks Intent, Defect, Scope, Requirements, Known gaps) → plan → results. -->

## Intent
<!-- Spec Author: why this change, for whom, and the outcome. Use the operator's
words. No technology choices. -->

Since 0.19.0, the operator authorizes a range of tasks once ("sdd implement
tasks 1-45") and the run goes to its end. Each task runs its own test, a
capability's tests run at the end of its tasks, and the full suite runs once.
The agent works out where those checkpoints go by reading the task list, so
two runs over the same tasks can place them differently. For the operator,
who runs large programs with SDD. The outcome: the script prints a run's plan
(each step, its command, and where each checkpoint goes) so that every run
follows the same plan.

## Scope
- In: a new read-only command, `run-plan`, for the active change or the one `--change` names, taking the same forms as `implement`: one task (`T7`), a range (`T1-T45`), `next` and `all`. It prints the plan and runs nothing.
- In: the plan lists, in task order, each task of the range with the command that runs its own test (from the design's `Test one:` line). A task already ticked is listed as done, with no command.
- In: a component checkpoint, which runs the capability's tests (the design's `Test component:` command with the prefix filled in), comes after the last task of a group of consecutive tasks with the same requirement prefix: before the next task with another prefix, or at the end of the range. A task with no scenario reference is listed but neither joins nor ends a group (0005 round 1 F6).
- In: a capability declared with two prefixes gets one checkpoint per prefix (0005 Q4, operator, 2026-10-28), recorded as a known gap.
- In: the full suite (the design's `Test command:`) runs once, as the last step.
- In: a header with how many tasks of the range are to do and how many are done (0005 round 1 F3).
- In: a design without `Test component:` gets a plan that says the component checkpoints are skipped, and the full suite still runs (as REQ-EVD-004 warns).
- In: refusals that write nothing: a malformed range, a reversed range, a task ID that isn't in the plan, no active change, an unknown `--change`, a `Test one:` or `Test command:` whose quotes don't close (0005 round 1 F9), and a change at any status other than planned or implementing, where implement can run (Q1).
- In: the plan starts with a step that records the tests passing before the run, the list change 0007 gives to sort-failures; 0007 is built before this change (Q2).
- In (method, project rule 1): `implement` follows the printed plan instead of reading checkpoints from the task list.
- Out: running the steps, ticking tasks or recording evidence; like `next`, the plan is advice, and a step's result isn't proof that it ran.
- Out: runs that span several changes, and components other than capabilities (architectural layers).

## Open questions
<!-- Mark unknowns where they occur as [NEEDS CLARIFICATION: question]; log
answers here as "- <question> → <answer> (operator, <date>)". -->
- Q1 From which statuses does run-plan print a plan? → A: planned and implementing only, where implement can run (operator, 2026-10-30, Claude Code chat)
- Q2 Once 0007 is done, should the plan start with a step that records the tests passing before the run? → A: yes, and 0007 is built before this change (operator, 2026-10-30, Claude Code chat)
- Q3 What does the step of a task with an empty test line show, since the Implementer writes the test line during the task? → A: the `Test one:` command unfilled, then "(no test line yet)" (REQ-ORC-009.B7) (operator, 2026-11-01, Claude Code chat)
- Q4 Does a ticked task of another prefix between two unticked tasks of one prefix split their group? → A: no, one checkpoint after the last of them; a ticked task neither joins nor ends a group (REQ-ORC-010.B4) (operator, 2026-11-01, Claude Code chat)

## Amendments
<!-- Spec changes after the spec gate, one line each, then `sdd.py approve amend`:
- A1 2026-10-08: <reason> → <what changed> -->

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
