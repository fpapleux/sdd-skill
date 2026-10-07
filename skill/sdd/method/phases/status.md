# Phase: `status`

1. Run `SDD status`. If there is an active change, also run `SDD check` and
   read its output.
2. Tell the operator, in a few lines:
   - the project assurance level, and whether the constitution is approved;
   - the active change: ID, title, status, size, assurance;
   - its counts: requirements, scenarios (happy / negative / boundary), tasks
     done/total, known gaps, open questions;
   - the check result. If it fails, give the top 3 errors in plain language;
   - other in-flight changes, if any.
3. End with the single next command from the script's `next:` line, written
   with the operator's prefix (`/sdd` or `$sdd`).
