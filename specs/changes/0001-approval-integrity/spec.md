---
id: 0001-approval-integrity
title: Results gate ignores the verdict; constitution edits go undetected
type: defect
size: mini
assurance: production
status: implementing
capabilities: approvals=APR
created: 2026-10-12
spec_hash: c85d3fc174bd
---

# 0001-approval-integrity — Results gate ignores the verdict; constitution edits go undetected

## Intent
Approvals must mean exactly what was approved. Today the results gate passes a
verification whose verdict is GAPS, and the constitution can be edited after
its approval — including lowering the assurance level — without anyone being
told. Operators and adopters need to trust that every recorded approval
covers what it claims to cover.

## Defect
- Symptom: approve results ignores the verdict, and constitution edits after approval go undetected
- Reproduce: (1) take a standard change to verifying with a clean verify check, end ## Verification with "Verdict: GAPS — F1 open: weak test for N1", run approve results. (2) run approve constitution, then append "10. Anything goes." and change "assurance: internal" to "assurance: prototype" in specs/constitution.md, run status.
- Current behavior: (1) "results approved → verified", exit 0, status verified. (2) status prints "project assurance: prototype" with no warning; the lowered level applies to new changes without any waiver or approval.
- Expected behavior: (1) the results gate accepts only a PASS verdict. (2) unapproved constitution changes are reported, block the gates, and have no effect until the operator re-approves them.
- Violates: spec gap — this repository has no living spec yet (specs/capabilities/ is empty)
- Root cause: (1) approve results runs only the structural verify check; nothing reads the Verifier's verdict. (2) approve constitution sets "approved: yes" once and stores no fingerprint or approved level, so later edits are invisible to status, check and the gates.

## Scope
- In: the results gate (and the mini verified step) reading the Verifier's verdict; a fingerprint of the approved constitution, kept in its front matter and in its approval row; reporting unapproved constitution changes; the gates refusing while they exist; the last approved assurance level staying in force until re-approval; approve constitution refusing an unchanged constitution or an invalid level, and labelling a lowered level.
- Out: fingerprinting other files (capability specs are already written only by sdd.py); a general waiver mechanism; changing what the Verifier writes beyond its Verdict line; requiring a first constitution approval before any gate (Q7).
- Changes existing behavior: approve results accepted any verdict → it requires PASS. Changes already in verifying need a Verdict line before approve results or advance verified; changes already verified or archived are not re-checked (archive does not read the verdict). Constitution edits after approval were silent and took effect at once → they are reported, block the gates, and take effect only when re-approved. Re-approving an unchanged constitution was recorded again → it is refused. An invalid or missing assurance level with no approved level crashed with a traceback → new, check and status refuse with an error naming the four levels.

## Requirements
### REQ-APR-001 The results gate requires a PASS verdict
When the operator approves the results of a standard change, or a mini change
is marked verified, sdd.py shall proceed only if the latest verdict line of the
Verification section has the verdict word PASS. A verdict line is a line of that
section, outside fenced code blocks and HTML comments, whose text after an
optional list marker (`-`, `*`, `+`, or a number followed by `.` or `)`) and
`*`/`_` emphasis begins with "Verdict:" in any case;
table rows and mid-line mentions are not verdict lines. The verdict word is the
run of letters after the colon: PASS or GAPS in any case; anything else, such as
PASSED, is unknown.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a standard change in verifying, verify check OK, the Verification section ending with "Verdict: PASS" | approve results | exit 0 · status verified · one results row in Approvals |
| R1 | validation | the S1 change, but the latest line is "Verdict: GAPS — F1 open" | approve results | exit 1 · the error contains "GAPS — F1 open" · status stays verifying · no results row |
| N1 | validation | the S1 change, but no verdict line | approve results | exit 1 · error "no verdict" · status stays verifying · no results row |
| N2 | validation | the S1 change, but the latest line is "Verdict: maybe" | approve results | exit 1 · the error lists PASS and GAPS · status stays verifying · no results row |
| B1 | boundary | the S1 change, but the latest line is "Verdict: pass — 0 findings" | approve results | exit 0 · status verified |
| B2 | boundary | the S1 change, with an earlier "Verdict: PASS" and a later "**Verdict:** GAPS — F3" | approve results | exit 1 · status stays verifying · no results row |
| B3 | boundary | the S1 change, with "Verdict: PASS" followed by a fenced code block containing "Verdict: GAPS" | approve results | exit 0 · status verified |
| B4 | boundary | the S1 change, with an earlier "Verdict: PASS" and a later "1. Verdict: GAPS — F4" | approve results | exit 1 · status stays verifying · no results row |
| B5 | boundary | the S1 change, with an earlier "Verdict: PASS" and a later "1) Verdict: GAPS — F4" | approve results | exit 1 · status stays verifying · no results row |
| B6 | boundary | the S1 change, with "Verdict: GAPS — F1" followed by a table row "\| Verdict \| PASS \|" | approve results | exit 1 · status stays verifying · no results row (a table row is not a verdict line) |
| B7 | boundary | the S1 change, with "Verdict: GAPS — F1" followed by "The final Verdict: PASS was expected" | approve results | exit 1 · status stays verifying · no results row (a mid-line mention is not a verdict line) |
| B8 | boundary | the S1 change, with "Verdict: GAPS — F1" followed by "<!-- Verdict: PASS -->" | approve results | exit 1 · status stays verifying · no results row (a comment is not a verdict line) |
| N3 | state | the S1 change, with an earlier "Verdict: PASS" and a later "Verdict: GAPS — F2" | approve results | exit 1 · status stays verifying · no results row |
| S2 | state | the S1 change, with an earlier "Verdict: GAPS" and a later "Verdict: PASS" | approve results | exit 0 · status verified (the latest verdict wins) |
| N4 | dependency | the S1 change, but its verification.md file was deleted | approve results | exit 1 · error "no verdict" · status stays verifying · no results row |
| S3 | happy | a mini change in verifying, verify check OK, the Verification section ending with "Verdict: PASS" | advance verified | exit 0 · status verified |
| R2 | validation | a mini change in verifying, verify check OK, the Verification section ending with "Verdict: GAPS" | advance verified | exit 1 · the error contains "GAPS" · status stays verifying · spec.md is unchanged |
| N5 | validation | a mini change in verifying, verify check OK, no verdict line | advance verified | exit 1 · error "no verdict" · status stays verifying · spec.md is unchanged |

- N/A access: sdd.py runs locally with no users or roles; who may approve is governed by the agent rules

### REQ-APR-002 Constitution changes after approval are detected
When the operator approves the constitution, sdd.py shall record its
fingerprint and approved level in the front matter (fingerprint,
approved_level) and at the end of that approval row's Evidence cell; only a
note at the very end of the cell counts. The constitution is changed since
approval when the newest approval row that carries a fingerprint differs from
the current content, or when the front matter's fingerprint is missing,
unreadable or different from that row's. When no approval row carries a
fingerprint, a valid fingerprint in the front matter is the reference. While
it is changed, status shall report it, check shall report it as an error and
exit 1, and approve spec, plan, results and amend, advance verified and archive
shall refuse; approve constitution, new and the other advance moves are not
blocked. The fingerprint is the first 12 hex digits of a SHA-256 over the
constitution with HTML comments and blank lines removed and runs of whitespace
inside each line collapsed (re-wrapping a paragraph is a change); it excludes
the Approvals section and the front-matter keys approved, fingerprint and
approved_level.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | an initialized repository whose constitution isn't approved | approve constitution | exit 0 · the front matter holds "fingerprint: <12 hex digits>" and "approved_level: <level>" · the row's Evidence cell ends with the same fingerprint and level · status shows no change note |
| R1 | state | an approved constitution to which "10. Anything goes." was then added | status | the output says the constitution changed since approval and names sdd approve · status --json has constitution_changed true and constitution_approved true · exit 0 |
| N1 | state | that changed constitution and a mini draft ready for plan approval | approve plan | exit 1 · the error says the constitution changed since approval · the change stays draft · no plan row · spec.md is unchanged |
| N5 | state | that changed constitution and an active change | check | exit 1 · the error says the constitution changed since approval |
| N6 | state | that changed constitution and a mini change in verifying, verify check otherwise OK, "Verdict: PASS" | advance verified | exit 1 · the error says the constitution changed since approval · status stays verifying |
| S2 | happy | that changed constitution | approve constitution | exit 0 · a "constitution (re-approval)" row · status shows no change note |
| N2 | validation | a constitution with approved: yes and a fingerprint that matches its content | approve constitution | exit 1 · error "nothing changed since approval" · no new row · the constitution file is unchanged |
| N3 | validation | an approved constitution whose fingerprint line was edited by hand | status | the output says the constitution changed since approval · exit 0 · nothing is rewritten |
| N7 | validation | an approved constitution whose fingerprint line was deleted | status | the output says the constitution changed since approval · exit 0 · nothing is rewritten |
| N8 | validation | an approved constitution whose front-matter delimiters were removed | status | the output says the constitution changed since approval · exit 0 · nothing is rewritten |
| B1 | boundary | an approved constitution with only blank lines and an HTML comment added | status | no change note · exit 0 · nothing is rewritten |
| B2 | boundary | an approved constitution with a double space added inside one rule | status | no change note · exit 0 · nothing is rewritten |
| B3 | boundary | an approved constitution with a row added by hand to the Approvals section, without a fingerprint | status | no change note · exit 0 · nothing is rewritten |
| N4 | state | a constitution approved by an earlier version (approved: yes, no fingerprint anywhere) | status | no change note · exit 0 · nothing is rewritten |
| S3 | state | that earlier-version constitution | approve constitution | exit 0 · a fingerprint is recorded in the front matter and the row · status shows no change note |
| S4 | state | a constitution that was never approved (approved: no, as init writes it) and a mini draft ready for plan approval | approve plan | exit 0 · the change is planned, as today |
| N9 | validation | approved at internal, edited to production, then re-approved with evidence quoting an older note "fingerprint 0123456789ab · level prototype" | status | no change note · assurance production · new changes are created at production |
| N10 | state | an approved constitution, then a hand-added newer row without a fingerprint and the front-matter fingerprint line deleted | status | the output says the constitution changed since approval · exit 0 · nothing is rewritten |
| S5 | state | an approved constitution whose fingerprinted approval rows were all deleted, front-matter fingerprint kept, then a rule added | status | the output says the constitution changed since approval · the front-matter approved level stays in force |

- N/A access: sdd.py runs locally with no users or roles; who may approve is governed by the agent rules
- N/A dependency: only the local constitution file is read; a missing file is already reported as not initialized

### REQ-APR-003 The approved assurance level stays in force
While the constitution has unapproved changes, sdd.py shall use the level
recorded at its last approval as the project level: the default and the floor
for new, the floor in check, and the level status shows. When an approval
accepts a lower level than the previous approved level, that row's Evidence
cell shall end with "assurance lowered <old> → <new>". When no approved level is
recorded and the front matter's level is missing or not one of the four
levels, new, check and status shall refuse with an error naming the four levels.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a constitution approved at internal, unchanged | new demo | the change is created at internal |
| R1 | state | approved at internal, then edited to "assurance: prototype", not re-approved | new demo | the change is created at internal · status shows "internal (prototype pending approval)" · status --json has assurance internal and assurance_pending prototype |
| N3 | state | approved at internal, edited to "assurance: prototype", not re-approved | new demo --assurance prototype | exit 1 · the error says it is lower than the project level 'internal' · no change folder is created |
| S2 | state | that edit, then the operator re-approves | approve constitution | exit 0 · the row's Evidence cell ends with "assurance lowered internal → prototype" · later changes are created at prototype |
| N1 | validation | the front matter edited to "assurance: sloppy", or its assurance line deleted | approve constitution | exit 1 · the error lists the four levels · no new row · internal stays in force · the constitution file is unchanged |
| B1 | boundary | approved at internal, edited to "assurance: production", not re-approved | new demo | the change is created at internal · status shows "internal (production pending approval)" |
| B2 | boundary | approved at internal, edited to "assurance: production" | approve constitution | exit 0 · the row has no "lowered" note · later changes are created at production |
| B3 | boundary | approved at internal, a project rule added, level unchanged | approve constitution | exit 0 · the row has no "lowered" note |
| N2 | state | a constitution approved by an earlier version (no recorded level) | new demo | the change uses the level in the front matter, as before · nothing is rewritten |
| S4 | state | a constitution approved by an earlier version at internal, then edited to "assurance: prototype" | approve constitution | exit 0 · fingerprint and approved_level prototype are recorded · the row has no "lowered" note |
| N4 | validation | a never-approved constitution with "assurance: prodution" | new demo | exit 1 · the error names "prodution" and lists the four levels · no change folder is created |
| N5 | validation | that never-approved constitution with "assurance: prodution" | status | exit 1 · the error names "prodution" and lists the four levels |
| N6 | validation | a constitution approved by an earlier version, then edited to "assurance: prodution", with an active change | check | exit 1 · the error names "prodution" and lists the four levels |

- N/A access: sdd.py runs locally with no users or roles; who may approve is governed by the agent rules
- N/A dependency: only the local constitution file is read; a missing file is already reported as not initialized

## Known gaps
- Only the constitution gains a fingerprint; capability specs stay protected by being written only through sdd.py.
- A constitution approved by an earlier version is unprotected until its first approval under this version; that approval records a fingerprint but cannot label a lowering.
- A constitution that was never approved blocks no gate (Q7); a later change may require the first approval.
- Approvals are plain-text records: a deliberately forged approval row is not detected. Review approval rows in pull requests.

## Design notes
- Modules: skill/sdd/scripts/sdd.py only; tests in tests/test_sdd.py.
- Verdict: a helper reads the Verification section without fenced blocks, comments and table rows, finds lines that begin with "Verdict:" after list markers and emphasis, and returns the latest verdict word. approve results (standard) and advance verified (mini) refuse anything but PASS, after the existing verify check, writing nothing on refusal.
- Fingerprint: SHA-256 (12 hex digits) of the constitution, comments and blank lines removed, whitespace runs collapsed per line, Approvals section and the approved/fingerprint/approved_level keys excluded. approve constitution stores it in the front matter and appends "· fingerprint <hex> · level <level>" (plus "· assurance lowered X → Y" when lower) to the row's Evidence cell; it refuses an unchanged constitution or an invalid level.
- Reference: the newest approval row whose Evidence carries a fingerprint. Changed = that row's fingerprint differs from the content, or the front-matter fingerprint is missing, unreadable or different. No such row: earlier-version behavior.
- While changed: Project.level() returns the reference row's level; status prints the change note and "X (Y pending approval)"; status --json gains constitution_changed and assurance_pending; analyze adds an error, which makes check exit 1 and every gate that runs it refuse.
- Existing tests that encode the old behavior are updated: results/verified approvals need a PASS verdict; a repeat constitution approval needs a change.
- Test strategy: one unit test per scenario through the Repo helper (temporary repositories), named test_REQ_APR_00N_<ID>_…; mutation-check every new rule (project rule 4).
- Test command: `python3 -m unittest tests.test_sdd`

## Tasks
- [x] T1 REQ-APR-001.R1 GAPS verdict refused at approve results (regression)
  - test: tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_R1_gaps_verdict_refused
  - red: AssertionError: 0 != 1 : 0001-durations: results approved → verified
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T2 REQ-APR-001.S1 PASS verdict accepted
  - test: tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_S1_pass_verdict_accepted
  - red: pre-existing — the results gate already accepted a PASS verdict; the fix must keep that
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T3 REQ-APR-001.N1 No verdict line refused
  - test: tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_N1_no_verdict_refused
  - red: AssertionError: 0 != 1 : 0001-durations: results approved → verified
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T4 REQ-APR-001.N2 Unknown verdict word refused
  - test: tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_N2_unknown_verdict_refused
  - red: AssertionError: 0 != 1 : 0001-durations: results approved → verified
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T5 REQ-APR-001.B1 Lowercase and trailing text accepted
  - test: tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_B1_lowercase_with_trailing_text_accepted
  - red: pre-existing — a lowercase PASS was already accepted, because no verdict was read
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T6 REQ-APR-001.B2 Emphasised later GAPS verdict refused
  - test: tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_B2_emphasised_later_gaps_refused
  - red: AssertionError: 0 != 1 : 0001-durations: results approved → verified
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T7 REQ-APR-001.B3 Verdict inside a fenced code block ignored
  - test: tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_B3_verdict_in_code_block_ignored
  - red: pre-existing — a verdict inside a code block was already ignored, because no verdict was read
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T8 REQ-APR-001.N3 Latest GAPS after an earlier PASS refused
  - test: tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_N3_latest_gaps_after_pass_refused
  - red: AssertionError: 0 != 1 : 0001-durations: results approved → verified
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T9 REQ-APR-001.S2 Latest PASS after an earlier GAPS accepted
  - test: tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_S2_latest_pass_after_gaps_accepted
  - red: pre-existing — a latest PASS was already accepted, because no verdict was read
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T10 REQ-APR-001.N4 Missing verification.md refused
  - test: tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_N4_missing_verification_file_refused
  - red: AssertionError: 0 != 1 : 0001-durations: results approved → verified
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T11 REQ-APR-001.R2 Mini GAPS verdict refused at advance verified (regression)
  - test: tests/test_sdd.py::VerdictMiniTests.test_REQ_APR_001_R2_mini_gaps_refused
  - red: AssertionError: 0 != 1 : 0001-parse-duration: verifying → verified
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T12 REQ-APR-001.S3 Mini PASS verdict accepted
  - test: tests/test_sdd.py::VerdictMiniTests.test_REQ_APR_001_S3_mini_pass_accepted
  - red: pre-existing — the mini verified step already accepted a PASS verdict
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T13 REQ-APR-001.N5 Mini change without a verdict refused
  - test: tests/test_sdd.py::VerdictMiniTests.test_REQ_APR_001_N5_mini_no_verdict_refused
  - red: AssertionError: 0 != 1 : 0001-parse-duration: verifying → verified
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T14 REQ-APR-002.R1 Status reports a constitution changed since approval (regression)
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_R1_status_reports_change
  - red: AssertionError: 'changed since approval' not found in 'project assurance: internal\nactive change: none\nnext: sdd quick "<idea>" (or sdd propose "<id
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T15 REQ-APR-002.S1 Approval records the fingerprint in front matter and row
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_S1_approval_records_fingerprint
  - red: AssertionError: unexpectedly None
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T16 REQ-APR-002.N1 approve plan refused while the constitution is changed
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N1_plan_gate_refused_while_changed
  - red: AssertionError: 0 != 1 : 0001-demo: plan approved → planned
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T17 REQ-APR-002.N5 check exits 1 while the constitution is changed
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N5_check_fails_while_changed
  - red: AssertionError: 0 != 1 : check 0001-demo (stage: plan, assurance: internal)
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T18 REQ-APR-002.N6 advance verified refused while the constitution is changed
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N6_advance_verified_refused_while_changed
  - red: AssertionError: 0 != 1 : 0001-demo: verifying → verified
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T19 REQ-APR-002.S2 Re-approval clears the change note
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_S2_reapproval_clears_change
  - red: AssertionError: '· fingerprint None ·' not found in '| constitution (re-approval) | 2026-10-12 | Operator: ok |'
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T20 REQ-APR-002.N2 Unchanged re-approval refused
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N2_unchanged_reapproval_refused
  - red: AssertionError: 0 != 1 : constitution re-approval recorded
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T21 REQ-APR-002.N3 Hand-edited fingerprint reported
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N3_edited_fingerprint_reported
  - red: AssertionError: fingerprint: None
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T22 REQ-APR-002.N7 Deleted fingerprint line reported
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N7_deleted_fingerprint_reported
  - red: AssertionError: fingerprint: None
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T23 REQ-APR-002.N8 Broken front matter reported
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N8_broken_front_matter_reported
  - red: AssertionError: 'changed since approval' not found in 'project assurance: None (constitution not approved)\nactive change: none\nnext: sdd quick "<ide
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T24 REQ-APR-002.B1 Blank lines and comments are not changes
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_B1_blank_lines_and_comments_ignored
  - red: pre-existing — no constitution change was ever reported, so this no-change case passed before the fix
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T25 REQ-APR-002.B2 Extra whitespace inside a line is not a change
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_B2_extra_whitespace_ignored
  - red: pre-existing — no constitution change was ever reported, so this no-change case passed before the fix
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T26 REQ-APR-002.B3 A hand-added row without fingerprint is not a change
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_B3_hand_added_row_ignored
  - red: pre-existing — no constitution change was ever reported, so this no-change case passed before the fix
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T27 REQ-APR-002.N4 Earlier-version constitution: no change note
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N4_earlier_version_not_flagged
  - red: pre-existing — an earlier-version constitution was never flagged; kept for backward compatibility
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T28 REQ-APR-002.S3 Earlier-version constitution: approval records a fingerprint
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_S3_earlier_version_gets_fingerprint
  - red: AssertionError: unexpectedly None
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T29 REQ-APR-002.S4 Never-approved constitution blocks nothing
  - test: tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_S4_never_approved_blocks_nothing
  - red: pre-existing — a never-approved constitution already blocked nothing; kept as decided in Q7
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T30 REQ-APR-003.R1 Lowered level not in force before re-approval (regression)
  - test: tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_R1_lowered_level_not_in_force
  - red: AssertionError: 'prototype' != 'internal'
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T31 REQ-APR-003.S1 Approved level applies to new changes
  - test: tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_S1_approved_level_applies
  - red: pre-existing — new changes already used the unchanged constitution level
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T32 REQ-APR-003.N3 Explicit lower level refused while pending
  - test: tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_N3_explicit_lower_level_refused_while_pending
  - red: AssertionError: 0 != 1 : created specs/changes/0001-demo/spec.md (size: mini, assurance: prototype)
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T33 REQ-APR-003.S2 Re-approval records the lowering, then applies it
  - test: tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_S2_reapproval_records_lowering
  - red: AssertionError: False is not true
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T34 REQ-APR-003.N1 Invalid or missing level refused at approval
  - test: tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_N1_invalid_or_missing_level_refused
  - red: AssertionError: 0 != 1 : constitution re-approval recorded
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T35 REQ-APR-003.B1 Raised level not in force before re-approval
  - test: tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_B1_raised_level_not_in_force
  - red: AssertionError: 'production' != 'internal'
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T36 REQ-APR-003.B2 Raised level approved without a lowered note
  - test: tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_B2_raised_level_approved_without_note
  - red: pre-existing — approving a raised level already worked, with no lowered note
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T37 REQ-APR-003.B3 Unchanged level approved without a lowered note
  - test: tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_B3_unchanged_level_approved_without_note
  - red: pre-existing — approving an unchanged level already worked, with no lowered note
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T38 REQ-APR-003.N2 Earlier-version constitution: front matter level, as before
  - test: tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_N2_earlier_version_uses_front_matter_level
  - red: pre-existing — an earlier-version constitution already used its front-matter level; kept for backward compatibility
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [x] T39 REQ-APR-003.S4 Earlier-version constitution: first approval records the level
  - test: tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_S4_earlier_version_first_approval_records_level
  - red: AssertionError: unexpectedly None
  - green: ok (Ran 39 tests in 2.609s, OK; full suite 194 OK)
- [ ] T40 REQ-APR-002.B2 Assert that status rewrites nothing (verify finding F1)
  - test:
  - red:
  - green:
- [ ] T41 REQ-APR-002.B3 Assert that status rewrites nothing (verify finding F2)
  - test:
  - red:
  - green:
- [ ] T42 REQ-APR-001.B4 Numbered '1.' GAPS after PASS refused
  - test:
  - red:
  - green:
- [ ] T43 REQ-APR-001.B5 Numbered '1)' GAPS after PASS refused
  - test:
  - red:
  - green:
- [ ] T44 REQ-APR-001.B6 Table row is not a verdict line
  - test:
  - red:
  - green:
- [ ] T45 REQ-APR-001.B7 Mid-line mention is not a verdict line
  - test:
  - red:
  - green:
- [ ] T46 REQ-APR-001.B8 Commented verdict is not a verdict line
  - test:
  - red:
  - green:
- [ ] T47 REQ-APR-002.N9 Only the trailing note in Evidence counts
  - test:
  - red:
  - green:
- [ ] T48 REQ-APR-002.N10 Newest fingerprinted row is the reference
  - test:
  - red:
  - green:
- [ ] T49 REQ-APR-002.S5 Front-matter fingerprint is the fallback reference
  - test:
  - red:
  - green:
- [ ] T50 REQ-APR-003.N4 Invalid level refused by new
  - test:
  - red:
  - green:
- [ ] T51 REQ-APR-003.N5 Invalid level refused by status
  - test:
  - red:
  - green:
- [ ] T52 REQ-APR-003.N6 Invalid level refused by check
  - test:
  - red:
  - green:

## Verification
<!-- Verifier: commands run, results, coverage, findings, verdict. -->
- Date: 2026-10-12 · Verifier: fresh session (production)
- Tests: `python3 -m unittest tests.test_sdd` → Ran 194 tests, OK
- Check: `sdd.py check --stage verify` (pinned tool) → OK · 0 errors · 14 warnings (the 14 pre-existing tasks)
- Coverage: coverage.py and pytest-cov are not installed, so branch coverage is not available. Line coverage with the standard-library `trace` module, on a scratch copy: 100 of the 101 executable lines this change added to sdd.py run. Uncovered: sdd.py:586 (a front-matter fingerprint becomes the reference when no approval row carries one). It is reachable, so it is not dead code → F5.
- Red evidence: the 39 new tests were run against sdd.py from 0cafdc9 (scratch copy). The 25 tasks with a red line fail with exactly their recorded assertion. The four regression reds (001.R1, 001.R2, 002.R1, 003.R1) reproduce the defect. 002.N3 and 002.N7 fail in their setup (`fingerprint: None`) because the old code wrote no fingerprint; accepted.
- Pre-existing (T2, T5, T7, T9, T12, T24–T27, T29, T31, T36–T38): all 14 pass on the old code, so the behavior existed. Each is killed by a mutation that removes its behavior (scratch copy), so every stated reason holds. T26 (B3) is killed by hashing ## Approvals; the row-choice rule it does not guard is part of F7.
- Probes (scratch copy) of statement clauses that have no scenario. A table row, a mid-line mention, an HTML comment, a lowercase key, PASSED, emphasis variants and a `~~~` fence all behave as specified. approve spec, results and amend, and archive, refuse while the constitution is changed; advance implementing and verifying don't. Re-wrapping a paragraph counts as a change. Ordered list markers → F3, a quoted fingerprint note → F4, a front-matter-only fingerprint → F5, an invalid unprotected level → F6.
- Mutations (19, scratch copy): 13 killed and 6 survived → F5, F7.

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-APR-001.S1 | tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_S1_pass_verdict_accepted | pass | yes |
| REQ-APR-001.R1 | tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_R1_gaps_verdict_refused | pass | yes |
| REQ-APR-001.N1 | tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_N1_no_verdict_refused | pass | yes |
| REQ-APR-001.N2 | tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_N2_unknown_verdict_refused | pass | yes |
| REQ-APR-001.B1 | tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_B1_lowercase_with_trailing_text_accepted | pass | yes |
| REQ-APR-001.B2 | tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_B2_emphasised_later_gaps_refused | pass | yes |
| REQ-APR-001.B3 | tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_B3_verdict_in_code_block_ignored | pass | yes |
| REQ-APR-001.N3 | tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_N3_latest_gaps_after_pass_refused | pass | yes |
| REQ-APR-001.S2 | tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_S2_latest_pass_after_gaps_accepted | pass | yes |
| REQ-APR-001.N4 | tests/test_sdd.py::VerdictStandardTests.test_REQ_APR_001_N4_missing_verification_file_refused | pass | yes |
| REQ-APR-001.S3 | tests/test_sdd.py::VerdictMiniTests.test_REQ_APR_001_S3_mini_pass_accepted | pass | yes |
| REQ-APR-001.R2 | tests/test_sdd.py::VerdictMiniTests.test_REQ_APR_001_R2_mini_gaps_refused | pass | yes |
| REQ-APR-001.N5 | tests/test_sdd.py::VerdictMiniTests.test_REQ_APR_001_N5_mini_no_verdict_refused | pass | yes |
| REQ-APR-002.S1 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_S1_approval_records_fingerprint | pass | yes |
| REQ-APR-002.R1 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_R1_status_reports_change | pass | yes |
| REQ-APR-002.N1 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N1_plan_gate_refused_while_changed | pass | yes |
| REQ-APR-002.N5 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N5_check_fails_while_changed | pass | yes |
| REQ-APR-002.N6 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N6_advance_verified_refused_while_changed | pass | yes |
| REQ-APR-002.S2 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_S2_reapproval_clears_change | pass | yes |
| REQ-APR-002.N2 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N2_unchanged_reapproval_refused | pass | yes |
| REQ-APR-002.N3 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N3_edited_fingerprint_reported | pass | yes |
| REQ-APR-002.N7 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N7_deleted_fingerprint_reported | pass | yes |
| REQ-APR-002.N8 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N8_broken_front_matter_reported | pass | yes |
| REQ-APR-002.B1 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_B1_blank_lines_and_comments_ignored | pass | yes |
| REQ-APR-002.B2 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_B2_extra_whitespace_ignored | pass | weak: "nothing is rewritten" not asserted |
| REQ-APR-002.B3 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_B3_hand_added_row_ignored | pass | weak: "nothing is rewritten" not asserted |
| REQ-APR-002.N4 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_N4_earlier_version_not_flagged | pass | yes |
| REQ-APR-002.S3 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_S3_earlier_version_gets_fingerprint | pass | yes |
| REQ-APR-002.S4 | tests/test_sdd.py::ConstitutionFingerprintTests.test_REQ_APR_002_S4_never_approved_blocks_nothing | pass | yes |
| REQ-APR-003.S1 | tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_S1_approved_level_applies | pass | yes |
| REQ-APR-003.R1 | tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_R1_lowered_level_not_in_force | pass | yes |
| REQ-APR-003.N3 | tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_N3_explicit_lower_level_refused_while_pending | pass | yes |
| REQ-APR-003.S2 | tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_S2_reapproval_records_lowering | pass | yes |
| REQ-APR-003.N1 | tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_N1_invalid_or_missing_level_refused | pass | yes |
| REQ-APR-003.B1 | tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_B1_raised_level_not_in_force | pass | yes |
| REQ-APR-003.B2 | tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_B2_raised_level_approved_without_note | pass | yes |
| REQ-APR-003.B3 | tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_B3_unchanged_level_approved_without_note | pass | yes |
| REQ-APR-003.N2 | tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_N2_earlier_version_uses_front_matter_level | pass | yes |
| REQ-APR-003.S4 | tests/test_sdd.py::ApprovedLevelTests.test_REQ_APR_003_S4_earlier_version_first_approval_records_level | pass | yes |

Findings:
- F1 (weak test) REQ-APR-002.B2: the test doesn't check that the constitution file is unchanged after status → T40.
- F2 (weak test) REQ-APR-002.B3: the test doesn't check that the constitution file is unchanged after status → T41.
- F3 (spec gap) REQ-APR-001: the statement allows "an optional list marker", and format.md says a list marker is fine, but VERDICT_LINE only knows `-`, `*` and `+`. With "Verdict: PASS" followed by a later "1. Verdict: GAPS — F4" (or "1) …"), approve results exits 0 and the change is verified. This fails open, in the same class as the defect. No scenario covers it, so a fix needs a new scenario → asked the operator: A) amend now (new boundary scenario and task, the code reads ordered markers) or B) accept it as a known gap (or narrow the statement to bullet markers).
- F4 (spec gap) REQ-APR-002/003: the fingerprint is recorded "at the end of that approval row's Evidence cell", but the code takes the first "fingerprint <hex> · level <level>" anywhere in the cell. Evidence that quotes an earlier row's note makes a fresh approval read as changed at once and puts the quoted level in force. Example: approved at production with evidence quoting "level prototype" → status "prototype (production pending approval)", and new changes are created at prototype. No scenario covers it → asked the operator: A) amend now (scenario and task: read the note at the end of the cell) or B) accept it as a known gap.
- F5 (spec gap) REQ-APR-002: when no approval row carries a fingerprint, the code uses a valid front-matter fingerprint as the reference (sdd.py:586). Edits are then reported, and its approved_level stays in force. Design notes say "No such row: earlier-version behavior". No test reaches the line, and removing it survives the suite → asked the operator: A) amend now (scenario and task pinning it, or remove the fallback) or B) accept it as a known gap.
- Operator decisions (2026-10-12): F3, F4, F5, F6 and F7 → A (amend), recorded as amendment A1.
- F6 (spec gap) REQ-APR-003: with no fingerprinted approval (never approved, or approved by an earlier version), an invalid level such as "sloppy" now silently falls back to internal: new creates the change at internal and status shows internal. Before this change it raised a ValueError. A typo like "prodution" therefore lowers new changes to internal, and Scope's "Changes existing behavior" doesn't list it → asked the operator: A) amend now (scenario and task, e.g. refuse with the four-levels error) or B) accept it as a known gap.
- F7 (test coverage, project rule 4) these statement rules can be broken without any test failing (mutations survive): table rows, mid-line mentions and HTML comments are not verdict lines (REQ-APR-001), and the reference is the newest row "that carries a fingerprint" (REQ-APR-002). Breaking the last one reopens the Q6 bypass: a hand-added newest row plus a deleted fingerprint line goes unreported. The code is correct in each case, but each needs a scenario → asked the operator: A) amend now (scenarios and tasks) or B) accept them as known gaps.

Verdict: GAPS — 7 findings (T40 and T41 added; F3–F7 awaiting the operator)

## Open questions
- Q1 Should the mini verified step also require PASS? → A: yes, one rule for both sizes (operator, 2026-10-12)
- Q4 Verdict grammar? → A: PASS or GAPS, case-insensitive, trailing text allowed, latest line wins (operator, 2026-10-12)
- Q2 Unapproved constitution changes? → A: report and block every other gate (operator, 2026-10-12)
- Q3 Re-approving an unchanged constitution? → A: refuse, "nothing changed since approval" (operator, 2026-10-12)
- Q5 Lowering the level by editing the constitution? → A: re-approval accepts it and records "assurance lowered X → Y" (operator, 2026-10-12)

## Clarifications
<!-- Spec Critic: one round per review, started with `sdd.py round`. Format:
method/format.md. Required before the gate at production and above. -->

### Round 1 — 2026-10-12 · Critic: fresh session

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-APR-001 | issues | F1, F2, F3, F4, F5 |
| REQ-APR-002 | issues | F6, F7, F8, F9, F10, F11, F12 |
| REQ-APR-003 | issues | F13, F14, F15 |

<!-- Questions are numbered from Q6 because Q1–Q5 already appear under ## Open questions. -->

- F1 [ambiguity] REQ-APR-001: "the latest `Verdict:` line" is undefined. The design's unanchored match would count a later findings bullet or pasted test output that mentions "Verdict: …"; a later "**Verdict:** GAPS" would not match, so an earlier plain PASS wins; "Verdict: PASSED" is undecided → fixed: state in the requirement that a verdict line is a line of ## Verification, outside fenced code blocks and HTML comments, whose text after an optional list marker and `*`/`_` emphasis begins with "Verdict:" (any case); table rows and mid-line mentions are not verdict lines; the verdict word is the run of letters after the colon, so "PASSED" is unknown and refused as in N2. Add B2: Given the S1 change with an earlier "Verdict: PASS" and a later "**Verdict:** GAPS — F3"; When approve results; Then exit 1 · status stays verifying · no results row. Add B3: Given the S1 change with "Verdict: PASS" followed by a fenced code block containing "Verdict: GAPS"; When approve results; Then exit 0 · status verified.
- F2 [untestable] REQ-APR-001: S3 and R2 don't say the verify check is OK, so R2 can fail on the check with today's code and its red run would not reproduce the bug; N1–N4, B1 and S2 only imply S1's setup; R1 "quotes the GAPS verdict" doesn't say what text → fixed: S3 and R2 Givens read "a mini change in verifying, verify check OK, ## Verification ending with …"; N1–N4, B1 and S2 Givens start "the S1 change, but"; R1 Then reads "the error contains 'GAPS — F1 open'".
- F3 [weak-negative] REQ-APR-001: R2 asserts no visible error, and "nothing else changes" can't be checked → fixed: R2 Then reads "exit 1 · the error contains 'GAPS' · status stays verifying · spec.md is unchanged".
- F4 [coverage] REQ-APR-001: the mini path (advance verified, separate code in cmd_advance) is tested only with PASS and GAPS, so a mini check that refuses only GAPS passes every test → fixed: add N5: Given a mini change in verifying, verify check OK, no Verdict line; When advance verified; Then exit 1 · error "no verdict" · status stays verifying · spec.md is unchanged.
- F5 [contradiction] REQ-APR-001: project rule 5 asks the change to state how existing specs are handled; the spec says nothing about changes already in verifying (written before a `Verdict:` line was required) or already verified under a GAPS verdict → fixed: add to Scope "Changes existing behavior": "Changes already in verifying need a `Verdict:` line before approve results or advance verified; changes already verified or archived are not re-checked (archive does not read the verdict)."
- F6 [ambiguity] REQ-APR-002: "a fingerprint of its content" is defined only in Design notes; "whitespace normalized" doesn't say whether re-wrapping a paragraph is a change; excluding ## Approvals isn't in the contract; S1 "the front matter holds a fingerprint" names no key → fixed: add to the requirement text: "The fingerprint is the first 12 hex digits of a SHA-256 over the constitution with HTML comments and blank lines removed and runs of whitespace inside each line collapsed (re-wrapping a paragraph is a change); it excludes the ## Approvals section and the front-matter keys approved, fingerprint and approved_level." S1 Then reads "the front matter holds `fingerprint: <12 hex digits>` and `approved_level: <level>`". Add B2: Given an approved constitution with a double space added inside one rule; When status; Then no change note · exit 0 · nothing is rewritten. Add B3: Given an approved constitution with a row added by hand to ## Approvals; When status; Then no change note · exit 0 · nothing is rewritten.
- F7 [ambiguity] REQ-APR-002: "every other approval gate" is undefined; the design blocks every command that runs the check (check itself, approve amend, advance verified, archive), and only approve plan is tested → fixed: the statement names them: "approve spec, plan, results and amend, advance verified and archive shall refuse, and check shall report it as an error and exit 1; approve constitution, new and the other advance moves are not blocked". Add N5: Given that changed constitution and any active change; When check; Then exit 1 · the error says the constitution changed since approval. Add N6: Given that changed constitution and a mini change in verifying, verify check otherwise OK, "Verdict: PASS"; When advance verified; Then exit 1 · the error says the constitution changed since approval · status stays verifying.
- F8 [contradiction] REQ-APR-002: N3 catches a hand-edited fingerprint, but a deleted fingerprint line (or a broken `---` front matter) makes the file look like an earlier version (N4), which silences detection and lets an edited level apply at once (REQ-APR-003 N2) → Q6
- F9 [weak-negative] REQ-APR-002: N1 and N2 don't assert that the files are unchanged, and N2's Given doesn't say what makes the constitution "approved" → fixed: N1 Then adds "spec.md is unchanged"; N2 Given reads "approved: yes and a fingerprint that matches the content"; N2 Then adds "the constitution file is unchanged".
- F10 [scope] REQ-APR-002: refusing an unchanged re-approval (N2), refusing an invalid level at approval (REQ-APR-003 N1) and labelling a lowered level are not in Scope "In", and N2 changes today's behavior (a repeat approval is recorded) without saying so → fixed: Scope "In" adds "approve constitution refusing an unchanged constitution or an invalid level, and labelling a lowered level"; Scope "Changes existing behavior" adds "re-approving an unchanged constitution was recorded again; now it is refused".
- F11 [coverage] REQ-APR-002: no scenario covers a constitution that was never approved ("approved: no", no fingerprint, as init writes it); today it blocks nothing, so an edited approved constitution would block every gate while a never-approved one blocks none → Q7
- F12 [ambiguity] REQ-APR-002: only the text output of status is specified; `status --json` is a documented CLI output (project rule 1) and gets no fields for a changed constitution or a pending level → fixed: R1 Then adds "`status --json` has `constitution_changed: true` and `constitution_approved: true`"; REQ-APR-003 R1 Then adds "`status --json` has `assurance: internal` and `assurance_pending: prototype`".
- F13 [ambiguity] REQ-APR-003: "apply the assurance level" doesn't say where; S2 doesn't say which cell carries the "lowered" note; B1 "nothing else changes until re-approval" can't be tested → fixed: reword the first clause to "sdd.py shall use the level recorded at its last approval as the project level: the default and the floor for new, the floor in check, and the level status shows"; S2 Then reads "the row's Evidence cell ends with the 'assurance lowered' note"; B1 Then reads "the change is created at internal · status shows 'internal (production pending approval)'".
- F14 [coverage] REQ-APR-003: missing are the defect's second path (an explicit lower level passed to new while it is pending), re-approval at a raised or unchanged level, and a deleted assurance line → fixed: add N3: Given approved at internal, edited to "assurance: prototype", not re-approved; When new demo --assurance prototype; Then exit 1 · the error says it is lower than the project level 'internal' · no change folder is created. Add B2: Given approved at internal, edited to "assurance: production"; When approve constitution; Then exit 0 · the row has no "lowered" note · later changes are created at production. Add B3: Given approved at internal, a project rule added, level unchanged; When approve constitution; Then exit 0 · the row has no "lowered" note. N1 also covers a deleted assurance line, and its Then adds "the constitution file is unchanged".
- F15 [coverage] REQ-APR-003: with N2 (and REQ-APR-002 N4), a constitution approved by an earlier version stays unprotected after the upgrade: an edit to "assurance: prototype" takes effect at once, and its first approval can't label the lowering. Rule 5 makes that the right default, but the spec doesn't say so → fixed: add to Known gaps "A constitution approved by an earlier version is unprotected until its first approval under this version; that approval records a fingerprint but cannot label a lowering." Add S4: Given a constitution approved by an earlier version at internal, then edited to "assurance: prototype"; When approve constitution; Then exit 0 · `fingerprint` and `approved_level: prototype` are recorded · the row has no "lowered" note.

- Q6 A constitution with no readable fingerprint counts as written by an earlier version (REQ-APR-002 N4, REQ-APR-003 N2). Deleting the fingerprint line or breaking the front matter therefore turns detection off, while editing the line is caught (N3); an agent refused at a gate could do this to get unblocked. How should a missing fingerprint be treated? A) accept it: a missing fingerprint always means an earlier version; list "deleting the fingerprint line defeats detection" in Known gaps B) approve constitution also writes the fingerprint and approved level into its Approvals row; once any constitution row carries a fingerprint, the newest one is the reference, so a missing fingerprint or broken front matter is reported as changed since approval and that row's level stays in force — recommended: B (it closes the one-line bypass; only deleting every fingerprinted row would defeat it)
  - Answer: B — back it up in Approvals; the newest fingerprinted row is the reference (operator, 2026-10-12)
- Q7 A constitution that was never approved ("approved: no", as init writes it) blocks no gate today, and this spec keeps that, so a plan can be approved under rules nobody approved. Should a never-approved constitution block the gates too? A) no: keep today's behavior, add a scenario that pins it, and add a Known gaps line B) yes: every gate except approve constitution refuses until the first approval — recommended: A (it is outside Scope "In", and B changes every new project's first run; a later change can add it)
  - Answer: A — keep today's behavior, pin it with a scenario, add a known gap (operator, 2026-10-12)

## Amendments
<!-- Spec changes after approval, one line each, then `sdd.py approve amend`:
- A1 2026-10-07: <reason> → <what changed> -->
- A1 2026-10-12: Verifier round 1 (fresh session) spec gaps F3–F7, operator chose A for all → REQ-APR-001: numbered list markers count, scenarios B4–B8 pin the exclusions (tables, mid-line, comments); REQ-APR-002: only the trailing Evidence note counts, the front-matter fingerprint is the fallback reference, scenarios N9, N10, S5; REQ-APR-003: a missing or invalid level with no approved level fails closed, scenarios N4–N6; Scope "Changes existing behavior" updated; tasks T42–T52 added

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
| plan | 2026-10-12 | Operator in Claude Code chat, 2026-10-12: "/sdd approve" (gate: plan for 0001-approval-integrity, after the fresh-session Critic round 1 with Q6=B and Q7=A applied) |
| amend | 2026-10-12 | Operator in Claude Code chat, 2026-10-12: "/sdd approve" (amendment A1: Verifier spec gaps F3–F7, all A) |
