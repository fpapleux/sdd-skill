<!-- Verifier: format in method/roles/verifier.md. The operator approves the
results at the third gate (sdd.py approve results). -->

## Verification

- Date: 2026-11-17 · Verifier: subagent (strong)
- Tests: `python3 -m tests.junit_run tests.test_sdd` → Ran 675 tests in 137.106s, OK
- Check: `sdd.py check --stage verify` → result: OK, 0 errors, 2 warnings (T16 pre-existing; the Verifier line, written by this section), run before T25 was appended; after it, the only error is "T25: not done"
- Replay: `sdd.py replay --base deb83e0` → replay: 24 confirmed, 0 mismatch, 0 skipped (T2, T4, T13, T15, T16, T18, T21, T23 confirmed now, as their (after T<n>) reds say)
- Mutate: `sdd.py mutate` → mutate: 151 caught, 0 survived or invalid
- Coverage: not available (coverage.py is not installed)
- Dogfood: `python3 skill/sdd/scripts/sdd.py test component ORC` (development checkout) → "result: 118 passed, 0 failed, 0 errors, 0 skipped (118 tests) in 7.4s", the no-baseline warning, "sorted: 0 regression, 0 expected, 0 outside the change", exit 0; last-run.json and last-run.log held no absolute path. `run-plan all` at verifying refused as REQ-ORC-011 says. The files it wrote (specs/.sdd/runs/, absent before) were deleted; it also rewrote the git-ignored build/junit.xml. It showed that write_atomic leaves its files at mode 0600 (F3).

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-ORC-009.S1 | tests/test_sdd.py::RunPlanStepTests.test_REQ_ORC_009_S1_a_range_prints_its_steps_and_checkpoint | pass | yes |
| REQ-ORC-009.S2 | tests/test_sdd.py::RunPlanStepTests.test_REQ_ORC_009_S2_change_names_a_change_that_is_not_active | pass | yes |
| REQ-ORC-009.S3 | tests/test_sdd.py::RunPlanStepTests.test_REQ_ORC_009_S3_next_is_the_first_unticked_task | pass | yes |
| REQ-ORC-009.B1 | tests/test_sdd.py::RunPlanStepTests.test_REQ_ORC_009_B1_a_one_task_range_is_not_reversed | pass | yes |
| REQ-ORC-009.B2 | tests/test_sdd.py::RunPlanStepTests.test_REQ_ORC_009_B2_next_is_the_default_form | pass | yes |
| REQ-ORC-009.B3 | tests/test_sdd.py::RunPlanEdgeTests.test_REQ_ORC_009_B3_a_range_with_nothing_to_do_prints_no_step | pass | yes |
| REQ-ORC-009.B4 | tests/test_sdd.py::RunPlanEdgeTests.test_REQ_ORC_009_B4_next_with_every_task_ticked_has_nothing_to_run | pass | yes |
| REQ-ORC-009.B5 | tests/test_sdd.py::RunPlanEdgeTests.test_REQ_ORC_009_B5_a_word_with_a_quote_is_single_quoted | pass | yes |
| REQ-ORC-009.B6 | tests/test_sdd.py::RunPlanEdgeTests.test_REQ_ORC_009_B6_a_test_line_without_colons_has_no_command | pass | yes |
| REQ-ORC-009.B7 | tests/test_sdd.py::RunPlanEdgeTests.test_REQ_ORC_009_B7_a_task_with_no_test_line_shows_the_template | pass | yes |
| REQ-ORC-009.B8 | tests/test_sdd.py::RunPlanStepTests.test_REQ_ORC_009_B8_a_mini_change_reads_its_design_notes | pass | yes |
| REQ-ORC-009.B10 | tests/test_sdd.py::RunPlanBaselineTests.test_REQ_ORC_009_B10_no_test_report_line_means_no_baseline | pass | yes |
| REQ-ORC-009.B9 | tests/test_sdd.py::RunPlanBaselineTests.test_REQ_ORC_009_B9_a_recorded_baseline_shows_its_time | pass | yes |
| REQ-ORC-010.S1 | tests/test_sdd.py::RunPlanStepTests.test_REQ_ORC_010_S1_a_checkpoint_at_a_prefix_change_and_at_the_range_end | pass | yes |
| REQ-ORC-010.B2 | tests/test_sdd.py::RunPlanStepTests.test_REQ_ORC_010_B2_a_split_prefix_gets_a_checkpoint_after_each_group | pass | yes |
| REQ-ORC-010.B3 | tests/test_sdd.py::RunPlanStepTests.test_REQ_ORC_010_B3_a_task_with_no_scenario_reference_keeps_the_group_open | pass | yes |
| REQ-ORC-010.B4 | tests/test_sdd.py::RunPlanStepTests.test_REQ_ORC_010_B4_a_ticked_task_neither_joins_nor_ends_a_group | pass | yes |
| REQ-ORC-010.B5 | tests/test_sdd.py::RunPlanEdgeTests.test_REQ_ORC_010_B5_no_component_line_skips_the_checkpoints | pass | yes |
| REQ-ORC-011.N1 | tests/test_sdd.py::RunPlanRefusalTests.test_REQ_ORC_011_N1_a_form_run_plan_does_not_take | pass | yes |
| REQ-ORC-011.N2 | tests/test_sdd.py::RunPlanRefusalTests.test_REQ_ORC_011_N2_a_reversed_range | pass | yes |
| REQ-ORC-011.N3 | tests/test_sdd.py::RunPlanRefusalTests.test_REQ_ORC_011_N3_a_task_that_is_not_in_the_plan | pass | yes |
| REQ-ORC-011.N4 | tests/test_sdd.py::RunPlanRefusalTests.test_REQ_ORC_011_N4_a_change_at_draft | pass | yes |
| REQ-ORC-011.N5 | tests/test_sdd.py::RunPlanRefusalTests.test_REQ_ORC_011_N5_no_active_change | pass | yes |
| REQ-ORC-011.N6 | tests/test_sdd.py::RunPlanRefusalTests.test_REQ_ORC_011_N6_a_change_that_does_not_exist | pass | yes |
| REQ-ORC-011.N7 | tests/test_sdd.py::RunPlanDesignRefusalTests.test_REQ_ORC_011_N7_no_test_one_line | pass | yes |
| REQ-ORC-011.N7 | tests/test_sdd.py::RunPlanDesignRefusalTests.test_REQ_ORC_011_N7_design_line_refusals_come_in_the_spec_order | pass | yes |
| REQ-ORC-011.N8 | tests/test_sdd.py::RunPlanDesignRefusalTests.test_REQ_ORC_011_N8_an_empty_test_command_line_is_not_read_from_prose | pass | yes |
| REQ-ORC-011.N9 | tests/test_sdd.py::RunPlanDesignRefusalTests.test_REQ_ORC_011_N9_a_test_one_quote_that_is_not_closed | pass | yes |
| REQ-ORC-011.N10 | tests/test_sdd.py::RunPlanDesignRefusalTests.test_REQ_ORC_011_N10_a_test_command_quote_that_is_not_closed | pass | yes |
| REQ-ORC-011.N11 | tests/test_sdd.py::RunPlanRefusalTests.test_REQ_ORC_011_N11_no_specs_folder | pass | yes |
| REQ-ORC-011.N12 | tests/test_sdd.py::RunPlanDesignRefusalTests.test_REQ_ORC_011_N12_a_baseline_file_with_no_header | pass | yes |
| REQ-EVD-007.S1 | tests/test_sdd.py::TestStepTests.test_REQ_EVD_007_S1_full_runs_the_suite_records_it_and_reports_its_failures | pass | yes |
| REQ-EVD-007.S2 | tests/test_sdd.py::TestStepTests.test_REQ_EVD_007_S2_component_runs_the_component_command | pass | yes |
| REQ-EVD-007.S3 | tests/test_sdd.py::TestStepTests.test_REQ_EVD_007_S3_a_task_step_runs_the_task_test | pass | yes |
| REQ-EVD-007.S4 | tests/test_sdd.py::TestStepTests.test_REQ_EVD_007_S4_a_failure_of_a_ticked_task_is_a_regression | pass | yes |
| REQ-EVD-007.N1 | tests/test_sdd.py::NoReportTests.test_REQ_EVD_007_N1_no_report_line_in_the_design | pass | yes |
| REQ-EVD-007.N7 | tests/test_sdd.py::NoReportTests.test_REQ_EVD_007_N7_an_empty_report_line_reads_as_absent | pass | yes |
| REQ-EVD-007.N2 | tests/test_sdd.py::NoReportTests.test_REQ_EVD_007_N2_a_stale_report_is_deleted_and_not_read | pass | yes |
| REQ-EVD-007.N3 | tests/test_sdd.py::NoReportTests.test_REQ_EVD_007_N3_a_malformed_report_is_no_report | pass | yes |
| REQ-EVD-007.N4 | tests/test_sdd.py::CannotStartTests.test_REQ_EVD_007_N4_a_command_that_cannot_start | pass | yes |
| REQ-EVD-007.N5 | tests/test_sdd.py::RunOfFilesTests.test_REQ_EVD_007_N5_an_unreadable_last_run_is_kept_as_run_of_unreadable | pass | weak: "the S1 report" is checked by its first and last lines only; the result, failure and sort lines are not asserted → T25 |
| REQ-EVD-007.N6 | tests/test_sdd.py::ExitWarningTests.test_REQ_EVD_007_N6_the_command_fails_but_the_report_shows_no_failure | pass | yes |
| REQ-EVD-007.B1 | tests/test_sdd.py::TestReportTests.test_REQ_EVD_007_B1_a_failure_message_is_cut_at_five_lines | pass | yes |
| REQ-EVD-007.B2 | tests/test_sdd.py::TestReportTests.test_REQ_EVD_007_B2_a_test_with_no_classname_is_named_by_its_name | pass | yes |
| REQ-EVD-007.B3 | tests/test_sdd.py::TestStepTests.test_REQ_EVD_007_B3_a_report_with_no_testcase | pass | yes |
| REQ-EVD-007.B4 | tests/test_sdd.py::TestStepTests.test_REQ_EVD_007_B4_verifying_runs_and_keeps_the_status | pass | yes |
| REQ-EVD-007.B5 | tests/test_sdd.py::RunOfFilesTests.test_REQ_EVD_007_B5_the_previous_run_is_renamed_to_run_of_its_time | pass | yes |
| REQ-EVD-007.B6 | tests/test_sdd.py::RunOfFilesTests.test_REQ_EVD_007_B6_a_run_of_name_that_is_taken_gets_a_number | pass | yes |
| REQ-EVD-007.B6 | tests/test_sdd.py::RunOfFilesTests.test_REQ_EVD_007_B6_a_taken_log_name_also_moves_both_files_on | pass | yes |
| REQ-EVD-007.B7 | tests/test_sdd.py::TestReportTests.test_REQ_EVD_007_B7_a_failure_with_no_message_and_no_text | pass | yes |
| REQ-EVD-007.B8 | tests/test_sdd.py::TestReportTests.test_REQ_EVD_007_B8_the_project_path_is_written_as_a_dot | pass | yes |
| REQ-EVD-008.S1 | tests/test_sdd.py::BaselineRecordTests.test_REQ_EVD_008_S1_baseline_records_the_tests_that_pass | pass | yes |
| REQ-EVD-008.S2 | tests/test_sdd.py::BaselineRecordTests.test_REQ_EVD_008_S2_a_later_run_sorts_against_the_baseline | pass | yes |
| REQ-EVD-008.N1 | tests/test_sdd.py::BaselineRefusalTests.test_REQ_EVD_008_N1_a_baseline_is_never_rerun | pass | yes |
| REQ-EVD-008.N2 | tests/test_sdd.py::BaselineRefusalTests.test_REQ_EVD_008_N2_a_baseline_after_a_task_is_ticked | pass | yes |
| REQ-EVD-008.N3 | tests/test_sdd.py::BaselineRefusalTests.test_REQ_EVD_008_N3_a_baseline_at_verifying | pass | yes |
| REQ-EVD-008.N4 | tests/test_sdd.py::BaselineRefusalTests.test_REQ_EVD_008_N4_a_baseline_needs_a_test_report_line | pass | yes |
| REQ-EVD-008.N5 | tests/test_sdd.py::BaselineRefusalTests.test_REQ_EVD_008_N5_a_baseline_run_that_leaves_no_report | pass | yes |
| REQ-EVD-008.B2 | tests/test_sdd.py::BaselineRecordTests.test_REQ_EVD_008_B2_baseline_outside_a_git_repository | pass | yes |
| REQ-EVD-008.B3 | tests/test_sdd.py::BaselineReuseTests.test_REQ_EVD_008_B3_a_baseline_from_a_reused_run | pass | yes |
| REQ-EVD-008.B1 | tests/test_sdd.py::BaselineRecordTests.test_REQ_EVD_008_B1_a_baseline_with_no_test_that_passed | pass | yes |
| REQ-EVD-009.S1 | tests/test_sdd.py::ReuseTests.test_REQ_EVD_009_S1_the_last_run_is_reused_on_unchanged_code | pass | yes |
| REQ-EVD-009.S2 | tests/test_sdd.py::ReuseTests.test_REQ_EVD_009_S2_a_reused_run_is_sorted_against_the_current_tasks | pass | yes |
| REQ-EVD-009.S3 | tests/test_sdd.py::ReuseTests.test_REQ_EVD_009_S3_rerun_runs_the_step_anyway | pass | yes |
| REQ-EVD-009.B1 | tests/test_sdd.py::ReuseKeyTests.test_REQ_EVD_009_B1_a_changed_byte_runs_the_step | pass | yes |
| REQ-EVD-009.B2 | tests/test_sdd.py::ReuseKeyTests.test_REQ_EVD_009_B2_a_new_untracked_file_runs_the_step | pass | yes |
| REQ-EVD-009.B3 | tests/test_sdd.py::ReuseKeyTests.test_REQ_EVD_009_B3_a_new_ignored_file_keeps_the_reuse | pass | yes |
| REQ-EVD-009.B4 | tests/test_sdd.py::ReuseKeyTests.test_REQ_EVD_009_B4_a_new_commit_with_no_content_change_runs_the_step | pass | yes |
| REQ-EVD-009.B5 | tests/test_sdd.py::ReuseKeyTests.test_REQ_EVD_009_B5_only_the_last_run_is_reused_and_only_for_its_step | pass | yes |
| REQ-EVD-009.B6 | tests/test_sdd.py::ReuseKeyTests.test_REQ_EVD_009_B6_a_deleted_tracked_file_runs_the_step | pass | yes |
| REQ-EVD-009.B7 | tests/test_sdd.py::ReuseKeyTests.test_REQ_EVD_009_B7_a_last_run_of_another_change_runs_the_step | pass | yes |
| REQ-EVD-009.N1 | tests/test_sdd.py::ReuseKeyTests.test_REQ_EVD_009_N1_outside_a_git_repository_every_step_runs | pass | yes |
| REQ-EVD-009.N2 | tests/test_sdd.py::ReuseKeyTests.test_REQ_EVD_009_N2_before_the_first_commit_every_step_runs | pass | yes |
| REQ-EVD-010.S1 | tests/test_sdd.py::RedGreenTests.test_REQ_EVD_010_S1_red_writes_the_failure_message | pass | yes |
| REQ-EVD-010.S2 | tests/test_sdd.py::RedGreenTests.test_REQ_EVD_010_S2_green_writes_passed_and_keeps_the_red_line | pass | yes |
| REQ-EVD-010.N1 | tests/test_sdd.py::EvidenceRefusalTests.test_REQ_EVD_010_N1_red_refused_when_the_test_passes | pass | yes |
| REQ-EVD-010.N2 | tests/test_sdd.py::EvidenceRefusalTests.test_REQ_EVD_010_N2_red_refused_when_the_test_errors | pass | yes |
| REQ-EVD-010.N3 | tests/test_sdd.py::EvidenceRefusalTests.test_REQ_EVD_010_N3_red_refused_when_the_test_is_not_in_the_report | pass | yes |
| REQ-EVD-010.N4 | tests/test_sdd.py::EvidenceRefusalTests.test_REQ_EVD_010_N4_green_refused_when_the_test_still_fails | pass | yes |
| REQ-EVD-010.N5 | tests/test_sdd.py::EvidenceRefusalTests.test_REQ_EVD_010_N5_red_refused_when_the_run_has_no_test_report | pass | yes |
| REQ-EVD-010.N6 | tests/test_sdd.py::EvidenceBeforeRunTests.test_REQ_EVD_010_N6_a_ticked_task_is_refused | pass | yes |
| REQ-EVD-010.N7 | tests/test_sdd.py::EvidenceBeforeRunTests.test_REQ_EVD_010_N7_green_with_an_empty_red_line_is_refused | pass | yes |
| REQ-EVD-010.N8 | tests/test_sdd.py::EvidenceRefusalTests.test_REQ_EVD_010_N8_red_refused_when_two_tests_match | pass | yes |
| REQ-EVD-010.B1 | tests/test_sdd.py::RedGreenTests.test_REQ_EVD_010_B1_the_old_red_text_is_replaced_and_a_line_without_colons_is_the_name | pass | yes |
| REQ-EVD-010.B2 | tests/test_sdd.py::RedGreenTests.test_REQ_EVD_010_B2_a_failure_with_no_message_writes_failed | pass | yes |
| REQ-EVD-010.B4 | tests/test_sdd.py::RedGreenTests.test_REQ_EVD_010_B4_a_missing_red_line_is_inserted_after_the_test_line | pass | yes |
| REQ-EVD-010.B5 | tests/test_sdd.py::EvidenceMatchTests.test_REQ_EVD_010_B5_a_reused_run_writes_the_line_with_its_time | pass | yes |
| REQ-EVD-010.N9 | tests/test_sdd.py::EvidenceRefusalTests.test_REQ_EVD_010_N9_red_refused_when_the_test_is_skipped | pass | yes |
| REQ-EVD-010.N10 | tests/test_sdd.py::EvidenceBeforeRunTests.test_REQ_EVD_010_N10_two_red_lines_are_refused | pass | yes |
| REQ-EVD-010.B6 | tests/test_sdd.py::EvidenceMatchTests.test_REQ_EVD_010_B6_a_message_with_a_comment_marker_writes_failed | pass | yes |
| REQ-EVD-010.B3 | tests/test_sdd.py::EvidenceMatchTests.test_REQ_EVD_010_B3_a_name_that_only_ends_with_the_part_does_not_match | pass | yes |
| REQ-EVD-011.N1 | tests/test_sdd.py::StepRefusalTests.test_REQ_EVD_011_N1_no_specs_folder | pass | yes |
| REQ-EVD-011.N2 | tests/test_sdd.py::StepRefusalTests.test_REQ_EVD_011_N2_no_active_change | pass | yes |
| REQ-EVD-011.N3 | tests/test_sdd.py::StepRefusalTests.test_REQ_EVD_011_N3_a_change_that_does_not_exist | pass | yes |
| REQ-EVD-011.N4 | tests/test_sdd.py::StepRefusalTests.test_REQ_EVD_011_N4_a_change_at_draft | pass | yes |
| REQ-EVD-011.N5 | tests/test_sdd.py::StepRefusalTests.test_REQ_EVD_011_N5_a_step_test_does_not_take | pass | yes |
| REQ-EVD-011.N6 | tests/test_sdd.py::StepKindRefusalTests.test_REQ_EVD_011_N6_a_task_that_is_not_in_the_plan | pass | yes |
| REQ-EVD-011.N7 | tests/test_sdd.py::StepKindRefusalTests.test_REQ_EVD_011_N7_a_prefix_the_change_does_not_declare | pass | yes |
| REQ-EVD-011.N8 | tests/test_sdd.py::StepKindRefusalTests.test_REQ_EVD_011_N8_red_needs_a_task_step | pass | yes |
| REQ-EVD-011.N9 | tests/test_sdd.py::StepKindRefusalTests.test_REQ_EVD_011_N9_red_and_green_together | pass | yes |
| REQ-EVD-011.N10 | tests/test_sdd.py::StepDesignRefusalTests.test_REQ_EVD_011_N10_no_test_component_line | pass | yes |
| REQ-EVD-011.N11 | tests/test_sdd.py::StepDesignRefusalTests.test_REQ_EVD_011_N11_a_test_command_quote_that_is_not_closed | pass | yes |
| REQ-EVD-011.N12 | tests/test_sdd.py::StepDesignRefusalTests.test_REQ_EVD_011_N12_a_task_with_no_test_line | pass | yes |
| REQ-EVD-011.N13 | tests/test_sdd.py::StepRefusalTests.test_REQ_EVD_011_N13_the_status_comes_before_the_step | pass | yes |
| REQ-EVD-011.N14 | tests/test_sdd.py::ReportPathRefusalTests.test_REQ_EVD_011_N14_a_path_outside_the_project | pass | yes |
| REQ-EVD-011.N14 | tests/test_sdd.py::ReportPathRefusalTests.test_REQ_EVD_011_N14_the_path_is_read_after_the_design_line_and_before_the_test_line | pass | yes |
| REQ-EVD-011.N15 | tests/test_sdd.py::ReportPathRefusalTests.test_REQ_EVD_011_N15_an_absolute_path | pass | yes |
| REQ-EVD-011.N19 | tests/test_sdd.py::ReportPathRefusalTests.test_REQ_EVD_011_N19_a_file_git_tracks | pass | yes |
| REQ-EVD-011.N20 | tests/test_sdd.py::ReportPathRefusalTests.test_REQ_EVD_011_N20_a_folder | pass | yes |
| REQ-EVD-011.N21 | tests/test_sdd.py::ReportPathRefusalTests.test_REQ_EVD_011_N21_a_symlink_that_leads_outside_the_project | pass | yes |
| REQ-EVD-011.N16 | tests/test_sdd.py::StepDesignRefusalTests.test_REQ_EVD_011_N16_a_test_line_with_no_double_colon | pass | yes |
| REQ-EVD-011.N17 | tests/test_sdd.py::StepDesignRefusalTests.test_REQ_EVD_011_N17_a_placeholder_test_line | pass | yes |
| REQ-EVD-011.N18 | tests/test_sdd.py::StepDesignRefusalTests.test_REQ_EVD_011_N18_a_baseline_file_with_no_header | pass | yes |

Red evidence:
- Every `red:` line is an assertion failure about the behavior. The stub notes (T8, T10, T13, T17, T22, T23, T24: an error first, stubbed so the assertion fails) follow the implementer table. T18's red writes "[comment opener]" for the `<!--` the run printed, because the real text would open an HTML comment in tasks.md; acceptable.
- Pre-existing parts, each sound by reading the code at the task named, and each guarded by a caught mutation: T2 B5 (after T1: task_command used shlex.join; M14); T4 N11, N5, N6 (after T1: require_init and current refuse before run-plan's own code); T15 B3, B4, N1, N2 (after T14: reuse already needed the same non-null commit, and with nothing else compared an ignored file kept the reuse; M98, M99, M102); T16 all (after T15: reuse doesn't depend on the step, and write_baseline takes the record's time; M104); T18 B3, B5 (after T17: equals-or-ends-with-dot match, record time; M118); T21 N1, N2, N3, N5 (after T6); T23 N18 (after T5: read_baseline refuses before the run).

Method files (project rule 1, by review against design.md "Method changes"): implement.md (run-plan before the first task; --red, code, --green; component and full through SDD test; the reworded checkpoint rule; the report first, last-run.log only when needed; sort-failures kept for a design with no Test report; baseline step; commit the run files), implementer.md steps 2, 3, 5 and the checkpoint row, verify.md step 4 and verifier.md step 1 (SDD test full --rerun), format.md (Test report line, first-list-line reading of the four lines, Run files, red/green written as (sdd test <time>)), overview.md rows, SKILL.md implement row, both templates (- Test report:), tests/junit_run.py and build/ in .gitignore: all present and as designed, except F5. This verification ran the full suite with the design's Test command, not `SDD test full --rerun`, because the pinned tool (rule 7) has no test command yet.

Findings:
- F1 (weak test) REQ-EVD-007.N5: the Then says "the S1 report", but the test checks only the report's first and last lines; the result, failure and sort lines are not asserted → task T25.
- F2 (spec gap, contradiction) REQ-ORC-009 / REQ-ORC-010: ORC-009 says a range with no unticked task prints "only the first line, the baseline line, its done lines and nothing to run", while ORC-010's clause prints the skipped line whenever the design has no Test component line. The code prints "component checkpoints skipped: …" as the second line of such a plan (checked: all tasks ticked, no Test component line), and no row covers the case. → asked the operator: A) amend now: say whether the skipped line is printed when there is nothing to run, with a row and a task (and a code fix if it must go); B) accept it as a known gap.
- F3 (spec gap) REQ-EVD-007, 008, 010: write_atomic writes a temporary file from mkstemp (mode 0600) and swaps it in, so tasks.md (or a mini change's spec.md) after `test --red`/`--green`, baseline.txt and the run files end up readable by the owner only (checked: a 0644 file became 0600). The spec says nothing else in the file changes but nothing about its mode. → asked the operator: A) amend now: keep an existing file's mode and give a new file the umask default, with a row and a task; B) accept it as a known gap.
- F4 (spec gap, rule 4) Rules no scenario or test catches, so they have no mutation entry: (a) reuse's same-command key of REQ-EVD-009: removing `and last["command"] == command` in a scratch copy left all 156 REQ_EVD_ tests passing, and since design.md is under specs/ (outside the digest), a changed Test command line would reuse the old command's run; (b) the reused suffix on the no-report result line; (c) a submodule in the digest; (d) skipping a tracked file deleted in the working tree (B6 passes with the skip or with the digest failing); (e) write_evidence's block ending at a heading and its keeping of CRLF line endings. → asked the operator: A) amend now: add rows (at least (a), as an EVD-009 boundary row: the Test command changed, fake.py is run), with tasks and mutations; B) accept them as known gaps.
- F5 (method review) overview.md's `SDD test` row says "Exit 1 = a regression or a failed run with no report", leaving out the exit-code warning (REQ-EVD-007.N6) and refusals; and implement.md/implementer.md send every task through `SDD test T<n> --red`/`--green`, while this repository's test lines name a test class, which matches no single test in the report, so the next change here would be refused at every red run with no guidance → `also:` on task T25.

Verdict: GAPS — 5 findings (T25 added for F1 and F5; F2, F3 and F4 awaiting the operator)

### Pass 2

- Date: 2026-11-25 · Verifier: subagent (strong)
- Scope: the changes since pass 1 (amendment A4, T25-T27, M152-M153, write_atomic, the F5 method edits); the rest of pass 1 stands.
- Tests: `python3 -m unittest tests.test_sdd` → Ran 677 tests in 155.311s, OK
- Check: `sdd.py check --stage verify` → result: OK, 0 errors, 4 warnings (T16, T25, T27 pre-existing, as recorded; size cap: 403 lines > 400 for standard, new with T25-T27 and M152-M153, not blocking)
- Mutate: full `sdd.py mutate` not run (151 entries, too long for this pass); M152 and M153 applied by hand in a scratch copy outside the repo (removed after), each with its task's test: M152 (mode = 0o600) → test_REQ_EVD_010_B7 failed, caught; M153 (`and True` for the command comparison) → test_REQ_EVD_009_B8 failed, caught. M1-M151 were caught in pass 1, and the only code change since is the added lines in write_atomic.
- Replay: not rerun; T26 has a real red, T25 and T27 are pre-existing (T27's reason confirmed by M153).

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-EVD-007.N5 | tests/test_sdd.py::RunOfFilesTests.test_REQ_EVD_007_N5_an_unreadable_last_run_is_kept_as_run_of_unreadable | pass | yes (the warning, the step line, the result counts, the failure and its message, the S1 sort lines and the log line) |
| REQ-EVD-010.B7 | tests/test_sdd.py::EvidenceMatchTests.test_REQ_EVD_010_B7_an_existing_tasks_file_keeps_its_mode | pass | yes (the S1 red line and nothing else in tasks.md, mode 0644, exit 0) |
| REQ-EVD-009.B8 | tests/test_sdd.py::ReuseKeyTests.test_REQ_EVD_009_B8_a_changed_test_command_runs_the_new_command | pass | yes (fake2.py run once, fake.py's counter still at the first run only, no "reused" on the result line, exit 0) |

write_atomic: correct and minimal. It takes the existing file's mode (`st_mode & 0o7777`) or, for a new file, 0o666 less the umask (read by setting and restoring it), and chmods the temporary file before `os.replace`; a chmod failure falls into the existing cleanup that deletes the temporary file. Nothing else changed.

Findings from pass 1:
- F1 → closed: T25; N5 now asserts the whole S1 report.
- F2 → closed: operator chose B; A4 Known gap "A range with nothing left to run still prints \"component checkpoints skipped\"…", which matches the code as checked in pass 1.
- F3 → closed: operator chose A; REQ-EVD-010.B7, T26 (real red: 384 != 420), M152 caught; a new file's mode is an A4 Known gap, which reads accurately (the umask default, from the code above).
- F4 → closed: operator chose A for (a): REQ-EVD-009.B8, T27, M153 caught; (b)-(e) are an A4 Known gap that names exactly the four rules pass 1 listed.
- F5 → closed: overview.md's `SDD test` row now lists the exit-code warning (N6) and refusals; implement.md step 3 and implementer.md step 5 say a test line naming a group of tests is refused by --red and --green, and to name one test or record by hand. This matches the finding.

New findings: none.

Verdict: PASS
