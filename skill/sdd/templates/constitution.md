---
assurance: {{assurance}}
approved: no
---

# Constitution

Non-negotiable rules for this project. Every SDD phase checks against them.
The operator approves this file and every change to it.

## Assurance level: `{{assurance}}`

{{assurance_meaning}}

This is set once for the project. A single change may raise its own level
(for example, payment code inside an internal tool). Lowering it needs a
recorded operator waiver.

## Article 1 — Test-first

No production code without a failing test that names the scenario it proves
(e.g. `test_REQ_CHK_007_S1_guest_pays`). Every task records its failing (red)
run and its passing (green) run. At `prototype`, this applies to happy-path
scenarios.

## Article 2 — Negative coverage

Every requirement covers the failure categories its assurance level requires,
or records `N/A <category>: <reason>`. At `prototype`, every change keeps a
Known gaps list instead.

## Article 3 — The spec is the contract

Behavior changes only through an approved change in `specs/changes/`. If
implementation shows the spec is wrong or incomplete, work stops and the
operator decides.

## Project rules
<!-- Add project-specific rules here: stack, dependency policy, supported
platforms, naming. Keep this file under one page. -->

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
