# Phase: `next`

Run the change's remaining steps, in order, up to the next operator gate.

1. Run `SDD next` (`--change <id>` for a change other than the active one).
   It writes nothing. It prints either numbered steps (`1. sdd design`,
   `2. sdd tasks`, …) followed by one `gate: …` line, or a single line that
   replaces them (an abandoned or blocked change, a changed constitution).
   A pending amendment prints `1. sdd amend` and its gate line, or only the
   gate line once the amendment is logged.
2. **Run each step in turn.** For a `sdd <phase>` line, read that phase's
   file and follow it as if the operator had typed it. When a phase stops
   (a question for the operator, a refusal, two failed fixes), stop too and
   report.
3. After each step, run `SDD next` again and continue with its first step.
   The steps come from the change's files, so the list follows your work. If
   the step you just ran is still listed first, it didn't fix the problem:
   stop and report instead of running it again.
4. **Stop at the `gate:` line.** Show the gate's review digest and ask the
   operator. Never approve: only the operator does, and `SDD approve` records
   it. `gate: none` means nothing waits on the operator.
5. A single line with no gate says what the operator must do (review the
   constitution, resolve the blocker). Report it and stop.
6. Report the steps you ran, each one's result in one line, and the gate.
