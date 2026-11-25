---
id: 0008-run-plan
title: A scripted plan of a run's steps and checkpoints
type: feature
size: standard
assurance: production
status: archived
capabilities: orchestration=ORC, evidence=EVD
created: 2026-10-30
spec_hash: 65f28de8f948
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
two runs over the same tasks can place them differently. And the agent runs
every test itself and reads all of its output: "we should engineer test
scripts; not having an agent executing tests. A test run of 1000 tests should
be a script running all the tests and recording their output. Then have an
agent read the report and identify exceptions." For the operator, who runs
large programs with SDD and wants testing operations streamlined now. The
outcome: the script prints a run's plan so that every run follows the same
plan, runs each test step of it, records the results, and gives the agent a
short report of the exceptions to deal with.

## Scope
- In: a new read-only command, `run-plan`, for the active change or the one `--change` names, taking the same forms as `implement`: one task (`T7`), a range (`T1-T45`), `next` and `all`, with `next` the default when no form is given (as implement.md step 2; round 1 F8). It prints the plan and runs nothing.
- In: the plan lists, in task order, each task of the range with the command that runs its own test (from the design's `Test one:` line). `Test one:` and `Test command:` are read from list lines (`-` or `*`) of the design (design.md, or a mini change's Design notes), as REQ-EVD-004 reads `Test component:`; the first such line counts and a mention elsewhere in the change doesn't (round 1 F1, round 2 F7). A task already ticked is listed as done, with no command.
- In: a component checkpoint, which runs the capability's tests (the design's `Test component:` command with the prefix filled in), comes after the last task of a group of consecutive tasks with the same requirement prefix: before the next task with another prefix, or at the end of the range. A task with no scenario reference is listed but neither joins nor ends a group (0005 round 1 F6).
- In: a capability declared with two prefixes gets one checkpoint per prefix (0005 Q4, operator, 2026-10-28), recorded as a known gap.
- In: the full suite (the design's `Test command:`) runs once, as the last step.
- In: a header with how many tasks of the range are to do and how many are done (0005 round 1 F3).
- In: a design without `Test component:` gets a plan that says the component checkpoints are skipped, and the full suite still runs (as REQ-EVD-004 warns).
- In: refusals that write nothing: a malformed range, a reversed range, a task ID that isn't in the plan, no active change, an unknown `--change`, a `Test one:` or `Test command:` whose quotes don't close (0005 round 1 F9), and a change at any status other than planned or implementing, where implement can run (Q1), a design with no or an empty `Test one:` or `Test command:` line (round 1 F8, round 2 F1), and a repository without specs/ (round 1 F9); when several apply, the first in a fixed order is named (round 2 F8).
- In: the plan starts with the baseline step when the change has none yet, and shows the recorded baseline otherwise (Q7; replaces the per-run record step of round 1 F5 and Q2).
- In (method, project rule 1): `implement` follows the printed plan instead of reading checkpoints from the task list, and `implement` and `verify` run each test step through the runner and read its report, not the runner's output.
- In (method, project rule 1): implement.md step 5's "One checkpoint per prefix" is reworded to the two-prefix capability it was written for (0005 Q4); a prefix whose tasks are split by tasks of another prefix gets one checkpoint after each of its groups, as REQ-ORC-010.B2 says (round 1 Q2).
- In: the design names where the runner writes its JUnit XML report, in a `Test report:` list line read like `Test one:`.
- In: a command that runs one test step (a task's own test, a capability's tests, or the full suite) with the design's commands, records the run (when, on which code, the command, its result and each test's outcome) and its full output, and prints a short report: the counts, then each test that didn't pass with its name and the lines of output that explain it. The agent reads the report, not the output. Each test's outcome is read from a JUnit XML report the runner writes, named by the design; a runner without one falls back to its exit code and the last lines of its output (Q5).
- In: the report sorts each failing test into regression, expected or outside, as sort-failures does (REQ-EVD-005), with the tests that passed before the run taken from a recorded run, so the agent no longer writes either list by hand.
- In: a task's red and green lines are written by the script from the task's own test run (Q6); a line typed by hand in the same form is not told apart (a Known gap).
- In: the tests that passed before the change are recorded once per change, by one run before its first task, on the code before any change; every later run of the change sorts against that record and never reruns it (Q7). A step on code that hasn't changed since the last run, when that run is the same step of the same change (the same commit and the same working-tree contents), reuses it (A1 review Q4) instead of rerunning it, and the report says "reused from <time>".
- In: the last run is kept in git; before each run, the previous last run is renamed `run of <its time>` and kept out of git, and the new run becomes the last run. The change's baseline is kept in git with the change (Q8). The project folder's absolute path is written as `.` in the committed files (A1 review Q2).
- Out: the run's steps other than tests: `advance implementing` at planned and the check after each task stay in implement.md (round 1 Q1); the sorts move into the runner's report.
- Out: running the whole plan unattended: code is written between a task's red and green runs, so the agent runs each step when the method reaches it; ticking tasks stays the agent's.
- Out: choosing which tests a change runs from its impact (change 0010, which builds on this runner).
- Out: runs that span several changes, and components other than capabilities (architectural layers).

## Open questions
<!-- Mark unknowns where they occur as [NEEDS CLARIFICATION: question]; log
answers here as "- <question> → <answer> (operator, <date>)". -->
- Q1 From which statuses does run-plan print a plan? → A: planned and implementing only, where implement can run (operator, 2026-10-30, Claude Code chat)
- Q2 Once 0007 is done, should the plan start with a step that records the tests passing before the run? → A: yes, and 0007 is built before this change (operator, 2026-10-30, Claude Code chat)
- Q3 What does the step of a task with an empty test line show, since the Implementer writes the test line during the task? → A: the `Test one:` command unfilled, then "(no test line yet)" (REQ-ORC-009.B7) (operator, 2026-11-01, Claude Code chat)
- Q4 Does a ticked task of another prefix between two unticked tasks of one prefix split their group? → A: no, one checkpoint after the last of them; a ticked task neither joins nor ends a group (REQ-ORC-010.B4) (operator, 2026-11-01, Claude Code chat)
- Q5 How does the script learn each test's outcome? → A: from a JUnit XML report named by the design, falling back to the exit code and the output's last lines (operator, 2026-11-16, Claude Code chat)
- Q6 Who writes a task's red and green lines? → A: the script, from the task's own test run (operator, 2026-11-16, Claude Code chat)
- Q8 Where are run records kept? → the last run is kept in git, older ones are not: "keep last run outside of the gitignore. We want it. What we don't want is any older one"; before a run the last run is renamed "run of <time>", then the tests run to "last run" (operator, 2026-11-16, Claude Code chat; replaces the earlier answer A, a local cache)
- Q7 Is a recorded result reused instead of rerun? → yes; the tests to run are decided before any change is made, so the passing tests are recorded once per change before its first task and every later run sorts against that record; a later step on unchanged code (same commit and working-tree contents) reuses its recorded run (operator, 2026-11-16, Claude Code chat)

## Amendments
<!-- Spec changes after the spec gate, one line each, then `sdd.py approve amend`:
- A1 2026-10-08: <reason> → <what changed> -->
- A1 2026-11-16: the operator folds a scripted test runner into this change ("fold it in and 0010 will be about targeting… Let's do this in 0008", Claude Code chat) → Intent widened from printing the plan to printing it, running each test step and reporting the exceptions; Scope adds the runner, its report, sorted failures, script-written red and green lines, reuse on unchanged code and the last run kept in git and older runs out of it, the baseline in the change's folder; the Out line on running steps narrowed; REQ-ORC-009 modified (the baseline step, row B9); REQ-EVD-007 to REQ-EVD-011 added (run a step and report, the baseline, reuse, red and green lines, refusals); Known gaps added and updated; capability evidence=EVD added; the Critic's amendment A1 review (23 findings, Q1-Q5) applied
- A2 2026-11-17: the design (Architect, design.md Questions Q1-Q5) found five cases the spec didn't cover; the operator answered "1 A, 2 A, 3 A, 4 A, 5 A" (Claude Code chat) → baseline.txt's commit is `none` outside git or before the first commit, and no reuse then (EVD-008.B2, EVD-009.N2); --red and --green insert a missing red or green line after test: (EVD-010.B4); a skipped test is refused by --red and --green (EVD-010.N9); a reused run counts as the run for --red, --green and baseline, with its time (EVD-008.B3, EVD-010.B5); an empty `- Test report:` line reads as none (EVD-007.N7); then the failure-mode review's spec gaps, answered "1 A, 2 A, 3 A, 4 A" (operator, 2026-11-17, Claude Code chat): a `Test report:` path that names a tracked file or a folder, or leads outside through a symlink, is refused (EVD-011.N19-N21); run-plan shows "- baseline: none (the design has no \"Test report:\" line)" (ORC-009.B10); a red message holding a comment marker or `(after T` is written as "red: failed" (EVD-010.B6); a task with two red or green lines is refused (EVD-010.N10); seven Known gaps added (concurrent runs, duplicate names, output size, runner artifacts, test-line filling, platforms, names with spaces)
- A4 2026-11-24: verification F2, F3, F4; the operator answered "F2 B, F3 A, F4 A" (Claude Code chat) → REQ-EVD-010.B7 (an existing tasks.md keeps its mode), REQ-EVD-009.B8 (a changed Test command is not reused), three Known gaps (F2; the rest of F4; a new file's mode)

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
| spec | 2026-11-04 | Operator in Claude Code chat, 2026-11-04: "/sdd approve spec" (reply to "Approve this spec?" for 0008-run-plan after Critic rounds 1 and 2) |
| amend | 2026-11-17 | Operator in Claude Code chat, 2026-11-17: "approve amendment A1" (reply to "Do you approve amendment A1?" for 0008-run-plan after the Critic's A1 review, 23 findings applied, Q1-Q5 answered) |
| amend | 2026-11-17 | Operator in Claude Code chat, 2026-11-17: "approved" (reply to "Do you approve amendment A2?" for 0008-run-plan: the Architect's Q1-Q5 answered 1 A-5 A and the failure-mode review's gaps answered 1 A-4 A) |
| plan | 2026-11-17 | Operator in Claude Code chat, 2026-11-17: "/sdd approve" (reply to "Do you approve this plan?" for 0008-run-plan: 24 tasks over 110 scenarios, refusals grouped by guard, mutation entries added per rule at green) |
| amend | 2026-11-25 | Operator in Claude Code chat, 2026-11-25: "/sdd aprove" (amendment A4 to 0008: REQ-EVD-010.B7, REQ-EVD-009.B8 and three Known gaps, after "F2 B, F3 A, F4 A") |
| results | 2026-11-25 | Operator in Claude Code chat, 2026-11-25: "/sdd approve" (results of 0008 after verification pass 2, PASS) |
