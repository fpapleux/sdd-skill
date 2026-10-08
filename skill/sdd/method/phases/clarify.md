# Phase: `clarify`

Review the spec independently before its gate. Roles: **Spec Critic**
(`method/roles/spec-critic.md`) reviews, and the **Spec Author** applies the
results. The operator answers the questions.

**When it's required** (the script enforces this at the gate):
- `standard` changes at `internal` and above, before the spec gate;
- any size at `production` and above: before the spec gate (`standard`) or
  the plan gate (`mini`).

Elsewhere it's optional. Offer it when the spec is large, the domain is
unfamiliar, or failure behavior was hard to pin down.

1. **Precondition.** The active change is `draft` or `clarifying`. After a
   gate, spec changes go through `sdd amend` instead.
2. **Independence.**
   - At `production` and above, run this phase in a **fresh session** (a new
     chat) and use `SDD round --fresh`.
   - At `internal`, the same session is fine. Re-read the spec from the files
     as written, not from memory of writing it.
3. Run `SDD round` (or `SDD round --fresh`). It appends a round that lists
   every requirement with verdict `?`. A `standard` change moves to
   `clarifying`.
4. **As Spec Critic:** audit every requirement using the role checklist. Give
   each a verdict (`ok` or `issues`), write the findings, and write **at most
   5** questions, most important first.
5. **Ask the operator** the questions. Give options (A/B) and your
   recommendation. Record each answer under its question:
   `  - Answer: <answer> (operator, <date>)`.
6. **As Spec Author:** apply the answers and fixes to the spec. Give each
   finding its outcome (`→ fixed: <what changed>`). Remove resolved
   `[NEEDS CLARIFICATION]` markers and log them under `## Open questions`.
7. Run `SDD check`. It must report OK: no open findings and no unanswered
   questions.
8. **Run another round** (step 3) if:
   - more than 5 questions were needed;
   - the answers raised new issues;
   - requirements were added.

   The gate requires that the **latest** round audited every current
   requirement.
9. Report the findings by type with their outcomes, plus the questions and
   answers. Next comes the gate:
   - `standard`: **Gate: spec** (`method/phases/specify.md` step 5);
   - `mini`: **Gate: plan** (`method/phases/tasks.md` step 5).
