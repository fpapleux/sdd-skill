---
id: 0003-design-depth-analyze-next
title: Design depth, analyze and next
type: feature
size: standard
assurance: production
status: archived
capabilities: analysis=ANL, orchestration=ORC
created: 2026-10-20
spec_hash: 155db3e34952
---

# 0003-design-depth-analyze-next — Design depth, analyze and next

<!-- A standard change is this folder: proposal.md (this file), spec-delta.md,
design.md, tasks.md and verification.md. sdd.py reads them as one spec.
Gates: spec (locks Intent, Defect, Scope, Requirements, Known gaps) → plan → results. -->

## Intent
v1 increment 5 (roadmap, `sdd-skill-study.md` §13): "`design` + Architect,
`analyze`, `next`: design, contracts, and the failure modes the design
introduces (returned as scenarios); cross-artifact consistency; run to the
next gate." For the operator, who today approves a plan without a machine
check that the spec, design and tasks agree, and who drives each phase by
hand. The outcome: a design that surfaces the failure points it adds, a
consistency check that runs before the plan gate, and one command that carries
a change as far as the next approval.

## Scope
- In: the Architect lists the failure modes the design introduces (a queue, a cache, a third-party call, a migration) in `design.md`, and each one is answered by a scenario in the spec or recorded as not applicable with a reason. A failure mode the locked spec doesn't cover goes to the operator through `amend`, never into the design quietly.
- In: `design.md` can name the contracts of new interfaces; `check` validates the section it defines. A contract is a `## Contracts` section with one entry per new interface (inputs, outputs, errors); `check` requires only that every interface the design lists has an entry (Q1).
- In: `sdd analyze`, a read-only cross-artifact check before the plan gate. It prints the plan-stage `check` findings and adds: the design's trace to the requirements, the failure-mode entries and their outcomes, a heuristic warning for requirement clauses no scenario exercises, and a happy-heavy balance warning. The plan gate refuses while it reports an error (Q4).
- In: `sdd next`, which lists the steps to the next gate, putting the step that fixes a problem first, and a `status` next line at designed that points to `analyze`. The script's `next` prints the ordered remaining steps up to the next gate; the method tells the agent to execute them in turn, and `status` stays the one-line summary (Q3).
- In: the method files for the `design` and `analyze` phases and the Architect's failure-mode review as a strong-tier read-only subagent (increment 4's tiers), with the fresh session as the fallback in Codex.
- Changes existing behavior: `status` at designed with tasks and a clean check said "awaiting operator approval of the plan: sdd approve" → now "sdd analyze, then ask for plan approval"; `approve plan` refuses on `analyze` errors that `check` doesn't report.
- Existing changes: a change still at designed must add a Failure modes section before plan approval at production; changes past the plan gate see the design-trace and failure-mode findings in `analyze` only, and contract findings in `check` from the plan stage on (no change has interface lines today); archived specs and `mini` changes are unaffected (project rule 5).
- Out: judging contradictions between artifacts, and constitution violations beyond what `check` already reports (the Spec Critic and the Architect do that).
- Out: separate contract files under `contracts/` (`full` size, v3).
- Out: delivery profiles, install options, release and deploy design (increment 6, operator, 2026-10-20).
- Out: blocking diff coverage and the adversarial probe (increment 7), and `harden` (increment 8).
- Out: the `full` size and its separate design gate and decision records (v3).
- Out: the other friction items recorded after change 0001 (unknown-heading warning, "proposed, not yet applied" outcome, per-question open-question count, the `amend` from `verifying` note).
- Out: dogfood run 3, which follows this increment as its own step.

## Open questions
<!-- Mark unknowns where they occur as [NEEDS CLARIFICATION: question]; log
answers here as "- <question> → <answer> (operator, <date>)". -->
- Q1 What is a contract, and how much does `check` validate? → A: a `## Contracts` section in `design.md`, one entry per new interface; `check` requires only that every listed interface has an entry. To be revisited after v1 (operator, 2026-10-20)
- Q2 Is clause coverage in `analyze` in this increment? → A: yes, as a heuristic warning, not a blocking error (operator, 2026-10-20)
- Q3 What does the script's `next` do? → A: prints the ordered remaining steps up to the next gate; the method says to execute them in turn (operator, 2026-10-20)
- Q4 Does the plan gate refuse on analyze errors? → A: yes; analyze is a real gate before the plan is approved (operator, 2026-10-20)
- Q5 Do the design-trace and failure-mode errors apply at prototype? → A: yes, unchanged; a Failure modes section that is written must be well formed (operator, 2026-10-20)
- R1Q1 What does next print while there are check errors or unanswered questions? → B: the phase that fixes them is listed first (operator, 2026-10-20, Critic round 1)
- R1Q2 May a failure-mode outcome be a living-spec scenario? → B: a scenario of the change or of the living spec, checked to exist (operator, 2026-10-20, Critic round 1)
- R1Q3 How strict is the Failure modes section? → A: strict, every bullet is an FM entry or a single None line (operator, 2026-10-20, Critic round 1)
- R1Q4 What does next print for a mini change past the plan gate? → B: it stops after verify, with a gate line for the operator's review before archive (operator, 2026-10-20, Critic round 1)
- R1Q5 Should status's next at designed account for analyze? → B: yes, "sdd analyze, then ask for plan approval" (operator, 2026-10-20, Critic round 1)
- F13 Keep contract well-formedness rules beyond presence (nameless interface line, repeated entry, unlisted entry)? → keep them, like the Failure modes rule in Q5 (operator, 2026-10-20, Critic round 1)
- R2Q1 What does next print at verifying with a GAPS verdict? → B: no step, and a gate for the operator's decision on the gaps (operator, 2026-10-20, Critic round 2)
- R2Q2 What does next print for a mini change at verified, or at verifying with PASS? → A: no step, and the gate where the operator reviews the verification before archive (operator, 2026-10-20, Critic round 2)
- R2Q3 What does next print while the constitution has changed? → B: one line, no step and no gate line (operator, 2026-10-20, Critic round 2)
- R3Q1 What does next print for a mini change at verifying with a GAPS verdict? → A: same as standard, no step and a gate for the operator's decision (operator, 2026-10-20, Critic round 3)
- R3Q2 What does next print when the spec was edited but no Amendments entry is logged? → B: '1. sdd amend' first, then the amendment gate line (operator, 2026-10-20, Critic round 3)

## Amendments
<!-- Spec changes after the spec gate, one line each, then `sdd.py approve amend`:
- A1 2026-10-08: <reason> → <what changed> -->
- A1 2026-10-20: the Architect found three edge cases of `next` the spec doesn't decide → REQ-ORC-004: a status outside the change's size gives exit 1 (N15 added, statement extended); two known gaps added (Critic-round errors that leave `next` on a refusing gate; tier-line and task-parse errors counted as spec errors)
- A2 2026-10-21: the Verifier's round 1 (GAPS) found code that differs from the spec text, and the operator decided: A for F2, F3, F4, F5, B for F6, F7, F8, F9, F11 → REQ-ANL-001.B3 (a mini change past the plan gate has no design finding), REQ-ANL-003.N16 (a failure mode with no text before its arrow) and N17 (a None line with no separator), REQ-ORC-005.N8 (a plan error at standard designed lists `sdd tasks`); five known gaps added

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
| spec | 2026-10-20 | Operator in Claude Code chat, 2026-10-20: chose 'Approve the spec' for 0003-design-depth-analyze-next (11 requirements, 3 Critic rounds, 0 open questions) |
| amend | 2026-10-20 | Operator in Claude Code chat, 2026-10-20: chose 'Approve A1' (REQ-ORC-004 unknown-status rule and N15, two Known gaps) |
| plan | 2026-10-20 | Operator in Claude Code chat, 2026-10-20: chose 'Approve the plan' for 0003-design-depth-analyze-next (136 tasks, 54 mutations) |
| amend | 2026-10-21 | Operator in Claude Code chat, 2026-10-21: "Approve amendment A2. Record it with sdd approve amend, then continue." (A2: REQ-ANL-001.B3, REQ-ANL-003.N16, N17, REQ-ORC-005.N8; five known gaps) |
| results | 2026-10-21 | Operator in Claude Code chat, 2026-10-21: "Approve the results of 0003-design-depth-analyze-next. Record it with sdd approve results, then archive." (round 2 verdict PASS: 439 tests, replay 146 confirmed, mutate 158 caught) |
