<!-- Spec Critic: one round per review, started with `sdd.py round`. Format:
method/format.md. Required before the spec gate (standard changes at internal
and above; any size at production and above). -->

## Clarifications

### Round 1 — 2026-10-28 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-EVD-004 | issues | F1, F2 |
| REQ-ORC-007 | issues | F3, F4, F5, F6, F7, F8 |
| REQ-DEF-001 | issues | F13, F14, F15 |
| REQ-ORC-008 | issues | F8, F9 |
| REQ-EVD-005 | issues | F8, F10, F11, F12 |
| REQ-DEF-002 | issues | F8, F16 |
| REQ-DEF-003 | issues | F17 |
| REQ-DEF-004 | issues | F18 |
| REQ-DEF-005 | issues | F8, F19 |
| REQ-DEF-006 | issues | F20, F21 |

<!-- Findings without an outcome are spec fixes for the Spec Author (no decision needed); the Author gives each its outcome (fixed: / rejected:). -->

- F1 [coverage] REQ-EVD-004: the statement covers the Design notes of a mini change, but every scenario uses a standard design.md; add one mini scenario (a mini spec.md with a component line and one without). → fixed: B6 and B7 add a mini Design notes change with and without the line
- F2 [ambiguity] REQ-EVD-004: whether a "Test component:" line without a list marker counts is not stated; `Test one:` requires a "- " bullet while `Test command:` matches anywhere in sdd.py today. Say which rule applies (and add a boundary if it differs from Test one). → fixed: the statement requires a list line (`-` or `*`), as Test one; B5 shows an unbulleted line is ignored
- F3 [ambiguity] REQ-ORC-007: "<m> done" in the header is undefined for a partial range: for `run-plan T3` with T1 ticked, is m 0 (ticked tasks in the range) or 1 (ticked tasks in the plan)? S3 fits both readings; define it and give it a scenario. → fixed: n and m count the range's unticked and ticked tasks (next: m is 0; all: the plan); B7 asserts the header, B10 covers run-plan T3 with T1 ticked
- F4 [ambiguity] REQ-ORC-007: "no command (the test line has no "::")" is stated unconditionally, but expand (REQ-EVD-001) returns a command for a line without "::" when the Test one template uses only {test}; state the condition (the template uses {file} or {name}) and add a {test}-only boundary. → fixed: "no command" only when the Test one command uses {file} or {name}; B11 covers a {test}-only template
- F5 [ambiguity] REQ-ORC-007: checkpoints compare prefixes, while Scope makes the capability the component; a capability declared with two prefixes (duration=DUR, duration=DU2, supported by REQ-ARC-001.B3) gets two component steps, each running part of its tests → fixed: per Q4 — one component checkpoint per prefix is kept; a Known gap records the two-prefix case
- F6 [untestable] REQ-ORC-007: a task with no scenario reference between two DUR tasks (T1 DUR, T2 none, T3 DUR) has no defined output: does T1 get "component DUR" because the next task's capability differs, and is the T3 step merged with T1's? The Known gap says only "no component checkpoint of its own"; state the rule and give it one boundary. → fixed: a task with no scenario reference is listed but neither joins nor ends a group, and a component step is placed before the next task with another prefix; B12 and B13; the Known gap is removed
- F7 [coverage] REQ-ORC-007: no scenario uses `--change`, and no scenario runs with no active change; the N/A lines point to REQ-ORC-008, which has neither (also F9). → fixed: S5 runs with --change on a change that isn't active; ORC-008 adds no active change (N12) and an unknown --change (N13)
- F8 [coverage] REQ-ORC-007, REQ-ORC-008, REQ-EVD-005, REQ-DEF-002, REQ-DEF-005: 109 scenarios is heavy for an intermediary release, and several restate a rule another row already proves. Candidates to drop or merge: ORC-007.S4 (same steps as S2, same rule as B1); ORC-008.N3 (N1 and N2 already prove the form check); ORC-008.N10 (N9 proves the status rule); EVD-005.N5 (every row already pins exact output of a pure read); DEF-002.N7 into N6 (one refusal, missing or blank); DEF-005.N2 (N1, N3 and N4 show the check error through each gate); DEF-005.N7 (archive is N3, major undecided is N6). That is 7 fewer, which leaves room for the rows F1, F4, F6, F7, F9-F18 add. → fixed: dropped ORC-007.S4, ORC-008.N3, ORC-008.N10, EVD-005.N5 and DEF-005.N2/N7 (rewritten per Q1); DEF-002.N7 merged into N6
- F9 [coverage] REQ-ORC-008: a Test one or Test command whose quotes don't close is not covered; shlex.split raises ValueError, which main() doesn't catch (only SddError), so today run-plan would end in a traceback. Add the refusal (exit 1, names the line, no step) with one scenario, and add "no active change" and an unknown `--change` to the statement with a scenario. → fixed: ORC-008 refuses a Test one or Test command whose quote doesn't close (N14), with no active change (N12) or an unknown --change (N13)
- F10 [ambiguity] REQ-EVD-005: the statement doesn't say which change it reads (the active one or `--change`), nor what happens with no active change; state it and add a state scenario. → fixed: the statement reads the active change or --change; N8 covers no active change
- F11 [ambiguity] REQ-EVD-005: a name carrying two scenario IDs of the change (say REQ-DUR-001.S1 of ticked T1 and REQ-DUR-001.N1 of unticked T2) has no defined result or printed <scenario>; nor does a scenario planned by two ticked tasks (N6 implies "the first", unstated). State the rule (for example: a done task's ID wins, the first such ID in the name is printed; the first ticked task is named) and add one boundary. → fixed: the printed scenario is the first ID in the name that decides the line (for a done regression, the first a ticked task plans), and the task the first in plan order (a ticked one for a done regression); B7
- F12 [ambiguity] REQ-EVD-005: the reading rules (blank lines, surrounding spaces, duplicates) are stated for the failing file only; say whether the baseline's lines are stripped the same way before the exact comparison of B5. → fixed: both files skip blank lines and strip surrounding spaces; B8 covers a padded baseline line
- F13 [untestable] REQ-DEF-001: the exact layout of a new log is not given (the separator row, a blank line after the title, the trailing newline), yet REQ-DEF-002 and REQ-DEF-003 assert every other line is unchanged and REQ-DEF-006 parses "its header and separator"; give the exact text of a newly created log. → fixed: REQ-DEF-001 gives the exact new-log text (title, empty line, header, separator, row, final newline); S1 asserts it
- F14 [coverage] REQ-DEF-001: no scenario for `--capability` with an unknown or lowercase prefix, for `--capability` overriding a different prefix in the test name, or for `--change` naming a change that doesn't exist; and the statement doesn't say whether a defect can be added for a change at any status (draft, verified, abandoned). State it and add the rows. → fixed: --capability is used as written and wins over the name; a defect may be recorded for a change at any status; N7 (lowercase), N8 (unknown --change), B4 (override), B6 (verified change)
- F15 [coverage] REQ-DEF-001: an existing specs/defects.md that is empty, or has the title but no table, is not covered: does add write the header, or refuse under REQ-DEF-006? → fixed: a blank file gets the new-log text, a file with lines but no table gets the header, separator and row appended; B5
- F16 [coverage] REQ-DEF-002: "with line breaks as spaces" has no scenario; add a boundary with evidence containing a newline. → fixed: B4 covers evidence on two lines, written as one line with a space
- F17 [coverage] REQ-DEF-003: closing is the only way to clear a REQ-DEF-005 block, and it records nothing (no evidence, no date), so a fix-now critical defect can be closed without a fix and the results go through; the Known gap "close doesn't check that the defect's test now passes" leaves the block easy to bypass → fixed: per Q2 — close requires --evidence, kept in a new Close evidence cell (nine columns); DEF-003.N6 refuses missing or blank; the Known gap is folded into the plain-text gap
- F18 [coverage] REQ-DEF-004: status with an invalid log is unspecified: REQ-DEF-006 names the defect commands and check, not status; say whether status prints the error and with which exit code, with a scenario. → fixed: REQ-DEF-006 says status prints "defect log: <problem>", exits 0 and shows no count, with "defects": null in --json (N4); REQ-DEF-004 points to it
- F19 [ambiguity] REQ-DEF-005: an open major defect decided fix-now doesn't block (B3) while the same defect undecided does (N6), so deciding "fix now" lets the results through without the fix; Q1 (critical fix-now) and Q5 (undecided non-minor) don't contradict each other but leave this combination undecided → fixed: per Q1 — REQ-DEF-005 is one rule: an open critical or major defect not decided later or wont-fix blocks; N4-N6 and B1-B3 cover undecided, fix-now, later, wont-fix and minor
- F20 [ambiguity] REQ-DEF-006: "its header" is not defined (the first table line, or a line equal to the REQ-DEF-001 header?); a log whose header has seven columns, or a second table, is not covered. → fixed: the header is the first table line and must equal the REQ-DEF-001 header, the second its separator; N7 (eight-column header) and N8 (a second table)
- F21 [ambiguity] REQ-DEF-006: the stages at which check reports an invalid log are not stated; as written, a malformed project log fails check for every change at every stage, so it also blocks the spec and plan gates of unrelated changes → fixed: per Q3 — an invalid log is an error at check's verify stage and in the defect commands, a warning at the other stages and in status; DEF-006.N2-N4

- Q1 Should an open major defect decided fix-now block results approval, advance verified and archive of the change that recorded it (today REQ-DEF-005.B3 says no)? A) no, as written: only critical fix-now and undecided critical or major block B) yes: any open critical or major defect blocks unless decided later or wont-fix; minor never blocks — recommended: B (deciding "fix now" should not be the step that lets the results through unfixed, and the rule becomes one sentence)
  - Answer: B — any open critical or major defect blocks unless decided later or wont-fix; minor never blocks (operator, 2026-10-28, Claude Code chat: "Yes: B, B, B, A")
- Q2 Should `defect close` record why the defect is closed? A) no, as written: close needs only a decision, and the Known gap stays B) yes: close requires `--evidence "<text>"` (what fixed it, such as the passing run, or why it is closed), kept in the row, and refuses without it — recommended: B (close is what clears a block, so it should leave a trace like decide does)
  - Answer: B — close requires `--evidence`, kept in the row (operator, 2026-10-28, Claude Code chat: "Yes: B, B, B, A")
- Q3 Where does an invalid defect log fail check? A) at every stage of every change, as written B) as an error at the verify stage (where defects block) and in the defect commands, as a warning at the other stages and in status — recommended: B (a broken log should not stop the spec or plan gate of an unrelated change)
  - Answer: B — an error at the verify stage and in the defect commands, a warning elsewhere and in status (operator, 2026-10-28, Claude Code chat: "Yes: B, B, B, A")
- Q4 When a capability has two prefixes (duration=DUR, duration=DU2), what is its component checkpoint? A) one per prefix, as written, recorded as a Known gap B) one per capability: consecutive DUR and DU2 tasks share one checkpoint that runs the component command once per prefix — recommended: A (rare case; keeps the intermediary release small)
  - Answer: A — one checkpoint per prefix, recorded as a Known gap (operator, 2026-10-28, Claude Code chat: "Yes: B, B, B, A")

### Round 2 — 2026-10-28 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-EVD-004 | issues | F4 |
| REQ-ORC-007 | issues | F4 |
| REQ-DEF-001 | issues | F1, F4 |
| REQ-ORC-008 | issues | F4 |
| REQ-EVD-005 | issues | F4 |
| REQ-DEF-002 | issues | F1, F4 |
| REQ-DEF-003 | issues | F1, F4 |
| REQ-DEF-004 | ok | |
| REQ-DEF-005 | issues | F3, F4 |
| REQ-DEF-006 | issues | F2, F4 |

<!-- All 21 round-1 fixes were checked against spec-delta.md and landed. Findings without an outcome are spec fixes for the Spec Author (no decision needed). No questions this round. -->

- F1 [untestable] REQ-DEF-001: the row's exact text is not given (one space around each cell? an empty cell written "|  |" or "| |"?), yet S1 says the file is "exactly" the new-log text, and REQ-DEF-002.B2 and REQ-DEF-003 assert byte-for-byte or every-other-line results; nor is it said whether decide and close re-render the whole row or replace only the cells they change (a hand-padded row would change under DEF-002.B2 if re-rendered). Give the row text in S1 (for example "| D1 \| open \| … \|  \|  \|" written out) and state the rewrite rule in DEF-002 and DEF-003. → fixed: DEF-001 states the row layout ("| " + cells joined by " | " + " |", an empty cell as two spaces) and S1 gives the row text; DEF-002 and DEF-003 rewrite only the cells they change, leaving the rest of the row as written
- F2 [ambiguity] REQ-DEF-006: the header and separator must be "exactly" the REQ-DEF-001 text, so a Markdown formatter that pads table cells ("\| ID  \| Status \|", "\| --- \| ------ \|") makes the whole log invalid and fails every verify check. Compare the header's trimmed cells and accept any separator row (dashes with optional colons), as sdd.py's table parsing does for other tables, and add one boundary with a padded header and separator. → fixed: DEF-006 compares the header's trimmed cells and accepts any separator row (dashes, optional colons); B3 covers a padded header and separator
- F3 [untestable] REQ-DEF-005: no row asserts the error's wording ("must be closed or decided later or wont-fix first") since the check row was dropped under round-1 F8; add it to N1's Then. → fixed: DEF-005 states the error text and N1 asserts "D1 (critical, fix-now) is open: close it, or decide later or wont-fix, first"
- F4 [coverage] REQ-EVD-004, REQ-ORC-007, REQ-DEF-001, REQ-ORC-008, REQ-EVD-005, REQ-DEF-002, REQ-DEF-003, REQ-DEF-005, REQ-DEF-006: 126 scenarios is still heavy for an intermediary release; these 15 rows repeat a code path another row proves. Drop EVD-004.B4 (comment stripping is shared by every design line) and B7 (B6 proves the mini source, B1 the warning); ORC-007.B9 (replacing every {prefix} is one call); merge DEF-001.N3 into N7 (one prefix check, derived or given); merge ORC-008.N2 into N1 (one range-form check) and drop ORC-008.N8 (argparse's required argument); drop EVD-005.N4 (argparse) and B4 (the exact-match path of S2), and merge B8 into N3 (one reader for both files: pad both); drop DEF-002.B1 (S1 already asserts every other line is unchanged); drop DEF-003.N3, N4 and N5 (the D<n> lookup and missing-log refusals are DEF-002.N2, N3 and N5's code); drop DEF-005.N4 (N1 proves critical blocks, N5 proves undecided blocks); drop DEF-006.N8 (a second table's header is a later line with the wrong cell count, as N6). That leaves 111. Keep the per-command no-active-change and unknown --change rows: the living spec tests them per command (REQ-ORC-004.N4, N6; REQ-ANL analyze N1, N4). → fixed: the 15 listed rows dropped or merged (DEF-001.N3 into N7, ORC-008.N2 into N1, EVD-005.B8 into N3); per-command no-active-change and unknown --change rows kept; DEF-003 gains an N/A dependency line pointing to REQ-DEF-002.N5 and REQ-DEF-006

### Round 3 — 2026-10-28 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-EVD-004 | issues | F3 |
| REQ-DEF-001 | ok | |
| REQ-EVD-005 | issues | F1, F2 |
| REQ-DEF-002 | ok | |
| REQ-DEF-003 | ok | |
| REQ-DEF-004 | ok | |
| REQ-DEF-006 | ok | |

<!-- Round-2 fixes F1 (row text, cell rewrite rule) and F2 (trimmed header, any separator; DEF-006.B3) landed. No dangling reference to REQ-ORC-007, REQ-ORC-008, REQ-DEF-005, the baseline, blocking or run-plan in spec-delta.md. Findings without an outcome are spec fixes for the Spec Author. No questions this round. -->

- F1 [contradiction] REQ-EVD-005: proposal Scope still defines "a regression is a test that passed before the task and fails after it", and the "Changes existing behavior" line says "only a regression is a break"; with no baseline, sort-failures reports such a test as outside (Scope's own sort line and the new Out line). Reword the Scope regression line to the name-based rule (a scenario of the change planned by a done task), or say that a test outside the change failing is judged by the agent under the method, so Scope and REQ-EVD-005 agree. → fixed: the Scope regression line keeps the operator's definition and adds that the agent applies it from its own runs, while sort-failures sorts by name only and reports a failing test outside the change as outside for the agent to judge
- F2 [coverage] REQ-EVD-005: the statement promises the hyphen form (REQ-DUR-001.S1) and any case, but since the rewrite every row uses test_REQ_DUR_… names; restore one boundary such as "REQ-DUR-001.N1 rejects letters" or "test_req_dur_001_n1_x". → fixed: EVD-005.B4 sorts "Req-Dur-001.N1 rejects letters" (hyphen form, mixed case) as expected
- F3 [scope] REQ-EVD-004: the front matter still declares orchestration=ORC, but no requirement of this change is ORC since REQ-ORC-007 and REQ-ORC-008 were removed; drop it from capabilities. Also R1Q4 in proposal.md is not marked superseded although the Known gap it recorded was removed. Dropping the gap is right (sdd.py no longer places checkpoints; the method does, under project rule 1), so mark R1Q4 superseded, with the method or design to say a two-prefix capability gets one checkpoint per prefix. → fixed: orchestration=ORC removed from the front matter capabilities; R1Q4 marked superseded (checkpoints are method work, one per prefix)
