# Phase: `specify`

Write the requirements of the active change. Role: **Spec Author**
(`method/roles/spec-author.md`). Grammar: `method/format.md`.

1. The active change must be `draft`. If it isn't, say why (show
   `SDD status`) and stop. If Intent or Scope is empty, write them first.
2. Write the requirements, with their scenarios and N/A lines, and the Known
   gaps list. Do the coverage walk from the role file for every requirement, at
   the change's assurance level.
3. Run `SDD check --stage spec` and fix every error. Read the warnings, and
   fix them unless you have a reason not to; if so, say it in the report.
4. Ask any open questions (at most 5, with options and your recommendation).
5. Report: the requirements as one line each, scenario counts (happy /
   negative / boundary), the N/A reasons, known gaps, and open questions.
   Next: `sdd tasks`.
