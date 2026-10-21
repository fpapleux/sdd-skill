<!-- Architect: how the change will be built. Every behavior mentioned here
must be a scenario in spec-delta.md; anything new goes back as a question. -->

## Approach
- **Two halves.** The script half (REQ-ANL-001 to REQ-ANL-008, REQ-ORC-004 to REQ-ORC-006) lives in `skill/sdd/scripts/sdd.py`. The method half (the design and analyze phases, `next` routing, the Architect's failure-mode review) is design work under project rule 1, verified by review and dogfood run 3.
- **Check findings stay in `analyze()`; analyze-only findings go in a new `cross_artifact()`.** Contracts are check findings from the plan stage on, so they join `analyze()`. The design trace, failure modes, clauses and balance are appended to the same `Report` by `cross_artifact()`, which only `analyze`, `approve plan` and `next` call, so an error that check also reports is printed once. Rejected: running them in `analyze()` behind a flag, which would put them in `status` and every gate.
- **design.md is read on its own,** through one view that drops comments and blanks fenced code, so the trace, Failure modes and Contracts rules share the same exclusions and a `## ` inside a fence can't split a section.
- **`next` derives its steps from reports, not new state.** It runs `analyze()` at the spec stage and the full analysis at the plan stage, and classifies errors by set difference. Rejected: tagging every `err()` call with a rule ID, which touches every existing check.
- **Read-only.** `analyze` and `next` write nothing; `approve plan` writes only after the analysis passes.

## Components and interfaces
- interface: sdd.py analyze
- interface: sdd.py next
- interface: design.md Failure modes
- interface: design.md Contracts
- **`Report`** (REQ-ANL-001): gains `reqs` (parsed requirements), `design_errors`, `round_errors` and `open_findings`. `render(head=None, scenarios=False)` swaps the header and adds the scenarios line. A new `report_json(report)` builds the dict `cmd_check` prints today; check and analyze both use it.
- **`design_view(path) -> str | None`** (REQ-ANL-002, REQ-ANL-003, REQ-ANL-005): None for a mini change; otherwise design.md's text (empty when the file is missing) after `strip_comments`, with each line from an opening fence (three backticks or tildes) to its closing fence, or to the end of the file, replaced by an empty line.
- **`analyze()`** (REQ-ANL-005): fills the new fields; wraps the `err` it passes to `check_rounds` so those errors also land in `round_errors`; `check_rounds` returns `(unanswered, open_findings)`, an open finding being one its existing "is open" errors report. At the plan stage and later, for a standard change, it calls the new `check_contracts(view, err, warn)`, whose errors also land in `design_errors`.
- **`cross_artifact(project, path, report)`** (REQ-ANL-002, REQ-ANL-003, REQ-ANL-004, REQ-ANL-006, REQ-ANL-007): appends, in this order, the trace, Failure modes and presence findings, only when `design_rules_apply(fm)` (size standard, and the effective status, `blocked_from` for a blocked change, at or past `designed` in `STATUS_ORDER`, so never when abandoned); then the clause and balance warnings, at any size and status. Its errors also land in `design_errors`.
  - Trace: named IDs are the distinct `REQ_TOKEN` matches in the view, in order of first appearance; known IDs are the change's plus the registry's.
  - Counting scenario references: the change's non-removed scenarios, plus those of the new `living_scenarios(project)` (REQ ID → scenario IDs, parsed from each capability's Requirements) for requirements the change neither modifies nor removes.
  - Clauses: `req.text.split(";")`, stripped, empties dropped, skipped below two; words are `[A-Za-z]{5,}` runs, lowercased; a clause is covered when one of its distinctive words is among the lowercased `[A-Za-z]+` runs of a scenario's Given, When and Then cells; removed requirements are skipped; the printed clause drops one final period.
  - Balance: warns when `happy > negative + boundary` in `report.counts["scenarios"]` and the level is above prototype.
- **`full_analysis(project, path) -> Report`**: `analyze(project, path, "plan")`, then `cross_artifact`. Used by `cmd_analyze`, `cmd_approve` plan and `cmd_next`.
- **`cmd_approve` plan** (REQ-ANL-008): calls `full_analysis` instead of `analyze(…, "plan")`; on an error it prints the analyze rendering and raises `plan approval refused: fix the analyze errors first`. The open-question and critic checks that follow are unchanged.
- **`cmd_next` and `next_lines(project, path) -> list`** (REQ-ORC-004, REQ-ORC-005): see the contract. `amendment_logged(whole) -> bool` (logged Amendments entries ≥ amend approvals + 1) is factored out of `cmd_approve` amend and shared.
- **`next_step_standard`** (REQ-ORC-006): at designed with tasks and a clean check it returns `sdd analyze, then ask for plan approval`, replacing "awaiting operator approval of the plan: sdd approve". Existing tests that assert the old line are updated.
- **Parser:** `analyze [--change] [--json]` and `next [--change]`; the module docstring lists both.
- **Method half** (project rule 1): `method/phases/design.md` gains Failure modes, Contracts and the failure-mode review: a strong-tier read-only subagent (a fresh session in Codex) reads the spec and design and returns missed failure modes, each answered by an existing scenario or N/A, or raised with the operator for `sdd amend`. New `method/phases/analyze.md` (run it, route design errors to design and plan errors to tasks, report warnings) and `method/phases/next.md` (run `SDD next`, execute each step in turn, stop at the gate line). `roles/architect.md`, `format.md` (both grammars), `overview.md` (script table), `SKILL.md` (routing rows; analyze and next leave "Not built yet") and `templates/standard/design.md` (both headings, examples only in comments) follow. README, RELEASE_NOTES and the version (rule 9) at delivery.

## Test strategy
- One test per scenario in `tests/test_sdd.py`, named `test_REQ_<PREFIX>_<NNN>_<ID>_…`, in new classes `AnalyzeTests`, `DesignTraceTests`, `FailureModeTests`, `ContractTests`, `ClauseTests`, `BalanceTests`, `PlanGateAnalyzeTests`, `NextTests` and `StatusAnalyzeTests`.
- All unit-level: the `Repo` helper drives `sdd.main` in a temporary folder, with no git and no subprocess. "No file is changed" compares `snapshot()` before and after.
- Fixtures: a `designed(level, design)` helper (requirements with N/A boundary and access lines, a fresh-session round, spec approval, design.md written, `advance designed`, a task per scenario), and a living-spec file `specs/capabilities/orchestration/spec.md` holding REQ-ORC-001 (S1, N1, N4) and REQ-ORC-002 (S1) for the living-spec, modified and removed rows.
- No test doubles: every requirement is N/A dependency (local files only).
- Mutation check (rule 4): the Planner adds one `## Mutations` entry per new rule; the Verifier runs the pinned `SDD mutate` (rule 7), which breaks a scratch copy of the development script.
- Test command: `python3 -m unittest tests.test_sdd`
- Test one: `python3 -m unittest tests.test_sdd.{name}`

## Failure modes
- FM1 design.md is missing from a standard change at designed or later, so the view is empty → REQ-ANL-004.N1, REQ-ANL-002.N2
- FM2 a fence in design.md is never closed, so the view blanks the rest of the file → REQ-ANL-002.B6, REQ-ANL-003.B5
- FM3 a living-spec scenario row doesn't parse (not five cells), so it doesn't count → REQ-ANL-003.N2
- FM4 the plan gate's analysis raises (an unreadable file, an invalid level) → N/A: the approval row is written only after it passes
- FM5 the files change between the two analyses `next` runs → N/A: a read-only advisory command, rerun for the current answer

## Contracts
### sdd.py analyze
- Input: `sdd.py analyze [--change <id>] [--json]`: the active change or the one named; the active change is never switched (REQ-ANL-001).
- Text: check's report with the header `analyze <id> (assurance: <level>)`; the cross-artifact findings appended at the end of the `errors (<n>):` and `warnings (<n>):` blocks (the counts include them); and `scenarios: <h> happy, <n> negative, <b> boundary` (from `counts["scenarios"]`) as the line just before `result: OK|FAIL`, after any open-questions line.
- `--json`: exactly check's keys (`ok`, `stage` = "plan", `errors`, `warnings`, `coverage`, `open_questions` and the counts), with the findings merged into `errors` and `warnings`.
- Exit: 1 when any error is printed, else 0; 2 for argparse usage errors; 1 with check's existing message when specs/ isn't initialized, no change is active, or the ID isn't in specs/changes/.
- Messages: `design.md names <ID>, which doesn't exist (in this change or the living spec)`; `<ID> is not named in design.md: trace each component to its requirements`; `design.md has no failure modes: list each as "- FM<n> <what fails> → <scenario>", or write "- None — <reason>"` (an error at production and above, a warning below); `<ID>: no scenario exercises the clause "<clause>" (heuristic)`; `<h> happy scenarios outweigh <k> non-happy ones`.
### sdd.py next
- Input: `sdd.py next [--change <id>]`. Exit 0 with the lines below, or 1 with check's existing message (not initialized, no active change, unknown or archived ID). It writes nothing.
- Only the first that applies, alone: abandoned → `nothing to run: the change is abandoned`; constitution changed → `the constitution changed since approval: review it, then sdd approve (constitution)`; the lock error → `1. sdd amend` unless `amendment_logged`, then `gate: the operator approves the amendment (sdd approve amend)`; blocked → `blocked: resolve the blocker, then sdd status`.
- Otherwise `<n>. sdd <phase>` lines numbered from 1, then one gate line. A spec error is a spec-stage error not in `round_errors`; a plan error is a plan-stage error absent at the spec stage and not in `design_errors`; clarify applies when `report.critic`, `open_questions` or `open_findings` is non-empty; the verdict is `latest_verdict` of Verification.

| Size and status | Steps, in order (condition) | Gate |
| --- | --- | --- |
| standard draft, clarifying | specify (no requirements or a spec error), clarify (clarify applies) | spec |
| standard spec-approved | design, tasks, analyze | plan |
| standard designed | design (any `design_errors`), tasks (no tasks or a plan error), analyze | plan |
| any planned, implementing | implement (planned, or a task unticked), verify | results (standard), review (mini) |
| any verifying | verify (no verdict); none for PASS, GAPS or another word | as above; gaps for GAPS or another word |
| standard verified | archive | none |
| mini draft | specify (as standard), tasks (as designed), clarify (clarify applies) | plan |
| mini verified | none | review |

- Gate lines: spec `gate: the operator approves the spec (sdd approve spec)`; plan `gate: the operator approves the plan (sdd approve plan)`; results `gate: the operator approves the results (sdd approve results)`; review `gate: the operator reviews the verification, then sdd archive`; gaps `gate: the operator decides on the gaps (amend or accept), then sdd verify`; none `gate: none`.
- Any other status (a front-matter typo, a mini change at a standard-only status): exit 1, `cannot list steps: unknown status "<value>"` (REQ-ORC-004.N15).
### design.md Failure modes
- Where: `## Failure modes` in a standard change's design.md, through `design_view`; checked by `cross_artifact` (REQ-ANL-003, REQ-ANL-004).
- A bullet is a line matching `^\s*[-*] `; other lines are ignored. An entry is a bullet whose text starts with `FM<n>` or `None`, then a space, `:`, `—` or the end of the line (case-sensitive).
- FM entry: split at the last `→`; the text between `FM<n>` and the arrow, after its separator, is non-empty; the outcome is `N/A` (any case), then `:` or `—` and a reason of 3+ words, or comma-separated parts that each fully match `SCENARIO_REF`. FM numbers compare as integers. None line: `None`, then `:` or `—` and a reason of 3+ words, as the section's only entry.
- Errors, each prefixed `Failure modes: `: `FM1 has no outcome (end the line with → <scenarios> or → N/A: <reason>)`; `FM1 has no text before its arrow`; `FM1's outcome is neither scenario references nor N/A: <reason>`; `FM1's N/A needs a real reason (at least 3 words)`; `FM1 names <ref>, which doesn't exist: a failure mode the spec doesn't cover needs an amendment (sdd amend)` (only when its requirement exists); `FM<int> is repeated` (once per number); `"<bullet>" is neither a failure-mode entry nor a None line`; `the None line needs a reason of at least 3 words`; `a None line can't sit next to entries` (once).
### design.md Contracts
- Where: interface lines `^\s*[-*]\s+interface\s*:(.*)$` (any case) anywhere in the view outside `## Contracts`, and `^###(?!#)(.*)$` entries inside it; checked by `analyze()` at the plan stage and later, standard changes only (REQ-ANL-005).
- Names are trimmed of spaces, then of surrounding backticks, and matched exactly; an interface listed twice counts once.
- Errors: `the interface "<name>" has no contract entry (add "### <name>" under ## Contracts)`, once per distinct interface; `an interface line has no name`; `a contract entry under ## Contracts has no name`; `the contract entry "<name>" is repeated`. Warning: `the contract entry "<name>" has no interface line`.
