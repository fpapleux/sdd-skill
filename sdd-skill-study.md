# SDD Skill — Design Study

Status: draft v4, decisions recorded · 2026-10-07

This study looks at how to build a **standalone** Spec-Driven Development (SDD)
skill that works in **Claude Code and Codex** from day one. It covers what the
skill does, which roles it defines, and how an operator uses it. It borrows
design principles from a role-based delivery process the author uses, but
does not depend on it.

### Decisions recorded

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | Standalone vs bound to an existing delivery process | **Standalone.** No dependency on any other process. Interop can come later. |
| 2 | Spec location | **`specs/` at the source-repo root** (de facto convention, §5.1). |
| 3 | Spec Critic and Spec Steward as full roles | **Yes.** |
| 4 | Requirement notation | **C: EARS rule + Given/When/Then scenarios** (§5.2). |
| 5 | Target tools | **Claude Code + Codex from v0.** |
| 6 | Default size | **`mini`**: one file, one gate. |
| 7 | Pre-commit gate | **Opt-in.** |
| 8 | Testing discipline | **TDD always. The project's assurance level sets how deep negative coverage goes.** `prototype` = happy-path TDD + a Known gaps list (§4.3, §6). |
| 9 | Scaling model | **Two independent dials: size (paperwork) × assurance (proof)** (§4.3). Operator guide: [`docs/two-dials.pdf`](docs/two-dials.pdf) and README. |
| 10 | Default assurance | **Proposed:** `sdd init` asks for it. No silent default. |

---

## 1. What SDD should mean here

In SDD, a written, reviewable **spec is the contract** between the operator's
intent and the agent's execution. Plans, tasks, tests and code are derived from
it. Each derived artifact traces back to it, and the spec stays true after the
code ships.

There are three levels of rigor:

| Level | Meaning | Verdict |
| --- | --- | --- |
| Spec-first | Write a spec, generate code, then let the spec go stale. | Too weak. This is what most "write a PRD first" flows end up as. |
| **Spec-anchored** | The spec is kept as the living truth of system behavior. Changes go through spec deltas, and tests are traced to requirement IDs. | **Target.** |
| Spec-as-source | Humans edit only specs, and code is regenerated from them. | Too early and too brittle for real products. |

The skill's job is to make spec-anchored work cheap enough that people actually
use it.

### 1.1 What existing SDD tools teach us (landscape, Oct 2026)

| Tool | Shape | Borrow | Avoid |
| --- | --- | --- | --- |
| **GitHub Spec Kit** (v1.1) | `constitution → specify → clarify → plan → checklist → tasks → analyze → implement → converge`, artifacts in `specs/NNN-slug/` | Constitution with plan-time gates. `[NEEDS CLARIFICATION]` markers. Read-only `analyze`. `[P]` tasks. The **converge** loop (verify, append missing tasks, repeat). | "Sea of markdown" (≈2,100 spec lines for 600 LOC in one review). Specs are per-feature snapshots with no merged system spec. |
| **AWS Kiro** | requirements → design → tasks, gated per phase. Steering files. Hooks. | **EARS** acceptance criteria. A **bugfix spec** (current vs expected behavior). **Quick Spec** fast path. Ambiguity surfaced as crisp A/B questions. | Ceremony on small changes. Stale steering. "Task complete" ≠ requirement works. |
| **OpenSpec** | `explore → propose → apply → archive`. `specs/<capability>/` + `changes/<id>/` | **Living capability specs + ADDED/MODIFIED/REMOVED deltas merged on archive.** Brownfield-first. Smallest artifacts (≈250 lines/change vs ≈800 for Spec Kit). | Duplication and contradictions accumulating in specs, which need a steward. |
| **BMAD** (v6) | Analyst/PM/Architect/Dev/UX personas. Story sharding. | Self-contained task context, so the Implementer never rereads all the planning docs. Adversarial review. | **Persona theatre.** Errors compound across handoffs. Heavy token use. Took ≈3× longer end-to-end than peers in one test. |
| **GSD** | discuss → plan → execute → verify → ship. `STATE.md`. | Fresh-context researcher/planner/checker/executor/**verifier** subagents. Resumable state file. `quick` path. | — |
| **Agent OS v3** | standards discovery + shape-spec in plan mode | Lesson: v3 **removed** its own task and orchestration commands because the host agent (plan mode, subagents) does it better. | Rebuilding what the host tool already provides. |
| **Tessl** | spec-as-source, code generated from specs | — | Closed beta, non-deterministic regeneration. Confirms that spec-as-source is premature. |

The design below is roughly **OpenSpec's artifact model**, **Spec Kit's
governance** (constitution, clarify, analyze, converge), **Kiro's notation**
(EARS, bugfix spec), and **GSD's fresh-context verification**. On top of that it
adds two ideas from role-based delivery processes that none of these tools have (§2).

## 2. Principles carried over from role-based delivery

These are borrowed as ideas, not as a dependency:

1. **Roles are authority boundaries, not personas.** Each role has a list of
   files it may write, things it must not do, and a gate it hands off to.
2. **Operator gates need approval evidence.** A phase advances only when the
   agent can point to the approval: a chat message, a status change in the
   artifact, or a PR comment.
3. **Two scaling dials**, as in the source process (artifact budget × assurance
   level). Size decides the paperwork and assurance decides the proof (§4.3).
4. **Test-first delivery.** Every task names the failing test to write first.
5. **No orphan work.** Every task traces to a requirement, and every
   requirement traces to the operator's intent.

## 3. Shape of the solution

The skill is **one self-contained, tool-neutral skill folder**
(`skill/sdd/` in this repository) that is **symlinked** into both tools.
Because of the symlinks, edits are live in both tools, with no copy step and
no wrapper.

```text
~/.claude/skills/sdd  ─┐
                       ├──► <checkout>/skill/sdd/   (single source)
~/.codex/skills/sdd   ─┘
```

Invocation: `/sdd <phase> …` in Claude Code, `$sdd <phase> …` in Codex.

## 4. Roles

### 4.1 Role set

| # | Role | Owns (writes) | Must not | Typical human analogue |
| --- | --- | --- | --- | --- |
| 0 | **Operator** (human) | Intent, priorities, approvals at gates, the constitution. | — | Product owner / lead |
| 1 | **Spec Author** | `proposal.md`, `spec-delta.md`: WHAT and WHY, requirements with IDs, scenarios, non-goals, open questions. | Name technologies, design solutions, touch code. | PO / business analyst |
| 2 | **Spec Critic** | `clarifications.md`: ambiguity, contradiction, untestable or missing criteria, conflicts with living specs. **Coverage audit** of every REQ against the taxonomy (§6). Asks ≤5 questions per round. | Edit the spec. It proposes and the Author applies. | Requirements reviewer |
| 3 | **Architect** | `design.md` (+ `contracts/`): approach, data model, interfaces, decisions, constitution check, REQ → component mapping. **Failure modes the design introduces**, returned to the Author as new scenarios. | Change requirements. Write code. | Architect |
| 4 | **Planner** | `tasks.md`: ordered, test-first tasks tagged with REQ IDs, `[P]` parallel markers, dependencies, checkpoints. Runs the consistency analysis. | Change spec or design without sending it back. | Tech lead |
| 5 | **Implementer** | Code + tests, task checkboxes, implementation notes. One task at a time, TDD. | Change the spec. If reality disagrees with it, raise a spec change request (`amend`). | Developer |
| 6 | **Verifier** | `verification.md`: REQ → scenario → test → result matrix, objective coverage signals (branch coverage, mutation score, adversarial probe), drift findings, verdict. Appends gap tasks. | Fix code. At `production`+, verify work produced in its own context. | QA |
| 7 | **Spec Steward** | `specs/capabilities/**`: merges approved deltas at archive, removes duplication and contradictions, runs drift audits, baselines existing code. | Accept behavior that was never approved. | Librarian / spec owner |

### 4.2 Why these and not more

- **Critic is separate from Author** because an agent reviewing its own
  spec misses the same gaps it created. Same reason **Verifier is separate from
  Implementer**. At `production` and `critical` both run in a fresh context
  (§8.3).
- **Steward is the role that makes SDD "anchored".** Without it, specs decay
  into spec-first, and they accumulate duplicates and contradictions, which is
  OpenSpec's main weakness.
- The operator owns the constitution. The Architect proposes amendments.
- No Scrum Master, Analyst, or Orchestrator personas. Their duties fold into
  Planner and Spec Author, which keeps handoffs (and compounding errors) low.

### 4.3 Scaling: size × assurance

There are two independent dials, and they answer different questions:

- **Size: how big is *this change*?** It decides the **paperwork**: which
  files exist, how many gates, and which roles run. It is set per change. The
  Spec Author suggests a size from the proposal, and the operator confirms it in
  the same approval.
- **Assurance: how much must *this product* be trusted?** It decides the
  **proof**: which failure categories are required, how independent the reviews
  are, and which verification signals run. It is set once per project in
  `constitution.md`. A single change may raise it (e.g. payment code inside an
  internal tool). Lowering it requires a recorded operator waiver.

> Size decides the paperwork. Assurance decides the proof.

#### Sizes (per change)

| Size | Typical change | Artifacts | Gates | Roles that run | Normal flow |
| --- | --- | --- | --- | --- | --- |
| `inline` | Typo, copy change, one-line fix, config tweak, dependency bump | None. The commit message cites the REQ or bug it touches. | None: the request is the approval | Implementer, plus the Steward if a REQ's wording changes | Just ask. If behavior changes, the project's test-first rule still applies. |
| `mini` **(default)** | One capability, up to ~5 REQs, no new component or interface | One `spec.md`: spec, design notes, tasks, verification summary | 1: spec + plan together | Author, Implementer, Verifier, Steward at archive. The Critic runs if assurance requires it. | `quick` → approve → `implement all` → `verify` → `archive` |
| `standard` | Several capabilities, or a new component, interface or data model | Full change folder | 3: spec · plan · verification | All 7 | `propose → specify → clarify → G1 → next → G3 → implement → verify → G4 → archive` |
| `full` | Cross-cutting or high-risk: data migration, public API, security model, irreversible operations | Full folder + contracts + decision records | 4: spec · design · tasks · verification | All 7 | Standard flow plus a separate design gate |

The Author bases its size suggestion on the number of REQs, the number of
capabilities touched, whether there is a new component, interface or schema,
and whether there are irreversible data operations.

#### Assurance levels (per project)

| | `prototype` | `internal` | `production` | `critical` |
| --- | --- | --- | --- | --- |
| **Means** | Exploring, demo, learning; may be thrown away | Used by you or your team; real data, small blast radius | External users or persistent business data | Money, security, safety, regulated, or irreversible |
| **Test-first** | Happy-path scenarios | Every scenario | Every scenario | Every scenario |
| **Negative coverage** | **None required.** Instead, a **Known gaps** list with one line per thing not handled. | Input validation, state & sequence, dependency failure | 6 core categories (§6.3) | 6 core + concurrency, rule combinations, invariants |
| **Negative "Then" asserts** | — | Error + no side effects | Error + no side effects + state unchanged | Same as production |
| **Coverage audit** | None. The Author only flags `[NEEDS CLARIFICATION]`. | Author self-audit, with `check` enforcing the matrix | Fresh-context Critic | Fresh-context Critic, every round |
| **Verification** | Same session: tests pass | Same session: tests pass, branch coverage reported | Fresh context: + branch coverage on the diff (blocking) + adversarial probe | Fresh context: + mutation testing + property-based tests |

#### What the combinations feel like (rough estimates)

| Combination | Example | Spec size | Operator effort |
| --- | --- | --- | --- |
| `prototype` × `mini` | Clickable guest-checkout demo for a pitch | ≈ 40–60 lines: 4 EARS rules, 1 scenario each, 5 known gaps | 1 approval |
| `internal` × `mini` | Team script that imports CSV invoices | ≈ 80–120 lines | 1 approval, maybe 1–2 questions |
| `production` × `mini` | "Resend confirmation email" on the live shop | ≈ 120–200 lines | 1 approval + Critic questions |
| `production` × `standard` | Guest checkout on the live shop | ≈ 250–400 lines | 3 approvals |
| `critical` × `full` | Change refund rules in the payment service | ≈ 600–800 lines + contracts | 4 approvals |

#### Graduating a prototype

The Known gaps list is the **hardening backlog**.
`sdd harden <capability> --to internal|production` raises the level. The Critic
builds the missing coverage matrices for the existing REQs, starting from
Known gaps, and the result goes through the normal process as a `standard`
change of type `hardening`. Prototypes cost nothing extra up front, and nothing
is lost when they become real.

These things hold at every combination: REQ IDs, the living spec updated at
archive, all state in files, and tests named after scenario IDs.

## 5. Artifacts and where they live

### 5.1 Where specs live: the de facto standard

There is **no formal SDD standard** (no ISO/IEEE equivalent). There is a clear
**de facto convention**, followed by every major tool: **specs live in the
source repository, committed alongside the code.**

| Tool | Location |
| --- | --- |
| Spec Kit | `specs/NNN-slug/` + `.specify/memory/constitution.md` |
| Kiro | `.kiro/specs/<feature>/` + `.kiro/steering/` |
| OpenSpec | `openspec/specs/<capability>/` + `openspec/changes/<id>/` (+ `archive/`) |
| BMAD | `_bmad-output/planning-artifacts/`, `implementation-artifacts/` |
| GSD | `.planning/` |
| Agent OS | `agent-os/specs/` + `agent-os/standards/` |

All of them keep specs in the repo for the same reasons. The spec delta is
reviewed in the same PR as the code, merged with it, reverted with it, and
visible to any agent that opens the repo.

They differ on two points:

1. **Per-feature snapshots** (Spec Kit, Kiro) vs **living capability specs +
   change folders** (OpenSpec). The latter is what makes a spec anchored, and we
   take it.
2. **Hidden tool folder** (`.kiro/`, `.specify/`, `.planning/`) vs **visible
   folder** (`specs/`, `openspec/`). We take a visible, tool-neutral
   **`specs/`**. Specs are meant to be read by humans in PRs, and the folder
   shouldn't be named after either Claude or Codex.

```text
<repo>/
  AGENTS.md                         # short SDD section (Codex reads this)
  CLAUDE.md                         # contains "@AGENTS.md" (Claude Code import)
  specs/
    constitution.md                 # non-negotiable project principles
    capabilities/                   # LIVING truth: current behavior
      checkout/spec.md
      auth/spec.md
    changes/                        # in-flight work, one folder per change
      0042-guest-checkout/
        proposal.md                 # why, scope, impacted capabilities, status
        spec-delta.md               # ADDED / MODIFIED / REMOVED requirements
        clarifications.md           # Critic rounds: questions + answers
        design.md                   # how (+ contracts/ when needed)
        tasks.md                    # ordered, test-first, REQ-tagged
        verification.md             # evidence matrix + verdict
    archive/
      0041-saved-carts/             # completed changes, moved by the Steward
    .sdd/active                     # pointer to the active change (resume)
```

`mini` changes collapse the change folder into one `spec.md`.

### 5.2 Requirement notation: what the choice actually is

The question is **how each requirement is written**. There are two established
notations, and they work at different levels:

- **EARS** (Easy Approach to Requirements Syntax, Rolls-Royce 2009) states the
  **rule**: one sentence, fixed keywords, general. It has five patterns:

  | Pattern | Template |
  | --- | --- |
  | Ubiquitous | The `<system>` shall `<response>`. |
  | Event-driven | **When** `<trigger>`, the `<system>` shall `<response>`. |
  | State-driven | **While** `<state>`, the `<system>` shall `<response>`. |
  | Unwanted behavior | **If** `<condition>`, **then** the `<system>` shall `<response>`. |
  | Optional feature | **Where** `<feature is included>`, the `<system>` shall `<response>`. |

- **Given/When/Then** (Gherkin, from BDD) gives **examples**: concrete data,
  one scenario at a time, each mapping 1:1 onto an automated test.

The same requirement in each of the three options:

**Option A — EARS only**

```markdown
### REQ-CHK-007 Guest checkout
When a visitor without a session submits a valid cart and email address,
the checkout service shall create a paid order and queue a confirmation
email to that address.
```

**Option B — Given/When/Then only**

```markdown
### REQ-CHK-007 Guest checkout
Scenario: guest pays for a cart
- Given a cart with 2 in-stock items and no session
- When the visitor submits email "a@b.c" and a valid payment
- Then an order is created with status "paid"
- And a confirmation email is queued to "a@b.c"
```

**Option C — EARS rule + Given/When/Then scenarios**

```markdown
### REQ-CHK-007 Guest checkout
When a visitor without a session submits a valid cart and email address,
the checkout service shall create a paid order and queue a confirmation
email to that address.

Scenario: guest pays for a cart
- Given a cart with 2 in-stock items and no session
- When the visitor submits email "a@b.c" and a valid payment
- Then an order is created with status "paid"
- And a confirmation email is queued to "a@b.c"

Scenario: item goes out of stock before payment   # from an "If…then" rule
- Given ...
```

| | A. EARS only | B. GWT only | C. Both |
| --- | --- | --- | --- |
| Precision of the rule | High | Low: the rule is implied by examples, and readers must generalize | High |
| Maps directly to tests | No: the agent invents test data, which is where misreadings creep in | Yes, 1:1 | Yes, 1:1 |
| Finding missing behavior | Good: the *If…then* pattern forces you to think about failure cases | Weak: gaps between examples stay invisible | Good |
| Size per requirement | ≈3 lines | ≈5 lines per scenario | ≈8–15 lines |
| Familiar to | Systems/requirements engineers. Used by Kiro. | Developers and QA (Cucumber/BDD) | OpenSpec does a version of this (SHALL + WHEN/THEN) |

**Decision: C.** Requirement and scenario IDs are mandatory. Tests carry the
scenario ID (`test_REQ_CHK_007_N5_payment_timeout`), so traceability is a
`grep`. How many negative scenarios are required depends on the project's
assurance level (§4.3). `prototype` requires none and keeps a Known gaps list
instead. `critical` requires nine categories. Negative scenarios can be written as compact table rows instead of full
Given/When/Then blocks to keep specs short.

Deltas use `## ADDED`, `## MODIFIED` (full new text + "was:"), and
`## REMOVED` (with reason) sections.

### 5.3 Constitution

A short (≤1 page) file of non-negotiable project rules. The Architect and
Implementer check every pass against it. Examples: test-first, no secrets in
artifacts, dependency policy, supported platforms. `init` proposes a starter
set, and the operator approves it and every later amendment.

### 5.4 Status machine

`proposal.md` front matter carries one status:

```text
draft → clarifying → spec-approved → designed → planned → implementing
      → verifying → verified → archived            (+ blocked, abandoned)
```

`specs/.sdd/active` points at the current change, so any new session in either
tool resumes from the files alone.

### 5.5 Size caps

| Size | Whole change folder |
| --- | --- |
| `mini` | ≤ 200 lines (single `spec.md`; `prototype` changes usually need ≈ 60) |
| `standard` | ≤ 400 lines |
| `full` | ≤ 800 lines, plus contracts |

`check` warns when a change exceeds its cap.

## 6. Coverage model: negative cases and TDD

### 6.1 What can and cannot be guaranteed

No method can *prove* a spec is complete, because nobody can list cases that
nobody has thought of. What the skill can guarantee is narrower and enforceable:

1. Every requirement goes through the **same failure categories** for its
   assurance level.
2. Every omission is an **explicit, reviewable decision** (`N/A — reason`),
   never silence.
3. **Independent reviewers and objective measurements** expose behavior that
   isn't specified or isn't tested.
4. Anything found late goes **back into the spec**, so coverage improves over
   time.

There are five layers, and each one catches what the previous one missed.

### 6.2 Layer 1 — Failure behavior is a spec decision, not a coding decision

What should happen when the payment provider times out is a *product* decision.
If the spec is silent, the Implementer decides silently while coding. So
negative behavior is written into the spec as EARS **If…then** rules, before any
code is written.

Rule: every event-driven (`When`) requirement has its `If…then` counterparts,
or its coverage matrix says why none apply.

### 6.3 Layer 2 — A fixed coverage taxonomy, applied per requirement

Every REQ has a coverage matrix. Each cell holds scenario IDs or
`N/A — <reason>`. **A blank cell fails `sdd check`.** "N/A" without a reason
fails too.

*v0 implementation:* nobody writes the matrix by hand. `sdd.py check`
computes it from the `Category` column of each scenario row plus
`- N/A <category>: <reason>` lines (at least 3 words), and prints it. This
keeps the spec shorter and removes a second copy that could drift.

| Category | Questions it forces | Test-design technique | Required at |
| --- | --- | --- | --- |
| Happy path | Nominal success? | — | all levels |
| Input validation | Missing, empty, malformed, wrong type, too long? | Equivalence partitioning | `internal`+ |
| Boundaries | Min/max, ±1, zero, one, many? | Boundary value analysis | `production`+ |
| State & sequence | Wrong state? Duplicate/replay (idempotency)? Out of order? Expired? | State transition testing (every *invalid* transition) | `internal`+ |
| Access | Unauthenticated? Wrong role? Someone else's resource? | — | `production`+ |
| Dependency failure | Timeout, error, or partial failure of anything called? What does the user see, and what gets rolled back? | Fault injection with test doubles | `internal`+ |
| Concurrency | Double submit? Simultaneous update? | — | `critical` (or when the Architect flags shared state) |
| Rule combinations | Rules with ≥2 conditions: every combination decided? | Decision table (one scenario per column) | `critical` |
| Invariants | What must *always* hold (totals ≥ 0, IDs unique)? | Property-based tests | `critical` (optional below) |

The first six are the **core** categories. At `prototype` none are required,
and a Known gaps list replaces the matrix. Any change can raise its own level
when it touches something sensitive. Projects can add their own categories in `constitution.md` (e.g.
"multi-currency", "offline mode"). A recurring defect class becomes a
permanent category.

Example matrix:

```markdown
#### Coverage — REQ-CHK-007 Guest checkout
| Category | Scenarios |
| --- | --- |
| Happy path | S1 |
| Input validation | N1 invalid email · N2 empty cart |
| Boundaries | B1 cart at 100-item limit · B2 101 items rejected |
| State & sequence | N3 item out of stock at submit · N4 double submit → one order |
| Access | N/A — guest flow has no identity; abuse covered by REQ-SEC-002 (rate limit) |
| Dependency failure | N5 payment timeout → order "pending", no email · N6 mailer down → order paid, email retried |
```

Negative scenarios use a compact row format:

```markdown
| ID | Given | When | Then |
| --- | --- | --- | --- |
| N1 | valid cart, no session | submit with email "abc" | 422 "invalid email" · no order created · no charge · no email |
```

**A negative "Then" must assert three things:** the visible error, the absence
of side effects (no order, no charge, no email), and unchanged state. The most
common weak negative test checks only the error code.

### 6.4 Layer 3 — Independent coverage audit

| When | Who | What |
| --- | --- | --- |
| Clarify (G1) | **Spec Critic**, fresh context | Audits every matrix: blank cells, lazy N/As ("not needed"), `If…then` rules without scenarios, negatives that assert only an error code. Where the expected failure behavior is unknown, it asks the operator an A/B question ("Payment timeout: **A)** order stays pending and retries, **B)** order fails and cart is kept"). |
| Design (before G3) | **Architect** | The design adds new failure points (queue, cache, third-party API, migration). The Architect lists these failure modes, the Author turns them into scenarios, and the operator sees them at G3. |

### 6.5 Layer 4 — TDD per scenario, with evidence

- **Planner:** every scenario ID gets a task step "write failing test
  `test_REQ_CHK_007_N5_…`". Negative scenarios are scheduled **next to** their
  happy path, never batched at the end where they get dropped under time
  pressure.
- **Implementer:** red → green → refactor, one scenario at a time. It records
  the **red run**, which must fail for the right reason (an assertion, not an
  import error or typo), and then the green run in `tasks.md`. A task without
  red evidence can't be ticked.
- **`sdd check`** (deterministic, no LLM judgment):
  - every scenario has a task;
  - every scenario ID appears in at least one test;
  - every ticked task has red and green evidence;
  - no blank matrix cells;
  - every N/A has a reason.

### 6.6 Layer 5 — Objective signals at Verify

The Verifier doesn't trust the matrix. It measures:

| Signal | What it reveals | Required at |
| --- | --- | --- |
| Full run of all scenario tests | Whether what's claimed matches reality | all levels |
| **Branch coverage on changed code** | Untested `else` / `except` / error branches, i.e. negative cases nobody wrote. Each one must map to a scenario or be justified. | `production`+ (`internal`: reported, not blocking) |
| **Mutation testing on changed code** (mutmut, Stryker, PIT, cargo-mutants) | Tests that run code without checking it. Mutants that survive in error handling are weak negatives. | `critical` (`production`: optional) |
| **Adversarial probe** | The Verifier tries 5–10 inputs or sequences that aren't in the spec | `production`+ |

Findings are routed by type:
- **Specified but untested** → an appended task, then implement → verify again.
- **Unspecified behavior** → `amend`. This is a spec gap, and the operator
  decides what should happen.
- **Found after shipping** → `sdd bug` classifies it as a *code defect* or a
  *spec gap*. A spec gap adds the missing scenario, and if the same kind of gap
  recurs, a new taxonomy category.

### 6.7 Built into the constitution

`init` seeds two non-negotiable articles. `analyze` treats any violation as
**blocking for G3**:

1. **Test-first:** no production code without a failing test that references
   a scenario ID. At `prototype`, this applies to happy-path scenarios.
2. **Negative coverage:** every requirement covers the categories its
   assurance level requires, or records why not. At `prototype`, the
   requirement is a Known gaps list.

The G3 summary shows the balance at a glance:

```text
14 REQs · 61 scenarios (14 happy · 39 negative · 8 boundary)
0 blank cells · 3 N/A (reasons listed) · 0 scenarios without task
Constitution: OK
```

## 7. Phases, commands and gates

Commands are written `sdd <phase>`: `/sdd` in Claude Code, `$sdd` in Codex.

| Phase | Command | Role | Output | Gate |
| --- | --- | --- | --- | --- |
| Setup | `sdd init` | Operator + Architect | `specs/` skeleton, `constitution.md`, SDD section in `AGENTS.md`, `@AGENTS.md` in `CLAUDE.md`, assurance level (asked), default size `mini` | Operator approves constitution |
| Baseline (brownfield) | `sdd baseline <area>` | Steward | `capabilities/<cap>/spec.md` drafted from existing code and tests, every REQ marked `observed` | Operator confirms or corrects |
| Harden | `sdd harden <cap> --to <level>` | Critic → Author | Coverage matrices built from Known gaps, as a `standard` change of type `hardening` | Normal gates |
| Propose | `sdd propose "<idea>"` | Spec Author | `changes/NNNN-slug/proposal.md` | — |
| Quick path | `sdd quick "<idea>"` | Spec Author → Planner | `mini` change in one pass | One gate: spec+plan |
| Defect | `sdd bug "<symptom>"` | Spec Author | Current vs expected behavior, the REQ violated (or "spec gap"), regression scenario | Spec gate (fast) |
| Specify | `sdd specify` | Spec Author | `spec-delta.md` with IDs, EARS rules incl. `If…then`, scenarios, coverage matrix per REQ (§6.3), `[NEEDS CLARIFICATION]` markers | — |
| Clarify | `sdd clarify` | Spec Critic → Author | Coverage audit + ≤5 questions per round (A/B where possible), answers folded in | **G1: spec approved** |
| Design | `sdd design` | Architect | `design.md` (+ `contracts/`), constitution check, failure modes the design introduces → new scenarios | G2 (`full` only) |
| Tasks | `sdd tasks` | Planner | `tasks.md`: one failing-test step per scenario ID, negatives next to their happy path, files, `[P]`, checkpoints | — |
| Analyze | `sdd analyze` | Planner + `check` script | Blank matrix cells, unexplained N/As, scenarios without tasks, orphan tasks, contradictions, constitution violations, happy/negative balance | **G3: plan approved → coding authorized** |
| Implement | `sdd implement [T-id\|next\|all]` | Implementer | Red → green → refactor per scenario, red and green evidence recorded, ticked tasks. Stops at checkpoints. | — |
| Amend | `sdd amend "<reason>"` | Implementer → Author → Operator | Spec change request for the affected REQs only | Mini-gate |
| Verify | `sdd verify` | Verifier (fresh context at `production`+) | `verification.md`: test run, branch coverage, mutation score, adversarial probe (by assurance level, §6.6). Gaps become appended tasks or `amend`, and implement → verify repeats until converged. | **G4: verification accepted** |
| Archive | `sdd archive` | Spec Steward | Delta merged into `capabilities/`, duplicates removed, folder moved to `archive/` | — |
| Status | `sdd status [--review]` | any | Active change, status, next step, open questions. `--review` = one-screen digest for approving. | — |
| Next | `sdd next` | per phase | Runs phases until the next gate, then stops | — |

## 8. Making it work in both Claude Code and Codex

### 8.1 Portability rules

1. **One portable `SKILL.md`.** Frontmatter is limited to the shared core
   (`name`, `description`, `metadata`). Claude-only fields are left out until v0
   testing confirms Codex ignores them.
2. **No reliance on host-side prompt preprocessing.** Claude Code's `$ARGUMENTS`
   and `` !`cmd` `` injection don't exist in Codex. Instead, the router tells
   the agent to read the phase from the user's invocation and to *run*
   `scripts/sdd.py status` as its first step.
3. **All state lives in files** (`specs/`, `.sdd/active`), never in chat memory
   or a tool-specific store. Either tool, or a fresh session, can pick up any
   change.
4. **Scripts are Python 3 standard library only**, so they run identically
   from either agent's shell.
5. **Host features are enhancements, never requirements.** Claude subagents
   and hooks make things better when present. The method stays correct without
   them.
6. **Codex UI metadata** goes in `agents/openai.yaml` (display name, short
   description, default prompt), as Codex skills commonly do. Claude Code
   ignores it.

### 8.2 Skill folder layout (repository root)

```text
sdd-skill/
  sdd-skill-study.md            # this document
  install.sh                    # symlinks skill/sdd into ~/.claude/skills and ~/.codex/skills
  skill/sdd/                    # ← the installable, portable skill
    SKILL.md                    # router: status → phase file → role file → act → stop at gate
    agents/openai.yaml          # Codex UI metadata
    method/
      overview.md               # lifecycle, status machine, gates, sizes, assurance, caps
      roles/   spec-author.md spec-critic.md architect.md planner.md
               implementer.md verifier.md spec-steward.md
      phases/  init.md baseline.md propose.md quick.md bug.md specify.md
               clarify.md design.md tasks.md analyze.md implement.md
               amend.md verify.md archive.md status.md
    templates/ constitution.md proposal.md spec-delta.md capability-spec.md
               mini-spec.md design.md tasks.md verification.md agents-md-section.md
    scripts/sdd.py              # init, new, status, check, approve, advance, archive, next-req, use
    hooks/pre-commit            # tool-neutral gate (see 7.4)
  extras/claude/                # optional Claude Code enhancements
    agents/ sdd-critic.md sdd-verifier.md sdd-implementer.md
    settings-hook.json          # PreToolUse gate snippet
  evals/                        # sample features + expected artifacts, run in both tools
```

### 8.3 Fresh-context review (Critic, Verifier)

| | Claude Code | Codex |
| --- | --- | --- |
| Mechanism | Subagents `sdd-critic` / `sdd-verifier` with `tools: Read, Grep, Glob, Bash` (no Edit/Write) | **Fresh session**: the skill ends the phase with "start a new session and run `$sdd verify`". It uses a Codex-native subagent instead if one is available when v0 is tested. |
| Why it works | Fresh context, and no write tools | Fresh context. The Verifier role file forbids edits outside `verification.md` and `tasks.md`. |

The portable baseline is the **fresh session**, which works because all state
is in files. Subagents are the convenience layer. Fresh context is required at
`production` and `critical`. At `prototype` and `internal`, review may run in
the same session, so there's no extra step.

### 8.4 Gate enforcement

| Layer | Tool-neutral? | What it does |
| --- | --- | --- |
| `sdd check --gate` | ✅ | Exit ≠ 0 if non-spec files changed while the active change is before `planned`, or, at `verify`, a scenario lacks a test or a ticked task lacks red/green evidence. |
| **git pre-commit hook** (installed by `init`, opt-in) | ✅ | Runs `sdd check --gate`. Covers both agents *and* humans. |
| CI job | ✅ | Same check on PRs. Archive must have happened before merge. |
| Claude `PreToolUse` hook on `Edit\|Write` | Claude only | Blocks the edit before it happens (exit `2` + message). An optional extra. |

### 8.5 Project instructions outside skill invocations

`init` writes a ~10-line SDD section into the project's `AGENTS.md` (which
Codex reads) and makes sure `CLAUDE.md` imports it with `@AGENTS.md`. It says:
specs live in `specs/`, don't change behavior without an approved change,
tests carry REQ IDs. Both agents then respect the spec even when the skill
isn't invoked.

### 8.6 Distribution (later)

- **Personal use:** `install.sh` creates the symlinks, so edits are live.
- **Team, Claude side:** package `skill/sdd` + `extras/claude` as a plugin in a
  git-hosted marketplace (`claude plugin marketplace add …`,
  `claude plugin install sdd@…`). That gives per-phase commands
  (`/sdd:verify`) with their own frontmatter (`disable-model-invocation`,
  `context: fork`).
- **Team, Codex side:** clone + `install.sh`, or Codex's own distribution
  mechanism if it has one by then.

## 9. How the operator uses it

### 9.1 Greenfield feature, `production` × `standard`

```text
/sdd init                                    # once per repo
/sdd propose "Guests can check out without creating an account"
/sdd specify
/sdd clarify            → 3 questions, e.g. "A) guest orders join history on later
                          sign-up, or B) stay separate?"
"Approve the spec."                          # G1
/sdd next               → design + tasks + analyze, stops at G3:
                          "14 REQs, 22 tasks, 0 uncovered, 1 constitution note"
"Approve the plan."                          # G3
/sdd implement all      → TDD task by task, pauses at checkpoints
/sdd verify             → fresh-context Verifier: matrix, 1 gap → 1 appended task
/sdd implement next ; /sdd verify            → converged
"Accept verification."                       # G4
/sdd archive            → living spec updated, change archived, PR ready
```

The same flow works in Codex with `$sdd …`. You can also switch tools mid-change,
for example specifying in Claude Code and implementing in Codex, because the
state is in `specs/`.

### 9.2 Mid-implementation surprise

The Implementer finds that the payment provider can't send emails for guest
orders. It stops and runs `sdd amend`. The operator sees a two-line delta
("REQ-CHK-007: confirmation sent by our mailer, not the provider"), approves
it, and work resumes. The spec never silently diverges from the code.

### 9.3 Defect

`sdd bug "guest order emails go to the wrong address"`. The Author records
current vs expected behavior and links it to REQ-CHK-007. That REQ is right, so
this is a code defect, and the fix starts with a failing regression test named
for the REQ. If no REQ covered the behavior, it's a **spec gap**: the fix adds
a requirement first.

### 9.4 Brownfield entry

`sdd baseline checkout` drafts the capability spec from code and tests, with
every requirement marked `observed`. The operator corrects anything that is
"observed but wrong". That correction is the first real spec, and the next
change is a normal delta against it.

### 9.5 Interaction modes

- **Guided** (default): one phase per command, stop and summarize.
- **Run-to-gate**: `sdd next` chains phases until the next approval.
- **Review**: `sdd status --review` prints a one-screen digest (new and modified
  REQs, open questions, risks, size vs cap) so approval doesn't require opening
  the files.

## 10. Pitfalls and how the design avoids them

| Pitfall (seen in existing SDD tools) | Countermeasure |
| --- | --- |
| Markdown bloat and review fatigue | Size and assurance dials, size caps, `mini` = one file, review digest. |
| Waterfall feel | Small change folders, `amend`, `quick`, run-to-gate. |
| Spec drift after shipping | Steward + archive before merge + drift audit in verify. |
| Agent ignores the spec while coding | One task per Implementer context. REQ IDs in test names. `check`. Pre-commit gate. `AGENTS.md` section. |
| LLM "verifies" its own work | Fresh-context Critic and Verifier (subagent or new session). |
| Persona theatre | Roles are authority boundaries, and handoffs are files, not conversations. |
| Rebuilding what the host already does | Use plan mode, native subagents and worktrees where present. The skill adds only artifacts, IDs, gates and checks. |
| "Task done" ≠ requirement works | Done = passing test naming the REQ. The Verifier reruns tests. |
| Upgrades overwrite customizations | The method lives in the skill. The project owns only `specs/`. |
| Tool lock-in | Portability rules (§8.1). Evals run in both tools. |
| Happy-path-only testing | Coverage taxonomy with no blank cells allowed, Critic audit, negatives scheduled next to happy paths, branch coverage and mutation testing at Verify (§6). |
| Weak negative tests (assert only the error code) | A negative "Then" must also assert no side effects and unchanged state (§6.3). |

## 11. Build plan

1. **v0: prove the loop in both tools.** Portable `SKILL.md` router,
   `agents/openai.yaml`, `install.sh`, templates, phases
   `init/propose/quick/specify/tasks/implement/verify/status`, `mini` size,
   `prototype` and `internal` assurance (Known gaps list, the three `internal`
   categories), red/green evidence, constitution seed (test-first + negative
   coverage), and `sdd check` covering status,
   blank matrix cells, and scenario → task → test traceability. Dogfood one small real feature in Claude Code
   *and* the same flow in Codex. Confirm how Codex handles frontmatter,
   arguments and subagents.
2. **v1: make it anchored.** `clarify` (with Critic coverage audit),
   `analyze`, `archive`, `bug`, `amend`, `harden`, living `capabilities/`,
   `standard` size, `production` assurance (six core categories, branch
   coverage on the diff, adversarial probe), size caps.
3. **v2: independence and enforcement.** Claude subagents (`extras/claude`),
   fresh-session protocol for Codex, pre-commit gate, CI recipe, `baseline`.
4. **v3: distribution and quality.** Claude plugin + marketplace, `full`
   size, `critical` assurance (concurrency, decision tables, property-based
   tests, mutation testing per stack), eval suite run
   in both tools. The evals include seeded specs with missing negative cases,
   to check that Critic and `check` catch them.

## 12. Next step

**v0 built 2026-10-07** in `skill/sdd/` (see the README for
contents and install). It differs from the v0 plan above in four ways:

- `approve` and `archive` were pulled into v0. Without them the loop can't
  close: there is no recorded gate and no living spec.
- The coverage matrix is computed by the script, not written by hand (§6.3).
- `sdd.py` enforces the category requirements of **all four** assurance
  levels. Independent review and the extra verification signals for
  `production`/`critical` are still v1.
- Status and approvals are owned by the script (`approve`, `advance`).
  Agents never edit them by hand.

**Dogfood run 1 (Claude Code, 2026-10-07).** A fresh agent followed the
skill from `init` to `archive` on a small Python repo: 2 requirements, 15
scenarios, 15 tasks, archived cleanly. It found 5 script bugs and 11 friction
points. All are fixed, with failing tests first (script tests: 63 → 82):

- **Bugs:**
  - the plan gate could be bypassed through `blocked`;
  - a failed archive left the change stuck;
  - any file mentioning an ID counted as a test;
  - red evidence like "1 passed" was accepted;
  - a status could be set by hand with no approval behind it.
- **Method gaps:**
  - `If…then` requirements were rejected;
  - there was no path for behavior that already exists (now
    `red: pre-existing — <reason>`);
  - Known gaps and change history were lost at archive (both now carried into
    the living spec);
  - there was no guidance for changing code that has no spec yet;
  - the size words "interface" and "component" were undefined;
  - questions came after planning;
  - it was unclear whether spec gaps block PASS (they do, until the operator
    decides).
- **The operator's break protocol** (stop, analyze, think, plan, execute; two
  failed fixes → report) is now a rule in `SKILL.md`, the roles and the
  AGENTS.md section.

Next:
- **Codex parity is in scope for v0.** The operator runs the same flow in
  Codex (`$sdd …`) separately, and the findings feed back into this study.
- A second Claude Code run to confirm the fixes.

## 13. v1 plan (started 2026-10-07)

Scope: the v1 line of §11, minus what v0 already shipped (archive, living
capabilities, size caps).

**Operator decisions:**

| # | Decision | Outcome |
| --- | --- | --- |
| 11 | Independence at `production`+ | **Fresh-session protocol in v1.** The Critic and Verifier run in a new session and hand off only through files, in both tools. Claude subagents stay in v2. |
| 12 | Blocking diff coverage | **Computed by `sdd.py`** from an lcov report plus the git diff. Each uncovered changed line or branch needs a scenario or a justification. |
| 13 | How v1 is built | **Current discipline:** failing tests first for every script change, plus a dogfood run after increments 4 and 6. |
| 14 | Publishing | **`v1` branch**, pushed as increments land, with one PR into `main` when v1 is done. |

**Increments:**

| # | Increment | Contents |
| --- | --- | --- |
| 1 | `amend` + `bug` | The spec is locked at approval (a hash of the spec sections). Edits after that need a logged, approved amendment. `bug` creates a defect change: symptom, reproduction, current vs expected behavior, the violated REQ or "spec gap", root cause, and regression scenarios (`R1`…). |
| 2 | `standard` foundation | A change folder (`proposal`, `spec-delta`, `clarifications`, `design`, `tasks`, `verification`), the full status machine, 3 gates, and multi-file `check` and `archive`. |
| 3 | `clarify` + Spec Critic | A coverage audit, at most 5 questions per round, a clarifications log, and the spec gate. |
| 4 | `design` + Architect, `analyze`, `next` | Design, contracts, and the failure modes the design introduces (returned as scenarios). Cross-artifact consistency. Run to the next gate. Followed by **dogfood run 2**. |
| 5 | `production` assurance | Fresh-session Critic and Verifier, lcov diff coverage that blocks, an adversarial probe, and the results gate. |
| 6 | `harden <cap> --to <level>` | Turns a capability's Known gaps into a hardening change. Followed by **dogfood run 3**. |

**Progress:**
- Increment 1 merged in fpapleux/sdd-skill#1.
- Increment 2 merged in fpapleux/sdd-skill#2. It added the `standard` size:
  a change folder read as one spec, a status machine with clarifying,
  spec-approved and designed, the spec, plan and results gates with
  integrity checks, a basic `design` phase and the Architect role.
- Increment 3 is in PR #3. It adds `clarify` and the Spec Critic:
  - Each review round is recorded in a fixed format: a verdict per
    requirement, typed findings that each need an outcome, and at most 5
    answered questions.
  - A round is required before the gate for `standard` changes at
    `internal`+, and for any size at `production`+. The latest round must
    have audited every current requirement.
  - New `sdd.py round` command. In this increment, same-session rounds at
    `production`+ only get a warning.

## Sources

- Principles only: the author's role-based delivery process (internal
  documentation, not public).
- Claude Code docs: https://code.claude.com/docs/en/skills.md ·
  https://code.claude.com/docs/en/sub-agents.md ·
  https://code.claude.com/docs/en/hooks-guide.md ·
  https://code.claude.com/docs/en/plugins/publish.md
- GitHub Spec Kit: https://github.com/github/spec-kit ·
  https://raw.githubusercontent.com/github/spec-kit/main/spec-driven.md
- Kiro: https://kiro.dev/docs/specs/ · https://kiro.dev/docs/steering/ ·
  https://kiro.dev/docs/hooks/
- OpenSpec: https://github.com/Fission-AI/OpenSpec
- BMAD Method: https://github.com/bmad-code-org/BMAD-METHOD
- GSD: https://github.com/open-gsd/gsd-core
- Agent OS: https://buildermethods.com/agent-os
- B. Böckeler, "Understanding SDD: Kiro, spec-kit, and Tessl":
  https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- Scott Logic, "Putting Spec Kit through its paces":
  https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html
- EARS: A. Mavin et al., "Easy Approach to Requirements Syntax", IEEE RE 2009
