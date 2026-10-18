---
id: 0002-subagent-fanout
title: Subagent fan-out: prime orchestrator, role tiers, scripted verification evidence
type: feature
size: standard
assurance: production
status: archived
capabilities: orchestration=ORC, evidence=EVD
created: 2026-10-14
spec_hash: b86e2172a5d1
---

# 0002-subagent-fanout — Subagent fan-out: prime orchestrator, role tiers, scripted verification evidence

<!-- A standard change is this folder: proposal.md (this file), spec-delta.md,
design.md, tasks.md and verification.md. sdd.py reads them as one spec.
Gates: spec (locks Intent, Defect, Scope, Requirements, Known gaps) → plan → results. -->

## Intent
Use subagents to detail intents, tasks, develop and verify, because "use of
subagents will create more adoption and performance" (operator, 2026-10-14).
Some tasks are simpler and more repetitive than others, so they can run on
cheaper models at a lower effort, while a prime model orchestrates. Work that
needs no judgment shouldn't need a model at all: in change 0001 most of each
verification round (about 180k tokens and 14–17 minutes) was mechanical
replay and mutation, done by hand. The outcome: independent review without
the operator opening a new chat, lower cost per change, and the same proof.

## Scope
- In: a prime model orchestrates every phase: it keeps the conversation with the operator, the gates and the routing, and delegates drafting, critique, implementation, verification and stewardship to subagents.
- In: each role declares a tier (strong, mid or light), an effort level and whether it is read-only, in a tool-neutral form; the method maps each tier to a Claude model, which the orchestrator passes when it spawns a general-purpose subagent. No agent files are installed (Q3), so read-only is an instruction to the subagent, not enforced by the host.
- In: the Spec Critic and the Verifier run as read-only subagents in a fresh context; a fresh session stays the fallback where subagents aren't available (Codex).
- In: the Planner gives each task a tier; a task moves up one tier after two failed attempts.
- In: the review records (Critic rounds, Verification) say how the review ran (subagent, fresh session or same session) and on which tier, and the check treats a strong-tier subagent as independent at production and above (Q6).
- In: sdd.py produces the mechanical verification evidence: it replays the change's tests against the base revision and compares the result with each task's red or pre-existing claim, running one test at a time through a per-test command template given in the design (Q2), and it runs the mutations the Planner lists for each new or changed rule (Q1) and reports which ones the suite catches.
- Out: blocking diff coverage and the adversarial probe (increment 7).
- Out: proving which model actually ran; the runner and tier are recorded, not verified, like approval rows.
- Out: running tasks in parallel worktrees.
- Out: agent definition files for any host, including Codex (Codex keeps the fresh-session fallback), and plugin or marketplace packaging (v3).
- Out: mutants generated automatically by sdd.py.
- Out: token budgets or cost limits enforced by the script.

## Open questions
<!-- Mark unknowns where they occur as [NEEDS CLARIFICATION: question]; log
answers here as "- <question> → <answer> (operator, <date>)". -->
- Q1 Who decides what gets mutated? → A: the Planner lists a mutation per new or changed rule (file, original, replacement, the test that should catch it); sdd.py runs them (operator, 2026-10-14)
- Q2 How does replay run one test in any language? → A: a per-test command template in the design, e.g. `python3 -m unittest {test}` (operator, 2026-10-14)
- Q3 How does Claude Code get the Critic and Verifier subagents? → A: no agent files; the orchestrator spawns general-purpose subagents with the model for the tier, read-only by instruction (operator, 2026-10-14)
- Q4 Which tests decide whether a mutation is caught? → A: only the test of the task that plans the mutation's scenario, which is stricter than rule 4's whole suite and proves that test pins the rule (operator, 2026-10-14)
- Q5 How is a twice-escalated tier written? → A: a chain such as "light → mid → strong", each step exactly one tier up; the task counts as the last tier (operator, 2026-10-15, Critic round 1)
- Q6 Which subagent counts as an independent Critic or Verifier at production? → B: a strong one only (operator, 2026-10-15, Critic round 1)
- Q7 Which current files does replay lay over the base copy? → A: every test file, tracked or untracked and not ignored (operator, 2026-10-15, Critic round 1)
- Q8 How are find and replace texts written? → A: between the line's first and last backtick, verbatim; an empty replace deletes (operator, 2026-10-15, Critic round 1)
- Q9 What do usage errors return? → A: exit 2 with argparse's message, like the other options (operator, 2026-10-15, Critic round 1)

## Amendments
<!-- Spec changes after the spec gate, one line each, then `sdd.py approve amend`:
- A1 2026-10-08: <reason> → <what changed> -->
- A1 2026-10-17: the dogfood replay of this change reported 10 false mismatches, because red and pre-existing claims are recorded when each test is written, after earlier tasks' code, not against the change's base → REQ-EVD-001: a task whose red line contains "(after T<n>)", naming an earlier task, depends on it and is checked only in the working tree ("confirmed now (depends on T<n>)"); S3, S4, N11, B5, B6 added; known gap added

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
| spec | 2026-10-15 | Operator in Claude Code chat, 2026-10-15: "/sdd approve" (spec after Critic round 1, fresh session, Q5–Q9 answered) |
| plan | 2026-10-17 | Operator in Claude Code chat, 2026-10-17: "/sdd approve" (plan: design.md and 64 tasks in tasks.md) |
| amend | 2026-10-17 | Operator in Claude Code chat, 2026-10-17: "/sdd approve" (amendment A1: replay dependency marker "(after T<n>)", REQ-EVD-001 S3, S4, N11, B5, B6, known gap) |
| results | 2026-10-18 | Operator in Claude Code chat, 2026-10-18: "Approve the results: run sdd approve results with my words as evidence." (verdict PASS, 290 tests, replay 68 confirmed, mutate 49 caught) |
