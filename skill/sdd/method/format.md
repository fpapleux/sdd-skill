# `spec.md` format

`SDD check` parses this grammar. Anything inside `<!-- … -->` is ignored.

A `mini` change is one file, `spec.md`. A `standard` change uses the **same
sections**, spread over a folder and read as one document:

| File | Sections |
| --- | --- |
| `proposal.md` | front matter, Intent, Defect, Scope, Open questions, Amendments, Approvals |
| `spec-delta.md` | Requirements, Known gaps |
| `design.md` | Approach, Components and interfaces, Test strategy (with `- Test command:`) |
| `tasks.md` | Tasks |
| `verification.md` | Verification |

## Front matter (written by the script)

```yaml
---
id: 0001-parse-duration
title: Parse durations
type: feature            # feature | defect | hardening
size: mini
assurance: internal      # project level, or higher for this change
status: draft            # change only via SDD approve / SDD advance
capabilities: duration=DUR   # name=PREFIX, comma-separated
created: 2026-10-07
---
```

To add a capability, edit `capabilities:` (e.g. `duration=DUR, cli=CLI`).
Names use lowercase and hyphens. Prefixes are 2–6 uppercase letters/digits. An
existing capability's prefix is fixed (see `specs/capabilities/*/spec.md`).

## Requirements

One block per requirement, under `## Requirements`:

```markdown
### REQ-DUR-001 Parse hours and minutes
When the user passes a duration string such as "1h30m", the parser shall
return the total number of minutes.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | the string "1h30m" | parse is called | it returns 90 |
| N1 | validation | the string "abc" | parse is called | it raises ValueError · nothing is returned |
| N2 | validation | an empty string | parse is called | it raises ValueError · nothing is returned |

- N/A state: the parser is a pure function without state
- N/A dependency: the parser calls no other component or service
```

- **Heading:** `### REQ-<PREFIX>-<NNN> <title>`. Get the ID from
  `SDD next-req <PREFIX>` and never reuse one.
- **Statement:** one EARS sentence containing **shall**. The patterns are:
  - ubiquitous: `The <system> shall <response>.`
  - event: `When <trigger>, the <system> shall <response>.`
  - state: `While <state>, the <system> shall <response>.`
  - unwanted behavior: `If <condition>, then the <system> shall <response>.`
  - optional feature: `Where <feature is included>, the <system> shall <response>.`

  Keep the statement to the main rule. Failure behavior goes either:
  - as **scenarios under this requirement** (the default, and the shortest), or
  - as **its own `If…then` requirement**, when it is a rule worth naming
    (e.g. "If the file cannot be read, then the tool shall print … and exit
    with status 2"). An `If…then` requirement needs no happy path and no
    coverage walk, but at least one non-happy scenario. In the main
    requirement, point to it: `- N/A dependency: covered by REQ-DUR-003`.
- **Scenario table:** the header must be exactly
  `| ID | Category | Given | When | Then |`.
  - IDs are a letter plus a number: `S` for happy, `N` for negative, `B` for
    boundary (`S1`, `N1`, `B1`).
  - Use concrete data, so that each row maps to exactly one test.
  - Write `\|` for a pipe inside a cell.
- **Categories** (exact keys):

  | Key | Meaning | Required at |
  | --- | --- | --- |
  | `happy` | Nominal success | all levels (≥ 1 per requirement) |
  | `validation` | Missing, empty, malformed, wrong type, too long | internal+ |
  | `state` | Wrong state, duplicate/replay, out of order, expired | internal+ |
  | `dependency` | Timeout/error/partial failure of anything called; what the user sees, what is rolled back | internal+ |
  | `boundary` | Min/max, ±1, zero, one, many | production+ |
  | `access` | Unauthenticated, wrong role, someone else's resource | production+ |
  | `concurrency` | Double submit, simultaneous update | critical |
  | `combination` | Rules with ≥ 2 conditions: one scenario per combination | critical |
  | `invariant` | What must always hold (property-based test) | critical |

- **N/A lines:** a required category with no scenario needs
  `- N/A <key>: <reason>`. The reason must be real and at least 3 words, for
  example "the parser calls no other component or service", or
  "covered by REQ-DUR-003". Any requirement ID you mention must exist.
  "Not needed" is rejected.
- **Failure scenarios** (any category except `happy`): the Then asserts the
  visible error **and** that nothing else happened, e.g.
  `error "invalid email" · no order created · no charge`. Separate assertions
  with `·`.

### Changing existing behavior

Requirements already in `specs/capabilities/` are changed by restating them
with a tag:

```markdown
### REQ-DUR-001 [MODIFIED] Parse hours, minutes and days
<full new statement and full scenario table>

### REQ-DUR-002 [REMOVED] Parse seconds
Reason: seconds moved to the timer capability.
```

An untagged requirement is new. Its ID must not exist yet.

## Defect (type `defect` only)

```markdown
## Defect
- Symptom: "1h 30m" returns 60 instead of 90
- Reproduce: parse_duration("1h 30m")
- Current behavior: returns 60
- Expected behavior: returns 90; spaces between parts are allowed
- Violates: REQ-DUR-001          # or: spec gap — <why no requirement covers it>
- Root cause: the regex ignored spaces between parts
```

Every field except Root cause is required from the start. Root cause is
required before verification passes.

- **Code defect** (`Violates: REQ-…`): that requirement must be restated in
  this change as `[MODIFIED]`, carrying the regression scenario.
- **Spec gap:** a new or modified requirement carries it.

**Regression scenarios** use IDs `R1`, `R2`…, and their test's red run must
reproduce the bug.

## Clarifications (Spec Critic rounds)

`## Clarifications` (in `clarifications.md` for a `standard` change) holds
one block per review round. Start a round with `SDD round`, which lists
every requirement:

```markdown
### Round 1 — 2026-10-08 · Critic: same session

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-DUR-001 | issues | F1, F2 |

- F1 [coverage] REQ-DUR-001: no scenario for an empty string → fixed: N2 added
- F2 [ambiguity] REQ-DUR-001: is "90" minutes? → Q1
- Q1 Should "90" (no unit) count as minutes? A) yes B) no, reject — recommended: B
  - Answer: B — reject (operator, 2026-10-08)
```

- **Verdict:** `ok` or `issues`. A `?` fails the check.
- **Finding types:** `ambiguity`, `contradiction`, `untestable`,
  `coverage`, `weak-negative`, `conflict` (with the living spec), `scope`.
- **Finding outcomes:** `→ fixed: …`, `→ accepted: …`,
  `→ rejected: <reason>`, or `→ Q<n>`. A finding without an outcome, or
  waiting on an unanswered question, fails the check.
- **Questions:** at most 5 per round. Each needs an `Answer:` line; an
  unanswered question counts as an open question and blocks the gate.
- **The gate:** when a Critic round is required, the **latest** round must
  audit every current requirement.

Clarifications are review history. They aren't locked and don't count toward
the size cap.

## Known gaps

`## Known gaps`: one bullet per behavior this change deliberately does not
handle. It is required at `prototype`; write `- None` if there are none. At
other levels it's optional, and useful for things out of scope.

## Design notes

`## Design notes`: just enough "how" for a small change: files or modules
touched, approach, test strategy. It must keep a line such as
``- Test command: `python3 -m unittest` ``.

## Tasks

```markdown
- [ ] T1 REQ-DUR-001.S1 Parse "1h30m"
  - test: tests/test_duration.py::test_REQ_DUR_001_S1_parses_hours_minutes
  - red: AssertionError: None != 90
  - green: 1 passed in 0.01s
- [ ] T2 REQ-DUR-001.N1 Reject "abc"
  - test:
  - red:
  - green:
```

- One task per scenario, normally. Group scenarios into one task when the
  same minimal code satisfies all of them: several happy or boundary
  examples of one rule (e.g. `REQ-DUR-001.S1 REQ-DUR-001.S2 REQ-DUR-001.S3`).
  Then write all their tests first, and take one red run. Otherwise the second
  example passes at once and proves nothing. Keep each failure path in its own
  task.
- Put each negative task right after its happy path, never batched at the end.
- Tick `[x]` only once `red` and `green` are both recorded:
  - `red:` is the failing run, failing on an assertion about the behavior.
    `SDD check` rejects reds that show no failure, such as "1 passed".
  - `red: pre-existing — <reason>` is for behavior that already existed when
    the test was written. It is accepted, reported, and reviewed by the
    Verifier.
  - `green:` is the passing run.

## Test naming

The test that proves a scenario carries its full ID in any style the stack
allows: `test_REQ_DUR_001_N1_rejects_letters`, `it("REQ-DUR-001.N1 rejects
letters")`, `TestREQ_DUR_001_N1`. `SDD check --stage verify` searches all
**test files** outside `specs/` for each scenario ID. Test files are files
in a `test`, `tests`, `__tests__`, `spec` or `testing` folder, or named
`test_*`, `*_test.*`, `*.test.*`, `*.spec.*` or `*Test.*`. A mention in a
README or a code comment doesn't count.

## Verification, Open questions, Approvals

- `## Verification`: written by the Verifier (see `method/roles/verifier.md`).
- `## Open questions`: write each unknown as `[NEEDS CLARIFICATION: …]` at
  the place where it matters. Plan approval is refused while any marker
  remains. When the operator answers, replace the marker with the decision and
  log it here as `- <question> → <answer> (operator, <date>)`.
- `## Amendments`: one line per spec change made after approval,
  `- A<n> <date>: <reason> → <what changed>`. `SDD approve amend` requires one
  new entry per amendment.
- `## Approvals`: a table written only by `SDD approve`. A change past
  `draft` must have a `plan` row; `SDD check` fails otherwise.
- The size cap excludes Clarifications, Tasks (including test/red/green evidence), Verification, Amendments, Approvals and comments; spec and design still count. Task coverage and evidence checks still apply.
- After plan approval, the front matter carries `spec_hash`, the lock. Never
  edit it.
