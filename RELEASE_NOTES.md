# Release notes

What each version published, newest first. Versions follow
`MAJOR.MINOR.BUILD`: every push raises MINOR, and MAJOR becomes 1 when v1
is complete. Versions before 0.5.0 are numbered by milestone (v0 = 0.1,
v1 increments 1–3 = 0.2–0.4).

**Behavior** marks changes to what the skill or `sdd.py` does. Other entries
are planning, specs and documentation.

## 0.17.0 — 2026-10-21

Change 0003-design-depth-analyze-next (v1 increment 5) passed its second
verification round and was archived. Living specs:
[`analysis`](specs/capabilities/analysis/spec.md) (8 requirements, new) and
[`orchestration`](specs/capabilities/orchestration/spec.md) (now 6
requirements). The change has 11 requirements, 147 scenarios and 146 tasks.
The suite is now 439 tests, and all 158 planned mutations are caught.

- **Behavior:** new `sdd.py analyze [--change] [--json]`. It prints check's
  plan-stage report headed `analyze <id>`, adds the cross-artifact findings
  and a scenario count, and exits 1 on any error. For a `standard` change at
  designed or later:
  - the design must not name a requirement that doesn't exist (error), and
    should name every requirement of the change (warning);
  - every `- FM<n> <text> → <outcome>` failure mode, or a single
    `- None — <reason>` line, must be well formed, and its outcome must be
    scenario references that exist or `N/A` with a reason of at least three
    words;
  - at `production` and above a design with no failure modes is an error
    (below, a warning).
  At any size it also warns about a requirement clause no scenario exercises
  and about a change with more happy than non-happy scenarios. Both are
  heuristics.
- **Behavior:** in a `standard` change, from the plan stage on, each
  `- interface: <name>` line needs a `### <name>` entry under `## Contracts`.
  `check` reports a missing, nameless or repeated entry as an error and an
  entry no interface lists as a warning.
- **Behavior:** `approve plan` runs the same analysis and refuses on any
  analyze error. It prints the report and records nothing. Warnings don't
  block, and a `mini` plan approval is unchanged.
- **Behavior:** new `sdd.py next [--change]`. It lists the numbered steps to
  the next gate for the change's size and status, then the gate line. It puts
  a fixing step first (`specify`, `design` or `tasks`) when a report shows the
  problem. A changed constitution, an edited approved spec, a blocked or an
  abandoned change each print their own line. It runs nothing and writes
  nothing.
- **Behavior:** `status` at designed, with tasks and a clean check, now says
  `sdd analyze, then ask for plan approval`.
- Method: the design phase adds Failure modes, Contracts and a failure-mode
  review by a strong read-only subagent (a fresh session in Codex). New
  `analyze` and `next` phases. The Architect role, `format.md`, `overview.md`,
  the `tasks` phase, `SKILL.md` and the standard design template follow.
- Upgrade: no spec needs editing, but a `standard` change at `production`
  that reaches the plan gate now needs a Failure modes section (or a `- None`
  line). A change already past the plan gate sees the design findings only in
  `analyze`.
- Built with the 0.16.0 fan-out: the prime session routed all 146 tasks to
  implementer subagents by tier (86 light, 43 mid, 11 strong, plus 6 light
  repair tasks). Verification ran in a separate fresh session. Round 1 found 12 gaps, and
  the operator chose to amend four (amendment A2: four new scenarios) and
  accept five as known gaps. Round 2 passed.
- Known issue: `archive` copies every known gap of a change into each
  capability it touches, so `analysis` and `orchestration` both list all 16.
- Roadmap: delivery profiles and install options move from increment 5 to 6,
  with releases and deploy. A visual design step (style guide, style sheets,
  mock-ups) is recorded as unscheduled after v1, and contract depth is to be
  revisited with the `full` size.
- Published on the `v1` branch; not merged into `main` yet.

## 0.16.0 — 2026-10-18

Change 0002-subagent-fanout (v1 increment 4) passed verification and was
archived. Living specs:
[`orchestration`](specs/capabilities/orchestration/spec.md) (3 requirements)
and [`evidence`](specs/capabilities/evidence/spec.md) (3 requirements).
It has 6 requirements, 81 scenarios and 68 tasks. The suite is now 290 tests,
and all 49 planned mutations are caught.

- **Behavior:** a task may carry `  - tier: light|mid|strong`, or an escalation
  such as `light → mid`. `check` rejects other values, and warns about a task
  without a tier from the plan stage on. `status` and `status --json` count
  tasks per tier.
- **Behavior:** `sdd.py round --subagent <tier>` heads a Critic round with its
  runner. At `production` and above, `check` warns unless the latest round ran
  in a fresh session or as a strong subagent.
- **Behavior:** at `production` and above, `check --stage verify` warns unless
  the latest `Verifier:` line names a fresh session or a strong subagent.
- **Behavior:** new `sdd.py replay --base <rev>`: reruns each ticked task's
  test at the base revision and in the working tree, and reports each task
  as confirmed or a mismatch. A red line marked `(after T<n>)` is checked in
  the working tree only.
- **Behavior:** new `sdd.py mutate`, with a `## Mutations` section (not counted
  toward the size cap) that `check` validates. Each mutation is run in a
  scratch copy and reported as caught, survived or invalid.
- **Behavior:** a design may name its single-test command with
  `- Test one:`, which `replay` and `mutate` need. Both need git, and neither
  changes your working tree.
- Method: `SKILL.md` gains an Orchestration section (prime model, subagent
  hand-off, tier → model, escalation after two failed attempts, Codex
  fallback). Every role file starts with its tier, effort and read-only rule.
  The Planner assigns tiers and mutations; the Verifier runs `replay` and
  `mutate`.
- Upgrade: no spec needs editing. Existing specs now show the new warnings
  (no tier, and a `production` change's Verifier or Critic runner) but still
  pass `check`.
- Known gaps carried into the living specs: runner and tier records are written
  by the agent and not verified; read-only subagents are an instruction, not
  enforced; `replay` and `mutate` have no time limit; a mutation is a
  single-line find and replace.
- Not yet exercised live: spawning a Critic or Verifier subagent. The method
  half was verified by review.
- Merged into `main` from the `v1` branch, together with 0.14.0 and 0.15.0.

## 0.15.0 — 2026-10-14

- These release notes, listing every version since v0.
- README: current status, the v1 increments with their state, and how SDD
  develops itself.
- Published on the `v1` branch; not merged into `main` yet.

## 0.14.0 — 2026-10-14

- Roadmap: **subagent fan-out** becomes v1 increment 4. A prime model will
  orchestrate, while the Critic and Verifier run as read-only subagents on
  strong models and routine tasks run on cheaper ones. A fresh session stays
  the fallback in Codex. The later increments move up by one: design depth
  (5), releases and deploy (6), `production` assurance (7), `harden` (8).
- Dogfood runs are scheduled after increments 4, 5 and 8.
- Published on the `v1` branch; not merged into `main` yet.

## 0.13.0 — 2026-10-14

- Change 0001-approval-integrity passed its third verification round and
  was archived.
- First living spec in this repository:
  [`specs/capabilities/approvals/spec.md`](specs/capabilities/approvals/spec.md),
  with 3 requirements, 53 scenarios and 4 known gaps.
- Merged into `main` in
  [fpapleux/sdd-skill#4](https://github.com/fpapleux/sdd-skill/pull/4),
  together with 0.5.0–0.12.0.

## 0.12.0 — 2026-10-14

- Tests for amendment A2: a verdict inside a comment spanning several lines
  is ignored; "Verdict: PASSED" is refused as unknown; re-wrapping a
  constitution rule counts as a change; a missing assurance level is
  refused. Each test is proven by a deliberately broken copy of the code.
  208 tests.

## 0.11.0 — 2026-10-12

- Verification round 2 found five gaps, mostly rules that were stated but
  not tested. Amendment A2 was approved to cover them.

## 0.10.0 — 2026-10-12

- **Behavior:** numbered list items ("1. Verdict: …", "1) Verdict: …") count
  as verdict lines.
- **Behavior:** only the fingerprint note at the very end of an approval's
  Evidence cell counts, so evidence that quotes an older note can't put an
  old level back in force.
- **Behavior:** with no approved level on record, a missing or invalid
  assurance level is refused by `new`, `check` and `status`, with an error
  naming the four levels. Before, a missing level silently became
  `internal` and an invalid one crashed.
- 205 tests.

## 0.9.0 — 2026-10-12

- Verification round 1 found seven gaps, five of them in the spec itself.
  Amendment A1 was approved to cover them.

## 0.8.0 — 2026-10-12

- **Behavior:** `approve results` (standard) and `advance verified` (mini)
  need the Verifier's latest verdict to be PASS. Before, a GAPS verdict was
  accepted.
- **Behavior:** approving the constitution records its fingerprint and
  approved level. Later edits are reported by `status`, fail `check`, and
  block the gates until you re-approve. Until then the last approved
  assurance level stays in force, and a re-approval that lowers the level
  is labelled "assurance lowered X → Y".
- **Behavior:** re-approving an unchanged constitution is refused.
- Upgrading: a change already in `verifying` needs a `Verdict:` line before
  it can be verified. A constitution approved by an earlier version is
  protected from its next approval on.
- 194 tests.

## 0.7.0 — 2026-10-12

- The first SDD change developed with SDD on this repository: defect
  0001-approval-integrity, planned and approved after a fresh-session Critic
  review.

## 0.6.0 — 2026-10-12

- Constitution re-approved with the versioning rule.

## 0.5.0 — 2026-10-11

- Versioning rule: `MAJOR.MINOR.BUILD`.
- SDD now develops itself: `specs/` was initialized on this repository at
  `production` assurance, with a pinned copy of the tool kept separate from
  the code being changed.
- Delivery design: releases are built once and approved by digest; deploys
  get their own lifecycle with receipts and rollback
  ([sdd-deployment-approach.md](sdd-deployment-approach.md)).

## 0.4 — 2026-10-08 · v1 increment 3

- **Behavior:** new `clarify` phase and Spec Critic role. Each review round
  gives a verdict per requirement, typed findings that each need an outcome,
  and at most 5 questions for you.
- **Behavior:** a Critic round is required before the gate for `standard`
  changes at `internal` and above, and for any size at `production` and
  above. New command `sdd.py round`.
- 151 tests.

## 0.3 — 2026-10-08 · v1 increment 2

- **Behavior:** the `standard` size: a change folder (proposal, spec delta,
  design, tasks, verification) with three gates: spec, plan and results.
- **Behavior:** new `design` phase and Architect role.
- 128 tests.

## 0.2 — 2026-10-08 · v1 increment 1

- **Behavior:** the approved spec is locked. Later edits fail `check` until
  an amendment is logged and approved (`amend`).
- **Behavior:** `bug` creates a defect change with a reproduction, a root
  cause and a regression scenario that lands in the living spec.
- 102 tests.

## 0.1 — 2026-10-07 · v0

- First release: the `mini` size end to end in Claude Code and Codex. EARS
  requirements with Given/When/Then scenarios, one approval gate, test-first
  tasks with recorded red and green evidence, verification, and a living
  spec.
- The two dials: size (paperwork) and assurance (proof), with failure
  categories enforced by the script at all four levels.
- `sdd.py`, standard library only. 82 tests.
