---
assurance: production
approved: yes
---

# Constitution

Non-negotiable rules for this project. Every SDD phase checks against them.
The operator approves this file and every change to it.

## Assurance level: `production`

External users or business data that must persist. The six core failure categories are covered, and review and verification are independent.

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

1. **What gets specified.** Requirements describe the observable behavior of
   `sdd.py`: CLI output, exit codes and the files it writes. Changes to
   `SKILL.md`, `method/` and `templates/` are design work, verified by review
   and a dogfood run until evals exist.
2. **Stack.** `sdd.py` uses the Python 3.8+ standard library only, with no
   third-party dependencies. Test command: `python3 -m unittest tests.test_sdd`.
3. **Portability.** `SKILL.md` frontmatter is limited to name, description,
   license and metadata. No host-specific prompt preprocessing; all state in
   files; it must work in Claude Code and Codex.
4. **Mutation check.** Before merge, every new or changed `sdd.py` rule is
   broken on purpose once, and the test suite must catch it.
5. **Backward compatibility.** Specs written by earlier versions keep working.
   A change to the spec grammar states how existing specs are handled.
6. **Public repository hygiene.** No private hosts, IP addresses, personal
   names, local paths or internal process names in any committed file.
7. **Pinned tool.** The installed skill is a pinned checkout of `main`,
   separate from the development checkout. A change is never developed with
   the tool pointing at the code being changed.
8. **Delivery.** One PR per increment, from `v1` into `main`. The operator
   decides when to merge.

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
| constitution | 2026-10-09 | Operator in Claude Code chat, 2026-10-09: "/sdd approve" (constitution at production with project rules 1–8 as proposed) |
