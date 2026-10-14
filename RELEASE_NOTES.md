# Release notes

What each version published, newest first. Versions follow
`MAJOR.MINOR.BUILD`: every push raises MINOR, and MAJOR becomes 1 when v1
is complete. Versions before 0.5.0 are numbered by milestone (v0 = 0.1,
v1 increments 1–3 = 0.2–0.4).

**Behavior** marks changes to what the skill or `sdd.py` does. Other entries
are planning, specs and documentation.

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
