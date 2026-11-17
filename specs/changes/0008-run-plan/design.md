<!-- Architect: how the change will be built. Every behavior mentioned here
must be a scenario in spec-delta.md; anything new goes back as a question. -->

## Approach
- **Two commands, one step builder.** `run-plan` (REQ-ORC-009 to 011) prints the steps; `test` (REQ-EVD-007 to 011) runs one. Both get a step's command from the same functions (`design_line`, `task_command`, `component_command`), so `test` runs exactly what `run-plan` prints. Rejected: `test` deriving its own commands, which would let the two drift.
- **Refuse first, then act; write whole files only.** Each command runs its refusals in the spec's order before it prints, deletes, renames or runs anything; a refusal is an `SddError` (`error: …`, exit 1 via `main()`). Every file sdd.py writes goes through `write_atomic`, and the previous last run is renamed only when the new one is saved, so a killed sdd.py leaves each file whole and the last run in place.
- **Outcomes from JUnit XML, read with `xml.etree.ElementTree`** (stdlib, rule 2); with no readable report, the exit code and the last 20 lines. Rejected: parsing each runner's text output, which differs per framework and version.
- **Run files in `specs/.sdd/runs/`, the baseline in the change folder.** `specs/` is outside the reuse digest, so ticking a task, writing red/green lines or recording a run never stops a reuse (REQ-EVD-009.S2). Rejected: a cache outside git (Q8 replaced it).
- **Sorting is the existing rule, factored out.** `cmd_sort_failures`'s loop becomes `sort_lines(names, passed, refs, tasks)`, used by `sort-failures` (output unchanged, REQ-EVD-005/006 tests guard it) and by the `test` report.
- **Method half** (project rule 1): implement and verify follow the plan and run each step through `SDD test`, reading its report; listed under Method changes.

## Components and interfaces
All in `skill/sdd/scripts/sdd.py` unless named otherwise.
- interface: run-plan
- interface: test
- interface: last-run.json
- interface: baseline.txt
- interface: Test report
- interface: tests.junit_run
- **`design_line(design, key) -> str`** (REQ-ORC-009, REQ-EVD-007): the first line matching `^\s*[-*]\s*<key>\s*:[ \t]*(.*)$` (multiline) of `design_text(path)`, stripped of spaces and backticks; `""` when absent. `test_component` becomes a call to it (same result). `test_command()` and `test_one()` stay as they are for check, `advance designed`, replay and mutate (Known gap).
- **`step_commands(path) -> dict`** (REQ-ORC-011, REQ-EVD-011): `one`, `full`, `component`, `report` from `design_line`; the checks "missing or empty" and "quote not closed" (`shlex.split` raising `ValueError`) per key, run only for the keys a caller needs, in the caller's order.
- **`task_command(one, task)`** (REQ-ORC-009, REQ-EVD-011): `("none", None)` when `not evidence_present(task["test"])`; `("no-colons", None)` when `expand()` returns `None`; else `("ok", argv)`. Printed as `shlex.join(argv)`, which quotes exactly the words REQ-ORC-009 names (verified by ORC-009.B5).
- **`component_command(template, prefix) -> str`**: `template.replace("{prefix}", prefix)`; run as `shlex.split` of that text. The full suite runs `shlex.split(full)`.
- **Run-plan**: `run_plan_selection(tasks, form)`, `plan_lines(...)` and `cmd_run_plan`, as the earlier draft had them (forms `^T\d+$`, `^(T\d+)-(T\d+)$`, `next`, `all`; unknown ID before range; reversed range by plan position, `>`; checkpoint walk keeping the open group's prefix, ticked and no-reference tasks leaving it untouched). Changed by A1/A2: the baseline line replaces the record step, chosen in the spec's order: baseline.txt present → `recorded <time>`; else no or an empty `Test report:` → `none (the design has no "Test report:" line)` (ORC-009.B10); else a ticked task → `none (a task is ticked…)`; else the numbered step. ORC-011 adds the baseline.txt check last.
- **`read_baseline(folder) -> (time, commit, names) | None`** (REQ-EVD-008, REQ-ORC-011.N12, REQ-EVD-011.N18): `None` when baseline.txt is absent; `SddError` naming baseline.txt and `# baseline <time> <commit>` when its first line doesn't match `^# baseline (\S+) (\S+)\s*$`; names are the other non-blank lines, stripped.
- **`read_junit(path) -> list | None`** (REQ-EVD-007): `None` when the file is missing, `ET.ParseError` or `OSError` is raised, or the root is not `testsuites`/`testsuite`. Else one entry per `testcase` found at any depth (`root.iter`, document order; duplicates kept, Known gap): `name` = `classname + "." + name`, or `name` when `classname` is absent or empty; outcome from its first `failure`, `error` or `skipped` child, else `passed` (other children, such as `rerunFailure` or `flakyFailure`, are ignored); `lines` = the `message` attribute then the text, split into lines, right-stripped, blank lines dropped, the first 5 kept.
- **`run_digest(project) -> (commit, digest)`** (REQ-EVD-009, REQ-EVD-008.B2): `commit` is `git rev-parse --verify HEAD`, `None` outside a git work tree or before the first commit (baseline.txt then writes `none`, and nothing is reused: EVD-009.N1, N2). The files are `git ls-files -z` (tracked) plus `git ls-files -z --others --exclude-standard`, NUL-split so quoted non-ASCII paths are kept, not under `specs/`, deduplicated and sorted; a tracked path that no longer exists is left out (B6); a submodule (a folder) counts by `git -C <path> rev-parse HEAD`. `digest` is SHA-256 over `rel + "\0" + sha256(content).hexdigest() + "\n"` per file. Any `OSError` or failed git call (unreadable or vanished file, git missing) gives `digest = None`: no reuse, the step runs. It is computed before the report path is deleted.
- **`RunStore(project)`** (REQ-EVD-007): `specs/.sdd/runs/`. `load()` → record or `"unreadable"` (missing → `None`). `save(previous, record, log)`, called once the run has ended: writes `.gitignore` (`run-of-*\n`) when missing; renames last-run.json and .log to `run-of-<time with - for :>`, or `run-of-unreadable-<now>`, adding `-2`, `-3`… while either target exists (both forms); then writes the new pair with `write_atomic`. A run killed before `save` leaves the previous last run as it was.
- **`write_atomic(path, text)`**: writes a temporary file in the same folder (`encoding="utf-8"`, `newline=""`, so line endings are kept), then `os.replace`; used for tasks.md, spec.md, last-run.json/.log, baseline.txt and `.gitignore`.
- **`report_path(project, rel)`** (REQ-EVD-011.N14, N15, N19-N21), checked before anything runs, first problem wins: `unsafe_path(rel)` absolute → "absolute"; `(root / rel).resolve()` (symlinks followed) not inside `root.resolve()` → "leads outside the project"; `git ls-files -z -- <rel>` non-empty → "git tracks <rel>" (skipped outside git); `is_dir()` → "names a folder".
- **`run_step(project, ...)`** (REQ-EVD-007): takes `run_digest`, deletes the report file, `Popen(argv, cwd=project.root, stdout=PIPE, stderr=STDOUT)` (an `OSError` → `SddError('cannot start "<argv[0]>": <reason>')`, nothing renamed or recorded); `communicate()`; wall clock by `time.monotonic()`; output decoded UTF-8 with `errors="replace"`; the return code kept as is, a negative one (a signal) included, in the record, the result line and the warning; then `save`. The project path (`str(project.root)` and its `resolve()`, longest first) becomes `.` in the log, the record and the report only where a `/` or `\` or the end of the text follows it (`re.escape(root) + r"(?=[/\\]|$)"`), so a sibling such as `/x/sdd-old` is untouched.
- **`report_lines(record, refs, tasks, baseline, reused) -> (lines, exit)`** (REQ-EVD-007, REQ-EVD-009): the report of REQ-EVD-007, built from a record only, so a reused run is printed by the same code with ` (reused from <time>)`. Reuse needs a commit, a digest and equal change, step and command; a reused run still feeds `--red`, `--green` and `baseline`, which write from it with its time (EVD-008.B3, EVD-010.B5).
- **`write_evidence(path, task_id, kind, text)`** (REQ-EVD-010): reads the file holding `## Tasks` (tasks.md, or a mini spec.md) again after the run, just before writing. In the task's block (its task line to the next task line or heading, outside HTML comments), the `red:`/`green:` line is rewritten as its own indent and bullet + `<kind>: <text>`; with none, a line with the `test:` line's indent and bullet is inserted right after it (B4); no other byte changes. Two lines of that kind are refused before the run, naming both (N10). The red text is `failed: <first message line>`, or `failed` when there is no message or the line holds `<!--`, `-->` or `(after T` (B6). The time is the run's own, a reused one's included (B5); a skipped test is refused (N9).
- **`cmd_test`** and **`build_parser`**: `run-plan [form] [--change]` (`form` `nargs="?"`, default `next`, no `choices`); `test <step…> [--change] [--red] [--green] [--rerun]` (`step` `nargs="*"`, joined by a space, so a bad step reaches the ordered checks and exits 1, not argparse's 2); a `now_utc()` helper (`%Y-%m-%dT%H:%M:%SZ`) that tests patch; module docstring lines for both.
- **`tests/junit_run.py`** (this repository's adapter; REQ-EVD-007 Known gap): run as `python3 -m tests.junit_run <unittest args>`; it calls `unittest.main(module=None, argv=…, exit=False)` with a result class that records each test, then writes `build/junit.xml` and exits 0 when the run was successful, else 1. `build/` is added to `.gitignore`, so the report never changes the digest.

## Test strategy
- Integration through `sdd.main()` with the `Repo` helper, as the existing classes do; no unit test of private helpers. New classes: `RunPlanTests`, `RunPlanCheckpointTests`, `RunPlanRefusalTests` (ORC-009 to 011, no git, no subprocess: "no file is changed" compares `snapshot()`), `TestStepTests` (EVD-007), `BaselineTests` (EVD-008), `ReuseTests` (EVD-009), `RedGreenTests` (EVD-010), `TestRefusalTests` (EVD-011).
- Fixture `RunnerBase(Base)`: a change 0001-x with the S1 design lines (varied per row), tasks via `set_file_section` or `Repo.fill`, the status set with `sdd.set_front_matter`; a temp git repository (the existing `git()` helper, `GIT`, `GIT_CEILING_DIRECTORIES`) committed before each run, except where a row needs no git (EVD-009.N1).
- Test double, the fake runner: `fake.py`, written into the project per test from a JSON plan (the report XML or none, the lines to print, the exit code); it appends one line per run to a counter file in the test's scratch folder, outside the project, so "fake.py is (not) run" is read without changing the digest. Run as `sys.executable`, quoted with `shlex.quote` in the design line. A malformed report, a stale report and a 30-line output are plan entries.
- Time: `mock.patch.object(sdd, "now_utc")` fixes the run time (EVD-007.B5, B6, EVD-009.S1); `<s>` and `<time>` are matched by regex. "No run is recorded" and "unchanged, not renamed" compare `snapshot(specs/.sdd/runs)`; "git status lists" uses `git status --porcelain`.
- Can't start (EVD-007.N4): a command `no-such-runner`, a real `FileNotFoundError`. Absolute path (EVD-007.B8): fake.py prints `os.getcwd() + "/t.py"`.
- Mutation check (rule 4): one `## Mutations` entry per rule, added by the Implementer once its task is green; the Verifier runs the pinned `SDD mutate` (rule 7).
- Test command: `python3 -m tests.junit_run tests.test_sdd`
- Test one: `python3 -m tests.junit_run tests.test_sdd.{name}`
- Test component: `python3 -m tests.junit_run tests.test_sdd -k REQ_{prefix}_`
- Test report: `build/junit.xml`

## Mutations guidance
One entry per rule. Run-plan: form regex anchors; reversed range `>` (ORC-009.B1 catches `>=`); unknown ID before the range; status set; status before form; list-line-only reader; empty and unclosed command refusals; placeholder test line; "no test line" before "no command"; `shlex.join`; ticked and no-reference tasks leave the group open; checkpoint at the range end; skipped line; baseline line's three forms; baseline.txt header regex. Test: step regex; status set (verifying allowed); refusal order (status before step, baseline refusals right after the step); undeclared prefix; `--red`/`--green` exclusivity; report path `unsafe_path`; report deleted before the run; rename only after start; `-2` suffix; `.gitignore` when missing; `.` for the root; 5-line cap; `(no message)`; classname join; exit-code warning; exit 1 on regression; no-report fallback and its exit; reuse keys (change, step, command, commit, digest) each; `--rerun`; no reuse outside git; name match (equals, or ends with `.` + part); `failed:` prefix on red; green refused without red; ticked refused.

## Method changes (design work, project rule 1)
Edits in `skill/sdd/` of the development checkout, never in the installed skill; the Planner attaches them as `also:` lines:
- also (the first task): `tests/junit_run.py` and `build/` in `.gitignore`, so this change's own design lines run from T1.
- also (last REQ-ORC-010 task): `method/phases/implement.md` step 5, "One checkpoint per prefix." becomes: a capability declared with two prefixes gets one checkpoint per prefix; a prefix whose tasks are split by tasks of another prefix gets one checkpoint after each of its groups.
- also (last REQ-EVD-010 task): `method/phases/implement.md`: before the first task, `SDD run-plan <selection>`, then follow its steps in order: `SDD test baseline` at the baseline step; per task `SDD test T<n> --red`, code, `SDD test T<n> --green` (`pre-existing` and `(after T<n>)` reds stay by hand); `SDD test component <PREFIX>` and `SDD test full` where the plan puts them; read the report, open last-run.log only when its lines don't explain a failure; the sorts come from the report (the `--passed-before` file and `sort-failures` remain for a design with no `Test report:`); commit the run files with the work.
- also (same task): `method/roles/implementer.md` steps 2, 3, 5 and the checkpoint row; `method/phases/verify.md` and `method/roles/verifier.md` step 1: `SDD test full --rerun`, recording its `result:` line; `method/format.md`: the `Test report:` line (git-ignored path), the first-list-line reading of all four design lines, baseline.txt, `specs/.sdd/runs/`, and red/green lines written as `(sdd test <time>)`; `method/overview.md` script table and `SKILL.md` implement row; `templates/standard/design.md` and `templates/mini-spec.md` gain `- Test report:`.
- At delivery: README, RELEASE_NOTES and the version (rule 9). Backward compatibility (rule 5): a design with no `Test report:` gets the fallback, a change with no baseline.txt sorts with the warning, and `sort-failures`, check, replay and mutate are unchanged.

## Failure modes
- FM1 no specs/, no active change, an unknown `--change` → REQ-ORC-011.N11, REQ-ORC-011.N5, REQ-ORC-011.N6, REQ-EVD-011.N1, REQ-EVD-011.N2, REQ-EVD-011.N3
- FM2 a status where the command can't run → REQ-ORC-011.N4, REQ-EVD-011.N4, REQ-EVD-011.N13
- FM3 a malformed form or step, or argparse rejecting it with exit 2 → REQ-ORC-011.N1, REQ-EVD-011.N5
- FM4 a reversed range, or T2-T2 refused as reversed → REQ-ORC-011.N2, REQ-ORC-009.B1
- FM5 a task or prefix that isn't in the change → REQ-ORC-011.N3, REQ-EVD-011.N6, REQ-EVD-011.N7
- FM6 a design line missing, empty, read from prose, or with an unclosed quote → REQ-ORC-011.N7, REQ-ORC-011.N8, REQ-ORC-011.N9, REQ-ORC-011.N10, REQ-EVD-011.N10, REQ-EVD-011.N11
- FM7 a filled word needing quotes prints unquoted → REQ-ORC-009.B5
- FM8 a test line without `::`, empty or a placeholder → REQ-ORC-009.B6, REQ-ORC-009.B7, REQ-EVD-011.N12, REQ-EVD-011.N16, REQ-EVD-011.N17
- FM9 a mini change's design looked for in design.md → REQ-ORC-009.B8
- FM10 a range with no task to do prints a step → REQ-ORC-009.B3, REQ-ORC-009.B4
- FM11 groups split or joined wrongly, or a skipped checkpoint printed empty → REQ-ORC-010.S1, REQ-ORC-010.B2, REQ-ORC-010.B3, REQ-ORC-010.B4, REQ-ORC-010.B5
- FM12 the `Test component:` command lacks `{prefix}` → REQ-EVD-004.N1, REQ-EVD-004.N2
- FM13 run-plan or test writes a file it shouldn't or moves the status → REQ-ORC-009.S1, REQ-ORC-009.B8, REQ-EVD-007.B4, REQ-EVD-008.S1
- FM14 a baseline step offered after a tick, again once recorded, or with no report line → REQ-ORC-009.S1, REQ-ORC-009.B9, REQ-ORC-009.B10
- FM15 baseline.txt has no header (a merge conflict) → REQ-ORC-011.N12, REQ-EVD-011.N18
- FM16 `--red`/`--green` misused → REQ-EVD-011.N8, REQ-EVD-011.N9
- FM17 the report path deletes or reads a file it shouldn't: absolute, outside, through a symlink, tracked, a folder → REQ-EVD-011.N14, REQ-EVD-011.N15, REQ-EVD-011.N19, REQ-EVD-011.N20, REQ-EVD-011.N21
- FM18 the runner can't start, and the last run is renamed anyway → REQ-EVD-007.N4
- FM19 no or an empty report line, a stale report, malformed XML → REQ-EVD-007.N1, REQ-EVD-007.N7, REQ-EVD-007.N2, REQ-EVD-007.N3
- FM20 last-run.json is unreadable, or its run-of-unreadable name is taken → REQ-EVD-007.N5, REQ-EVD-007.B6
- FM21 the runner fails after writing a clean report → REQ-EVD-007.N6
- FM22 a message too long or empty, a testcase without classname, none at all → REQ-EVD-007.B1, REQ-EVD-007.B7, REQ-EVD-007.B2, REQ-EVD-007.B3
- FM23 an older run overwritten, or a run-of name taken → REQ-EVD-007.B5, REQ-EVD-007.B6
- FM24 the absolute project path committed → REQ-EVD-007.B8
- FM25 the regression rule not applied to a run → REQ-EVD-007.S4, REQ-EVD-008.S2
- FM26 a baseline rerun, after a tick, at verifying, without a report, empty, outside git, or from a reused run → REQ-EVD-008.N1, REQ-EVD-008.N2, REQ-EVD-008.N3, REQ-EVD-008.N4, REQ-EVD-008.N5, REQ-EVD-008.B1, REQ-EVD-008.B2, REQ-EVD-008.B3
- FM27 a reuse on changed code, another step, change or commit → REQ-EVD-009.B1, REQ-EVD-009.B2, REQ-EVD-009.B4, REQ-EVD-009.B5, REQ-EVD-009.B6, REQ-EVD-009.B7
- FM28 an ignored file, or a tick under specs/, stops a reuse or keeps a stale sort → REQ-EVD-009.B3, REQ-EVD-009.S2
- FM29 `--rerun` ignored, or a reuse outside git or before the first commit → REQ-EVD-009.S3, REQ-EVD-009.N1, REQ-EVD-009.N2
- FM30 a red or green line from the wrong outcome, a skipped test included → REQ-EVD-010.N1, REQ-EVD-010.N2, REQ-EVD-010.N3, REQ-EVD-010.N4, REQ-EVD-010.N5, REQ-EVD-010.N9
- FM31 evidence on a ticked task, green before red, or two red lines → REQ-EVD-010.N6, REQ-EVD-010.N7, REQ-EVD-010.N10
- FM32 a loose name match (two tests, or a plain suffix) → REQ-EVD-010.N8, REQ-EVD-010.B3
- FM33 the old text kept, a missing line, a reused run, a message that breaks the red line → REQ-EVD-010.S1, REQ-EVD-010.B1, REQ-EVD-010.B2, REQ-EVD-010.B4, REQ-EVD-010.B5, REQ-EVD-010.B6
- FM34 sdd.py killed mid-run loses the last run → N/A: the previous last run is renamed only in `save`, after the run has ended, so an interrupted run leaves it in place
- FM35 a file half-written (tasks.md, the run files, baseline.txt) → N/A: `write_atomic` writes a temporary file in the same folder and swaps it in with `os.replace`, keeping line endings
- FM36 tasks.md edited during the run is overwritten → N/A: `write_evidence` reads the file again after the run, just before writing
- FM37 the digest drops quoted non-ASCII paths, misses a submodule, or fails → N/A: NUL-split `git ls-files -z` lists, a submodule by its commit, and any failure means no reuse and a run
- FM38 deleting the report path changes the digest compared next time → N/A: the digest is computed before the report path is deleted
- FM39 a sibling folder such as /x/sdd-old rewritten as `.`-old → N/A: the root is replaced only before a path separator or the end of the text
- FM40 a nested testcase missed, or a rerun child read as the outcome → N/A: `root.iter("testcase")` finds every depth, and only the first failure, error or skipped child decides
- FM41 a run killed by a signal shown as a clean exit → N/A: the negative return code is printed as is, so the no-report result and the exit-code warning show it and exit 1
- FM42 a code edit during the run → N/A: the digest is taken before the command starts, so the next step sees a different digest and reruns
- FM43 a run that never ends → N/A: an accepted Known gap; sdd.py waits for the command, as the spec says
- FM44 concurrent runs, duplicate names, output size, runner artifacts, test-line filling, platforms, names with spaces → N/A: accepted A2 Known gaps; the design adds no handling for them

## Contracts
### run-plan
- Input: `sdd.py run-plan [T<n>|T<a>-T<b>|next|all] [--change <id>]`; reads the change's files and baseline.txt only.
- Output: the lines of REQ-ORC-009/010 on stdout, exit 0; no file written, no process started.
- Errors (stderr `error: …`, exit 1, no plan line), first in order: not initialized; no active change; no change `<id>`; `run-plan needs a change at planned or implementing: <id> is at <status>`; `"<form>" is not a form run-plan takes: use T<n>, T<a>-T<b>, next or all`; `<id> is not a task of the plan`; `<a> comes after <b> in the plan`; `no "Test one:" line in the design`; `no "Test command:" line in the design (or it is empty)`; `the "<key>" command has a quote that is not closed: <command>`; `baseline.txt does not start with a "# baseline <time> <commit>" line`.
### test
- Input: `sdd.py test <T<n>|component <PREFIX>|full|baseline> [--change <id>] [--red|--green] [--rerun]`.
- Output: the report of REQ-EVD-007 (REQ-EVD-008 for baseline, `(reused from <time>)` for REQ-EVD-009); files written: the report path deleted before the run, the run files (last-run.json), baseline.txt for `baseline`, one `red:`/`green:` line for `--red`/`--green`. Exit 1 on a regression, the exit-code warning, a non-zero exit with no report, or an EVD-008/010 error after the run; else 0.
- Errors before any run, first in order: not initialized; no active change; no change; status not planned, implementing or verifying; `"<step>" is not a step test takes: use T<n>, component <PREFIX>, full or baseline`; for baseline: recorded at `<time>` and never rerun, a task is ticked, status not planned or implementing, no `Test report:` line; task not in the plan; prefix not declared (naming the declared ones); `--red`/`--green` need a task step; not both; the step's design line missing, empty or unclosed; `Test report:` absolute, outside the project (symlinks followed), tracked by git or a folder; no test line; no `::`; baseline.txt header; then `T<n> is ticked`; two `red:` or `green:` lines; for `--green`, record red first. After the run: `cannot start "<cmd>"`; the EVD-010 outcome errors (passed, errored, skipped, not in the report, two matches, no report); a baseline needs a test report.
### last-run.json
- A JSON object: `time`, `change`, `step` (`T<n>`, `component <P>`, `full`, `baseline`), `command` (as printed), `commit` and `digest` (null outside git, before the first commit, or when the digest fails), `exit`, `seconds`, `tests` (list of `{name, outcome, lines}`, or null with no report), `tail` (the last 20 output lines). Readable when it parses and holds these keys; else kept as `run-of-unreadable-<now>`. last-run.log holds the full output; both have the project path written as `.`; `.gitignore` holds `run-of-*`.
### baseline.txt
- In the change folder: `# baseline <time> <commit>` (`none` without a commit; a reused run's time when reused), then one passed test name per line; written once by `test baseline`, never rewritten; header checked by `^# baseline (\S+) (\S+)\s*$`.
### Test report
- A design list line `- Test report: <path>`, read like `Test one:`; relative to the folder holding specs/, refused, before anything runs, when absolute, resolving outside it (symlinks followed), tracked by git or a folder; empty reads as absent (EVD-007.N7); deleted before each run; it should be git-ignored, or no step is ever reused.
### tests.junit_run
- Input: `python3 -m tests.junit_run <unittest names and options>` from the repository root.
- Output: the normal unittest output; `build/junit.xml` with `<testsuites><testsuite>` and one `<testcase classname="<module>.<class>" name="<method>">` per test, holding `<failure>`, `<error>` or `<skipped>` with a `message` (`<Exception>: <first line>`) and the traceback as text; an import error is an `<error>` testcase. Exit 0 when successful, else 1.
