# Phase: `quick "<idea>"`

A whole `mini` change in one pass, ending at the single gate. Roles: **Spec
Author** (`method/roles/spec-author.md`), then **Planner**
(`method/roles/planner.md`).

1. **Size.** Apply the size ladder from the overview.
   - `inline`: say so, and do it directly, test-first if behavior changes. No
     spec files.
   - `standard`: `quick` is for `mini`. Say so, and continue with the
     `standard` path: `propose` → `specify`. Alternatively, offer a split
     into `mini` changes if the parts are truly independent.
2. **Capability.** Look in `specs/capabilities/` for the capability this
   belongs to, and reuse its `name=PREFIX`. Otherwise choose a short name and a
   2–6 letter prefix.
3. Run `SDD new <slug> --title "<title>" --capability <name>=<PREFIX>`. Add
   `--type defect` for a bug fix. If the change touches something more
   sensitive than the project level (money, auth, data deletion), propose
   raising it with `--assurance <level>`.
4. **As Spec Author:** write Intent, Scope, Requirements (scenarios, N/A lines)
   and Known gaps. Write `[NEEDS CLARIFICATION: …]` for anything that is a
   product decision you can't settle from the request or the code.
5. Run `SDD check --stage spec` and fix every error.
6. **Open questions:** ask them now, before planning, because answers change
   the plan. Ask at most 5 at a time, each with options and your
   recommendation. Fold the answers in, remove the markers, and log them under
   `## Open questions`. Re-run `SDD check --stage spec`.
7. **As Planner:** write Design notes (including the real test command) and
   Tasks.
8. Run `SDD check` until it reports `result: OK`.
9. **Gate: plan.** Show the review digest (overview, "Reporting") and ask:
   "Approve this spec and plan?" Then **stop**. Don't write tests or code in
   this turn.
