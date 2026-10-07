<!-- sdd:begin -->
## Spec-driven development (SDD)

This repository uses SDD. Specs in `specs/` are the contract for behavior.

- Don't change behavior without an approved change in `specs/changes/`
  (status `planned` or later). Tiny fixes are the exception, but a behavior
  change still needs a failing test first.
- Tests name the scenario they prove, e.g. `test_REQ_CHK_007_N1_invalid_email`.
- Current behavior: `specs/capabilities/`. Project rules and assurance level:
  `specs/constitution.md`.
- When something breaks: stop, analyze, think, plan, execute. No blind
  retries. After two failed fixes for the same problem, report to the operator.
- Work on changes with the `sdd` skill: `/sdd` in Claude Code, `$sdd` in Codex.
<!-- sdd:end -->
