# Phase: `archive`

Fold the verified change into the living spec. Role: **Spec Steward**
(`method/roles/spec-steward.md`).

1. **Precondition.** The active change is `verified`. Otherwise, show
   `SDD status` and stop.
2. Run `SDD archive`. It merges each requirement into
   `specs/capabilities/<name>/spec.md` (added, modified or removed), carries
   the change's Known gaps over (tagged with the change ID), and adds a
   `## Change history` line. Then it sets the status to `archived` and moves
   the change to `specs/archive/`. If anything fails, nothing is changed.
3. Review each capability spec it touched, following the role file.
4. Report what was added, modified and removed per capability, plus any
   review findings. Remind the operator to commit `specs/` together with the
   code, in the same commit or PR. Next: `sdd quick "<next idea>"`.
