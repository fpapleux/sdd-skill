<!-- Verifier: format in method/roles/verifier.md. The operator approves the
results at the third gate (sdd.py approve results). -->

## Verification
- Date: 2026-10-21 · Verifier: fresh session (production) — a side session started by the prime session; it did no implementation work on this change and read everything from the files under this folder, the tests and sdd.py
- Tests: `python3 -m unittest tests.test_sdd` → Ran 435 tests, OK (290 before this change; 145 new tests for 143 scenarios: REQ-ANL-006.B3 and REQ-ORC-004.N6 each have two)
- Check: `sdd.py check --stage verify` (pinned tool, `~/.claude/skills/sdd`, a link to the separate `sdd-tool` checkout) → OK, 0 errors, 87 warnings, all of them `pre-existing` tasks (reviewed below); before this record's Verifier line was written there was an 88th, about the missing Verifier line. The development checkout's `analyze` on this change: result OK, 0 errors, 1 warning (the REQ-ANL-005 clause heuristic); `next` prints "1. sdd verify" and the results gate.
- Replay: `sdd.py replay --base HEAD` (development checkout; HEAD is 47f4536, the commit the change started from) → replay: 136 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` (development checkout) and the pinned `sdd.py mutate` (rule 7: it breaks a scratch copy of the development script) → mutate: 143 caught, 11 survived or invalid, both runs. Not clean: finding F1.
- Mutation cross-check, by hand, in scratch copies outside the repository (a script that applies one find text occurring exactly once, runs the scenario's own tests before and after): M1, M4, M9, M13, M16, M19, M22, M24, M30, M40, M41, M45, M60, M67, M75, M80, M86, M100, M120, M128, M137, M140, M154 → 23 of 23 caught (M13 by an error, not an assertion). The five stale entries (M2, M115, M116, M118, M129) re-written against the current code → 5 of 5 caught. Mutants of my own for clauses the plan doesn't break → 28 tried: 15 caught, 13 survived (F2, F6 to F9; one survivor, a split on the first comma only, differs from the original only for three or more references, which no scenario uses). The working tree was unchanged afterwards (same 16 changed paths before and after; all scratch copies were removed).
- Coverage: not available (no coverage tool installed; none was installed)

Scenario matrix: all 143 scenarios of the eleven requirements have a test named for them, and I read each test's setup, action and assertions against the scenario's Given, When and Then. "No file is changed" is asserted by `snapshot()` before and after, "no approval row" and "status unchanged" by `gate_state()`, "no file is created" by the absence of `specs/`. Every test passes. One scenario is `weak` (REQ-ORC-004.S13); the survivors below show test and scenario gaps that no row records.

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-ANL-001.S1 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_S1_analyze_prints_header_scenarios_and_result | pass | yes |
| REQ-ANL-001.S2 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_S2_json_merges_trace_warning_into_checks_keys | pass | yes |
| REQ-ANL-001.S3 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_S3_change_option_analyzes_another_change | pass | yes |
| REQ-ANL-001.N1 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_N1_unknown_change_refused | pass | yes |
| REQ-ANL-001.N2 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_N2_unknown_option_is_usage_error | pass | yes |
| REQ-ANL-001.N3 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_N3_uninitialized_repository_refused | pass | yes |
| REQ-ANL-001.N4 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_N4_no_active_change_refused | pass | yes |
| REQ-ANL-001.N5 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_N5_scenario_without_task_fails_like_check | pass | yes |
| REQ-ANL-001.N6 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_N6_json_with_trace_error_is_not_ok | pass | yes |
| REQ-ANL-001.B1 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_B1_draft_without_tasks_fails_analyze | pass | yes |
| REQ-ANL-001.B2 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_B2_mini_change_has_no_design_finding | pass | yes |
| REQ-ANL-002.S1 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_S1_design_naming_every_requirement_raises_no_finding | pass | yes |
| REQ-ANL-002.N1 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_N1_design_naming_nonexistent_requirement_is_error | pass | yes |
| REQ-ANL-002.N2 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_N2_requirement_the_design_never_names_is_a_warning | pass | yes |
| REQ-ANL-002.N3 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_N3_no_trace_finding_before_designed | pass | yes |
| REQ-ANL-002.N4 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_N4_blocked_change_counts_at_the_status_it_was_blocked_from | pass | yes |
| REQ-ANL-002.N5 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_N5_abandoned_change_gets_no_trace_finding | pass | yes |
| REQ-ANL-002.N6 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_N6_failure_mode_outcome_naming_missing_requirement_is_one_error | pass | yes |
| REQ-ANL-002.B1 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_B1_removed_requirement_is_not_warned_about | pass | yes |
| REQ-ANL-002.B2 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_B2_living_spec_requirement_is_known | pass | yes |
| REQ-ANL-002.B3 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_B3_mention_inside_html_comment_does_not_count | pass | yes |
| REQ-ANL-002.B4 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_B4_underscore_form_does_not_count | pass | yes |
| REQ-ANL-002.B5 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_B5_scenario_reference_names_its_requirement | pass | yes |
| REQ-ANL-002.B6 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_B6_mention_inside_fenced_code_block_does_not_count | pass | yes |
| REQ-ANL-002.B7 | tests/test_sdd.py::DesignTraceTests.test_REQ_ANL_002_B7_one_error_per_distinct_id | pass | yes |
| REQ-ANL-003.S1 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_S1_well_formed_entries_with_na_raise_no_finding | pass | yes |
| REQ-ANL-003.S2 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_S2_lone_none_line_with_reason_is_accepted | pass | yes |
| REQ-ANL-003.S3 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_S3_living_spec_scenario_counts | pass | yes |
| REQ-ANL-003.S4 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_S4_colon_separator_raises_no_finding | pass | yes |
| REQ-ANL-003.N1 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N1_failure_mode_without_arrow_has_no_outcome | pass | yes |
| REQ-ANL-003.N2 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N2_missing_scenario_reference_needs_an_amendment | pass | yes |
| REQ-ANL-003.N3 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N3_na_outcome_needs_three_word_reason | pass | yes |
| REQ-ANL-003.N4 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N4_none_line_needs_three_word_reason | pass | yes |
| REQ-ANL-003.N5 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N5_repeated_fm_number | pass | yes |
| REQ-ANL-003.N6 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N6_bullet_that_is_neither_entry_nor_none_line | pass | yes |
| REQ-ANL-003.N7 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N7_none_line_next_to_an_entry | pass | yes |
| REQ-ANL-003.N8 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N8_outcome_neither_references_nor_na | pass | yes |
| REQ-ANL-003.N9 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N9_no_failure_mode_finding_before_designed | pass | yes |
| REQ-ANL-003.N10 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N10_wrapped_entry_has_no_outcome | pass | yes |
| REQ-ANL-003.N11 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N11_fm1_and_fm01_are_the_same_number | pass | yes |
| REQ-ANL-003.N12 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N12_scenario_dropped_by_modified_restatement_does_not_count | pass | yes |
| REQ-ANL-003.N13 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N13_second_none_line_is_refused | pass | yes |
| REQ-ANL-003.N14 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N14_na_without_separator_is_refused | pass | yes |
| REQ-ANL-003.N15 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N15_bare_none_line_needs_a_reason | pass | yes |
| REQ-ANL-003.B1 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_B1_several_scenario_references_on_one_entry | pass | yes |
| REQ-ANL-003.B2 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_B2_scenario_of_removed_requirement_does_not_count | pass | yes |
| REQ-ANL-003.B3 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_B3_na_reason_of_three_words_is_accepted | pass | yes |
| REQ-ANL-003.B4 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_B4_prose_ignored_and_indented_sub_bullet_checked | pass | yes |
| REQ-ANL-003.B5 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_B5_entry_inside_fenced_code_block_is_ignored | pass | yes |
| REQ-ANL-003.B6 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_B6_entry_inside_html_comment_is_ignored | pass | yes |
| REQ-ANL-004.S1 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_004_S1_one_failure_mode_entry_satisfies_presence_rule | pass | yes |
| REQ-ANL-004.S2 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_004_S2_none_line_satisfies_presence_rule | pass | yes |
| REQ-ANL-004.N1 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_004_N1_production_design_without_failure_modes_section_is_error | pass | yes |
| REQ-ANL-004.N2 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_004_N2_no_presence_finding_before_designed | pass | yes |
| REQ-ANL-004.N3 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_004_N3_section_with_only_a_malformed_bullet_still_lacks_an_entry | pass | yes |
| REQ-ANL-004.B1 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_004_B1_below_production_missing_section_is_a_warning | pass | yes |
| REQ-ANL-004.B2 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_004_B2_section_with_no_bullet_lacks_an_entry | pass | yes |
| REQ-ANL-004.B3 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_004_B3_bullet_starting_with_none_but_not_a_none_line_is_no_entry | pass | yes |
| REQ-ANL-004.B4 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_004_B4_entry_inside_a_comment_does_not_count | pass | yes |
| REQ-ANL-005.S1 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_S1_interface_with_its_contract_entry | pass | yes |
| REQ-ANL-005.S2 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_S2_backticks_around_interface_name_are_trimmed | pass | yes |
| REQ-ANL-005.S3 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_S3_no_interface_line_and_no_contracts_section | pass | yes |
| REQ-ANL-005.N1 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_N1_listed_interface_without_contract_entry | pass | yes |
| REQ-ANL-005.N2 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_N2_interface_line_with_no_name | pass | yes |
| REQ-ANL-005.N3 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_N3_repeated_contract_entry | pass | yes |
| REQ-ANL-005.N4 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_N4_no_contract_finding_at_the_spec_stage | pass | yes |
| REQ-ANL-005.N5 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_N5_contract_heading_with_no_name | pass | yes |
| REQ-ANL-005.N6 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_N6_interface_line_in_fenced_block_is_ignored | pass | yes |
| REQ-ANL-005.B1 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_B1_two_interfaces_one_entry_one_error_for_second | pass | yes |
| REQ-ANL-005.B2 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_B2_entry_with_no_interface_line_is_a_warning | pass | yes |
| REQ-ANL-005.B3 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_B3_interface_listed_twice_counts_once | pass | yes |
| REQ-ANL-005.B4 | tests/test_sdd.py::ContractTests.test_REQ_ANL_005_B4_missing_entry_error_shows_at_implement_stage | pass | yes |
| REQ-ANL-006.S1 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_S1_clauses_all_exercised_raise_no_warning | pass | yes |
| REQ-ANL-006.N1 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_N1_clause_no_scenario_exercises_is_warning | pass | yes |
| REQ-ANL-006.N2 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_N2_one_warning_per_uncovered_clause | pass | yes |
| REQ-ANL-006.N3 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_N3_removed_requirement_gets_no_clause_warning | pass | yes |
| REQ-ANL-006.N4 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_N4_category_cell_does_not_count_as_a_mention | pass | yes |
| REQ-ANL-006.N5 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_N5_only_whole_words_match | pass | yes |
| REQ-ANL-006.B1 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_B1_one_clause_statement_is_not_checked | pass | yes |
| REQ-ANL-006.B2 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_B2_clause_with_no_distinctive_word_is_skipped | pass | yes |
| REQ-ANL-006.B3 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_B3_trailing_semicolon_empty_clause_is_dropped | pass | yes |
| REQ-ANL-006.B3 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_B3_one_clause_with_trailing_semicolon_is_not_checked | pass | yes |
| REQ-ANL-006.B4 | tests/test_sdd.py::ClauseTests.test_REQ_ANL_006_B4_one_distinctive_word_is_enough | pass | yes |
| REQ-ANL-007.S1 | tests/test_sdd.py::BalanceTests.test_REQ_ANL_007_S1_balanced_change_does_not_warn | pass | yes |
| REQ-ANL-007.N1 | tests/test_sdd.py::BalanceTests.test_REQ_ANL_007_N1_happy_heavy_change_warns_with_both_counts | pass | yes |
| REQ-ANL-007.N2 | tests/test_sdd.py::BalanceTests.test_REQ_ANL_007_N2_no_balance_warning_at_prototype | pass | yes |
| REQ-ANL-007.B1 | tests/test_sdd.py::BalanceTests.test_REQ_ANL_007_B1_equal_happy_and_non_happy_does_not_warn | pass | yes |
| REQ-ANL-007.B2 | tests/test_sdd.py::BalanceTests.test_REQ_ANL_007_B2_no_requirements_no_balance_warning | pass | yes |
| REQ-ANL-007.B3 | tests/test_sdd.py::BalanceTests.test_REQ_ANL_007_B3_boundary_counts_as_non_happy | pass | yes |
| REQ-ANL-008.S1 | tests/test_sdd.py::PlanGateAnalyzeTests.test_REQ_ANL_008_S1_warning_alone_does_not_stop_plan_approval | pass | yes |
| REQ-ANL-008.N1 | tests/test_sdd.py::PlanGateAnalyzeTests.test_REQ_ANL_008_N1_plan_approval_refused_on_analyze_error | pass | yes |
| REQ-ANL-008.N2 | tests/test_sdd.py::PlanGateAnalyzeTests.test_REQ_ANL_008_N2_missing_failure_mode_entry_blocks_plan_gate | pass | yes |
| REQ-ANL-008.N3 | tests/test_sdd.py::PlanGateAnalyzeTests.test_REQ_ANL_008_N3_mini_plan_approval_is_unchanged | pass | yes |
| REQ-ANL-008.B1 | tests/test_sdd.py::PlanGateAnalyzeTests.test_REQ_ANL_008_B1_error_check_also_reports_is_printed_once | pass | yes |
| REQ-ORC-004.S1 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S1_draft_needing_a_critic_round_lists_clarify | pass | yes |
| REQ-ORC-004.S2 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S2_spec_approved_lists_design_tasks_analyze_and_plan_gate | pass | yes |
| REQ-ORC-004.S3 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S3_designed_with_tasks_lists_analyze_then_the_plan_gate | pass | yes |
| REQ-ORC-004.S4 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S4_planned_lists_implement_verify_and_the_results_gate | pass | yes |
| REQ-ORC-004.S5 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S5_verified_standard_change_lists_archive | pass | yes |
| REQ-ORC-004.S6 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S6_mini_change_at_planned_ends_at_the_review_gate | pass | yes |
| REQ-ORC-004.S7 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S7_verifying_with_no_verdict_lists_verify | pass | yes |
| REQ-ORC-004.S8 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S8_verifying_with_pass_verdict_lists_no_step | pass | yes |
| REQ-ORC-004.S9 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S9_clean_mini_draft_prints_the_plan_gate_alone | pass | yes |
| REQ-ORC-004.S10 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S10_round_with_question_verdicts_keeps_clarify | pass | yes |
| REQ-ORC-004.S11 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S11_mini_change_at_verified_prints_review_gate_alone | pass | yes |
| REQ-ORC-004.S12 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S12_mini_change_at_verifying_with_pass_prints_review_gate_alone | pass | yes |
| REQ-ORC-004.S13 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_S13_gaps_verdict_names_the_gaps_gate | pass | weak: a standard change only; the mini half of "standard or mini" has no test (F9) |
| REQ-ORC-004.N1 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N1_blocked_change_prints_its_blocker_line | pass | yes |
| REQ-ORC-004.N2 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N2_abandoned_change_prints_nothing_to_run | pass | yes |
| REQ-ORC-004.N3 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N3_edited_spec_lists_amend_then_its_gate | pass | yes |
| REQ-ORC-004.N11 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N11_logged_edit_prints_amendment_gate_alone | pass | yes |
| REQ-ORC-004.N12 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N12_blocked_change_with_changed_constitution_prints_its_line | pass | yes |
| REQ-ORC-004.N13 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N13_blocked_change_with_unlogged_edit_lists_amend | pass | yes |
| REQ-ORC-004.N14 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N14_abandoned_change_beats_changed_constitution | pass | yes |
| REQ-ORC-004.N15 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N15_unknown_status_is_refused | pass | yes |
| REQ-ORC-004.N4 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N4_no_active_change_refused | pass | yes |
| REQ-ORC-004.N5 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N5_uninitialized_repository_refused | pass | yes |
| REQ-ORC-004.N6 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N6_unknown_change_id_refused | pass | yes |
| REQ-ORC-004.N6 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N6_archived_change_id_refused | pass | yes |
| REQ-ORC-004.N7 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N7_open_question_with_no_finding_keeps_clarify | pass | yes |
| REQ-ORC-004.N8 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N8_changed_constitution_prints_its_line_alone | pass | yes |
| REQ-ORC-004.N9 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N9_round_predating_an_amendment_adds_no_clarify_step | pass | yes |
| REQ-ORC-004.N10 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_N10_open_marker_keeps_clarify_at_prototype | pass | yes |
| REQ-ORC-004.B1 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_B1_all_tasks_ticked_lists_verify_only | pass | yes |
| REQ-ORC-004.B2 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_B2_no_round_required_no_clarify_step | pass | yes |
| REQ-ORC-004.B3 | tests/test_sdd.py::NextTests.test_REQ_ORC_004_B3_complete_round_no_clarify_step | pass | yes |
| REQ-ORC-005.S1 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_S1_draft_with_no_requirements_lists_specify_first | pass | yes |
| REQ-ORC-005.S2 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_S2_designed_with_no_tasks_lists_tasks_first | pass | yes |
| REQ-ORC-005.S3 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_S3_design_error_puts_design_first | pass | yes |
| REQ-ORC-005.S4 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_S4_mini_draft_lists_specify_tasks_clarify | pass | yes |
| REQ-ORC-005.N1 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_N1_spec_error_puts_specify_before_clarify | pass | yes |
| REQ-ORC-005.N2 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_N2_mini_draft_with_no_tasks_lists_tasks | pass | yes |
| REQ-ORC-005.N3 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_N3_design_error_and_no_tasks_lists_design_then_tasks | pass | yes |
| REQ-ORC-005.N4 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_N4_check_error_at_planned_adds_no_fixing_step | pass | yes |
| REQ-ORC-005.N5 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_N5_question_verdicts_alone_do_not_add_specify | pass | yes |
| REQ-ORC-005.N6 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_N6_contract_error_puts_design_first | pass | yes |
| REQ-ORC-005.N7 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_N7_mini_draft_missing_coverage_lists_tasks | pass | yes |
| REQ-ORC-005.B1 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_B1_warnings_alone_add_no_fixing_step | pass | yes |
| REQ-ORC-005.B2 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_B2_failure_mode_error_puts_design_first | pass | yes |
| REQ-ORC-006.S1 | tests/test_sdd.py::StatusAnalyzeTests.test_REQ_ORC_006_S1_status_points_to_analyze_in_text | pass | yes |
| REQ-ORC-006.S2 | tests/test_sdd.py::StatusAnalyzeTests.test_REQ_ORC_006_S2_status_points_to_analyze_in_json | pass | yes |
| REQ-ORC-006.N1 | tests/test_sdd.py::StatusAnalyzeTests.test_REQ_ORC_006_N1_no_tasks_keeps_the_next_line | pass | yes |
| REQ-ORC-006.N2 | tests/test_sdd.py::StatusAnalyzeTests.test_REQ_ORC_006_N2_check_error_keeps_the_next_line | pass | yes |
| REQ-ORC-006.B1 | tests/test_sdd.py::StatusAnalyzeTests.test_REQ_ORC_006_B1_planned_keeps_the_next_line | pass | yes |
| REQ-ORC-006.B2 | tests/test_sdd.py::StatusAnalyzeTests.test_REQ_ORC_006_B2_warnings_only_gives_the_new_next_line | pass | yes |

Pre-existing tasks (87 of 136; 49 have an assertion failure as their red run, all of them real assertions about the behavior): each names the earlier task whose code made it pass (`after T<n>`), and replay confirms each now. Soundness: 83 are covered by a caught mutation on their scenario (by `mutate`, or by hand for the 11 that `mutate` misreports). T82 (REQ-ANL-007.S1), T87 (REQ-ANL-008.N2) and T136 (REQ-ORC-006.B2) have no entry; breaking the behavior by hand failed their tests (3 of 3), so they are sound. T14 (REQ-ANL-001.B2) is **unsound**: deleting the mini guard in `design_rules_apply` leaves all 435 tests green (F2).

Method half (project rule 1, review): `SKILL.md` (two routing rows, "Not built yet" shortened, frontmatter limited to name, description, license and metadata, only the description text changed), `method/phases/design.md` (failure-mode review by a strong read-only subagent, a fresh session in Codex), the new `analyze.md` and `next.md`, `roles/architect.md`, `format.md` (both grammars), `overview.md` and `templates/standard/design.md` match the design, except F10. No private path, host or personal name appears in the added lines (rule 6; the repository URL and licence line in README.md are not in this diff). The Architect's failure-mode review as a live subagent and `next`'s run-each-step loop were written but not run live; dogfood run 3 is where they are tried.

Findings (spec gaps are put to the operator: **A)** amend now with a scenario and a task, or **B)** accept as a known gap by `sdd amend`; the verdict stays GAPS until they answer):
- F1 (plan, scripted evidence) `mutate` reports 11 entries as survived or invalid. Invalid, find text no longer in sdd.py after later refactoring: M2, M115, M116, M118, M129. Survived: M40, M41, M67, M80, M128, M137. Each survivor's scenario is the second or third of a grouped task (T82, T26, T51, T106, T118) whose single `test:` line runs only the first scenario's test, so `mutate` never runs the scenario's own test; by hand, all 11 mutations are caught by their own scenario's test. Fix is in the plan, not the code: re-align the five finds, and split each grouped task or add the missing scenario tests to the entries. `mutate` must then print 0 survived or invalid.
- F2 (weak test, and the open note on REQ-ANL-001.B2 / T14) B2 tests a mini **draft**, where the status keeps `design_rules_apply` false whatever its size guard says. With the guard deleted, a mini change at planned or later gets "design.md has no failure modes" from `analyze` (an error at production), and all 435 tests pass. The spec says mini changes are unaffected (Known gaps; project rule 5), so a scenario for a mini change past the plan gate is missing. A) add scenario REQ-ANL-001.B3 (mini change at planned: no design finding) with a task and a mutation entry. B) accept.
- F3 (spec gap; code differs from the REQ-ANL-003 statement) The statement requires "non-empty text before its arrow", and design.md lists the error "FM1 has no text before its arrow". sdd.py has no such error: `- FM1 → REQ-ANL-001.N1` and `- FM1: → REQ-ANL-001.N1` give no finding (probed, exit 0), and the method's `format.md` says an entry has text. A) add a scenario and fix the code, in a task. B) accept it as a known gap.
- F4 (spec gap; code differs from the statement) A None line needs "`:` or `—` and the same kind of reason". `check_none_line` strips an optional separator, so `- None the design adds nothing` is accepted (probed, exit 0). Only the 1-word and the bare forms have scenarios (N4, N15). A) add a scenario (separator missing) and fix the code. B) accept.
- F5 (spec gap; code differs from the REQ-ORC-005 statement) The statement lists `sdd tasks` for a standard change at designed that has "no tasks or a plan error" (one only the plan stage adds). `plan_stage_steps` adds `tasks` only when there are no tasks. Probed: a designed change whose scenario S1 has no task, which `analyze` reports as an error, prints "1. sdd analyze" and the plan gate, with no "sdd tasks" line (T131 covers the mini case only). A) add the scenario and fix the code. B) accept (the known gap about tier and task-parse errors then covers it).
- F6 (spec gap, code right, clause has no scenario) Dropping or changing any of these keeps all 435 tests green: the em dash in `FM_ENTRY`'s separator set; the `*` bullet marker (`BULLET`); the split at the **last** arrow (`rsplit`, replaced by the first arrow); `N/A` in any case (`re.I` on `NA_OUTCOME`); `interface` key in any case (`re.I` on `INTERFACE_LINE`); a None reason of exactly 2 words (3 is the minimum, only 1 word and none are tried); `~~~` fences (design.md names them; the spec says "fenced code blocks"). A) add one scenario each, with a test and a mutation entry. B) accept, as one Known gaps line.
- F7 (spec gap) REQ-ANL-004 says an error "at production and above"; the scenarios test production (N1) and internal (B1) only. Changing `>=` to `==` in `check_failure_modes_present` survives. Probed by hand: at `critical` the error is raised, so the code is right. A) add a critical scenario. B) accept.
- F8 (spec gap) REQ-ORC-004: S13 says "a standard or mini change at verifying whose latest verdict is GAPS"; the test uses a standard change. Probed by hand: a mini change with GAPS, and any other verdict word (MAYBE), get the gaps gate, as the statement says. Replacing the `!= "PASS"` test with `== "GAPS"` survives, so "unknown verdict" has no test. A) add the mini S13 test and a scenario for an unknown verdict word. B) accept.
- F9 (spec gap, heuristic) REQ-ANL-006 defines a "distinctive" word as one no other clause has. No scenario shows that a word shared between clauses doesn't cover a clause: counting any clause word as covering (instead of only distinctive words) survives. A) add a scenario (a scenario mentions only a shared word; the clause is still flagged). B) accept; the heuristic is already a Known gap.
- F10 (method) `method/phases/tasks.md` step 3 still says to run `SDD check` until OK, and doesn't mention `SDD analyze`, though `approve plan` now refuses on analyze errors; step 5's gate is where `analyze.md` points. This is a design-work item (rule 1), not a spec item: A) amend the phase file (a task, or a one-line edit by the Implementer). B) accept.
- F11 (dead code) `design_findings` falls back to `project.level()` when `report.level` isn't a valid level (sdd.py:1529). No scenario reaches it: `analyze()` already resolves the level. A) remove the fallback in a task. B) accept as defensive code.
- F12 (note, no action) M86 injects a made-up interface into the loop instead of breaking a real line; it is caught by REQ-ANL-005.S3 and is not evidence for a rule that no other entry covers. Accepted as it stands.

Not findings: the size cap is 397 of 400 lines; the pinned tool has no `analyze` or `next` (it is the `main` checkout, as rule 7 wants), so `analyze` and `next` were run from the development checkout; the 87 pre-existing warnings are the `after T<n>` tasks reviewed above.

Verdict: GAPS — 12 findings (F1 plan repair; F2 to F11 await the operator's A or B; no task was appended and the status was left at verifying, because the tasks to add depend on the answers)

### Round 2
- Date: 2026-10-21 · Verifier: fresh session (production) — the same side session as round 1; it still did no implementation work and re-ran everything from the files. Round 1 ended GAPS; the operator decided A for F2 to F5, B for F6 to F9 and F11, and the prime session wrote amendment A2 (new scenarios REQ-ANL-001.B3, REQ-ANL-003.N16, REQ-ANL-003.N17, REQ-ORC-005.N8; tasks T137 to T146; the realigned Mutations; five Known gaps).
- Tests: `python3 -m unittest tests.test_sdd` → Ran 439 tests, OK (435 in round 1; 4 new, one per new scenario)
- Check: `sdd.py check --stage verify` (pinned tool) → OK, 0 errors, 95 warnings: 94 `pre-existing` tasks (reviewed below) and the size cap (406 lines against 400 for standard, a warning at every stage). Development checkout `analyze`: result OK, 0 errors, 96 warnings (the same plus the REQ-ANL-005 clause heuristic); its `next` prints the gaps gate only because round 1's verdict is GAPS.
- Replay: `sdd.py replay --base HEAD` (development checkout; HEAD is still 47f4536) → replay: 146 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` (development checkout) and the pinned `sdd.py mutate` → mutate: 158 caught, 0 survived or invalid, both runs (round 1: 143 caught, 11 survived or invalid)
- Mutation cross-check, by hand, in scratch copies outside the repository (one find text occurring exactly once, the scenario's own tests run before and after): the new M155, M156, M157, M158; the realigned M2, M115, M116, M118, M129; the six round-1 survivors M40, M41, M67, M80, M128, M137; and a sample of M3, M12, M20, M33, M50, M70, M90, M110, M125, M145, M150 → 26 of 26 caught, each test passing before. Edge probes of the amended rules by hand: "- FM1: → …", "- FM1 — → …" and "- FM1    → …" each give the one error "FM1 has no text before its arrow"; "- None x" gives the separator error; "- None:" gives the 3-word error; "- None: the design adds nothing" and a normal entry give none. The working tree was unchanged afterwards (17 changed paths before and after, apart from this file); scratch copies were removed or kept outside the repository.
- Coverage: not available

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-ANL-001.B3 | tests/test_sdd.py::AnalyzeTests.test_REQ_ANL_001_B3_mini_change_past_the_plan_gate_has_no_design_finding | pass | yes: a mini change that really reached `planned` (status asserted), no design.md, exit 0, no "design.md" and no "no failure modes" in the output, snapshot unchanged |
| REQ-ANL-003.N16 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N16_failure_mode_with_no_text_before_its_arrow_is_refused | pass | yes: exit 1, exactly one error with the message, result FAIL, snapshot unchanged |
| REQ-ANL-003.N17 | tests/test_sdd.py::FailureModeTests.test_REQ_ANL_003_N17_none_line_with_no_separator_is_refused | pass | yes: exit 1, exactly one error with the message, result FAIL, snapshot unchanged |
| REQ-ORC-005.N8 | tests/test_sdd.py::NextTests.test_REQ_ORC_005_N8_plan_error_at_designed_lists_tasks | pass | yes: the plan error is shown in `check`, the output is exactly "1. sdd tasks", "2. sdd analyze" and the plan gate, snapshot unchanged |

The other 143 scenarios keep their round-1 tests and rows; round 1's rows still hold (the suite is green and the tests are unchanged apart from the four additions and the REQ-ANL-001.B2/B3 split).

Closures:
- F1 closed. `mutate` is clean (158 caught, 0 survived or invalid). The five stale finds are realigned (each occurs once in sdd.py), and T141 to T146 split the grouped tasks so each scenario has its own task and `test:` line; all six round-1 survivors are caught by `mutate` and by hand.
- F2 closed. REQ-ANL-001.B3 and T137 test a mini change at `planned`; M155 (the size guard to `if False`) fails that test. Its red run is `pre-existing (after T14)`, which holds: the guard existed, and removing it fails the test (M155).
- F3 closed. REQ-ANL-003.N16 and T138 (red run is a real assertion: exit 0 against 1); `check_fm_entry` now errors on an empty text; M156 caught.
- F4 closed. REQ-ANL-003.N17 and T139 (real red run); `check_none_line` now requires `:` or `—`; M157 caught.
- F5 closed. REQ-ORC-005.N8 and T140 (real red run); `plan_stage_steps` now lists `tasks` for a plan error, through `needs_tasks`; M158 caught. The REQ-ORC-005 statement and the known gap about tier and task-parse errors agree with the code.
- F6, F7, F8, F9 and F11 are closed by the operator's decision B: each is now a line in `## Known gaps` (em dash, `*`, last arrow, any case, 2-word None and `~~~`; critical for REQ-ANL-004; mini and unknown verdict for REQ-ORC-004.S13; shared words for REQ-ANL-006; the level fallback). I confirmed each line says what the code does, as probed in round 1.
- F10 closed. `method/phases/tasks.md` step 3 now says to run `SDD analyze` after `SDD check` and that `approve plan` refuses on its errors; the line is not wrapped at 78 columns like its neighbours, which is cosmetic.
- F12 stays a note: M86 is a synthetic mutant, caught.

Pre-existing tasks (94 of 146): the 87 of round 1, plus T137 and T141 to T146. Each names the earlier task whose code made it pass, and replay confirms each now. All seven new ones are backed by a caught mutation on their own scenario (M155, M67, M80, M41, M40, M128, M137, each caught by hand and by `mutate`). The round-1 unsound T14 is now sound together with T137 (the guard is exercised by M155).

New findings in round 2: none. Nothing new was found in the amended code beyond the probes above, and the size-cap warning (406 of 400 lines) comes from the five added Known gaps and four scenarios; it is a warning, not an error. Not done, by design: the live run of the Architect's failure-mode review and of `next`'s step loop is for dogfood run 3; delivery items (version, README, RELEASE_NOTES, the PR from `v1`) follow the results gate.

Verdict: PASS
