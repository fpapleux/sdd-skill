---
capability: approvals
prefix: APR
---

# Capability: approvals

<!-- Living spec: the current, approved behavior of this capability.
Maintained by `sdd.py archive`. Do not edit by hand. -->

## Known gaps
<!-- Behavior deliberately not handled yet, carried from archived changes. -->
- Only the constitution gains a fingerprint; capability specs stay protected by being written only through sdd.py. (0001-approval-integrity)
- A constitution approved by an earlier version is unprotected until its first approval under this version; that approval records a fingerprint but cannot label a lowering. (0001-approval-integrity)
- A constitution that was never approved blocks no gate (Q7); a later change may require the first approval. (0001-approval-integrity)
- Approvals are plain-text records: a deliberately forged approval row is not detected. Review approval rows in pull requests. (0001-approval-integrity)

## Change history
- 0001-approval-integrity — Results gate ignores the verdict; constitution edits go undetected (2026-10-14): added REQ-APR-001, added REQ-APR-002, added REQ-APR-003

## Requirements

### REQ-APR-001 The results gate requires a PASS verdict
When the operator approves the results of a standard change, or a mini change
is marked verified, sdd.py shall proceed only if the latest verdict line of the
Verification section has the verdict word PASS. A verdict line is a line of that
section, outside fenced code blocks and HTML comments, whose text after an
optional list marker (`-`, `*`, `+`, or a number followed by `.` or `)`) and
`*`/`_` emphasis begins with "Verdict:" in any case;
table rows and mid-line mentions are not verdict lines. The verdict word is the
run of letters after the colon: PASS or GAPS in any case; anything else, such as
PASSED, is unknown.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a standard change in verifying, verify check OK, the Verification section ending with "Verdict: PASS" | approve results | exit 0 · status verified · one results row in Approvals |
| R1 | validation | the S1 change, but the latest line is "Verdict: GAPS — F1 open" | approve results | exit 1 · the error contains "GAPS — F1 open" · status stays verifying · no results row |
| N1 | validation | the S1 change, but no verdict line | approve results | exit 1 · error "no verdict" · status stays verifying · no results row |
| N2 | validation | the S1 change, but the latest line is "Verdict: maybe" | approve results | exit 1 · the error lists PASS and GAPS · status stays verifying · no results row |
| B1 | boundary | the S1 change, but the latest line is "Verdict: pass — 0 findings" | approve results | exit 0 · status verified |
| B2 | boundary | the S1 change, with an earlier "Verdict: PASS" and a later "**Verdict:** GAPS — F3" | approve results | exit 1 · status stays verifying · no results row |
| B3 | boundary | the S1 change, with "Verdict: PASS" followed by a fenced code block containing "Verdict: GAPS" | approve results | exit 0 · status verified |
| B4 | boundary | the S1 change, with an earlier "Verdict: PASS" and a later "1. Verdict: GAPS — F4" | approve results | exit 1 · status stays verifying · no results row |
| B5 | boundary | the S1 change, with an earlier "Verdict: PASS" and a later "1) Verdict: GAPS — F4" | approve results | exit 1 · status stays verifying · no results row |
| B6 | boundary | the S1 change, with "Verdict: GAPS — F1" followed by a table row "\| Verdict \| PASS \|" | approve results | exit 1 · status stays verifying · no results row (a table row is not a verdict line) |
| B7 | boundary | the S1 change, with "Verdict: GAPS — F1" followed by "The final Verdict: PASS was expected" | approve results | exit 1 · status stays verifying · no results row (a mid-line mention is not a verdict line) |
| B8 | boundary | the S1 change, with "Verdict: GAPS — F1" followed by a multi-line HTML comment whose middle line is "Verdict: PASS" | approve results | exit 1 · status stays verifying · no results row (a comment is not a verdict line) |
| N3 | state | the S1 change, with an earlier "Verdict: PASS" and a later "Verdict: GAPS — F2" | approve results | exit 1 · status stays verifying · no results row |
| S2 | state | the S1 change, with an earlier "Verdict: GAPS" and a later "Verdict: PASS" | approve results | exit 0 · status verified (the latest verdict wins) |
| N6 | validation | the S1 change, but the latest line is "Verdict: PASSED" | approve results | exit 1 · the error lists PASS and GAPS · status stays verifying · no results row |
| N4 | dependency | the S1 change, but its verification.md file was deleted | approve results | exit 1 · error "no verdict" · status stays verifying · no results row |
| S3 | happy | a mini change in verifying, verify check OK, the Verification section ending with "Verdict: PASS" | advance verified | exit 0 · status verified |
| R2 | validation | a mini change in verifying, verify check OK, the Verification section ending with "Verdict: GAPS" | advance verified | exit 1 · the error contains "GAPS" · status stays verifying · spec.md is unchanged |
| N5 | validation | a mini change in verifying, verify check OK, no verdict line | advance verified | exit 1 · error "no verdict" · status stays verifying · spec.md is unchanged |

- N/A access: sdd.py runs locally with no users or roles; who may approve is governed by the agent rules

### REQ-APR-002 Constitution changes after approval are detected
When the operator approves the constitution, sdd.py shall record its
fingerprint and approved level in the front matter (fingerprint,
approved_level) and at the end of that approval row's Evidence cell; only a
note at the very end of the cell counts. The constitution is changed since
approval when the newest approval row that carries a fingerprint differs from
the current content, or when the front matter's fingerprint is missing,
unreadable or different from that row's. When no approval row carries a
fingerprint, a valid fingerprint in the front matter is the reference. While
it is changed, status shall report it, check shall report it as an error and
exit 1, and approve spec, plan, results and amend, advance verified and archive
shall refuse; approve constitution, new and the other advance moves are not
blocked. The fingerprint is the first 12 hex digits of a SHA-256 over the
constitution with HTML comments and blank lines removed and runs of whitespace
inside each line collapsed (re-wrapping a paragraph is a change); it excludes
the Approvals section and the front-matter keys approved, fingerprint and
approved_level.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | an initialized repository whose constitution isn't approved | approve constitution | exit 0 · the front matter holds "fingerprint: <12 hex digits>" and "approved_level: <level>" · the row's Evidence cell ends with the same fingerprint and level · status shows no change note |
| R1 | state | an approved constitution to which "10. Anything goes." was then added | status | the output says the constitution changed since approval and names sdd approve · status --json has constitution_changed true and constitution_approved true · exit 0 |
| N1 | state | that changed constitution and a mini draft ready for plan approval | approve plan | exit 1 · the error says the constitution changed since approval · the change stays draft · no plan row · spec.md is unchanged |
| N5 | state | that changed constitution and an active change | check | exit 1 · the error says the constitution changed since approval |
| N6 | state | that changed constitution and a mini change in verifying, verify check otherwise OK, "Verdict: PASS" | advance verified | exit 1 · the error says the constitution changed since approval · status stays verifying |
| S2 | happy | that changed constitution | approve constitution | exit 0 · a "constitution (re-approval)" row · status shows no change note |
| N2 | validation | a constitution with approved: yes and a fingerprint that matches its content | approve constitution | exit 1 · error "nothing changed since approval" · no new row · the constitution file is unchanged |
| N3 | validation | an approved constitution whose fingerprint line was edited by hand | status | the output says the constitution changed since approval · exit 0 · nothing is rewritten |
| N7 | validation | an approved constitution whose fingerprint line was deleted | status | the output says the constitution changed since approval · exit 0 · nothing is rewritten |
| N8 | validation | an approved constitution whose front-matter delimiters were removed | status | the output says the constitution changed since approval · exit 0 · nothing is rewritten |
| B1 | boundary | an approved constitution with only blank lines and an HTML comment added | status | no change note · exit 0 · nothing is rewritten |
| B2 | boundary | an approved constitution with a double space added inside one rule | status | no change note · exit 0 · nothing is rewritten |
| B3 | boundary | an approved constitution with a row added by hand to the Approvals section, without a fingerprint | status | no change note · exit 0 · nothing is rewritten |
| B4 | boundary | an approved constitution in which one rule's line was split into two lines with the same words | status | the output says the constitution changed since approval · exit 0 · nothing is rewritten |
| N4 | state | a constitution approved by an earlier version (approved: yes, no fingerprint anywhere) | status | no change note · exit 0 · nothing is rewritten |
| S3 | state | that earlier-version constitution | approve constitution | exit 0 · a fingerprint is recorded in the front matter and the row · status shows no change note |
| S4 | state | a constitution that was never approved (approved: no, as init writes it) and a mini draft ready for plan approval | approve plan | exit 0 · the change is planned, as today |
| N9 | validation | approved at internal, edited to production, then re-approved with evidence quoting an older note "fingerprint 0123456789ab · level prototype" | status | no change note · assurance production · new changes are created at production |
| N10 | state | an approved constitution, then a hand-added newer row without a fingerprint and the front-matter fingerprint line deleted | status | the output says the constitution changed since approval · exit 0 · nothing is rewritten |
| S5 | state | an approved constitution whose fingerprinted approval rows were all deleted, front-matter fingerprint kept, then a rule added | status | the output says the constitution changed since approval · the front-matter approved level stays in force |

- N/A access: sdd.py runs locally with no users or roles; who may approve is governed by the agent rules
- N/A dependency: only the local constitution file is read; a missing file is already reported as not initialized

### REQ-APR-003 The approved assurance level stays in force
While the constitution has unapproved changes, sdd.py shall use the level
recorded at its last approval as the project level: the default and the floor
for new, the floor in check, and the level status shows. When an approval
accepts a lower level than the previous approved level, that row's Evidence
cell shall end with "assurance lowered <old> → <new>". When no approved level is
recorded and the front matter's level is missing or not one of the four
levels, new, check and status shall refuse with an error naming the four levels.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a constitution approved at internal, unchanged | new demo | the change is created at internal |
| R1 | state | approved at internal, then edited to "assurance: prototype", not re-approved | new demo | the change is created at internal · status shows "internal (prototype pending approval)" · status --json has assurance internal and assurance_pending prototype |
| N3 | state | approved at internal, edited to "assurance: prototype", not re-approved | new demo --assurance prototype | exit 1 · the error says it is lower than the project level 'internal' · no change folder is created |
| S2 | state | that edit, then the operator re-approves | approve constitution | exit 0 · the row's Evidence cell ends with "assurance lowered internal → prototype" · later changes are created at prototype |
| N1 | validation | the front matter edited to "assurance: sloppy", or its assurance line deleted | approve constitution | exit 1 · the error lists the four levels · no new row · internal stays in force · the constitution file is unchanged |
| B1 | boundary | approved at internal, edited to "assurance: production", not re-approved | new demo | the change is created at internal · status shows "internal (production pending approval)" |
| B2 | boundary | approved at internal, edited to "assurance: production" | approve constitution | exit 0 · the row has no "lowered" note · later changes are created at production |
| B3 | boundary | approved at internal, a project rule added, level unchanged | approve constitution | exit 0 · the row has no "lowered" note |
| N2 | state | a constitution approved by an earlier version (no recorded level) | new demo | the change uses the level in the front matter, as before · nothing is rewritten |
| S4 | state | a constitution approved by an earlier version at internal, then edited to "assurance: prototype" | approve constitution | exit 0 · fingerprint and approved_level prototype are recorded · the row has no "lowered" note |
| N4 | validation | a never-approved constitution with "assurance: prodution" | new demo | exit 1 · the error names "prodution" and lists the four levels · no change folder is created |
| N5 | validation | that never-approved constitution with "assurance: prodution" | status | exit 1 · the error names "prodution" and lists the four levels |
| N6 | validation | a constitution approved by an earlier version, then edited to "assurance: prodution", with an active change | check | exit 1 · the error names "prodution" and lists the four levels |
| N7 | validation | a never-approved constitution whose assurance line was deleted | new demo | exit 1 · the error says "(missing)" and lists the four levels · no change folder is created |

- N/A access: sdd.py runs locally with no users or roles; who may approve is governed by the agent rules
- N/A dependency: only the local constitution file is read; a missing file is already reported as not initialized
