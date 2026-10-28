<!-- Verifier: format in method/roles/verifier.md. The operator approves the
results at the third gate (sdd.py approve results). -->

## Verification

- Date: 2026-10-28 · Verifier: subagent (strong)
- Tests: `python3 -m unittest tests.test_sdd` → Ran 531 tests in 66.840s, OK
- Check: `sdd.py check --stage verify` → result: OK, 0 errors, 30 warnings (24 pre-existing red runs; 6 about Critic rounds 1-2 auditing the removed REQ-ORC-007, REQ-ORC-008 and REQ-DEF-005)
- Replay: `sdd.py replay --base df2fc46` → replay: 68 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` → mutate: 56 caught, 0 survived or invalid
- Coverage: not available (coverage.py is not installed)

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-EVD-004.N1 | tests/test_sdd.py::ComponentCommandTests.test_REQ_EVD_004_N1_component_command_without_prefix_is_an_error | pass | yes |
| REQ-EVD-004.S1 | tests/test_sdd.py::ComponentCommandTests.test_REQ_EVD_004_S1_valid_component_command_raises_no_message | pass | yes |
| REQ-EVD-004.N2 | tests/test_sdd.py::ComponentCommandTests.test_REQ_EVD_004_N2_component_command_with_unclosed_quote_is_an_error | pass | yes |
| REQ-EVD-004.N3 | tests/test_sdd.py::ComponentCommandTests.test_REQ_EVD_004_N3_second_component_line_is_an_error | pass | yes |
| REQ-EVD-004.B1 | tests/test_sdd.py::ComponentCommandTests.test_REQ_EVD_004_B1_no_component_command_warns | pass | yes |
| REQ-EVD-004.B2 | tests/test_sdd.py::ComponentCommandTests.test_REQ_EVD_004_B2_empty_component_command_warns | pass | yes |
| REQ-EVD-004.B5 | tests/test_sdd.py::ComponentCommandTests.test_REQ_EVD_004_B5_component_line_without_list_marker_does_not_count | pass | yes |
| REQ-EVD-004.B3 | tests/test_sdd.py::ComponentCommandTests.test_REQ_EVD_004_B3_spec_stage_ignores_the_component_command | pass | yes |
| REQ-EVD-004.B6 | tests/test_sdd.py::ComponentCommandTests.test_REQ_EVD_004_B6_mini_change_reads_its_design_notes | pass | yes |
| REQ-DEF-001.S1 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_S1_first_defect_creates_the_log | pass | yes |
| REQ-DEF-001.S2 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_S2_next_number_is_highest_plus_one | pass | yes |
| REQ-DEF-001.S3 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_S3_capability_option_names_the_capability | pass | yes |
| REQ-DEF-001.N1 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_N1_unknown_severity_is_a_usage_error | pass | yes |
| REQ-DEF-001.N2 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_N2_name_without_requirement_id_asks_for_capability | pass | yes |
| REQ-DEF-001.N4 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_N4_empty_test_name_refused | pass | yes |
| REQ-DEF-001.N7 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_N7_capability_must_be_a_known_prefix | pass | yes |
| REQ-DEF-001.N8 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_N8_unknown_change_refused | pass | yes |
| REQ-DEF-001.N6 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_N6_no_active_change_refused | pass | yes |
| REQ-DEF-001.N5 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_N5_one_open_defect_per_test | pass | yes |
| REQ-DEF-001.B1 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_B1_closed_defect_does_not_block_a_new_one | pass | yes |
| REQ-DEF-001.B2 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_B2_pipe_in_the_test_name_is_escaped | pass | yes |
| REQ-DEF-001.B3 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_B3_first_requirement_id_in_the_name_counts | pass | yes |
| REQ-DEF-001.B4 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_B4_capability_option_wins_over_the_name | pass | yes |
| REQ-DEF-001.B5 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_B5_title_only_file_gets_the_table_appended | pass | yes |
| REQ-DEF-001.B6 | tests/test_sdd.py::DefectAddTests.test_REQ_DEF_001_B6_any_change_status_may_record_a_defect | pass | yes |
| REQ-EVD-005.S1 | tests/test_sdd.py::SortFailuresTests.test_REQ_EVD_005_S1_regression_and_expected_failures_are_sorted | pass | yes |
| REQ-EVD-005.S2 | tests/test_sdd.py::SortFailuresTests.test_REQ_EVD_005_S2_names_outside_the_change_are_sorted_outside | pass | yes |
| REQ-EVD-005.N1 | tests/test_sdd.py::SortFailuresTests.test_REQ_EVD_005_N1_unreadable_file_refused | pass | yes |
| REQ-EVD-005.N2 | tests/test_sdd.py::SortFailuresTests.test_REQ_EVD_005_N2_blank_lines_and_duplicate_names_skipped | pass | yes |
| REQ-EVD-005.N3 | tests/test_sdd.py::SortFailuresTests.test_REQ_EVD_005_N3_no_active_change_refused | pass | yes |
| REQ-EVD-005.N4 | tests/test_sdd.py::SortFailuresTests.test_REQ_EVD_005_N4_unknown_change_refused | pass | yes |
| REQ-EVD-005.B1 | tests/test_sdd.py::SortFailuresTests.test_REQ_EVD_005_B1_empty_file_sorts_nothing | pass | yes |
| REQ-EVD-005.B2 | tests/test_sdd.py::SortFailuresTests.test_REQ_EVD_005_B2_first_id_that_decides_is_printed | pass | yes |
| REQ-EVD-005.B3 | tests/test_sdd.py::SortFailuresTests.test_REQ_EVD_005_B3_scenario_no_task_plans_prints_no_task | pass | yes |
| REQ-EVD-005.B4 | tests/test_sdd.py::SortFailuresTests.test_REQ_EVD_005_B4_hyphen_form_in_any_case_is_recognized | pass | yes |
| REQ-DEF-002.S1 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_S1_decide_writes_the_decision_and_the_evidence | pass | yes |
| REQ-DEF-002.S2 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_S2_decision_can_be_changed_while_open | pass | yes |
| REQ-DEF-002.N6 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_N6_decision_without_evidence_refused | pass | yes |
| REQ-DEF-002.N1 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_N1_unknown_decision_is_a_usage_error | pass | yes |
| REQ-DEF-002.N2 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_N2_unknown_defect_id_refused | pass | yes |
| REQ-DEF-002.N3 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_N3_malformed_defect_id_refused | pass | yes |
| REQ-DEF-002.N4 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_N4_closed_defect_cannot_be_decided | pass | yes |
| REQ-DEF-002.N5 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_N5_missing_log_refused | pass | yes |
| REQ-DEF-002.B2 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_B2_same_decision_and_evidence_leaves_the_file_untouched | pass | yes |
| REQ-DEF-002.B3 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_B3_pipe_in_the_evidence_is_escaped | pass | yes |
| REQ-DEF-002.B4 | tests/test_sdd.py::DefectDecideTests.test_REQ_DEF_002_B4_line_breaks_in_the_evidence_become_spaces | pass | yes |
| REQ-DEF-003.S1 | tests/test_sdd.py::DefectCloseTests.test_REQ_DEF_003_S1_close_writes_status_and_close_evidence | pass | yes |
| REQ-DEF-003.S2 | tests/test_sdd.py::DefectCloseTests.test_REQ_DEF_003_S2_wont_fix_defect_can_be_closed | pass | yes |
| REQ-DEF-003.N6 | tests/test_sdd.py::DefectCloseTests.test_REQ_DEF_003_N6_close_without_evidence_refused | pass | yes |
| REQ-DEF-003.N1 | tests/test_sdd.py::DefectCloseTests.test_REQ_DEF_003_N1_undecided_defect_cannot_be_closed | pass | yes |
| REQ-DEF-003.N2 | tests/test_sdd.py::DefectCloseTests.test_REQ_DEF_003_N2_closed_defect_cannot_be_closed_again | pass | yes |
| REQ-DEF-003.B1 | tests/test_sdd.py::DefectCloseTests.test_REQ_DEF_003_B1_later_defect_can_be_closed | pass | yes |
| REQ-DEF-004.S1 | tests/test_sdd.py::DefectCountTests.test_REQ_DEF_004_S1_status_counts_the_open_defects | pass | yes |
| REQ-DEF-004.S2 | tests/test_sdd.py::DefectCountTests.test_REQ_DEF_004_S2_check_counts_the_open_defects | pass | yes |
| REQ-DEF-004.N1 | tests/test_sdd.py::DefectCountTests.test_REQ_DEF_004_N1_status_counts_without_an_active_change | pass | yes |
| REQ-DEF-004.B1 | tests/test_sdd.py::DefectCountTests.test_REQ_DEF_004_B1_no_log_gives_zeros_and_no_line | pass | yes |
| REQ-DEF-004.B2 | tests/test_sdd.py::DefectCountTests.test_REQ_DEF_004_B2_all_closed_gives_zeros_and_no_line | pass | yes |
| REQ-DEF-004.B3 | tests/test_sdd.py::DefectCountTests.test_REQ_DEF_004_B3_open_defects_do_not_fail_a_check | pass | yes |
| REQ-DEF-006.N1 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_N1_invalid_severity_row_refused_by_defect_add | pass | yes |
| REQ-DEF-006.N7 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_N7_wrong_header_refused | pass | yes |
| REQ-DEF-006.N6 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_N6_row_with_eight_cells_refused | pass | yes |
| REQ-DEF-006.N5 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_N5_repeated_defect_id_refused | pass | yes |
| REQ-DEF-006.N2 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_N2_invalid_log_is_an_error_at_verify | pass | yes |
| REQ-DEF-006.N3 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_N3_invalid_log_is_a_warning_at_other_stages | pass | yes |
| REQ-DEF-006.N4 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_N4_status_prints_the_problem_and_exits_0 | pass | yes |
| REQ-DEF-006.B1 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_B1_blank_line_and_comment_between_rows_accepted | pass | yes |
| REQ-DEF-006.B2 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_B2_escaped_pipe_in_a_cell_accepted | pass | yes |
| REQ-DEF-006.B3 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_B3_padded_header_and_aligned_separator_accepted | pass | yes |

Matrix: 68 scenarios, 68 yes, 0 weak, 0 wrong. Each test sets up its Given,
runs the command through `sdd.main()` and asserts every Then part; every
failure row compares a snapshot (or the log's bytes) before and after.

Pre-existing red runs (24 tasks: T2, T6-T9, T18, T22, T23, T25, T30, T32,
T35, T37, T48, T52, T55-T58, T63, T64, T66-T68; the 25th `red: pre-existing`
match in tasks.md is the Planner's comment). All are sound. T7, T22, T23,
T57, T63, T64, T66 and T68 are backed by planned mutations that `mutate`
reports caught (M1, M7, M8, M41, M45, M46, M56, M52/M53). The other 16 were
checked by reverting the named earlier task's behavior in a scratch copy of
the checkout and rerunning the test: it fails each time (T2: no-{prefix}
rule inverted; T6: the warning keyed on "no line" only; T8: the call moved
before the stage gate; T9: no Design notes for a mini change; T18, T30: no
active-change lookup; T25: a verified change refused; T32: exit 1 on an
empty file; T35: underscore form only; T37: an earlier decision kept; T48,
T52: close limited to fix-now; T55: log read only with an active change;
T56: a missing log gives None; T58: an open critical defect made an error;
T67: cells split on every pipe).

Method review (project rule 1). Each Scope In line is delivered:
implement.md (ranges `T1-T45`, one authorization, the three test levels,
component checkpoints one per prefix, sort-failures, the three stop
conditions, the end-of-run triage with defect add, decide and close, the
report); implementer.md (own test only; the expected / regression / outside
row); SKILL.md (break = regression; routing row with ranges); format.md and
both templates (the `Test component:` line, the defect log); overview.md
(script rows); spec-author.md and propose.md (what a capability is; the
Spec Author proposes, the operator confirms at the spec gate). No Scope In
line is missing from the method or the code.
- Rule 5: a design without `Test component:` gets a warning only (B1; exit
  0; `Report.ok` counts errors only, so no gate refuses on it). The fixture
  edit to ANL_DESIGN (T5) follows from B1 being new behavior.
- Rule 6: the diff and the change folder hold no personal names, hosts or
  local paths.
- Not findings: README, RELEASE_NOTES and the version (T68's `also:` line,
  rule 9) are not done yet; by precedent they go with the archive commit.
  The Architect and Planner roles name `Test command:` only (as before for
  `Test one:`); the templates and format.md carry the new line.

Findings:
- F1 (missing scenario, rule 4) REQ-DEF-006 states that the second table
  line must be a separator row, and the code refuses one that isn't, but no
  scenario or test proves the refusal (B3 proves only acceptance). Disabling
  the check (`if False:`) leaves the whole suite green, and no planned
  mutation breaks it. The same holds for the row-ID rule (`an ID D<n>`):
  disabling it survives, with no mutation entry. A test needs a scenario
  to name, and adding one changes the locked spec → asked the operator:
  A) amend now (e.g. REQ-DEF-006.N8 a non-separator second line, N9 a row
  ID that isn't D<n>, each with a task and a mutation); B) accept as a
  known gap. → outcome: A (operator, 2026-10-28; amendment A1: N8, N9,
  T69, T70, M57, M58); resolved in round 2.
- F2 (spec gap) A log whose only table line is the header (no separator)
  isn't flagged: REQ-DEF-006 says "the second isn't a separator row" but
  doesn't decide the case where there is no second table line. REQ-DEF-001
  then appends the row as "any other log", and the row becomes the second
  table line, so the log is now invalid: reproduced in a scratch copy,
  `defect add` exits 0, then `status` prints `defect log: specs/defects.md
  line 4: the second table line must be a separator row` and the next
  `defect add` exits 1. → asked the operator: A) amend now (a log whose
  header has no separator row after it is refused, naming the header's
  line; or `defect add` writes the separator before the row), with a
  scenario and a task; B) accept as a known gap. → outcome: A (operator,
  2026-10-28; amendment A1: a missing separator row is refused, N10, T71,
  M59); resolved in round 2.

Verdict: GAPS — 2 findings (F1 and F2 awaiting the operator: A amend now or B known gap; no task added, since each needs a new scenario)

### Round 2

- Date: 2026-10-28 · Verifier: subagent (strong)
- Tests: `python3 -m unittest tests.test_sdd` → Ran 534 tests in 65.029s, OK
- Check: `sdd.py check --stage verify` → result: OK, 0 errors, 32 warnings (26 pre-existing red runs; the same 6 about Critic rounds 1-2 auditing the removed REQ-ORC-007, REQ-ORC-008 and REQ-DEF-005)
- Replay: `sdd.py replay --base df2fc46` → replay: 71 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` → mutate: 59 caught, 0 survived or invalid
- Coverage: not available (coverage.py is not installed)

New rows (amendment A1); the 68 rows of round 1 are unchanged and pass:

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-DEF-006.N8 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_N8_bad_separator_row_refused | pass | yes |
| REQ-DEF-006.N9 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_N9_bad_row_id_refused | pass | yes |
| REQ-DEF-006.N10 | tests/test_sdd.py::DefectLogTests.test_REQ_DEF_006_N10_header_with_no_separator_row_refused | pass | yes |

Matrix: 71 scenarios, 71 yes, 0 weak, 0 wrong. The three new tests use the
`refused` helper (exit 1, the log byte-for-byte unchanged, no other file
changed) and assert the exact error with the file, the line and the problem.

- Pre-existing red runs T69 (after T60) and T70 (after T59) are sound: round 1
  showed the separator and row-ID checks already in the code, and the
  mutations that disable them (M57, M58) are now caught by N8 and N9. T71
  has a real red run (`0 != 1 : D1 added`), and replay confirms it fails at
  the base.
- Since round 1, sdd.py gains only the `len(self.table) == 1` refusal in
  `DefectLog` (3 lines, the A1 statement), and tests/test_sdd.py gains only
  the three tests above. The method files and templates are unchanged. The
  amendment is recorded (A1) and approved ("Approve A1", 2026-10-28).
- F1 and F2 are closed (outcome A, amendment A1). No new findings.

Verdict: PASS
