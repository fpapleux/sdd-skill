---
id: 0006-blocking-defects
title: Open defects block the verify gates
type: feature
size: mini
assurance: production
status: archived
capabilities: defects=DEF
created: 2026-10-30
spec_hash: fba0758eaed7
---

# 0006-blocking-defects — Open defects block the verify gates

## Intent
<!-- Spec Author: why this change, for whom, and the outcome. Use the operator's
words. No technology choices. 2–5 lines. -->

Since 0.19.0, failures are recorded as defects and triaged with the operator,
"so that critical ones are fixed and the rest are accounted for", but no
defect stops a change: its results can be approved and it can be archived
while a critical defect it recorded is still open. For the operator, who runs
large programs with SDD. The outcome: "only non-minor defects block". A change
can't pass its verify gates while it has an open critical or major defect
that the operator hasn't put off (later) or accepted (won't fix).

## Scope
- In: `approve results` (standard), `advance verified` (including a return from blocked, Q2) and `archive` refuse while the change has a blocking defect: a defect it recorded (its Change cell names the change) that is open, critical or major, and decided neither later nor wont-fix. Undecided and fix-now both block; minor never blocks (0005 Q1, Q5 and R1Q1, operator, 2026-10-28).
- In: the refusal names each blocking defect with its severity and decision, and says how to clear it, e.g. "D1 (critical, fix-now) is open: close it, or decide later or wont-fix, first" (0005 round 2 F3). Nothing is written when a gate refuses.
- In: `check --stage verify` reports each blocking defect as an error, so the operator sees it before the gate.
- In: an invalid specs/defects.md (REQ-DEF-006) refuses the same three gates, because the gate can't show that nothing blocks (Q1); this matches `check --stage verify`, which already reports it as an error.
- Changes existing behavior: an open critical or major defect didn't stop results approval, advance verified or archive → it does, unless it is decided later or wont-fix; an invalid specs/defects.md didn't stop them either → it does.
- Existing changes (project rule 5): a project with no specs/defects.md, or whose log has no blocking defect of the change, behaves as before; archived changes are unaffected.
- Out: a defect recorded by another change, or a defect blocking a change other than the one that recorded it.
- Out: blocking the spec or plan gates; `next` and `status` stay as they are (they already count open defects).
- Out: checking that a closed defect's test now passes; close keeps taking the agent's evidence, like approval rows.
- Out: changing a defect's severity after it is added.

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

### REQ-DEF-007 A blocking defect refuses the verify gates
When `sdd.py approve results` (standard), `sdd.py advance verified` (from verifying or back from blocked) or `sdd.py archive` is run on a change that has a blocking defect, a row of a valid specs/defects.md whose Change cell is the change's ID and which is open, critical or major, and undecided or decided fix-now, sdd.py shall exit 1, print for each blocking defect, in the log's order, `D<n> (<severity>, <decision>) is open: close it, or decide later or wont-fix, first`, and change no file; this is the only refusal shown, checked right after the gate's argument, size and status checks and before the verify check, the verdict and archive's destination check; a minor or closed defect, one decided later or wont-fix, and one whose Change cell names another change never block, and no other approve or advance is refused because of the defects.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a standard change 0007-x in verifying, verify check OK, "Verdict: PASS", a log with D1 open, critical, later and D2 open, major, wont-fix, both of 0007-x | approve results | exit 0 · status verified · one results row · specs/defects.md is byte-for-byte unchanged |
| S2 | happy | a mini change 0007-x in verifying, verify check OK, "Verdict: PASS", a log with D1 closed, critical, fix-now, of 0007-x | advance verified | exit 0 · status verified (a closed defect never blocks) |
| S3 | happy | a verified mini change 0007-x and the S1 log | archive | exit 0 · the change is in specs/archive/0007-x |
| N1 | state | the S1 change and a log with D1 open, critical, fix-now, of 0007-x | approve results | exit 1 · the output has "D1 (critical, fix-now) is open: close it, or decide later or wont-fix, first" · status stays verifying · no results row · specs/defects.md is byte-for-byte unchanged |
| N2 | state | the S2 change and a log with D1 open, major, undecided, of 0007-x | advance verified | exit 1 · the output has "D1 (major, undecided) is open: close it, or decide later or wont-fix, first" · status stays verifying · spec.md is byte-for-byte unchanged |
| N3 | state | a verified mini change 0007-x and a log with D1, added after verified, open, critical, undecided, of 0007-x | archive | exit 1 · the output has "D1 (critical, undecided) is open: …" · status stays verified · the change stays in specs/changes · spec.md is byte-for-byte unchanged · no capability spec is written · specs/defects.md is byte-for-byte unchanged |
| N4 | state | a verified standard change 0007-x whose verify check fails (its test file no longer names a scenario) and a log with D1 open, critical, fix-now, D2 open, minor, undecided and D3 open, major, fix-now, all of 0007-x | archive | exit 1 · the output is only the D1 and D3 lines: D1, then "D3 (major, fix-now) is open: …" (no "verify check fails") · it doesn't name D2 · status stays verified · the change stays in specs/changes · spec.md is byte-for-byte unchanged · no capability spec is written · specs/defects.md is byte-for-byte unchanged |
| N5 | state | the N1 setup, then defect decide D1 later --evidence "After the demo" | approve results | exit 0 · status verified (deciding later clears the block) |
| N6 | state | the N1 setup, with T1 left unticked (the verify check fails) and the latest line "Verdict: GAPS — F1" | approve results | exit 1 · the output is only the D1 refusal "D1 (critical, fix-now) is open: …" (no "verify check fails", no "GAPS") · status stays verifying · no results row |
| N7 | state | a mini change 0007-x blocked from verified (blocked_from: verified), with T1 left unticked (the verify check fails), the latest line "Verdict: GAPS — F1", a log with D1 open, critical, undecided, of 0007-x | advance verified | exit 1 · the output is only the D1 refusal "D1 (critical, undecided) is open: …" (no "verify check fails", no "GAPS") · status stays blocked · spec.md is byte-for-byte unchanged |
| B1 | boundary | the S2 change and no specs/defects.md | advance verified | exit 0 · status verified · no specs/defects.md is created |
| B2 | boundary | the S1 change and a log with D1 open, minor, undecided and D2 open, minor, fix-now, both of 0007-x | approve results | exit 0 · status verified (minor never blocks) |
| B3 | boundary | the S1 change and a log with D1 open, critical, fix-now, of 0008-y | approve results | exit 0 · status verified (another change's defect doesn't block) |
| B4 | boundary | a mini draft 0007-x ready for plan approval and a log with D1 open, critical, undecided, of 0007-x | approve plan, then advance implementing | exit 0 each time · status implementing (the plan gate and other moves aren't refused because of defects) |
| B5 | boundary | the N2 setup | advance implementing | exit 0 · status implementing (the way back to fix a defect isn't refused) |

- N/A validation: the gates take no new argument; a log whose rows aren't valid is covered by REQ-DEF-008
- N/A dependency: a missing log is B1; a log that can't be read as rows is covered by REQ-DEF-008
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

### REQ-DEF-008 An invalid defect log refuses the verify gates
If specs/defects.md isn't valid (REQ-DEF-006) when `sdd.py approve results`, `sdd.py advance verified` or `sdd.py archive` is run, then sdd.py shall exit 1, print the problem as REQ-DEF-006 names it (specs/defects.md, the line number and the problem) and change no file, even when no row names the change; as in REQ-DEF-007, this is the only refusal shown, checked right after the gate's argument, size and status checks; no other approve or advance is refused because of the log.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| N1 | dependency | the REQ-DEF-007.S1 change and a log whose row D1, on line 5, has the severity blocker | approve results | exit 1 · the output is only that problem, naming specs/defects.md, line 5 and "blocker" · status stays verifying · no results row · specs/defects.md is byte-for-byte unchanged |
| N2 | dependency | the REQ-DEF-007.S2 change and the N1 log | advance verified | exit 1 · the N1 problem · status stays verifying · spec.md is byte-for-byte unchanged |
| N3 | dependency | a verified mini change 0007-x and a log with two rows D1, both of 0008-y | archive | exit 1 · the output says D1 is repeated · status stays verified · the change stays in specs/changes · spec.md is byte-for-byte unchanged · no capability spec is written · specs/defects.md is byte-for-byte unchanged |
| B1 | boundary | the REQ-DEF-007.B4 draft and the N1 log | approve plan | exit 0 · status planned (an invalid log refuses only the verify gates) |
| B2 | boundary | the REQ-DEF-007.S2 change and the N1 log | advance implementing | exit 0 · status implementing (no other advance is refused because of an invalid log) |

### REQ-DEF-009 check lists the blocking defects at the verify stage
When `sdd.py check` runs at the verify stage (`--stage verify`, or without `--stage` on a change in verifying or verified), sdd.py shall report each blocking defect of the change (REQ-DEF-007) as an error with the REQ-DEF-007 text, in the log's order, and exit 1; at the other stages it reports none of them, and the open defects line and `defects` key of REQ-DEF-004 are unchanged.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a mini change 0007-x in verifying, otherwise clean, a log with D1 open, critical, later, D2 open, minor, undecided and D3 closed, critical, fix-now, of 0007-x, and D4 open, critical, fix-now, of 0008-y | check --stage verify | exit 0 · no error names a defect · "open defects: 3 (2 critical, 1 undecided)" · no file is changed |
| N1 | state | the S1 change and a log with D1 open, critical, fix-now and D2 open, major, undecided, of 0007-x | check --stage verify | exit 1 · the errors "D1 (critical, fix-now) is open: close it, or decide later or wont-fix, first" and "D2 (major, undecided) is open: …", in that order · check --json's errors hold each of the two lines exactly once · no file is changed |
| B1 | boundary | the N1 setup | check, without --stage | exit 1 · the N1 errors (the stage is verify) · no file is changed |
| B2 | boundary | the N1 log, naming an otherwise clean standard change 0007-x at designed | check --stage plan | exit 0 · no error names a defect · "open defects: 2 (1 critical, 1 undecided)" · no file is changed |

- N/A validation: check takes no new argument; a log whose rows aren't valid is covered by REQ-DEF-006
- N/A dependency: a missing log gives no defect error (REQ-DEF-004.B1); an invalid one is REQ-DEF-006.N2
- N/A access: sdd.py runs locally with no users or roles; who may run it is governed by the agent rules

## Known gaps
<!-- Behavior this change deliberately does not handle, one line each.
Required at `prototype` (write "- None" if there are none). Optional otherwise. -->
- A defect blocks only the change its Change cell names, as written: a defect recorded under another change, a mistyped ID or an archived change blocks nothing.
- Closing a blocking defect or deciding it later or wont-fix clears the block on the agent's evidence; close doesn't check that the defect's test now passes.
- status and next count the open defects but don't name the blocking ones; check at the verify stage and the three gates do.

## Design notes
- Files: `skill/sdd/scripts/sdd.py` (the gates, `defect_findings`, one new gate helper) and `tests/test_sdd.py` (new classes `DefectBlockTests`, `DefectLogGateTests`, `DefectCheckTests`).
- **One helper, `defect_gate(project, change_id)`**, next to `read_defect_log`. It reads the log once. A `log.problem` raises `SddError(log.problem)` (REQ-DEF-008); else it collects the blocking rows with `blocking_defects(log, change_id)` and raises one `SddError` with a line per defect, in the log's order (REQ-DEF-007). A missing log has no rows and no problem, so it passes and creates nothing (B1).
- **`blocking_defects(log, change_id) -> list[str]`**: rows whose Change cell (`row["cells"][5]`) equals the change ID, status `open`, severity `critical` or `major`, decision `undecided` or `fix-now`; each text is `D<n> (<severity>, <decision>) is open: close it, or decide later or wont-fix, first`. The same function feeds the gates and check, so the two texts can't drift (REQ-DEF-009).
- **Where the gates call it**: `cmd_approve` (results branch, right after the `verifying` check), `cmd_advance` (first in the `target == "verified"` block, after the transition checks, so a return from blocked is gated too, REQ-DEF-007.N7) and `cmd_archive` (right after the `verified` check, before `analyze(...)` and the destination check). Each call comes before `analyze(...)` and the verdict, so the defect refusal is the only one shown and nothing is printed or written before it; one row per call site proves the position (REQ-DEF-007.N6 results, N7 advance, N4 archive, whose destination check comes after `analyze(...)`). The plan, spec, amend and other advance paths don't call it (REQ-DEF-007.B4, B5, REQ-DEF-008.B1, B2). `analyze()` still never reads the log (0005's decision): the helper is called by the three commands, not by `analyze()`.
- **`defect_findings`** (check and analyze) additionally appends `blocking_defects(log, report.change_id)` to `report.errors` when `report.stage == "verify"` and the log is valid; at other stages it adds none. `cmd_analyze` runs at the plan stage, so it is unaffected. The `defects` counts and line stay as they are.
- Test strategy: integration through `sdd.main()` with the `Repo` helper and `snapshot()` in a temporary folder, no subprocess and no test doubles; the log is a real file built with `defect_log(...)`. The changes under test are built like `VerdictMiniTests` and `VerifierRunnerTests.verifying` (verifying, verify check OK, Verdict PASS). Byte-for-byte checks compare the log's and spec's bytes before and after.
- Test command: `python3 -m unittest tests.test_sdd`
- Test one: `python3 -m unittest tests.test_sdd.{name}`
- Test component: `python3 -m unittest tests.test_sdd -k REQ_{prefix}_`
- Checkpoints: the one capability here, DEF, gives one component checkpoint, run by the Implementer when the last task ends.

## Tasks
<!-- Order exceptions. Where an "exit 0" scenario passes before its rule exists,
it comes after the negative that creates the rule, so its red run is real:
- REQ-DEF-007: N1 creates the helper and the results refusal, right after the
  status check; N2 and N3 wire advance verified and archive; N4 adds the order
  and the minor exclusion; S1 to S3, N5 to N7 and B1 to B5 follow and may
  already pass (`red: pre-existing (after T<n>)`).
- REQ-DEF-008: N1 to N3 create the invalid-log refusal; B1 and B2 follow.
- REQ-DEF-009: N1 creates the check errors; S1, B1, B2 follow. -->

- [x] T1 REQ-DEF-007.N1 Results approval refuses a critical fix-now defect
  - tier: strong
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N1_results_approval_refuses_a_critical_fix_now_defect
  - red: AssertionError: 0 != 1 : 0007-x: results approved → verified
  - green: Ran 1 test in 0.205s OK
- [x] T2 REQ-DEF-007.N6 Results approval shows only the defect refusal, before the verify check and the verdict
  - tier: light
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N6_results_approval_shows_only_the_defect_refusal_before_the_verify_check_and_the_verdict
  - red: pre-existing (after T1) — T1's call already sits before analyze() and the verdict, and the test asserts the whole output is the one D1 line
  - green: Ran 1 test in 0.625s OK
- [x] T3 REQ-DEF-007.S1 Later and wont-fix defects don't block results approval
  - tier: light
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_S1_later_and_wont_fix_defects_dont_block_results_approval
  - red: pre-existing (after T1) — T1's decision test lets later and wont-fix rows through, and the test asserts exit 0, status, one results row and the log's bytes
  - green: Ran 1 test in 0.257s OK
- [x] T4 REQ-DEF-007.N5 Deciding later clears the block
  - tier: light
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N5_deciding_later_clears_the_block
  - red: pre-existing (after T1) — T1's gate refuses the fix-now row (asserted first), and the decision test passes it once decided later
  - green: Ran 1 test in 0.299s OK
- [x] T5 REQ-DEF-007.N2 Advance verified refuses a major undecided defect
  - tier: mid
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N2_advance_verified_refuses_a_major_undecided_defect
  - red: AssertionError: 0 != 1 : 0007-x: verifying → verified
  - green: Ran 1 test in 0.168s OK
- [x] T6 REQ-DEF-007.N7 Advance verified back from blocked shows only the defect refusal, before the verify check and the verdict
  - tier: light
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N7_advance_verified_back_from_blocked_shows_only_the_defect_refusal_before_the_verify_check_and_the_verdict
  - red: pre-existing (after T5) — T5's call sits first in the verified branch, before analyze() and the verdict, and the test asserts the whole output is the one D1 line
  - green: Ran 1 test in 0.275s OK
- [x] T7 REQ-DEF-007.S2 REQ-DEF-007.B1 A closed defect or no log doesn't block advance
  - tier: light
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_S2_and_REQ_DEF_007_B1_a_closed_defect_or_no_log_doesnt_block_advance
  - red: pre-existing (after T5) — T5's gate runs on a mini advance and lets a closed row and a missing log through; the test asserts exit 0, status verified and no log created
  - green: Ran 1 test in 0.447s OK
- [x] T8 REQ-DEF-007.B5 Advance implementing from verifying isn't refused
  - tier: light
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_B5_advance_implementing_from_verifying_isnt_refused
  - red: pre-existing (after T5) — T5 calls the gate only when the target is verified, so advance implementing never reads the log
  - green: Ran 1 test in 0.146s OK
- [x] T9 REQ-DEF-007.N3 Archive refuses a defect added after verified
  - tier: mid
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N3_archive_refuses_a_defect_added_after_verified
  - red: AssertionError: 0 != 1 : specs/capabilities/duration/spec.md: added REQ-DUR-001
  - green: Ran 1 test in 0.232s OK
- [x] T10 REQ-DEF-007.S3 Archive passes with later and wont-fix defects
  - tier: light
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_S3_archive_passes_with_later_and_wont_fix_defects
  - red: pre-existing (after T9) — T9's call in archive lets later and wont-fix rows through; the test asserts exit 0 and the folder moved to specs/archive/0007-x
  - green: Ran 1 test in 0.311s OK
- [x] T11 REQ-DEF-007.N4 Archive shows only the blocking defects, in order and without the minor, before the verify check
  - tier: mid
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N4_archive_shows_only_the_blocking_defects_in_order_and_without_the_minor_before_the_verify_check
  - red: AssertionError: 'erro[77 chars]st\nD2 (minor, undecided) is open: close it, o…' != 'erro[77 chars]st\nD3 (major, fix-now) is open: close it, or …'
  - green: Ran 1 test in 0.352s OK
- [x] T12 REQ-DEF-007.B2 REQ-DEF-007.B3 Minor and other-change defects don't block
  - tier: light
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_B2_and_REQ_DEF_007_B3_minor_and_other_change_defects_dont_block
  - red: pre-existing (after T11) — T11's severity test lets minor rows through and T1's Change cell comparison skips another change's row; the test asserts exit 0 and status verified for each
  - green: Ran 1 test in 1.206s OK
- [x] T13 REQ-DEF-007.B4 The plan gate and other moves ignore defects
  - tier: light
  - test: tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_B4_the_plan_gate_and_other_moves_ignore_defects
  - red: pre-existing (after T1) — only the results, advance verified and archive paths call defect_gate, so approve plan and advance implementing never read the log
  - green: Ran 1 test in 0.103s OK
- [x] T14 REQ-DEF-008.N1 Results approval refuses an invalid log
  - tier: mid
  - test: tests/test_sdd.py::DefectLogGateTests.test_REQ_DEF_008_N1_results_approval_refuses_an_invalid_log
  - red: AssertionError: 0 != 1 : 0007-x: results approved → verified
  - green: Ran 1 test in 0.183s OK
- [x] T15 REQ-DEF-008.N2 Advance verified refuses an invalid log
  - tier: light
  - test: tests/test_sdd.py::DefectLogGateTests.test_REQ_DEF_008_N2_advance_verified_refuses_an_invalid_log
  - red: pre-existing (after T14) — T14's log.problem refusal sits in defect_gate, which T5's call in advance verified already runs
  - green: Ran 1 test in 0.222s OK
- [x] T16 REQ-DEF-008.N3 Archive refuses a repeated defect ID
  - tier: light
  - test: tests/test_sdd.py::DefectLogGateTests.test_REQ_DEF_008_N3_archive_refuses_a_repeated_defect_id
  - red: pre-existing (after T14) — T14's log.problem refusal sits in defect_gate, which T9's call in archive already runs
  - green: Ran 1 test in 0.269s OK
- [x] T17 REQ-DEF-008.B1 REQ-DEF-008.B2 The plan gate and advance implementing accept an invalid log
  - tier: light
  - test: tests/test_sdd.py::DefectLogGateTests.test_REQ_DEF_008_B1_and_REQ_DEF_008_B2_the_plan_gate_and_advance_implementing_accept_an_invalid_log
  - red: pre-existing (after T14) — the gate is called only by results approval, advance verified and archive, so approve plan and advance implementing never read the log
  - green: Ran 1 test in 0.210s OK
- [x] T18 REQ-DEF-009.N1 Check lists each blocking defect as an error
  - tier: mid
  - test: tests/test_sdd.py::DefectCheckTests.test_REQ_DEF_009_N1_check_lists_each_blocking_defect_as_an_error
  - red: AssertionError: 0 != 1 : check 0007-x (stage: verify, assurance: internal) result: OK
  - green: Ran 1 test in 0.251s OK
- [x] T19 REQ-DEF-009.S1 Check passes with only non-blocking defects
  - tier: light
  - test: tests/test_sdd.py::DefectCheckTests.test_REQ_DEF_009_S1_check_passes_with_only_non_blocking_defects
  - red: pre-existing (after T18) — T18's errors list only open critical or major rows decided undecided or fix-now of this change, so the S1 log adds none and the counts line is unchanged
  - green: Ran 1 test in 0.218s OK
- [x] T20 REQ-DEF-009.B1 REQ-DEF-009.B2 Check without a stage lists them; the plan stage doesn't
  - tier: light
  - test: tests/test_sdd.py::DefectCheckTests.test_REQ_DEF_009_B1_and_REQ_DEF_009_B2_check_without_a_stage_lists_them_the_plan_stage_doesnt
  - red: pre-existing (after T18) — a check without --stage picks verify for a verifying change, and T18 appends the errors only when the stage is verify
  - green: Ran 1 test in 0.296s OK

## Mutations
- M1 REQ-DEF-007.S2 skill/sdd/scripts/sdd.py
  - find: `change_id and r["status"] == "open"`
  - replace: `change_id and r["status"] != ""`
- M2 REQ-DEF-007.S1 skill/sdd/scripts/sdd.py
  - find: `r["decision"] in ("undecided", "fix-now")`
  - replace: `r["decision"] in ("undecided", "fix-now", "later", "wont-fix")`
- M3 REQ-DEF-007.B3 skill/sdd/scripts/sdd.py
  - find: `r["cells"][5] == change_id`
  - replace: `r["cells"][5] != ""`
- M4 REQ-DEF-007.B2 skill/sdd/scripts/sdd.py
  - find: `r["severity"] in ("critical", "major")`
  - replace: `r["severity"] in ("critical", "major", "minor")`
- M5 REQ-DEF-007.N4 skill/sdd/scripts/sdd.py
  - find: `for r in log.rows if r["cells"]`
  - replace: `for r in reversed(log.rows) if r["cells"]`
- M6 REQ-DEF-007.N1 skill/sdd/scripts/sdd.py
  - find: `        defect_gate(project, path.parent.name)`
  - replace: `        pass`
- M7 REQ-DEF-007.N2 skill/sdd/scripts/sdd.py
  - find: `        defect_gate(project, change_id)`
  - replace: `        pass`
- M8 REQ-DEF-007.N3 skill/sdd/scripts/sdd.py
  - find: `    defect_gate(project, change_id=change_id)`
  - replace: `    pass`
- M9 REQ-DEF-008.N1 skill/sdd/scripts/sdd.py
  - find: `    if log.problem:  # REQ-DEF-008`
  - replace: `    if False:  # REQ-DEF-008`
- M10 REQ-DEF-009.N1 skill/sdd/scripts/sdd.py
  - find: `    elif report.stage == "verify":  # REQ-DEF-009`
  - replace: `    elif False:  # REQ-DEF-009`
- M11 REQ-DEF-009.B2 skill/sdd/scripts/sdd.py
  - find: `    elif report.stage == "verify":  # REQ-DEF-009`
  - replace: `    elif True:  # REQ-DEF-009`

<!-- No entry moves a call: a one-line find/replace can't, so M6 to M8 break each
call and REQ-DEF-007.N6, N7 and N4 guard its position (project rule 4). -->

## Verification
<!-- Verifier: commands run, results, coverage, findings, verdict. -->
- Date: 2026-11-02 · Verifier: subagent (strong)
- Tests: `python3 -m unittest tests.test_sdd` → Ran 554 tests, OK
- Check: `sdd.py check --stage verify` → result: OK (14 warnings for the pre-existing tasks, audited below; 1 warning for the missing Verifier line, which this record answers)
- Replay: `sdd.py replay --base 416850f` → replay: 20 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` → mutate: 11 caught, 0 survived or invalid
- Coverage: not available (no coverage tool installed)
- Test diff: `git diff tests/test_sdd.py` only adds lines (helpers `drow`, `blocking_line` and the classes DefectGateBase, DefectBlockTests, DefectLogGateTests, DefectCheckTests); no existing test is changed, VerdictStandardTests included.

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-DEF-007.S1 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_S1_later_and_wont_fix_defects_dont_block_results_approval | pass | yes |
| REQ-DEF-007.S2 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_S2_and_REQ_DEF_007_B1_a_closed_defect_or_no_log_doesnt_block_advance | pass | yes |
| REQ-DEF-007.S3 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_S3_archive_passes_with_later_and_wont_fix_defects | pass | yes |
| REQ-DEF-007.N1 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N1_results_approval_refuses_a_critical_fix_now_defect | pass | yes |
| REQ-DEF-007.N2 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N2_advance_verified_refuses_a_major_undecided_defect | pass | yes |
| REQ-DEF-007.N3 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N3_archive_refuses_a_defect_added_after_verified | pass | yes |
| REQ-DEF-007.N4 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N4_archive_shows_only_the_blocking_defects_in_order_and_without_the_minor_before_the_verify_check | pass | yes |
| REQ-DEF-007.N5 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N5_deciding_later_clears_the_block | pass | yes |
| REQ-DEF-007.N6 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N6_results_approval_shows_only_the_defect_refusal_before_the_verify_check_and_the_verdict | pass | yes |
| REQ-DEF-007.N7 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_N7_advance_verified_back_from_blocked_shows_only_the_defect_refusal_before_the_verify_check_and_the_verdict | pass | yes |
| REQ-DEF-007.B1 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_S2_and_REQ_DEF_007_B1_a_closed_defect_or_no_log_doesnt_block_advance | pass | yes |
| REQ-DEF-007.B2 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_B2_and_REQ_DEF_007_B3_minor_and_other_change_defects_dont_block | pass | yes |
| REQ-DEF-007.B3 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_B2_and_REQ_DEF_007_B3_minor_and_other_change_defects_dont_block | pass | yes |
| REQ-DEF-007.B4 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_B4_the_plan_gate_and_other_moves_ignore_defects | pass | yes |
| REQ-DEF-007.B5 | tests/test_sdd.py::DefectBlockTests.test_REQ_DEF_007_B5_advance_implementing_from_verifying_isnt_refused | pass | yes |
| REQ-DEF-008.N1 | tests/test_sdd.py::DefectLogGateTests.test_REQ_DEF_008_N1_results_approval_refuses_an_invalid_log | pass | yes |
| REQ-DEF-008.N2 | tests/test_sdd.py::DefectLogGateTests.test_REQ_DEF_008_N2_advance_verified_refuses_an_invalid_log | pass | yes |
| REQ-DEF-008.N3 | tests/test_sdd.py::DefectLogGateTests.test_REQ_DEF_008_N3_archive_refuses_a_repeated_defect_id | pass | yes |
| REQ-DEF-008.B1 | tests/test_sdd.py::DefectLogGateTests.test_REQ_DEF_008_B1_and_REQ_DEF_008_B2_the_plan_gate_and_advance_implementing_accept_an_invalid_log | pass | yes |
| REQ-DEF-008.B2 | tests/test_sdd.py::DefectLogGateTests.test_REQ_DEF_008_B1_and_REQ_DEF_008_B2_the_plan_gate_and_advance_implementing_accept_an_invalid_log | pass | yes |
| REQ-DEF-009.S1 | tests/test_sdd.py::DefectCheckTests.test_REQ_DEF_009_S1_check_passes_with_only_non_blocking_defects | pass | yes |
| REQ-DEF-009.N1 | tests/test_sdd.py::DefectCheckTests.test_REQ_DEF_009_N1_check_lists_each_blocking_defect_as_an_error | pass | yes |
| REQ-DEF-009.B1 | tests/test_sdd.py::DefectCheckTests.test_REQ_DEF_009_B1_and_REQ_DEF_009_B2_check_without_a_stage_lists_them_the_plan_stage_doesnt | pass | yes |
| REQ-DEF-009.B2 | tests/test_sdd.py::DefectCheckTests.test_REQ_DEF_009_B1_and_REQ_DEF_009_B2_check_without_a_stage_lists_them_the_plan_stage_doesnt | pass | yes |

Red evidence:
- T1, T5, T9, T11, T14 and T18 record real assertion failures about the behavior (the gate passed when it should refuse; T11's output held the minor D2 line).
- The 14 `pre-existing (after T<n>)` tasks are sound. Every reason matches the code: one `defect_gate` call per gate, placed before `analyze()`; `blocking_defects` filters on status, severity, decision and the Change cell; `defect_findings` adds the errors only at the verify stage. I ran the new test classes against the base `sdd.py` (416850f) in a scratch copy: T2, T4, T6, T15, T16 and T20 fail there, as do T1, T5, T9, T11, T14 and T18. The exit-0 tasks (T3, T7, T8, T10, T12, T13, T17 and T19) pass at the base by design. They protect against over-blocking, and they fail when the earlier task's exclusions are removed (M1 to M4 and M11, all caught). They also fail under these extra scratch mutations, none of which survived: the advance gate run on every move breaks T8, T13 and T17; the approve gate run for every gate breaks T13 and T17; each call moved after `analyze()` breaks T2, T6 and T11 in turn; the errors reported twice in check breaks T18 and T20; a missing log refused breaks T7 and T10; the gate writing the log breaks T1, T2, T3, T9 and T11; `status: archived` written before the archive gate breaks T9, T11 and T16.
- Four methods each prove two scenarios (T7: S2 and B1; T12: B2 and B3; T17: REQ-DEF-008 B1 and B2; T20: REQ-DEF-009 B1 and B2). Each half builds a fresh repository and asserts its own whole Then, and each mutation anchored at one of these scenarios (M1 S2, M3 B3, M4 B2, M11 REQ-DEF-009.B2) is caught by the half it is anchored to. This is not a finding, but a failing first half hides the result of the second.

Known gaps: the three bullets hold. The Change cell is compared exactly as written, so archived or mistyped IDs block nothing; close and decide take the agent's evidence; `status` and `next` only count defects, and `next` still says "sdd archive" for a verified change that has a blocking defect, which the Scope puts out of scope ("next and status stay as they are").

Constitution: rule 4 is met, because every new rule has an entry (M1 to M5 for the filters, M6 to M8 for the three calls, M9 for the invalid log, M10 and M11 for the check stage) and the call positions are guarded by N6, N7 and N4. Rule 5 is met: with no log, or no blocking row of the change, nothing changes (REQ-DEF-007.B1, B2, B3).

Findings: none. Note, not a finding: a specs/defects.md that can't be decoded as text raises an uncaught error in the gates (exit 1, nothing written) rather than a REQ-DEF-006 message. Every other file `sdd.py` reads, including `check`'s reading of the same log since 0.19.0, behaves this way, so it isn't new behavior of this change.

Verdict: PASS

## Open questions
<!-- Mark unknowns where they occur as [NEEDS CLARIFICATION: question] and list them here. -->
- Q1 Does an invalid specs/defects.md refuse approve results, advance verified and archive? → A: yes, the gate refuses, because it can't show that nothing blocks (operator, 2026-10-30, Claude Code chat)

## Clarifications
<!-- Spec Critic: one round per review, started with `sdd.py round`. Format:
method/format.md. Required before the gate at production and above. -->

### Round 1 — 2026-11-01 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-DEF-007 | issues | F2, F3, F4, F5, F6 |
| REQ-DEF-008 | issues | F1, F4, F5 |
| REQ-DEF-009 | ok | |

<!-- Findings without an outcome are spec or plan fixes for the Spec Author (each says what to add or change). Design notes, Tasks and the Mutations comment were reviewed with the spec (mini). REQ-DEF-009 matches the code's paths: auto_stage maps verifying and verified to verify, cmd_analyze runs at the plan stage, and the gates call analyze(), which never reads the log, so no defect line is printed twice. -->

- F1 [coverage] REQ-DEF-008: the clause "no other approve or advance looks at the log" is exercised only by B1 (approve plan); no advance is tested with an invalid log (REQ-DEF-007.B4 uses a valid log, so it doesn't cover this clause), and nothing is tested on a verifying change, the one place a wrongly placed call would sit. Add B2: the REQ-DEF-007.S2 change and the N1 log | advance implementing | exit 0 · status implementing (an invalid log refuses only the verify gates). → fixed: REQ-DEF-008.B2 added (advance implementing from verifying with the invalid log: exit 0, status implementing); task T17
- F2 [coverage] REQ-DEF-007: B4 tests the "no other approve or advance" clause only away from the verify gates (approve plan, planned → implementing); the moves a verifying change with a blocking defect needs (advance implementing to fix a fix-now defect, blocked, abandoned, approve amend) are untested, so a call wired into every advance from verifying would pass. Add B5: the N2 setup | advance implementing | exit 0 · status implementing. Also "looks at the defects" isn't observable: say "no other approve or advance is refused because of them" (same in REQ-DEF-008). → fixed: REQ-DEF-007.B5 added (the N2 setup, advance implementing: exit 0, status implementing); "looks at" replaced by "is refused because of" in REQ-DEF-007, REQ-DEF-008 and B4's note; task T8
- F3 [contradiction] REQ-DEF-007: the statement limits the gate to `advance verified` of a mini change and says no other advance looks at the defects, but the Design notes wire it into cmd_advance's `target == "verified"` branch, which also runs when a mini or standard change returns from blocked (blocked_from: verified); that path already runs the verify check and the verdict → Q2 → fixed: per Q2, "(mini)" dropped from REQ-DEF-007's advance verified (now from verifying or back from blocked, also in Scope); REQ-DEF-007.N7 added (blocked from verified: exit 1, the D1 line, status stays blocked); Design notes say the call covers the return from blocked; task T6
- F4 [ambiguity] REQ-DEF-007, REQ-DEF-008: Known gap 4 leaves the refusal order unspecified, but the Design notes already fix it (the defect refusal before analyze(), the verdict and, in archive, the existing-folder check), and a gate shows only one refusal, so "which is shown first" misdescribes it. The Design's reason ("so nothing is printed or written before the refusal") holds for either order. The order is observable output, and without a row a reordering survives the mutation check → Q1 → fixed: per Q1, REQ-DEF-007 and REQ-DEF-008 now say the defect refusal is the only one shown, checked right after the status check; REQ-DEF-007.N6 added (Verdict GAPS: the D1 line, no "GAPS"); Known gap 4 dropped; task T2
- F5 [weak-negative] REQ-DEF-007, REQ-DEF-008: the archive refusals REQ-DEF-007.N3, N4 and REQ-DEF-008.N3 assert the change stays in specs/changes but not that its status stays verified; archive writes `status: archived` into spec.md before it moves the folder, so a check placed after that write would pass them. Add "status stays verified · spec.md is byte-for-byte unchanged" to all three, and "specs/defects.md is byte-for-byte unchanged" to REQ-DEF-007.N4 and REQ-DEF-008.N3. → fixed: REQ-DEF-007.N3, N4 and REQ-DEF-008.N3 now also assert status stays verified and spec.md is byte-for-byte unchanged; N4 and REQ-DEF-008.N3 also assert specs/defects.md is byte-for-byte unchanged
- F6 [coverage] REQ-DEF-007 (Mutations): M1 is anchored at N1 but is meant to cover the status and decision tests; `SDD mutate` runs only the tests of tasks that plan N1, and N1's row (open, critical, fix-now) still blocks when the closed or later/wont-fix exclusion is removed, so those mutations would survive. Anchor the status test at S2 and the decision test at S1 or N5 (severity is M3). Also add an entry for the results-gate call in cmd_approve, anchored at N1 (M5 and M6 cover only the other two call sites). → fixed: Mutations comment now anchors the status test at REQ-DEF-007.S2 (M1) and the decision test at S1 (M2), severity at B2 (M4), and adds M6, the results-gate call in cmd_approve, at N1 (now M1 to M11)

- Q1 When a verify gate would refuse for a defect (a blocking defect or an invalid log) and for another reason too (the verify check fails, a GAPS or missing verdict, archive's folder already exists), which refusal does it show? A) specify the Design's order: only the defect refusal, checked right after the status check; add a row (the REQ-DEF-007.N1 setup with the latest line "Verdict: GAPS — F1": exit 1 · the D1 line · the output doesn't contain "GAPS") and drop Known gap 4 B) keep it unspecified, as Known gap 4 — recommended: A (it's observable output at production, the code fixes the order anyway, a reordering would otherwise go undetected, and `check --stage verify` already shows the defect errors and the check errors together)
  - Answer: A — the defect refusal alone, checked right after the status check; a row proves it and Known gap 4 is dropped (operator, 2026-11-02, Claude Code chat)
- Q2 Does a blocking defect or an invalid log refuse a change that returns from blocked to verified (`advance verified` with blocked_from: verified, mini or standard)? A) yes: every `advance verified` runs the defect gate, as it already runs the verify check and the verdict on that path; the statement drops "(mini)" and gains a row (a mini change blocked from verified, a log with D1 open, critical, undecided of it | advance verified | exit 1 · the D1 line · status stays blocked) B) no: only verifying → verified is gated; the return from blocked skips the defect gate (an extra condition in the code) — recommended: A (same path as the existing checks, archive would refuse right after anyway, and the change can still be abandoned)
  - Answer: A — every `advance verified` runs the defect gate, including a return from blocked; "(mini)" is dropped and a row is added (operator, 2026-11-02, Claude Code chat)

### Round 2 — 2026-11-02 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-DEF-007 | issues | F1, F2, F3, F4, F5 |
| REQ-DEF-008 | issues | F1, F5 |
| REQ-DEF-009 | issues | F6 |

<!-- Findings without an outcome are spec or plan fixes for the Spec Author (each says what to add or change); none needs a product decision, so this round has no questions. Design notes, Tasks and the Mutations comment were reviewed with the spec (mini). Round 1's outcomes are applied as recorded: REQ-DEF-008.B2 and REQ-DEF-007.B5 exist with tasks T17 and T8; "(mini)" is gone and N7 covers the return from blocked (T6); "is refused because of" replaces "looks at" in both statements and B4; N6 exists (T2) and Known gap 4 is gone; N3, N4 and REQ-DEF-008.N3 assert status and spec.md unchanged; the Mutations comment anchors M1 at S2, M2 at S1, M4 at B2 and adds M6 at N1. Every scenario is planned by a task. The answers to R1 Q1 and Q2 are kept: the findings below only make the rows prove what the statements now say. -->

- F1 [weak-negative] REQ-DEF-007, REQ-DEF-008: no Then proves "this is the only refusal shown". A gate wired as analyze() followed by defect_findings() (the reuse the Design invites, since defect_findings gains the blocking errors at the verify stage for check) prints the check report, which holds the D1 line or the log problem, then "the verify check fails"; REQ-DEF-007.N1 to N7 and REQ-DEF-008.N1 to N3 all still pass (exit 1, the line is in the output, no "GAPS" because the verdict is never reached, nothing written). Add to REQ-DEF-007.N6 "the output is only the D1 refusal (no "verify check fails", no "GAPS")" and to REQ-DEF-008.N1 "the output is only that problem". → fixed: REQ-DEF-007.N6 now asserts the output is only the D1 refusal (no "verify check fails", no "GAPS"); REQ-DEF-008.N1 asserts the output is only that problem
- F2 [coverage] REQ-DEF-007: N6 proves only "before the verdict": its verify check passes, so a call placed between analyze() and verdict_problem() passes it, while the statement says before the verify check. Give N6 a failing verify check as well (e.g. T1 left unticked), keeping "Verdict: GAPS — F1"; with F1's Then this one row proves the whole results-gate position. → fixed: N6's Given adds a failing verify check (T1 left unticked) and keeps "Verdict: GAPS — F1"; T2 retitled
- F3 [coverage] REQ-DEF-007: the order is stated for all three gates, but each gate has its own call and only the results call has an order row; N2, N3, N4 and N7 all have a passing verify check, so an advance or archive call placed after analyze() (or archive's after the destination check) passes every row. One row per call site is enough at production, folded into existing rows: N7 (verifying and back-from-blocked share the advance call) gets a failing verify check and "Verdict: GAPS — F1" with "the output is only the D1 refusal"; N4 gets a failing verify check (e.g. the test file no longer names a scenario) with "the output is only the D1 and D3 lines" (the destination check comes after analyze(), so it is covered). REQ-DEF-008 needs no order row: the invalid log is raised by the same defect_gate call, before the rows are read. No new task: retitle T2 ("before the verify check and the verdict"), T6 and T11 to say the order, and have the Design notes cite N6, N7 and N4 instead of N6 alone. → fixed: N7 gets a failing verify check, "Verdict: GAPS — F1" and "the output is only the D1 refusal"; N4 gets a failing verify check and "the output is only the D1 and D3 lines"; T2, T6 and T11 retitled with the order; Design notes cite N6, N7 and N4; no new task
- F4 [coverage] REQ-DEF-007 (Mutations): no planned mutation breaks a call's position, and none can honestly: an entry is a one-line find/replace and can't move a call. M6 to M8 break each call and F1 to F3's rows guard the position, which meets project rule 4. Add one line to the Mutations comment saying so, rather than new entries. → fixed: one line added to the Mutations comment: no entry moves a call, M6 to M8 break each call and N6, N7 and N4 guard its position (project rule 4)
- F5 [ambiguity] REQ-DEF-007, REQ-DEF-008: "the only refusal shown, checked right after the gate's status check" isn't true for every earlier check: cmd_approve refuses a blank --evidence before reading the status, and approve results refuses a mini change before its status check. Say "checked right after the gate's argument, size and status checks" (or "a refusal of --evidence, size or status still comes first"). → fixed: REQ-DEF-007 and REQ-DEF-008 now say "checked right after the gate's argument, size and status checks"
- F6 [weak-negative] REQ-DEF-009.N1: "check --json's errors hold both" still passes when a defect error is reported twice, which is what happens if the blocking errors are also added inside analyze() (that wiring would also refuse approve amend on a verifying change, and no gate row catches it because defect_gate runs before analyze()). Say "check --json's errors hold each of the two lines exactly once". → fixed: REQ-DEF-009.N1 now says "check --json's errors hold each of the two lines exactly once"

## Amendments
<!-- Spec changes after approval, one line each, then `sdd.py approve amend`:
- A1 2026-10-07: <reason> → <what changed> -->

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
| plan | 2026-11-02 | Operator in Claude Code chat, 2026-11-02: "approved" (reply to "Approve this spec and plan?" for 0006-blocking-defects after Critic rounds 1 and 2) |
