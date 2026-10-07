---
id: {{id}}
title: {{title}}
type: {{type}}
size: mini
assurance: {{assurance}}
status: draft
capabilities: {{capabilities}}
created: {{date}}
---

# {{id}} — {{title}}

## Intent
<!-- Spec Author: why this change, for whom, and the outcome. Use the operator's
words. No technology choices. 2–5 lines. -->

## Scope
- In:
- Out:

## Requirements
<!-- Spec Author: one block per requirement. Grammar: method/format.md.

### REQ-CHK-001 Guest can pay without an account
When a visitor without a session submits a valid cart and email address,
the checkout service shall create a paid order and queue a confirmation email.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a cart with 2 in-stock items, no session | the visitor pays with "a@b.c" | an order is "paid" · an email is queued to "a@b.c" |
| N1 | validation | a valid cart, no session | the visitor submits email "abc" | error "invalid email" · no order · no charge |

- N/A access: guest flow has no identity; abuse is covered by REQ-SEC-002

Get the next free ID with `sdd.py next-req <PREFIX>`. -->

## Known gaps
<!-- Behavior this change deliberately does not handle, one line each.
Required at `prototype` (write "- None" if there are none). Optional otherwise. -->

## Design notes
<!-- Planner: just enough "how" for a small change: modules touched, approach,
test strategy. Keep the test command line. -->
- Test command:

## Tasks
<!-- Planner: one task per scenario; schedule each negative next to its happy path.

- [ ] T1 REQ-CHK-001.S1 Guest pays for a cart
  - test:
  - red:
  - green:

Implementer: fill test/red/green while working, then tick the box. -->

## Verification
<!-- Verifier: commands run, results, coverage, findings, verdict. -->

## Open questions
<!-- Mark unknowns where they occur as [NEEDS CLARIFICATION: question] and list them here. -->

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
