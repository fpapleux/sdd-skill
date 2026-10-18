<!-- Verifier: format in method/roles/verifier.md. The operator approves the
results at the third gate (sdd.py approve results). -->

## Verification
- Date: 2026-10-18 · Verifier: fresh session (production) — the session that ran this verify did no implementation work on this change; it started at `/sdd` status and read everything from files
- Tests: `python3 -m unittest tests.test_sdd` → Ran 290 tests, OK (the bare `python3 -m unittest` discovers 0 tests in this repository; project rule 2 names `tests.test_sdd`)
- Check: `sdd.py check --stage verify` (development checkout) → OK, 0 errors, 15 warnings: 14 `pre-existing` tasks (reviewed below) and the size cap (510 lines against 400 for standard)
- Replay: `sdd.py replay --base HEAD` (development checkout; HEAD is the commit the change started from, 8ee464f) → replay: 68 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` (development checkout) → mutate: 49 caught, 0 survived or invalid
- Mutation cross-check, by hand (the design says the development checkout's `mutate` is not evidence, and the pinned tool has none): in scratch copies outside the repository, M3, M11, M15, M23, M31, M40 and M49 each applied by a separate script, each find text occurring exactly once; every scenario's test passed before and failed after (7 of 7 caught). The working tree was unchanged afterwards (19 changed paths before and after).
- Coverage: not available (no coverage tool installed; none was installed)

Scenario matrix: every scenario of the six requirements (81) has a test named for it, and I read each test's setup, action and assertions against the scenario's Given, When and Then. A failure scenario's Then ("the error · no file is changed", "no test is run", "working tree unchanged", "no scratch copy is left") is asserted by the snapshot comparison (`snapshot`, `tree_state`), by `run_test` call counts, or by the scratch-folder listing in `run_tool`. REQ-ORC-003.B3 has two tests (comment and fenced block); both pass.

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-ORC-001.S1 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_S1_three_tiers_pass_and_status_counts_them | pass | yes |
| REQ-ORC-001.S2 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_S2_escalation_counts_as_the_higher_tier | pass | yes |
| REQ-ORC-001.S3 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_S3_chain_counts_as_its_last_tier | pass | yes |
| REQ-ORC-001.N1 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_N1_unknown_tier_refused | pass | yes |
| REQ-ORC-001.N2 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_N2_downward_escalation_refused | pass | yes |
| REQ-ORC-001.N3 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_N3_capitalised_tier_refused | pass | yes |
| REQ-ORC-001.N4 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_N4_two_tier_lines_refused | pass | yes |
| REQ-ORC-001.N5 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_N5_two_tier_jump_refused | pass | yes |
| REQ-ORC-001.N6 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_N6_ascii_arrow_refused | pass | yes |
| REQ-ORC-001.B1 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_B1_same_tier_escalation_refused | pass | yes |
| REQ-ORC-001.B2 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_B2_missing_tier_warns | pass | yes |
| REQ-ORC-001.B3 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_B3_status_counts_untiered_tasks | pass | yes |
| REQ-ORC-001.B4 | tests/test_sdd.py::TierTests.test_REQ_ORC_001_B4_no_tiers_line_without_tasks | pass | yes |
| REQ-ORC-002.S1 | tests/test_sdd.py::CriticRunnerTests.test_REQ_ORC_002_S1_round_subagent_heads_the_round | pass | yes |
| REQ-ORC-002.S2 | tests/test_sdd.py::CriticRunnerTests.test_REQ_ORC_002_S2_strong_subagent_round_is_independent | pass | yes |
| REQ-ORC-002.N1 | tests/test_sdd.py::CriticRunnerTests.test_REQ_ORC_002_N1_unknown_subagent_tier_is_a_usage_error | pass | yes |
| REQ-ORC-002.N2 | tests/test_sdd.py::CriticRunnerTests.test_REQ_ORC_002_N2_subagent_with_fresh_is_a_usage_error | pass | yes |
| REQ-ORC-002.N3 | tests/test_sdd.py::CriticRunnerTests.test_REQ_ORC_002_N3_round_after_spec_gate_points_to_amend | pass | yes |
| REQ-ORC-002.N4 | tests/test_sdd.py::CriticRunnerTests.test_REQ_ORC_002_N4_hand_written_invalid_tier_not_independent | pass | yes |
| REQ-ORC-002.B1 | tests/test_sdd.py::CriticRunnerTests.test_REQ_ORC_002_B1_later_same_session_round_warns | pass | yes |
| REQ-ORC-002.B2 | tests/test_sdd.py::CriticRunnerTests.test_REQ_ORC_002_B2_subagent_without_tier_not_independent | pass | yes |
| REQ-ORC-002.B3 | tests/test_sdd.py::CriticRunnerTests.test_REQ_ORC_002_B3_mid_subagent_not_independent_at_production | pass | yes |
| REQ-ORC-002.B4 | tests/test_sdd.py::CriticRunnerTests.test_REQ_ORC_002_B4_no_runner_warning_below_production | pass | yes |
| REQ-ORC-003.S1 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_S1_strong_subagent_verifier | pass | yes |
| REQ-ORC-003.S2 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_S2_fresh_session_verifier | pass | yes |
| REQ-ORC-003.N1 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_N1_same_session_verifier_warns | pass | yes |
| REQ-ORC-003.N2 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_N2_missing_verifier_line_warns | pass | yes |
| REQ-ORC-003.N3 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_N3_invalid_tier_verifier_warns | pass | yes |
| REQ-ORC-003.N5 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_N5_mid_subagent_verifier_warns | pass | yes |
| REQ-ORC-003.N4 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_N4_no_verifier_warning_in_draft | pass | yes |
| REQ-ORC-003.B1 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_B1_no_verifier_warning_below_production | pass | yes |
| REQ-ORC-003.B2 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_B2_latest_verifier_line_counts | pass | yes |
| REQ-ORC-003.B3 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_B3_verifier_line_in_comment_ignored | pass | yes |
| REQ-ORC-003.B3 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_B3_verifier_line_in_fenced_code_ignored | pass | yes |
| REQ-ORC-003.B4 | tests/test_sdd.py::VerifierRunnerTests.test_REQ_ORC_003_B4_verifier_line_in_any_case | pass | yes |
| REQ-EVD-001.S1 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_S1_red_task_confirmed | pass | yes |
| REQ-EVD-001.S2 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_S2_pre_existing_task_confirmed | pass | yes |
| REQ-EVD-001.N1 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N1_red_claimed_but_passes_at_base | pass | yes |
| REQ-EVD-001.N2 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N2_pre_existing_claimed_but_fails_at_base | pass | yes |
| REQ-EVD-001.N3 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N3_test_fails_now | pass | yes |
| REQ-EVD-001.N4 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N4_no_test_one_line | pass | yes |
| REQ-EVD-001.N5 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N5_unknown_base_revision | pass | yes |
| REQ-EVD-001.N6 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N6_not_a_git_repository | pass | yes |
| REQ-EVD-001.N7 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N7_missing_runner_fails_every_task | pass | yes |
| REQ-EVD-001.N8 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N8_ticked_task_without_test_line | pass | yes |
| REQ-EVD-001.N9 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N9_test_line_without_separator | pass | yes |
| REQ-EVD-001.N10 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N10_replay_without_base_is_a_usage_error | pass | yes |
| REQ-EVD-001.B1 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_B1_unticked_task_skipped | pass | yes |
| REQ-EVD-001.B2 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_B2_nothing_ticked | pass | yes |
| REQ-EVD-001.B3 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_B3_file_and_name_substituted_and_printed | pass | yes |
| REQ-EVD-001.B4 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_B4_untracked_fixture_laid_over_base | pass | yes |
| REQ-EVD-001.S3 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_S3_pre_existing_after_earlier_task | pass | yes |
| REQ-EVD-001.S4 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_S4_red_after_earlier_task | pass | yes |
| REQ-EVD-001.N11 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_N11_dependent_task_fails_now | pass | yes |
| REQ-EVD-001.B5 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_B5_later_task_is_not_a_dependency | pass | yes |
| REQ-EVD-001.B6 | tests/test_sdd.py::ReplayTests.test_REQ_EVD_001_B6_task_id_without_marker_is_not_a_dependency | pass | yes |
| REQ-EVD-002.S1 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_S1_complete_entry_accepted | pass | yes |
| REQ-EVD-002.N1 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_N1_missing_replace_is_an_error | pass | yes |
| REQ-EVD-002.N2 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_N2_scenario_outside_the_change_is_an_error | pass | yes |
| REQ-EVD-002.N3 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_N3_missing_file_is_an_error | pass | yes |
| REQ-EVD-002.N4 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_N4_duplicate_id_is_an_error | pass | yes |
| REQ-EVD-002.N5 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_N5_path_leaving_the_project_is_an_error | pass | yes |
| REQ-EVD-002.N6 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_N6_absolute_path_is_an_error | pass | yes |
| REQ-EVD-002.N7 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_N7_find_without_backticks_is_an_error | pass | yes |
| REQ-EVD-002.B1 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_B1_no_mutations_section_no_error | pass | yes |
| REQ-EVD-002.B2 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_B2_replace_equal_to_find_is_an_error | pass | yes |
| REQ-EVD-002.B3 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_B3_empty_replace_accepted | pass | yes |
| REQ-EVD-002.B4 | tests/test_sdd.py::MutationsCheckTests.test_REQ_EVD_002_B4_mutations_not_counted_toward_the_size_cap | pass | yes |
| REQ-EVD-003.S1 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_S1_mutation_caught | pass | yes |
| REQ-EVD-003.N1 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_N1_mutation_survived | pass | yes |
| REQ-EVD-003.N2 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_N2_test_fails_without_the_mutation | pass | yes |
| REQ-EVD-003.N3 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_N3_find_text_not_in_file | pass | yes |
| REQ-EVD-003.N4 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_N4_find_text_found_twice | pass | yes |
| REQ-EVD-003.N5 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_N5_no_test_one_line | pass | yes |
| REQ-EVD-003.N6 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_N6_file_does_not_exist | pass | yes |
| REQ-EVD-003.N7 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_N7_task_without_test_line | pass | yes |
| REQ-EVD-003.N8 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_N8_not_a_git_repository | pass | yes |
| REQ-EVD-003.N9 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_N9_scenario_no_task_plans | pass | yes |
| REQ-EVD-003.B1 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_B1_no_mutations_section | pass | yes |
| REQ-EVD-003.B2 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_B2_one_caught_one_survived | pass | yes |
| REQ-EVD-003.B3 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_B3_leading_spaces_kept | pass | yes |
| REQ-EVD-003.B4 | tests/test_sdd.py::MutateTests.test_REQ_EVD_003_B4_scenario_planned_by_two_tasks | pass | yes |

Pre-existing tasks (14) reviewed: T8, T12, T15, T16, T20, T22, T25, T33, T46, T52, T62, T63, T64, T68. Each names the earlier task whose code made its test pass (`after T<n>`, amendment A1), and replay confirms each now. Soundness spot-check by removing the behavior in a scratch copy: T8 (untiered count), T15 (latest round only), T46 (`--base` required) and T68 (literal `(after T<n>)` marker) each made their scenario's test fail (4 of 4). The others are covered by their planned mutations (all caught). T12, T20, T22, T25, T33, T52, T62, T63 and T64 were checked through those mutations, not one by one.

Method half (project rule 1, review): `SKILL.md` Orchestration, the `Tier · Effort · Read-only` line on all seven role files (the values match the design's table), the Planner's tier and Mutations guidance, the Implementer's `(after T<n>)` and escalation rules, `clarify.md` and `verify.md` independence wording, `format.md`, `overview.md` and the three templates match the design. No private paths, host names, or personal names in the diff or the change folder (rule 6); `SKILL.md` frontmatter is unchanged (rule 3).

Notes for the results gate (not findings, nothing here contradicts the spec):
- N-a. The spawn of a strong Critic or Verifier subagent, and the tier → model routing, were written but not run live in this change: Round 1 was a fresh session, and this verify ran in the prime session with no subagent. The method half is verified by review only.
- N-b. The size cap warning (510 lines against 400) is a warning, not an error, at every stage. Task checklists and Mutations are excluded from the cap, so the count comes from the requirements and design.
- N-c. Delivery items remain: version bump, README and RELEASE_NOTES (design, last bullet; project rule 9) and the PR from `v1` (rule 8). They belong after the results gate.

Findings:
- None.

Verdict: PASS
