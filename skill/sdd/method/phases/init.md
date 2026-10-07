# Phase: `init [level]`

You are setting up the repository with the operator.

1. If `specs/constitution.md` already exists, the repository is set up. Show
   `SDD status` and stop. Mention that `SDD init --force` only refreshes the
   folders and the AGENTS.md/CLAUDE.md wiring; it never touches the
   constitution or specs.
2. Make sure you are at the repository root (usually the git root). If that's
   unclear, ask.
3. **Assurance level.** If the operator gave one (`init internal`), use it.
   Otherwise ask one question with four answers. They should start at the top,
   and the first "yes" wins:
   - Money, security, safety, regulated, or irreversible? → `critical`
   - External users, or business data that persists? → `production`
   - Used by you or your team, with real data? → `internal`
   - Demo or experiment; may be thrown away? → `prototype`

   If the answer falls between two levels, recommend the higher one. Never
   choose a level silently.
4. Run `SDD init --assurance <level>`.
5. Show the operator, briefly, the level and what it means in practice
   (overview table) and the three articles of `specs/constitution.md`. Ask
   whether to add project rules (stack, dependency policy, supported
   platforms). Write any answers under `## Project rules`.
6. **Gate: constitution.** Ask the operator to approve it. When they approve,
   run `SDD approve constitution --evidence "<their words, where, date>"`.
7. Report what was created (`specs/`, AGENTS.md section, `@AGENTS.md` in
   CLAUDE.md). Remind them to commit `specs/` with the code. Next:
   `sdd quick "<idea>"`.
