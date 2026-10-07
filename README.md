# SDD — a spec-driven development skill for Claude Code and Codex

SDD makes your AI coding agent **write the spec first, get your approval, then
build it test-first** and keep the spec true after the code ships.

You describe what you want. The agent turns it into short, testable
requirements with IDs, asks you about the decisions that are yours to make, and
waits for your go-ahead. Then it writes a failing test for each scenario before
the code, verifies the result against the spec, and merges the change into a
**living spec** of how your system behaves.

- **One skill, two tools:** `/sdd …` in Claude Code, `$sdd …` in Codex. All
  state lives in plain files, so you can start a change in one tool and finish
  it in the other.
- **Light when the work is light.** Two independent dials, *size* and
  *assurance*, decide how much process a change gets. A demo
  stays a demo, and payment code gets the proof it needs.
- **Failure cases aren't optional.** A script, not the AI, checks that each
  requirement covers the failure categories its assurance level demands.
- **Test-first with evidence.** No task is done without a recorded failing run
  and a recorded passing run.
- **You stay in control.** Gates need your approval. Every approval is
  recorded with your words, and the agent can't skip a gate.
- **No dependencies.** Markdown instructions plus one Python standard-library
  script.

> **Status: v0.** The `mini` change size works end to end at every assurance
> level. Larger sizes, an independent reviewer, and extra verification for
> high-assurance work are on the [roadmap](#roadmap).

---

## Contents

- [Requirements](#requirements)
- [Install](#install)
- [Your first change](#your-first-change)
- [How it works](#how-it-works)
- [The two dials](#the-two-dials)
- [Testing discipline](#testing-discipline)
- [Working with existing code](#working-with-existing-code)
- [Reference](#reference)
- [Limitations in v0](#limitations-in-v0)
- [Roadmap](#roadmap)
- [FAQ](#faq)
- [Development](#development)
- [Acknowledgements](#acknowledgements) · [License](#license)

---

## Requirements

- [Claude Code](https://code.claude.com) and/or [Codex](https://developers.openai.com/codex).
- Python 3.8 or newer, on your `PATH` as `python3`. Only the standard library
  is used; v0 was tested on Python 3.14.
- A git repository for your project (recommended: specs are meant to be
  committed with the code).

## Install

```bash
git clone https://github.com/fpapleux/sdd-skill.git
cd sdd-skill
./install.sh
```

`install.sh` symlinks `skill/sdd` into `~/.claude/skills/sdd` and
`~/.codex/skills/sdd`, skipping any tool that isn't installed. It never
overwrites an existing folder.

| Task | How |
| --- | --- |
| Check it works | Open a project and type `/sdd status` (Claude Code) or `$sdd status` (Codex). |
| Update | `git pull` in your `sdd-skill` checkout. The symlinks make it live at once. |
| Uninstall | `./install.sh --uninstall` removes only the links that point at this checkout. |
| Install for one project only | Copy or symlink `skill/sdd` into that project's `.claude/skills/sdd`. |

Restart your agent session after installing, so that it discovers the skill.

## Your first change

Inside your project:

```text
/sdd init
```

The agent asks one question to set your project's **assurance level** (see
[the two dials](#the-two-dials)). Then it creates `specs/` and adds a short SDD
section to `AGENTS.md` (plus `@AGENTS.md` in `CLAUDE.md`), and shows you a
one-page **constitution** to approve. The constitution holds the project rules
every change is checked against.

```text
/sdd quick "Add a total command that sums durations listed in a file"
```

The agent writes the whole change in one file,
`specs/changes/0001-total-command/spec.md`, and checks it with the script. It
asks you only the questions that are product decisions (for example, *"A line
that can't be parsed: A) stop with an error, or B) skip it?"*), then shows a
short review digest:

```text
REQ-DUR-001  Parse "1h30m", "45m", "2h" → minutes; anything else raises ValueError
             scenarios: 3 happy · 4 invalid inputs · state/dependency: N/A (pure function)
REQ-DUR-002  `total <file>` prints the sum; bad line → exit 1; unreadable file → exit 2
             scenarios: 2 happy · 2 boundary (empty file) · 4 failure
Behavior change: parse_duration returned 0 for garbage → now raises ValueError
check: OK · 2 REQs · 15 scenarios · 15 tasks · 0 open questions
Approve this spec and plan?
```

```text
/sdd approve
/sdd implement all      # failing test first, then code, for every scenario
/sdd verify             # re-runs everything, checks each test against its scenario
/sdd archive            # merges the change into specs/capabilities/
```

At any time, `/sdd status` shows where things stand and the single next step.
In Codex, type `$sdd` instead of `/sdd`.

If you prefer to go step by step instead of using `quick`:
`propose` → `specify` → `tasks` → `approve`.

## How it works

### The loop

```text
 you: idea ─► spec (requirements + scenarios) ─► plan (test-first tasks) ─► YOU APPROVE
                                                                               │
 living spec ◄─ archive ◄─ verify ◄─ implement (red → green → refactor, per task)
```

For a `mini` change there is **one gate**: you approve the spec and the plan
together. Until then, the agent doesn't touch production code for that change.
The script enforces this: a change can't move past `draft` without a recorded
approval.

### Roles

The agent works through a sequence of roles. Each role has a boundary: what
it may write, and what it must not do. Handoffs happen through the spec file,
not through conversation.

| Role | Writes | Must not |
| --- | --- | --- |
| **Spec Author** | Intent, scope, requirements, scenarios, known gaps | Choose technology, write code, invent product decisions |
| **Planner** | Design notes, test-first tasks | Change requirements |
| **Implementer** | Code, tests, red/green evidence | Change the spec (it stops and asks instead) |
| **Verifier** | Verification report, gap tasks | Fix code, or trust a ticked box without re-running |
| **Spec Steward** | The living spec (via the script) | Accept behavior that was never approved |
| **You (operator)** | Intent, answers, approvals | — |

### What it creates in your repository

```text
specs/
  constitution.md                  # assurance level + project rules (you approve it)
  capabilities/<name>/spec.md      # LIVING spec: current approved behavior, known gaps, history
  changes/0001-total-command/spec.md   # in-flight changes
  archive/0001-total-command/spec.md   # finished changes
  .sdd/active                      # which change is active
AGENTS.md                          # short SDD section (read by Codex and others)
CLAUDE.md                          # gains "@AGENTS.md" (read by Claude Code)
```

Commit `specs/` with your code, in the same pull request. Then the spec change
is reviewed, merged and reverted together with the code it describes.

### A requirement, as written in the spec

```markdown
### REQ-DUR-002 Total the durations in a file
When the user runs the total command on a readable file that holds one
duration per line, the durations tool shall print the sum in minutes.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | lines "1h30m", "45m", "2h" | `total f.txt` | stdout "255" · exit 0 |
| B1 | boundary | an empty file | `total f.txt` | stdout "0" · exit 0 |
| N1 | validation | lines "1h", "abc" | `total f.txt` | stderr "error: line 2: invalid duration 'abc'" · exit 1 · stdout empty |
| N3 | dependency | no file "missing.txt" | `total missing.txt` | stderr "error: cannot read missing.txt" · exit 2 · stdout empty |

- N/A state: the command keeps no state between runs and writes no files
```

Each requirement is one [EARS](#faq) sentence with **shall**. Each
scenario is a concrete Given/When/Then row that becomes exactly one test,
named after its ID (`test_REQ_DUR_002_N1_rejects_bad_line`). And each task
records its evidence:

```markdown
- [x] T9 REQ-DUR-002.N1 Bad line stops with exit 1
  - test: tests/test_total.py::test_REQ_DUR_002_N1_rejects_bad_line
  - red: AssertionError: 1 != 0
  - green: 1 passed in 0.02s
```

---

## The two dials

Every piece of work runs with two **independent** settings: one describes the
**change**, the other describes the **product**. Together they decide how much
process you get. Small work stays light, and important work gets the proof it
needs.

> **Size decides the paperwork. Assurance decides the proof.**

There's also a two-page illustrated guide: [docs/two-dials.pdf](docs/two-dials.pdf).

| | Dial 1 · Size | Dial 2 · Assurance |
| --- | --- | --- |
| **Question** | How big is this change? | How much trust does the product need? |
| **Controls** | Paperwork: which files exist, how many approvals, which roles run | Proof: which tests, how many failure cases, how independent the review is |
| **Set** | Per change. The skill suggests one, and you confirm or change it. | Once per project, at `sdd init`. A change may go **higher**; going lower needs your recorded waiver. |
| **Scale** | `inline` · **`mini`** (default) · `standard` · `full` | `prototype` · `internal` · `production` · `critical` |

### Picking the settings

Start at the top of each ladder, and stop at the first "yes". If you're
unsure between two, take the higher one.

| Size | | Assurance | |
| --- | --- | --- | --- |
| Migration, public API, security, irreversible? | `full` | Money, security, safety, regulated, irreversible? | `critical` |
| Several areas, or a new component or interface? | `standard` | External users, or business data that persists? | `production` |
| One area, up to ~5 requirements, nothing new? | `mini` | Used by you or your team, with real data? | `internal` |
| Typo, one-line fix, config tweak? | `inline` | Demo or experiment; may be thrown away? | `prototype` |

### Dial 1 · Size: the paperwork (per change)

| Size | Typical change | What you get | Approvals | Normal flow |
| --- | --- | --- | --- | --- |
| `inline` | Typo, copy change, one-line fix, config tweak, dependency bump | No spec files. The commit message cites the requirement or bug. | None: your request is the approval | Just ask |
| **`mini`** (default) | One area, up to ~5 requirements, no new component | One `spec.md`: requirements, design notes, tasks, results | 1: spec + plan together | `quick` → approve → `implement` → `verify` → `archive` |
| `standard` *(v1)* | Several areas, or a new component, interface or data model | A change folder: proposal, spec changes, design, tasks, verification | 3: spec · plan · results | propose → specify → clarify → **✓ spec** → design + tasks → **✓ plan** → implement → verify → **✓ results** → archive |
| `full` *(v3)* | Data migration, public API, security model, irreversible operations | Change folder + interface contracts + decision records | 4: spec · design · tasks · results | Like standard, plus a separate design approval |

### Dial 2 · Assurance: the proof (per project)

| | `prototype` | `internal` | `production` | `critical` |
| --- | --- | --- | --- | --- |
| **Means** | Demo, experiment, learning; may be thrown away | Used by you or your team; real data, small blast radius | External users or business data that must persist | Money, security, safety, regulated, or irreversible |
| **Tests first** | Happy path | Every scenario | Every scenario | Every scenario |
| **Failure cases** | **None required.** A **Known gaps** list instead, one line per thing not handled | Bad input · wrong state or duplicates · failure of anything it calls | The above + boundaries · access rights (6 core categories) | The 6 core + concurrency · rule combinations · invariants |
| **A failure test checks** | — | The error shown, and that nothing else happened | The error, no side effects, state unchanged | Same as production |
| **Spec review** | Only open questions are flagged | Self-check; the script rejects blank coverage | Independent reviewer, fresh context *(v1)* | Independent reviewer, every round *(v3)* |
| **Verification** | Tests pass | Tests pass, coverage reported | Independent verifier: blocking coverage of changed code, plus probing for unexpected inputs *(v1)* | Production checks + mutation testing + property-based tests *(v3)* |

### Same dials, different results

Spec sizes are rough estimates.

| | `inline` | `mini` | `standard` | `full` |
| --- | --- | --- | --- | --- |
| **`critical`** | *Fix a typo in a refund error message.* No spec files, but the test still comes first. | | | *New refund rules in the payment service.* ≈ 700 lines + contracts · 4 approvals · full proof |
| **`production`** | | *"Resend confirmation" on the live shop.* ≈ 150 lines · 1 approval + reviewer questions | *Guest checkout on the live shop.* ≈ 300 lines · 3 approvals | |
| **`internal`** | | *Team script that imports CSV invoices.* ≈ 100 lines · 1 approval | | |
| **`prototype`** | *Change a label in the demo.* Just ask. | *Clickable checkout demo for a pitch.* ≈ 50 lines · 1 approval · happy-path tests + Known gaps | | |

### When a prototype grows up

The **Known gaps** list is not waste: it is the to-do list for hardening.
When a change is archived, its known gaps are carried into the living spec.
In v1, `sdd harden <capability> --to production` will turn them into
failure-case scenarios and tests, delivered as one normal change.
Prototypes cost nothing extra up front, and nothing is forgotten when they
become real.

---

## Testing discipline

**Test-first, always.** Every task follows the same loop:
1. Write the test for one scenario, named with its ID.
2. Run it, and record the **red** output. It must fail on an assertion about
   the behavior, not on an import error.
3. Write the minimal code.
4. Run it, and record the **green** output.
5. Refactor.

If the behavior already existed, the agent records
`red: pre-existing — <reason>`. Such tasks are reported to you and reviewed
by the Verifier.

**Failure cases are planned, not hoped for.** Each requirement is walked
through the failure categories its assurance level requires:

| Category | Questions it forces |
| --- | --- |
| `validation` | Missing, empty, malformed, wrong type, too long? |
| `state` | Wrong state, duplicate/replay, out of order, expired? |
| `dependency` | What it calls fails or times out: what does the user see, and what gets rolled back? |
| `boundary` | Min/max, ±1, zero, one, many? |
| `access` | Unauthenticated, wrong role, someone else's resource? |
| `concurrency` · `combination` · `invariant` | Double submit · every combination of conditions · what must always hold |

Each required category gets a scenario, or `- N/A <category>: <real reason>`.
A blank is an error, and so is a lazy "not needed".

**What the script checks (no AI judgment involved):**
- requirement and scenario IDs are unique and well formed, and every
  requirement has a happy path (an `If…then` rule needs a failure scenario
  instead);
- the required failure categories are covered, or have a real N/A reason;
- every scenario has a task, and every task proves a scenario;
- every ticked task has red evidence that shows a failure, and green
  evidence;
- before verification passes, every scenario is named in a **test file**;
- a change can't leave `draft` without a recorded approval, and a blocked
  change can only return to where it was;
- spec size stays under the cap (200 lines for `mini`);
- a `prototype` change keeps a Known gaps list.

The **Verifier** then does what a script can't. It re-runs everything, reads
each test against its scenario ("does it assert every part of the Then,
including that nothing else happened?"), and reports coverage if your project
has a coverage tool. Spec gaps it finds are put to you: amend now, or accept
as a known gap.

## Working with existing code

You can adopt SDD in an existing repository at any time. `init` adds files and
never changes your code. Specs grow as you change things: each archived change
adds its requirements to `specs/capabilities/`.

When a change alters behavior that exists in code but isn't specified yet, the
agent writes the new behavior as a requirement and lists it in the digest as
**"Changes existing behavior: old → new"**, so that you approve it knowingly.
Drafting specs for untouched existing code (`sdd baseline`) is planned for v2.

## Reference

### Phases

| Command | What happens |
| --- | --- |
| `sdd init [level]` | Set up `specs/`, choose the assurance level, approve the constitution |
| `sdd quick "<idea>"` | Whole `mini` change in one pass, ending at the approval gate |
| `sdd propose "<idea>"` | Start a change: intent and scope only |
| `sdd specify` | Requirements, scenarios, coverage |
| `sdd tasks` | Test-first plan, then the approval gate |
| `sdd approve` | Record your approval of the pending gate (constitution, plan, or an amendment) |
| `sdd implement [T3\|next\|all]` | Red → green → refactor, task by task |
| `sdd verify` | Check the work against the spec |
| `sdd archive` | Merge into the living spec |
| `sdd status` | Where things stand, and the next step |

### The script

The agent drives `skill/sdd/scripts/sdd.py`, and you can run it yourself:

```bash
python3 ~/.claude/skills/sdd/scripts/sdd.py status
python3 ~/.claude/skills/sdd/scripts/sdd.py check            # validate the active change
python3 ~/.claude/skills/sdd/scripts/sdd.py check --stage verify
python3 ~/.claude/skills/sdd/scripts/sdd.py next-req DUR     # next free requirement ID
```

Other commands: `init`, `new`, `approve`, `advance`, `archive`, `use`. Run
`sdd.py --help` for details. Exit code `1` means errors were found.

### Rules the agent follows

Defined in [`skill/sdd/SKILL.md`](skill/sdd/SKILL.md):
- Only you approve. Approvals are recorded with your words.
- No production code before the plan is approved.
- Test-first, always.
- Files are the memory.
- When the spec and reality disagree, the agent stops and asks.
- **When something breaks: stop, analyze, think, plan, execute.** No blind
  retries. After two failed fixes for the same problem, the agent reports to
  you.

## Limitations in v0

- Only the `inline` and `mini` sizes. Larger work should be split into several
  `mini` changes.
- The `production` and `critical` levels: the script enforces their failure
  categories, but the independent reviewer, blocking coverage, mutation
  testing and property-based tests aren't built yet. For now, run `verify` in
  a fresh session.
- No `clarify`, `design`, `analyze`, `amend`, `bug`, `baseline` or `harden`
  phases. Small amendments work through `sdd approve` during implementation.
- No repository-wide CI check or pre-commit hook yet.
- Codex support is designed in from the start (portable `SKILL.md`, all state
  in files, `agents/openai.yaml`), but has had less hands-on testing than
  Claude Code so far.

## Roadmap

| Version | Adds |
| --- | --- |
| **v1** | `standard` size (separate proposal / design / tasks / verification files, three gates); `clarify` with a Spec Critic coverage audit; `analyze`; `bug`, `amend` and `harden` phases; `production` assurance: blocking diff coverage, adversarial probing |
| **v2** | Fresh-context Critic and Verifier subagents (Claude Code) and a fresh-session protocol (Codex); opt-in git pre-commit gate and CI recipe; `baseline` for existing code |
| **v3** | `full` size and `critical` assurance (contracts, decision records, mutation and property-based testing); Claude Code plugin + marketplace; an eval suite run in both tools |

The full design rationale is in [sdd-skill-study.md](sdd-skill-study.md).

## FAQ

**Isn't this waterfall?** No. A `mini` change is one file and one approval,
usually a few minutes of reading. When implementation discovers the spec is
wrong, the agent stops and you amend it. The ceremony scales with the dials.

**What is EARS?** The *Easy Approach to Requirements Syntax* (Mavin et al.,
IEEE RE 2009): five sentence templates that make requirements unambiguous.
- ubiquitous: `The <system> shall …`
- event: `When <trigger>, the <system> shall …`
- state: `While <state>, …`
- unwanted behavior: `If <condition>, then …`
- optional feature: `Where <feature>, …`

Given/When/Then scenarios under each requirement turn the rule into concrete
tests.

**Which languages does it work with?** Any. The agent finds your test command.
The script only needs the scenario ID in a test's name or description
(`test_REQ_DUR_001_N1_…`, `it("REQ-DUR-001.N1 …")`, `TestREQ_DUR_001_N1`),
in a file that follows common test-file conventions (`tests/`, `test_*`,
`*_test.*`, `*.test.*`, `*.spec.*`, `*Test.*`).

**Can I switch between Claude Code and Codex in the middle of a change?**
Yes. Everything lives in `specs/`. Any session in either tool continues from
the files.

**Where are my approvals stored?** In the `## Approvals` table of each change
spec, and in the constitution. Each row records the gate, the date and your
words.

**Can the agent approve on my behalf?** The instructions forbid it. The script
also refuses to move a change past `draft` without a recorded plan approval.
Because approvals are plain files, review them in the pull request like the
rest of the spec.

## Development

```bash
python3 -m unittest tests.test_sdd     # the script's test suite
```

| Path | What |
| --- | --- |
| `skill/sdd/SKILL.md` | Entry point: routes `sdd <phase>` to the method files |
| `skill/sdd/method/` | `overview.md`, `format.md` (spec grammar), `phases/*.md`, `roles/*.md` |
| `skill/sdd/templates/` | Constitution, change spec, capability spec, AGENTS.md section |
| `skill/sdd/scripts/sdd.py` | The deterministic helper (Python standard library only) |
| `skill/sdd/agents/openai.yaml` | Codex UI metadata |
| `tests/test_sdd.py` | Tests for `sdd.py`, including failure cases |
| `docs/two-dials.html` / `.pdf` | The two-dials guide. Rebuild with `weasyprint docs/two-dials.html docs/two-dials.pdf`, and keep the README section in sync. |
| `sdd-skill-study.md` | Design study: rationale, landscape review, decisions |

The skill is developed with its own discipline. Script changes start with a
failing test, and each release is dogfooded end to end by a fresh agent that
reads only `SKILL.md`. Issues and pull requests are welcome; please include a
failing test for script changes.

## Acknowledgements

SDD borrows ideas from:
- [GitHub Spec Kit](https://github.com/github/spec-kit): constitution,
  clarification markers, consistency analysis;
- [OpenSpec](https://github.com/Fission-AI/OpenSpec): living capability specs
  and change deltas;
- [Kiro](https://kiro.dev): EARS and bugfix specs;
- [GSD](https://github.com/open-gsd/gsd-core): fresh-context verification;
- [BMAD](https://github.com/bmad-code-org/BMAD-METHOD) and
  [Agent OS](https://buildermethods.com/agent-os): lessons on what *not* to
  rebuild.

## License

[MIT](LICENSE) © 2026 Fabien Papleux
