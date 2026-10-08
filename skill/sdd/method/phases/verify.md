# Phase: `verify`

Check the delivered work against the spec. Role: **Verifier**
(`method/roles/verifier.md`).

1. **Precondition.** The change is `implementing` with every task ticked, or
   already `verifying`. If tasks remain, say which, and point to
   `sdd implement`.
2. **Independence.** At `prototype` and `internal`, verifying in the same
   session is fine. At `production` and `critical`, the independent reviewer isn't built yet.
   Recommend that the operator run `verify` in a **fresh session** (new
   chat), which works because all state is in files. Continue here only if
   they say so.
3. If the status is `implementing`, run `SDD advance verifying`.
4. Follow the Verifier checklist and write `## Verification`.
5. **Gaps found:**
   - The behavior is specified but untested, weakly tested, or failing:
     append a new task for each (next free `T` number, same scenario ref), run
     `SDD advance implementing`, and report. Next: `sdd implement`.
   - The behavior exists but isn't in the spec (a spec gap): don't add it
     silently. Describe it to the operator and ask: **A)** amend now, or
     **B)** accept it as a known gap. The verdict stays GAPS until they
     answer. See the Verifier role.
6. **No gaps:**
   - `mini`: run `SDD advance verified`. Next: `sdd archive`.
   - `standard`: **Gate: results.** Show the verdict, the scenario matrix
     summary and any accepted findings, then ask "Approve these results?"
     Stop. The operator's approval is recorded with `SDD approve results`.
