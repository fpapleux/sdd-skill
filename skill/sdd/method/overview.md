# SDD method overview (v0)

## The two dials

Every change runs with two independent settings. **Size decides the
paperwork. Assurance decides the proof.**

- **Size** is set per change: how big is this change? v0 supports `inline`
  and `mini`.
- **Assurance** is set once per project in `specs/constitution.md`: how much
  trust does the product need? The levels are `prototype`, `internal`,
  `production` and `critical`. A change may raise its own level (`new
  --assurance`). Lowering it needs a recorded waiver, which v0 doesn't support.

### Sizes in v0

| Size | When | What happens |
| --- | --- | --- |
| `inline` | Typo, copy change, one-line fix, config tweak, dependency bump | No spec files. Just do it when asked. If behavior changes, write the failing test first. The commit message cites the requirement or bug touched. If the fix contradicts a requirement in `specs/capabilities/`, it isn't inline: start a `mini` change. |
| `mini` | One area, up to ~5 requirements, no new component or interface | One `specs/changes/NNNN-slug/spec.md` holds requirements, design notes, tasks and verification. One gate: the operator approves spec + plan together. |

Larger work (several areas, or a new component, interface or data model) is
`standard`/`full`, which v0 doesn't have. Offer to split it into several
`mini` changes, or to wait for v1.

What the words mean:
- **New component:** a new service, a new module boundary that others
  depend on, or a new data store.
- **New interface / public API:** a contract that other systems or teams
  consume, such as an HTTP API, a schema, an event, or a file format read
  elsewhere.
- Not either of these: a new command or option inside an existing tool, a new
  function inside an existing module, or tightening an internal function.

Pick the size by asking from the top, and stop at the first "yes":
1. Migration, public API, security model, irreversible? → `full` (not in v0)
2. Several areas, or a new component or interface? → `standard` (not in v0)
3. One area, up to ~5 requirements, nothing new? → `mini`
4. Typo, one-line fix, config tweak? → `inline`

### Assurance: what each level requires

| | `prototype` | `internal` | `production` | `critical` |
| --- | --- | --- | --- | --- |
| Tests first | Happy path | Every scenario | Every scenario | Every scenario |
| Failure categories required | none: keep a **Known gaps** list | validation, state, dependency | + boundary, access | + concurrency, combination, invariant |
| A failure scenario's Then asserts | — | The error + nothing else happened | The error + no side effects + state unchanged | Same as production |
| Coverage review | Flag open questions only | Self-audit; `SDD check` enforces coverage | Independent reviewer *(v1)* | Independent reviewer every round *(v1)* |
| Verification | Tests pass | Tests pass, coverage reported if available | + blocking coverage on the diff, adversarial probe *(v1)* | + mutation and property-based tests *(v1)* |

In v0, `SDD check` enforces the category requirements at **every** level.
The independent review and the extra verification signals for `production`
and `critical` arrive in v1. When a change is at those levels, tell the
operator this once.

## Changing code that has no spec yet

v0 has no `baseline` (it drafts specs from existing code; that's v2). When a
change alters behavior that exists in code but not in `specs/capabilities/`:
- Write the **new** behavior as a normal, untagged requirement.
- Add a line to Scope: `- Changes existing behavior: <old> → <new>`, for
  example "parse_duration returned 0 for garbage → now raises ValueError". It
  appears in the review digest, so the operator approves it knowingly.
- Existing tests that encode the old behavior are updated by the Implementer
  and listed in the implement report.

## Lifecycle of a `mini` change

```text
draft ──(operator approves: SDD approve plan)──► planned ──► implementing ──► verifying ──► verified ──► archived
                                                                  ▲               │
                                                                  └── gaps found ─┘
any non-final status ──► blocked | abandoned
```

| Phase | Role | Status after |
| --- | --- | --- |
| `quick` or `propose` → `specify` → `tasks` | Spec Author, then Planner | `draft` |
| `approve` | Operator (you record it) | `planned` |
| `implement` | Implementer | `implementing` |
| `verify` | Verifier | `verified`, or back to `implementing` |
| `archive` | Spec Steward | `archived` (folder moved to `specs/archive/`) |

The **gate** is the operator's approval of the plan. Before it, nobody touches
production code for this change.

**The approved spec is locked.** Approval stores a fingerprint of Intent,
Defect, Scope, Requirements and Known gaps. Changing any of them later is an
**amendment**: logged, shown to the operator and approved (`sdd amend`).
Until then, `SDD check` fails. Tasks and Design notes stay editable.

**Defects** are changes of type `defect` (`sdd bug`). They carry a `## Defect`
record and at least one regression scenario (`R1`). That scenario lands in the
living spec, so the bug can't return silently.

## Files

```text
specs/
  constitution.md            # assurance level + non-negotiable rules (operator-approved)
  capabilities/<name>/spec.md  # LIVING spec: current approved behavior (written by SDD archive)
  changes/NNNN-slug/spec.md    # in-flight changes
  archive/NNNN-slug/spec.md    # finished changes
  .sdd/active                  # the active change ID
AGENTS.md                    # SDD section (read by Codex)
CLAUDE.md                    # contains @AGENTS.md (read by Claude Code)
```

The grammar of `spec.md` (requirements, scenario tables, N/A lines, tasks and
evidence) is in `method/format.md`. Read it before writing or editing a spec.

## The script

| Command | Use |
| --- | --- |
| `SDD init --assurance <level> [--force]` | Create `specs/` and wire AGENTS.md/CLAUDE.md |
| `SDD new <slug> --title "…" --capability name=PREFIX [--type feature\|defect\|hardening] [--assurance <higher level>]` | Create a change and make it active |
| `SDD next-req <PREFIX>` | Next free requirement ID |
| `SDD check [--stage spec\|plan\|implement\|verify]` | Validate the active change. Exit 1 = errors. |
| `SDD status [--json]` | Summary + next step |
| `SDD approve constitution\|plan\|amend --evidence "…"` | Record an operator approval. `plan` locks the spec; `amend` needs a logged spec change and a clean check, then re-locks it. |
| `SDD advance implementing\|verifying\|verified\|blocked\|abandoned` | Move the status. A blocked change returns only to the status it had (`SDD advance <that status>`). |
| `SDD archive` | Merge a verified change into `specs/capabilities/` (requirements, known gaps, history line) and archive it |
| `SDD use <change-id>` | Switch the active change |

All take `--change <id>` to target a change other than the active one, where
relevant.

## Reporting to the operator

Keep reports short and decision-oriented:
- what you did (files touched);
- the check result in one line (`check: OK · 3 REQs · 9 scenarios (3 happy, 6 negative) · 0 open questions`);
- at a gate, a **review digest**: each requirement's one-line rule, its
  scenarios as short phrases, N/A reasons, known gaps, **behavior changes to
  existing code**, assumptions you made, and open questions;
- the single next command, using the operator's prefix (`/sdd` or `$sdd`).
