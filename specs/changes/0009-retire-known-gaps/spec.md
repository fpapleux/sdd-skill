---
id: 0009-retire-known-gaps
title: A change retires the known gaps it resolves
type: feature
size: mini
assurance: production
status: draft
capabilities: archive=ARC
created: 2026-11-02
---

# 0009-retire-known-gaps — A change retires the known gaps it resolves

## Intent
<!-- Spec Author: why this change, for whom, and the outcome. Use the operator's
words. No technology choices. 2–5 lines. -->

`archive` adds known gaps to the living spec and never removes one, so a gap
that a later change resolves stays listed as if it were still open. After
0007 lands, the `evidence` and `defects` specs will still say a failing test
outside the change "needs a baseline (follow-up change)". For the operator,
who reads the living spec as the truth. The outcome: a change can name the
living gaps it resolves, and archiving it removes them, with a record of why.

## Scope
- In: a change lists the living known gaps it resolves, each by its capability and its text as the living spec has it. The list is part of the spec, so it is locked at approval like Known gaps.
- In: `archive` removes each listed gap from that capability's Known gaps and adds to the Change history line that the gap was retired by the change.
- In: a listed gap that isn't in the living spec as written [NEEDS CLARIFICATION: what happens to a listed gap the living spec doesn't have? A) check reports it as an error from the spec stage, and archive refuses or B) archive skips it with a warning]
- In: which capabilities a change may retire gaps from [NEEDS CLARIFICATION: may a change retire a gap from a capability it doesn't touch with a requirement? A) yes, any capability, since a gap can be resolved by work recorded elsewhere or B) only the capabilities the change touches]
- Existing changes (project rule 5): a change without the list archives exactly as before; archived changes and their gaps are unaffected.
- Out: retiring the stale gaps themselves: the gaps 0005 left ("needs a baseline", once 0007 lands) and those 0002 and 0003 copied into every capability (a 0004 known gap) are retired by a change archived with a pinned tool that has this rule (project rule 7), not by this change.
- Out: editing or rewording a living gap; removing one by hand.
- Out: detecting that a gap is resolved; the change says so and the operator approves it.

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
test strategy. Keep the test command line; "Test one" runs a single test
for sdd replay and sdd mutate, e.g. `python3 -m unittest {name}`. "Test
component" runs the tests of one capability at a checkpoint; `{prefix}` stands
for its requirement prefix, e.g. `python3 -m unittest -k REQ_{prefix}_`. -->
- Test command:
- Test one:
- Test component:

## Tasks
<!-- Planner: one task per scenario; schedule each negative next to its happy path.

- [ ] T1 REQ-CHK-001.S1 Guest pays for a cart
  - tier: mid
  - test:
  - red:
  - green:

Implementer: fill test/red/green while working, then tick the box.
When the constitution asks for a mutation check, add a "## Mutations"
section after the tasks (format: method/format.md). -->

## Verification
<!-- Verifier: commands run, results, coverage, findings, verdict. -->

## Open questions
<!-- Mark unknowns where they occur as [NEEDS CLARIFICATION: question] and list them here. -->

## Clarifications
<!-- Spec Critic: one round per review, started with `sdd.py round`. Format:
method/format.md. Required before the gate at production and above. -->

## Amendments
<!-- Spec changes after approval, one line each, then `sdd.py approve amend`:
- A1 2026-10-07: <reason> → <what changed> -->

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
