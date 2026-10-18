<!-- Architect: how the change will be built. Every behavior mentioned here
must be a scenario in spec-delta.md; anything new goes back as a question. -->

## Approach
- **Two halves.** The script half (REQ-ORC-001–003, REQ-EVD-001–003) lives in `skill/sdd/scripts/sdd.py`. The method half (prime orchestrator, role tiers, subagent Critic and Verifier, Planner mutations) is design work under project rule 1, so it is verified by review and a dogfood run, not by tests.
- **Parsing stays in `analyze`.** Tier lines, the Verifier line and `## Mutations` are parsed and checked where the other sections already are, so `check`, `status` and every gate see them with no new entry point.
- **Scratch copies are built from git, not by worktree.** The base copy is `git archive <rev>` extracted with `tarfile`. The working-tree copy is the files `git ls-files --cached --others --exclude-standard` lists. Rejected: `git worktree add`, which writes into `.git` and leaves a registered worktree behind if the run is killed.
- **Commands run without a shell.** The `Test one:` template is split with `shlex`, then `{test}`, `{file}` and `{name}` are substituted inside each token, so a test name stays one argument. The command runs with `subprocess.run(shell=False)`, and an `OSError` (missing runner) counts as a failure. Rejected: `shell=True`, which needs quoting rules for test names and would run any shell text found in a spec.
- **Results are printed only** (REQ-EVD-001, REQ-EVD-003). The Verifier quotes the summary in Verification, and the runner and tier are recorded by the agent, as the Known gaps say.

## Components and interfaces

### Tiers (REQ-ORC-001) — `sdd.py`
- `TIERS = ["light", "mid", "strong"]`. `parse_tasks` collects every `  - tier: …` line per task into `task["tiers"]` (the test/red/green regex stays unchanged).
- `tier_problem(value) -> str | None`: it splits on `→` and expects each part to be in `TIERS` (lowercase only) and each step to rise by exactly one. Error texts:
  - not in `TIERS`: `T1: tier 'cheap' is not one of: light, mid, strong`
  - a bad step: `T1: tier 'light → strong': each step must go up exactly one tier`
  - an ASCII arrow: `T1: tier 'light -> mid': an escalation is written with "→"`
  - two tier lines: `T1 has more than one tier line`
- The tier errors run in `analyze` for every task at every stage. The warning `T1: no tier (add '  - tier: light|mid|strong')` runs in `check_plan`, so at plan stage and later.
- `report.counts["tiers"]` holds only the non-zero counts, in the order light, mid, strong, untiered, and only when the change has tasks. A task counts as the last tier of its chain. `cmd_status` prints `  tiers: 1 light, 1 untiered` after the counts line, and `status --json` carries the same dict.

### Critic runner (REQ-ORC-002) — `sdd.py`
- `round` gets `--subagent {light,mid,strong}` in an argparse mutually exclusive group with `--fresh`. Usage errors exit 2 with argparse's own message ("argument --fresh: not allowed with argument --subagent"). The header becomes `Critic: subagent (<tier>)`.
- `parse_rounds` reads the runner after `Critic:`, in any case: `fresh session`, `same session`, `subagent (<word>)` or a bare `subagent`.
- `check_rounds`, at production and above, inspects only the latest round:
  - `fresh session` or `subagent (strong)`: no warning;
  - any other subagent form: `Round N's runner (subagent (mid)) is not independent: at production and above the Critic runs as a strong subagent or in a fresh session`;
  - anything else: the existing same-session warning.
- The gate's critic requirement (`critic_gate_errors`) is unchanged.

### Verifier runner (REQ-ORC-003) — `sdd.py`
- `latest_verifier(section_text) -> str | None` follows the same pattern as `latest_verdict`. It removes comments, skips fenced blocks, and returns the text after the last `verifier:` (any case).
- In `analyze`, at stage `verify` and level production or above, a missing value, or one that doesn't begin with `fresh session` or `subagent (strong)`, warns: `the Verifier should run in a fresh session or a strong subagent (latest Verifier line: <value or none>)`.

### Mutations section (REQ-EVD-002) — `sdd.py`
- `"Mutations"` is added to `UNCOUNTED_SECTIONS`.
- `parse_mutations(section_text) -> (list, problems)` reads entries `- M<n> <REQ-….ID> <file>` and their `find:`/`replace:` sub-lines. A text is the slice between the first and last backtick, and a line with fewer than two backticks is a problem naming the field.
- In `analyze`, when the section exists, it reports one error per problem, naming the mutation:
  - a missing field (`M1: missing replace`);
  - a duplicate ID;
  - a scenario not in this change's `scenario_refs`;
  - an unsafe path: `PurePosixPath(file).is_absolute()`, a drive letter, or a `..` part after normalization;
  - find equal to replace (`M1 changes nothing`).
- Templates: `templates/standard/tasks.md` and `templates/mini-spec.md` gain a tier line and a comment showing the `## Mutations` grammar. There is no empty section: an empty one would shadow a section written earlier in the same file.

### Runner helpers — `sdd.py` (REQ-EVD-001, REQ-EVD-003)
- `test_one(clean_text) -> str`: the first bullet line `- Test one: …` (anchored to the line start, so prose mentioning "Test one:" doesn't match), with backticks stripped like `test_command`. Its absence raises `SddError` naming "Test one:" (exit 1) before anything runs.
- `git_root(project)`: `git rev-parse --show-toplevel` and `--show-prefix`. On failure it raises `SddError("replay needs a git repository")` (or "mutate needs …").
- `expand(template, test_line) -> list | None`: the argv after substitution. It returns None when the template uses `{file}` or `{name}` and the line has no `::`.
- `run_test(argv, cwd) -> bool`: `subprocess.run(argv, cwd=cwd, stdout=DEVNULL, stderr=DEVNULL)`. Exit 0 is a pass; a non-zero exit or an `OSError` is a failure. There is no timeout (known gap).
- `scratch(kind)`: a context manager around `tempfile.mkdtemp(prefix=f"sdd-{kind}-")` that removes the folder in `finally`, so Ctrl-C cleans up too. A killed process leaves the folder (known gap).

### `replay --base <rev>` (REQ-EVD-001)
- `--base` is required (argparse, so exit 2). It also takes `--change`.
- Order of checks:
  1. a `Test one:` line exists;
  2. the folder is a git repository;
  3. `git rev-parse --verify --quiet <rev>^{commit}` succeeds, or the error is `unknown base revision 'nosuchrev'`.
- The base copy is `git archive <rev>` extracted into a scratch folder. Every current test file (`is_test_path`, outside `specs/`, existing on disk) is then copied over it, as bytes. The project root inside the copy is `<scratch>/<prefix>`.
- Per task, in order:
  - unticked: `T2 skipped (not ticked)`, nothing run;
  - empty test line, or a line with no `::` when the template needs one: a mismatch, nothing run;
  - a red line containing `(after T<n>)` where T<n> is listed earlier (A1): run once in the working tree only, `T2 confirmed now (depends on T1)` or `T2 mismatch: the test fails now`. A mention of a task ID without `(after` is not a dependency;
  - otherwise the command runs from the project root of the base copy and then of the working tree, and the output prints `run: <argv joined>` and `T1 confirmed` or `T1 mismatch: <reason>`. A test that fails now is reported first.
- Summary line `replay: 2 confirmed, 1 mismatch, 1 skipped`, or `nothing to replay: no ticked task`. Exit 1 on any mismatch.

### `mutate` (REQ-EVD-003)
- It takes `--change` and reads Mutations through `parse_mutations`. Structural problems are left to `check`: an entry it can't parse is reported invalid.
- Order of checks: an empty section prints `no mutations are planned` (exit 0); then a `Test one:` line must exist; then the folder must be a git repository.
- Per mutation:
  1. The file must exist in the working tree, else `invalid: the file doesn't exist`.
  2. It counts the find text's occurrences: `invalid: the find text is not in the file` or `invalid: the find text occurs N times`.
  3. It collects the test lines of every task whose refs include the scenario, ignoring tasks with an empty test line: none gives `invalid: no test to run`.
  4. It copies the working tree into a scratch folder, runs each test, and stops with `invalid: the test fails without the mutation` if any fails.
  5. It writes the replaced file and checks, by resolving the path, that it stays inside the scratch folder. Then it runs each test again.
- Result `M1 caught` / `M1 survived`, then a summary line. Exit 1 on any survived or invalid mutation.

### Method half (design work, project rule 1)
- `SKILL.md`, a new section "Orchestration":
  - The prime model keeps the operator conversation, the gates, `SDD approve` and routing.
  - It spawns a general-purpose subagent per role invocation, passing the tier's model and the role's effort and read-only instruction.
  - Tier → model: strong = `opus`, mid = `sonnet`, light = `haiku`, passed as the subagent's model.
  - Where the host has no subagents (Codex), the same session plays every role, and the Critic and Verifier run in a fresh session as today.
- Each `method/roles/*.md` gains a first line `Tier: … · Effort: … · Read-only: yes|no`:

  | Role | Tier | Effort | Read-only |
  | --- | --- | --- | --- |
  | Spec Author | strong | high | no |
  | Spec Critic | strong | high | yes |
  | Architect | strong | high | no |
  | Planner | mid | medium | no |
  | Implementer | the task's tier | medium | no |
  | Verifier | strong | high | yes |
  | Spec Steward | light | low | no |

- `planner.md`: a tier per task (light for mechanical tasks, mid by default, strong for tricky rules), and one `## Mutations` entry per new or changed rule. For a changed rule the Planner writes the whole entry. For a new rule the code doesn't exist yet, so the Planner names the scenario that guards it, and the Implementer adds the file, find and replace once that task is green (`implementer.md`).
- `implementer.md`: after two failed attempts at a task, the orchestrator appends the next tier to its chain and respawns the task.
- `clarify.md`: spawn the Critic with `SDD round --subagent strong`. `verify.md`: spawn the Verifier, which runs `SDD replay --base <merge-base>` and `SDD mutate`, quotes both summaries, and writes `Verifier: subagent (strong)`.
- `format.md`: the tier line, `## Mutations`, `Test one:` and the runner forms. The design template gains `- Test one:`.
- README and RELEASE_NOTES are updated at delivery, and the version follows project rule 9.

## Test strategy
- Every scenario gets one test in `tests/test_sdd.py`, named `test_REQ_<PREFIX>_<NNN>_<ID>_…`, in the new classes `TierTests`, `CriticRunnerTests`, `VerifierRunnerTests`, `MutationsCheckTests`, `ReplayTests` and `MutateTests`.
- **Unit-level** (ORC-001–003, EVD-002): the existing `Repo` helper drives `sdd.main` in a temporary folder. "No file is changed" is asserted by snapshotting the folder's files before and after.
- **Integration-level** (EVD-001, EVD-003): real `git` in a temporary repository, initialised with `git -c user.name=sdd-test -c user.email=test@example.invalid`.
  - The `Test one:` runner is a small checker script written by the test: `<sys.executable> -B tests/check.py {name}`. It exits 0 or 1 depending on the content of `src/dur.py`, so base, current and mutated states are set by editing one file.
  - B3 uses a runner script that only exits 0, and asserts on the printed `run:` line.
- **Doubles:**
  - N6/N8 (no git repository): a folder outside any repository, with `GIT_CEILING_DIRECTORIES` set through `mock.patch.dict(os.environ)`.
  - N7 (missing runner): a `Test one:` naming `no-such-runner`.
  - Scratch cleanup: `tempfile.tempdir` patched to a folder the test owns, asserted empty afterwards.
  - Working tree unchanged: `git status --porcelain` plus the bytes of every listed file, compared before and after.
- These tests need `git` on the path, as the development machine and CI have.
- **Mutation check (project rule 4).** The Planner lists this change's own mutations in `## Mutations`. The pinned tool (rule 7) has no `mutate` yet, so the Verifier breaks each rule by hand, as in 0001. The dev checkout's `mutate` may be run on them as a dogfood check, but it is not evidence.
- Test command: `python3 -m unittest tests.test_sdd`
- Test one: `python3 -m unittest tests.test_sdd.{name}`
