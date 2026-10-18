<!-- Spec Critic: one round per review, started with `sdd.py round`. Format:
method/format.md. Required before the spec gate (standard changes at internal
and above; any size at production and above). -->

## Clarifications

### Round 1 — 2026-10-14 · Critic: fresh session

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-ORC-001 | issues | F1, F2, F3 |
| REQ-ORC-002 | issues | F4, F5, F6 |
| REQ-ORC-003 | issues | F6, F7 |
| REQ-EVD-001 | issues | F8, F9, F10, F11, F12, F13 |
| REQ-EVD-002 | issues | F14, F15, F16, F17 |
| REQ-EVD-003 | issues | F18, F19, F20 |

<!-- Question IDs continue after the proposal's Q1–Q4 to keep references unambiguous. -->

- F1 [ambiguity] REQ-ORC-001: a second escalation (light to mid, then two more failures) has no written form, and an escalation to any higher tier allows light to strong although Scope says a task moves up one tier → Q5 → fixed: statement allows a chain of one-tier steps; S3 (light, mid, strong chain) and N5 (light straight to strong refused) added; N2 and B1 errors reworded
- F2 [ambiguity] REQ-ORC-001: where the tier line sits is not said, nor which arrow counts → fixed: statement names the `  - tier:` line under the task and the Unicode arrow; N6 (an ASCII "->" refused) added
- F3 [untestable] REQ-ORC-001: status output is pinned only when every task has a tier; what it shows for tasks without one, and whether status --json carries the counts, is undecided → fixed: tasks without a tier count as untiered, status --json carries "tiers"; S1 extended, B3 and B4 added
- F4 [coverage] REQ-ORC-002: no scenario for a hand-written header with an invalid tier, "Critic: subagent (cheap)" → fixed: N4 added
- F5 [ambiguity] REQ-ORC-002: N1 and N2 pin exit 1 for a bad --subagent value and for --subagent with --fresh, but every other option's usage error exits 2 through argparse (e.g. check --stage bogus) → Q9 → fixed: N1 and N2 now exit 2 with argparse's message
- F6 [ambiguity] REQ-ORC-002: any valid tier counts as independent, so a light-tier Critic (or Verifier, REQ-ORC-003) satisfies production → Q6 → fixed: only "subagent (strong)" or a fresh session counts; ORC-002 B3 (mid) and B4 (internal, light), ORC-003 N5 (mid) added; Scope updated
- F7 [ambiguity] REQ-ORC-003: "the latest line that contains Verifier:" also matches HTML comments and fenced code (the mini template's Verification section holds a comment that begins "Verifier:"), and the accepted forms are not pinned (case; "fresh session" with or without "(production)") → fixed: a Verifier line is outside comments and fenced code; the text after "Verifier:" must begin with "fresh session" or "subagent (strong)", in any case; B3 (comment) and B4 (case) added
- F8 [ambiguity] REQ-EVD-001: "the current test files" laid over the base copy is undefined: only the files named in test lines, or every test file including new fixtures, tracked and untracked → Q7 → fixed: every file format.md counts as a test file, tracked or untracked and not ignored; B4 (untracked fixture) added
- F9 [coverage] REQ-EVD-001: a ticked task with an empty test line has no scenario (mutate has N7, replay has none) → fixed: such a task is a mismatch; N8 added
- F10 [coverage] REQ-EVD-001: a test line without "::" when the template uses {file} or {name} has no scenario → fixed: N9 added (mismatch, no command run)
- F11 [untestable] REQ-EVD-001: "the working tree is unchanged" is undefined while replay runs the suite inside the working tree; B3's "the command run is" needs the output to show each command; the command's working directory is not said → fixed: unchanged is defined through git status and file content; replay prints each command; commands run from the root; B3 reworded; known gap added for files a test itself writes
- F12 [ambiguity] REQ-EVD-001: "report" doesn't say whether replay and mutate only print, or also write into verification.md → fixed: both print only (statements say "print"); the Verifier records the result
- F13 [coverage] REQ-EVD-001: replay without --base has no scenario → Q9 → fixed: N10 added (exit 2, argparse names --base)
- F14 [ambiguity] REQ-EVD-002: which file holds `## Mutations` in a standard change, and whether it counts toward the size cap, is not said → fixed: tasks.md (standard) or spec.md (mini), not counted toward the size cap; B4 added
- F15 [ambiguity] REQ-EVD-002: the entry grammar is not pinned, and in particular how find and replace texts are delimited (leading spaces, backticks inside code, an empty replace that deletes) → Q8 → fixed: entry line and find/replace lines pinned; text between the first and last backtick; S1 shows the grammar; N7 (no backticks) and B3 (empty replace) added, EVD-003 B3 (leading spaces kept) added
- F16 [coverage] REQ-EVD-002: a file that is absolute or leaves the project ("../x.py") has no scenario; mutate would then edit a file outside its scratch copy, a real file → fixed: check refuses such paths (N5, N6 added); mutate never writes outside its scratch copies
- F17 [ambiguity] REQ-EVD-002: "unknown scenario" doesn't say whether it means a scenario of this change only → fixed: "a scenario that isn't one of this change's"; N2 reworded
- F18 [ambiguity] REQ-EVD-003: "a scratch copy of the working tree" doesn't say which files (ignored folders such as virtualenvs?), nor whether mutate needs git like replay (no dependency scenario for a folder outside git) → fixed: tracked and untracked, not ignored, files; mutate needs git; N8 added
- F19 [ambiguity] REQ-EVD-003: "the task that plans its scenario" assumes one task, but check accepts two tasks listing the same scenario → fixed: every such task's test runs; caught when all pass before and at least one fails after; B4 added; N9 (no task plans the scenario) added
- F20 [coverage] REQ-EVD-003: an interrupted run (Ctrl-C, a killed hang) can leave a scratch copy behind; neither a scenario nor a known gap says so → fixed: known gap added
- Q5 How is a twice-escalated tier written? A) a chain such as "light → mid → strong", each step exactly one tier up, a skip is an error B) one arrow to any higher tier, rewritten on each escalation — recommended: A
  - Answer: A — chained, one step at a time (operator, 2026-10-15)
- Q6 At production, which subagent counts as an independent Critic or Verifier? A) any valid tier, as written B) a strong one only — recommended: A
  - Answer: B — strong only (operator, 2026-10-15)
- Q7 Which current files does replay lay over the base copy? A) every test file per format.md, tracked or untracked and not ignored B) only the files named in ticked tasks' test lines — recommended: A
  - Answer: A — every test file (operator, 2026-10-15)
- Q8 How are find and replace texts written? A) between the line's first and last backtick, verbatim; an empty pair deletes B) the rest of the line, trimmed — recommended: A
  - Answer: A — between backticks (operator, 2026-10-15)
- Q9 What do usage errors (bad --subagent, --subagent with --fresh, replay without --base) return? A) exit 2 with argparse's message, like the other options B) exit 1 with sdd.py's own message, as written — recommended: A
  - Answer: A — exit 2, argparse (operator, 2026-10-15)
