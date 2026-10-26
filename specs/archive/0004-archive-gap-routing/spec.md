---
id: 0004-archive-gap-routing
title: Archive carries each known gap only to the capability it concerns
type: feature
size: mini
assurance: production
status: archived
capabilities: archive=ARC
created: 2026-10-21
spec_hash: e39630970596
---

# 0004-archive-gap-routing — Archive carries each known gap only to the capability it concerns

## Intent
`sdd.py archive` copies every known gap of a change into each capability spec
the change touches. Archiving 0002 put all 9 gaps into both orchestration and
evidence, and 0003 put all 16 into both analysis and orchestration, so a
capability's Known gaps list fills with gaps about other capabilities. The
Steward review flagged it after each archive. The outcome: each gap lands only
in the capability it concerns, and the spec author can say which one.

## Scope
- In: how `sdd.py archive` chooses the capability specs a known gap is written
  into. A capability the change *touches* is one holding at least one of its
  requirements (added, modified or removed).
- In: the capability tag, a new piece of Known gaps grammar (REQ-ARC-002),
  documented in `method/format.md` and `method/phases/archive.md` (design
  work under project rule 1).
- Changes existing behavior: archive wrote every known gap into every
  capability the change touches → a gap goes to the capabilities its tag
  names, else to those whose requirement IDs it names, else to every touched
  capability as before.
- Backward compatibility (project rule 5): a gap written for an earlier
  version that names no requirement ID and doesn't end with a tag is carried
  exactly as before. An in-flight gap whose text happens to end with a touched
  capability's name in parentheses, e.g. "… shared with (cli).", is now read
  as a tag: stripped and narrowed to that capability. Capability specs
  already written are not rewritten.
- Out: moving the gaps that 0002 and 0003 already carried into every
  capability. `specs/capabilities/` is written only by archive; cleaning them
  up is a separate decision for the operator.
- Out: any `sdd.py check` rule on Known gaps lines (tags or IDs).
- Out: the archive output lines, the change history line and requirement
  merging, which stay as they are.

## Requirements

### REQ-ARC-001 Archive carries each known gap to the capabilities it concerns
When `sdd.py archive` merges a change, sdd.py shall write each known gap that
has no capability tag (REQ-ARC-002), followed by the change ID in
parentheses, into the Known gaps of each capability the change touches (one
holding at least one of its added, modified or removed requirements) whose
prefix appears in a requirement ID the gap names (`REQ-<PREFIX>-<digits>` in
capitals, with or without a scenario suffix), or of every capability the
change touches when the gap names no touched capability's prefix.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a verified change with REQ-DUR-001 (duration) and REQ-CLI-001 (cli), and the gap "- REQ-DUR-001.N1 is tested on Linux only" | archive | duration's Known gaps has "- REQ-DUR-001.N1 is tested on Linux only (<change-id>)" · cli's spec has no line containing "tested on Linux only" |
| S2 | happy | the same change, and the gap "- Output is not localized" | archive | duration's and cli's Known gaps each have "- Output is not localized (<change-id>)" |
| B1 | boundary | the same change, and the gap "- REQ-DUR-001 and REQ-DUR-001.S1 depend on REQ-CLI-001" | archive | duration's and cli's specs each have the line "- REQ-DUR-001 and REQ-DUR-001.S1 depend on REQ-CLI-001 (<change-id>)" exactly once |
| B2 | boundary | the same change also removing REQ-APR-001 from a living approvals (APR) spec, and the gap "- REQ-APR-001 is gone" | archive | approvals' Known gaps has "- REQ-APR-001 is gone (<change-id>)" · duration's and cli's specs have no line containing "is gone" |
| B3 | boundary | a verified change declaring duration=DUR and duration=DU2, with REQ-DUR-001 and REQ-DU2-001, and the gap "- Output is not localized" | archive | duration's spec has the line "- Output is not localized (<change-id>)" exactly once · its Change history has the line for <change-id> exactly once |
| B4 | boundary | a verified change declaring duration=DUR and duration=DU2, with REQ-DUR-001 and REQ-DU2-001, and the gap "- REQ-DUR-001 is slow" | archive | duration's spec has the line "- REQ-DUR-001 is slow (<change-id>)" exactly once · no folder other than duration is created under specs/capabilities |
| B5 | boundary | a verified change declaring duration=DUR and duration=DU2, with REQ-DUR-001 and REQ-DU2-001, and the gaps "- REQ-DUR-001 is slow" and "- REQ-DU2-001 is slow" | archive | duration's spec has each of the lines "- REQ-DUR-001 is slow (<change-id>)" and "- REQ-DU2-001 is slow (<change-id>)" exactly once · no folder other than duration is created under specs/capabilities |
| N1 | validation | the change with REQ-DUR-001 and REQ-CLI-001, a living approvals spec, and the gap "- REQ-APR-001 is not rechecked" | archive | duration's and cli's Known gaps each have "- REQ-APR-001 is not rechecked (<change-id>)" · the approvals spec is byte-for-byte unchanged |
| N2 | validation | the same change, and the gap "- REQ-ZZZ-001 is out of reach" (no capability has prefix ZZZ) | archive | duration's and cli's Known gaps each have "- REQ-ZZZ-001 is out of reach (<change-id>)" · no folder other than duration and cli is created under specs/capabilities |
| N3 | validation | the same change, a living approvals spec, and the gap "- REQ-DUR-001 waits for REQ-APR-001" | archive | only duration's Known gaps has "- REQ-DUR-001 waits for REQ-APR-001 (<change-id>)" · cli's spec has no line containing "waits for" · the approvals spec is byte-for-byte unchanged |
| N4 | validation | the same change, and the gap "- DUR, CLI-001 and req-dur-001 are slow" | archive | duration's and cli's Known gaps each have "- DUR, CLI-001 and req-dur-001 are slow (<change-id>)" |

- N/A state: routing reads only the change text and the capability prefixes; archive's verified-status and existing-folder refusals are unchanged
- N/A dependency: routing calls nothing; archive still builds every capability text in memory before writing any file
- N/A access: a local command with no users, roles or other people's resources

### REQ-ARC-002 A capability tag names the capabilities a gap concerns
When a known gap's bullet line ends with a capability tag (after some text, a
space and, in parentheses, one or more names of capabilities the change
touches, separated by commas each optionally followed by one space, then
optionally a period), `sdd.py archive` shall write the gap with the tag
removed and any period kept, followed by the change ID in parentheses, only
into those capabilities' Known gaps, whatever requirement IDs the gap names.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a verified change with REQ-DUR-001 (duration) and REQ-CLI-001 (cli), and the gap "- Output is not localized (cli)" | archive | cli's Known gaps has "- Output is not localized (<change-id>)" · duration's spec has no line containing "not localized" |
| S2 | happy | the same change, and the gap "- REQ-DUR-001 errors are printed by the cli layer (cli)" | archive | cli's Known gaps has "- REQ-DUR-001 errors are printed by the cli layer (<change-id>)" · duration's spec has no line containing "printed by the cli layer" |
| S3 | happy | the same change, and the gap "- Output is not localized (cli)." | archive | cli's Known gaps has "- Output is not localized. (<change-id>)" · duration's spec has no line containing "not localized" |
| B1 | boundary | the same change, and the gap "- Units are English only (duration, cli)" | archive | duration's and cli's Known gaps each have "- Units are English only (<change-id>)" · neither has "(duration, cli)" |
| B2 | boundary | the same change, and the gap "- Units are English only (duration,cli,cli)" | archive | duration's and cli's specs each have the line "- Units are English only (<change-id>)" exactly once |
| B3 | boundary | the same change also removing REQ-APR-001 from a living approvals spec, and the gap "- Its replacement is pending (approvals)" | archive | approvals' Known gaps has "- Its replacement is pending (<change-id>)" · duration's and cli's specs have no line containing "replacement is pending" |
| N1 | validation | the change with REQ-DUR-001 and REQ-CLI-001, a living approvals spec, and the gap "- Output is not localized (approvals)" | archive | duration's and cli's Known gaps each have "- Output is not localized (approvals) (<change-id>)" · the approvals spec is byte-for-byte unchanged |
| N2 | validation | the same change, a living approvals spec, and the gap "- Output is not localized (cli, approvals)" | archive | duration's and cli's Known gaps each have "- Output is not localized (cli, approvals) (<change-id>)" · the approvals spec is byte-for-byte unchanged |
| N3 | validation | the same change, and the gap "- (cli) Output is not localized" | archive | duration's and cli's Known gaps each have "- (cli) Output is not localized (<change-id>)" |
| N4 | validation | the same change, and the gap "- Output is not localized (CLI)" | archive | duration's and cli's Known gaps each have "- Output is not localized (CLI) (<change-id>)" |
| N5 | validation | the same change, and the gap "- (cli)" | archive | duration's and cli's Known gaps each have "- (cli) (<change-id>)" |
| N6 | validation | the same change, a living approvals spec, and the gap "- REQ-DUR-001 is slow (approvals)" | archive | only duration's Known gaps has "- REQ-DUR-001 is slow (approvals) (<change-id>)" · cli's spec has no line containing "is slow" · the approvals spec is byte-for-byte unchanged |
| N7 | validation | the change with REQ-DUR-001 and REQ-CLI-001, and the gap "- Output (cli) is not localized" | archive | duration's and cli's Known gaps each have "- Output (cli) is not localized (<change-id>)" · neither has a line "- Output (<change-id>)" |

- N/A state: covered by REQ-ARC-001, whose routing this tag only narrows
- N/A dependency: covered by REQ-ARC-001, whose routing this tag only narrows
- N/A access: a local command with no users, roles or other people's resources

## Known gaps
- A tag naming a capability the change doesn't touch, or a misspelled one, is not reported: the gap keeps its text and is routed as an untagged gap (REQ-ARC-001).
- A requirement ID routes a gap by its prefix alone: an ID that doesn't exist in that capability still sends the gap there.
- `sdd.py check` doesn't look at tags or requirement IDs in Known gaps, so a misrouted gap is seen only in the capability specs archive writes.
- A gap is its bullet line (Q2): a tag on a continuation line isn't seen, and continuation lines are dropped, as before this change.
- Spaces inside the parentheses, as in "( cli )", and an empty "()" are not tags; no scenario of their own shows it.
- The gaps 0002 and 0003 already carried into every capability they touched stay where they are.

## Design notes
- Files: `skill/sdd/scripts/sdd.py` (`cmd_archive` and one new helper),
  `tests/test_sdd.py` (a new `ArchiveGapRoutingTests` class), and the docs
  `skill/sdd/method/format.md` (Known gaps: the tag, the routing order, a gap
  is its bullet line) and `skill/sdd/method/phases/archive.md` (step 2).
- While merging requirements, `cmd_archive` records each touched capability
  as prefix → (name, path), so removed requirements count as touching too.
- New helper `route_gap(gap, touched) -> (text, prefixes)`:
  1. tag: the gap matches `^(.*\S) \(([a-z0-9-]+(?:, ?[a-z0-9-]+)*)\)(\.?)$`
     and every name is a touched capability's name → those prefixes, text =
     group 1 + group 3 (the period kept);
  2. otherwise the prefixes of every `REQ-([A-Z][A-Z0-9]{1,5})-\d{3,}` in the
     gap that are touched (a set, so a capability gets the gap once);
  3. otherwise every touched prefix. The text is unchanged in 2 and 3.
- The Known gaps loop then writes, per capability path, only the gaps routed
  to it. It iterates capability files, not prefixes: a spec reached through
  two prefixes (`duration=DUR, duration=DU2`) collects both, and gets each
  gap and the history line once (A1, REQ-ARC-001.B3), routed through any
  of its prefixes (A2, REQ-ARC-001.B4; A3, REQ-ARC-001.B5). The carried-count line, history line and requirement merge stay as
  they are, and every text is still built in memory before any file is
  written.
- Test strategy: integration through `sdd.main()` like
  `ArchiveCarryOverTests`. One fixture builds a verified mini change with
  REQ-DUR-001 (duration=DUR) and REQ-CLI-001 (cli=CLI), optionally a living
  `approvals` (APR) spec holding REQ-APR-001 and optionally a
  `REQ-APR-001 [REMOVED]` block in the change, takes the gaps text, archives,
  and returns each capability spec's text. "byte-for-byte unchanged" compares
  the approvals file before and after. No test doubles: archive calls no
  other component.
- Mutations: the routing rules are new code, so the Implementer adds one
  `## Mutations` entry per rule once its task is green: tag recognized, tag
  stripped, period kept, untouched tag name rejected, ID prefix routing,
  touched-only filter, all-touched fallback, removals counted as touching.
- Test command: `python3 -m unittest tests.test_sdd`
- Test one: `python3 -m unittest tests.test_sdd.{name}`

## Tasks
- [x] T1 REQ-ARC-001.S1 A gap naming REQ-DUR-001 goes to duration only
  - tier: mid
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_S1_gap_naming_an_id_goes_to_that_capability_only
  - red: AssertionError: Lists differ: ['- REQ-DUR-001.N1 is tested on Linux only (0001-gaps)'] != []
  - green: Ran 1 test in 0.252s · OK
- [x] T2 REQ-ARC-001.N3 A touched and an untouched ID: touched capability only
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_N3_touched_and_untouched_ids_go_to_the_touched_capability
  - red: pre-existing (after T1) — T1's ID routing already keeps the gap out of the capability its touched ID doesn't name
  - green: Ran 1 test in 0.264s · OK
- [x] T3 REQ-ARC-001.N1 A gap naming only an untouched capability's ID goes everywhere
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_N1_gap_naming_only_an_untouched_id_goes_everywhere
  - red: pre-existing — today's archive already writes every gap into every touched capability
  - green: Ran 1 test in 0.238s · OK
- [x] T4 REQ-ARC-001.N2 A gap naming an unknown prefix goes everywhere, no new folder
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_N2_gap_naming_an_unknown_prefix_goes_everywhere
  - red: pre-existing — today's archive already writes every gap into every touched capability
  - green: Ran 1 test in 0.260s · OK
- [x] T5 REQ-ARC-001.N4 Bare and lowercase prefixes don't route
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_N4_bare_and_lowercase_prefixes_do_not_route
  - red: pre-existing — today's archive already writes every gap into every touched capability
  - green: Ran 1 test in 0.214s · OK
- [x] T6 REQ-ARC-001.S2 A gap naming nothing goes to every touched capability
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_S2_gap_naming_nothing_goes_to_every_touched_capability
  - red: pre-existing — today's archive already writes every gap into every touched capability
  - green: Ran 1 test in 0.254s · OK
- [x] T7 REQ-ARC-001.B1 Repeated IDs of two capabilities: each gets the gap once
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_B1_repeated_ids_of_two_capabilities_give_each_one_line
  - red: pre-existing — today's archive already writes every gap once into every touched capability
  - green: Ran 1 test in 0.229s · OK
- [x] T8 REQ-ARC-001.B2 A capability touched only by a removal receives its gap
  - tier: mid
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_B2_capability_touched_only_by_a_removal_gets_its_gap
  - red: pre-existing (after T1) — T1 records a removed requirement's capability as touched, so it gets the gap
  - green: Ran 1 test in 0.267s · OK
- [x] T9 REQ-ARC-002.S1 A "(cli)" tag sends the gap to cli, tag removed
  - tier: mid
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_S1_tag_sends_the_gap_to_that_capability_with_the_tag_removed
  - red: AssertionError: '- Output is not localized (0001-gaps)' not found in ['<!-- … -->', '- Output is not localized (cli) (0001-gaps)', '']
  - green: Ran 1 test in 0.224s · OK
- [x] T10 REQ-ARC-002.N1 A tag naming an untouched capability is kept as text
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N1_tag_naming_an_untouched_capability_is_kept_as_text
  - red: pre-existing — today's archive keeps the gap text whole and writes it into every touched capability
  - green: Ran 1 test in 0.289s · OK
- [x] T11 REQ-ARC-002.N2 A tag list with one untouched name is kept as text
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N2_tag_list_with_one_untouched_name_is_kept_as_text
  - red: pre-existing — today's archive keeps the gap text whole and writes it into every touched capability
  - green: Ran 1 test in 0.235s · OK
- [x] T12 REQ-ARC-002.N3 A tag at the start of the gap is not a tag
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N3_tag_at_the_start_of_the_gap_is_not_a_tag
  - red: pre-existing — today's archive keeps the gap text whole and writes it into every touched capability
  - green: Ran 1 test in 0.243s · OK
- [x] T13 REQ-ARC-002.N4 A capitalised name is not a tag
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N4_capitalised_name_is_not_a_tag
  - red: pre-existing — today's archive keeps the gap text whole and writes it into every touched capability
  - green: Ran 1 test in 0.206s · OK
- [x] T14 REQ-ARC-002.N5 A gap that is only a tag is not a tag
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N5_gap_that_is_only_a_tag_is_not_a_tag
  - red: pre-existing — today's archive keeps the gap text whole and writes it into every touched capability
  - green: Ran 1 test in 0.245s · OK
- [x] T15 REQ-ARC-002.N6 An unrecognised tag still routes by the touched ID
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N6_unrecognised_tag_still_routes_by_the_touched_id
  - red: pre-existing (after T1) — T1's ID routing already sends the gap to duration only
  - green: Ran 1 test in 0.269s · OK
- [x] T16 REQ-ARC-002.S2 The tag wins over a named requirement ID
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_S2_tag_wins_over_a_named_requirement_id
  - red: AssertionError (after T1): '- REQ-DUR-001 errors are printed by the cli layer (0001-gaps)' not found in ['<!-- … -->', '']
  - green: Ran 1 test in 0.254s · OK
- [x] T17 REQ-ARC-002.S3 A tag followed by a period: tag removed, period kept
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_S3_tag_before_a_period_is_removed_and_the_period_kept
  - red: AssertionError: '- Output is not localized. (0001-gaps)' not found in ['<!-- … -->', '- Output is not localized (cli). (0001-gaps)', '']
  - green: Ran 1 test in 0.253s · OK
- [x] T18 REQ-ARC-002.B1 A two-name tag sends the gap to both, tag removed
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_B1_two_name_tag_sends_the_gap_to_both_with_the_tag_removed
  - red: AssertionError: '- Units are English only (0001-gaps)' not found in ['<!-- … -->', '- Units are English only (duration, cli) (0001-gaps)', '']
  - green: Ran 1 test in 0.229s · OK
- [x] T19 REQ-ARC-002.B2 A tag without spaces and a repeated name: each once
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_B2_tag_without_spaces_and_a_repeated_name_gives_each_one_line
  - red: AssertionError: 0 != 1
  - green: Ran 1 test in 0.250s · OK
- [x] T20 REQ-ARC-002.B3 A tag naming a capability touched only by a removal
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_B3_tag_naming_a_capability_touched_only_by_a_removal
  - red: AssertionError: '- Its replacement is pending (0001-gaps)' not found in ['- Its replacement is pending (approvals) (0001-gaps)', '']
  - green: Ran 1 test in 0.374s · OK

- [x] T21 REQ-ARC-002.N7 A tag-shaped "(cli)" mid-line is not a tag
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N7_tag_shaped_name_mid_line_is_not_a_tag
  - red: pre-existing — GAP_TAG already anchors the tag at the end of the line, so a mid-line "(cli)" stays plain text
  - green: Ran 1 test in 0.220s · OK
- [x] T22 REQ-ARC-001.B3 One capability under two prefixes: each gap and history line once
  - tier: mid
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_B3_one_capability_under_two_prefixes_gets_each_line_once
  - red: AssertionError (after T1): 2 != 1
  - green: Ran 1 test in 0.173s · OK
- [x] T23 REQ-ARC-001.B4 One capability under two prefixes: a gap naming REQ-DUR-001 lands once
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_B4_gap_naming_one_of_two_prefixes_of_a_capability_lands_once
  - red: pre-existing — the base archive writes every gap once per capability file, and T22's per-file loop already routes through all of a file's prefixes
  - green: Ran 1 test in 0.246s · OK
- [x] T24 REQ-ARC-001.B5 One capability under two prefixes: gaps naming each prefix land once each
  - tier: light
  - test: tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_B5_gaps_naming_each_of_two_prefixes_land_once_each
  - red: pre-existing — the base archive writes every gap once per capability file, and T22's per-file loop already routes through all of a file's prefixes
  - green: Ran 1 test in 0.320s · OK

## Mutations
- M1 REQ-ARC-002.S1 skill/sdd/scripts/sdd.py
  - find: `    if tag:`
  - replace: `    if False:`
- M2 REQ-ARC-002.S1 skill/sdd/scripts/sdd.py
  - find: `return tag.group(1) + tag.group(3), {by_name`
  - replace: `return gap, {by_name`
- M3 REQ-ARC-002.S3 skill/sdd/scripts/sdd.py
  - find: `tag.group(1) + tag.group(3)`
  - replace: `tag.group(1)`
- M4 REQ-ARC-002.N2 skill/sdd/scripts/sdd.py
  - find: `if names <= set(by_name):`
  - replace: `if names & set(by_name):`
- M5 REQ-ARC-001.S1 skill/sdd/scripts/sdd.py
  - find: `-\d{3,}", gap)`
  - replace: `-\d{3,}", "")`
- M6 REQ-ARC-001.N1 skill/sdd/scripts/sdd.py
  - find: `if m in touched}`
  - replace: `if m}`
- M7 REQ-ARC-001.S2 skill/sdd/scripts/sdd.py
  - find: `named or set(touched)`
  - replace: `named`
- M8 REQ-ARC-001.B2 skill/sdd/scripts/sdd.py
  - find: `        touched[req.prefix] = (info["name"], cap_path)  # removed requirements touch too`
  - replace: `        if req.tag != "REMOVED": touched[req.prefix] = (info["name"], cap_path)`
- M9 REQ-ARC-002.N7 skill/sdd/scripts/sdd.py
  - find: `\)(\.?)$")`
  - replace: `\)(\.?)")`
- M10 REQ-ARC-001.B3 skill/sdd/scripts/sdd.py
  - find: `    for cap_path, done in actions.items():  # per file: one spec may hold several prefixes`
  - replace: `    for cap_path, done in [(path, actions[path]) for _, path in touched.values()]:`
- M11 REQ-ARC-001.B4 skill/sdd/scripts/sdd.py
  - find: `        prefixes = {prefix for prefix, (_, path) in touched.items() if path == cap_path}`
  - replace: `        prefixes = {[prefix for prefix, (_, path) in touched.items() if path == cap_path][-1]}`
- M12 REQ-ARC-001.B5 skill/sdd/scripts/sdd.py
  - find: `        prefixes = {prefix for prefix, (_, path) in touched.items() if path == cap_path}`
  - replace: `        prefixes = {[prefix for prefix, (_, path) in touched.items() if path == cap_path][0]}`

## Verification
<!-- Verifier: commands run, results, coverage, findings, verdict. -->
- Date: 2026-10-21 · Verifier: subagent (strong)
- Tests: `python3 -m unittest tests.test_sdd` → 459 passed
- Check: `sdd.py check --stage verify` (pinned) → OK; 13 warnings for the pre-existing tasks (T2–T8, T10–T15), plus one asking for an independent Verifier, which this record is
- Replay: `sdd.py replay --base HEAD` (dev) → replay: 20 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` (dev) → mutate: 8 caught, 0 survived or invalid
- Hand mutations (scratch copy, rule 4): H1 tag needs text before it (`(.*\S) ` → `(.*?) ?`) caught by REQ-ARC-002.N5 · H2 comma without a space (`, ?` → `, `) caught by REQ-ARC-002.B2 · H3 tag names not stripped caught by REQ-ARC-002.B1 · H7 no per-capability filter caught by REQ-ARC-001.S1 · optional `REQ-` and case-insensitive IDs each caught by REQ-ARC-001.N4 · H6 tag need not end the line (drop `$` from `GAP_TAG`) **survived the full suite** → finding F1
- Coverage: not available
- Pre-existing reds: T3–T7 and T10–T14 pass at the base (replay), and the planned or hand mutations of the rule each relies on (fallback M7, touched-only M6, untouched tag M4, H1, case-sensitive names) make them fail. T2, T8 and T15 (after T1) hold: N3, B2 and N6 fail under M5 or M8. All sound.
- Rule 5 (scratch repository, dev tool vs pinned tool): a change adding REQ-DUR-001 (new duration) and modifying REQ-CLI-001 (living cli with an earlier gap), with untagged gaps naming no requirement ID ("Output is not localized.", a wrapped gap, a `*` bullet ending "shared with (orchestration).", "None"), archives byte-for-byte the same with both tools: all 3 gaps in both capabilities, continuation dropped, "None" skipped, the earlier gap kept.

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-ARC-001.S1 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_S1_gap_naming_an_id_goes_to_that_capability_only | pass | yes |
| REQ-ARC-001.S2 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_S2_gap_naming_nothing_goes_to_every_touched_capability | pass | yes |
| REQ-ARC-001.B1 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_B1_repeated_ids_of_two_capabilities_give_each_one_line | pass | yes |
| REQ-ARC-001.B2 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_B2_capability_touched_only_by_a_removal_gets_its_gap | pass | yes |
| REQ-ARC-001.N1 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_N1_gap_naming_only_an_untouched_id_goes_everywhere | pass | yes |
| REQ-ARC-001.N2 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_N2_gap_naming_an_unknown_prefix_goes_everywhere | pass | yes |
| REQ-ARC-001.N3 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_N3_touched_and_untouched_ids_go_to_the_touched_capability | pass | yes |
| REQ-ARC-001.N4 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_N4_bare_and_lowercase_prefixes_do_not_route | pass | yes (note: its gap names both DUR and CLI, so a mutation routing every bare capital word still passes it; REQ-ARC-002.N4 catches that one) |
| REQ-ARC-002.S1 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_S1_tag_sends_the_gap_to_that_capability_with_the_tag_removed | pass | yes |
| REQ-ARC-002.S2 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_S2_tag_wins_over_a_named_requirement_id | pass | yes |
| REQ-ARC-002.S3 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_S3_tag_before_a_period_is_removed_and_the_period_kept | pass | yes |
| REQ-ARC-002.B1 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_B1_two_name_tag_sends_the_gap_to_both_with_the_tag_removed | pass | yes |
| REQ-ARC-002.B2 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_B2_tag_without_spaces_and_a_repeated_name_gives_each_one_line | pass | yes |
| REQ-ARC-002.B3 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_B3_tag_naming_a_capability_touched_only_by_a_removal | pass | yes |
| REQ-ARC-002.N1 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N1_tag_naming_an_untouched_capability_is_kept_as_text | pass | yes |
| REQ-ARC-002.N2 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N2_tag_list_with_one_untouched_name_is_kept_as_text | pass | yes |
| REQ-ARC-002.N3 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N3_tag_at_the_start_of_the_gap_is_not_a_tag | pass | yes |
| REQ-ARC-002.N4 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N4_capitalised_name_is_not_a_tag | pass | yes |
| REQ-ARC-002.N5 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N5_gap_that_is_only_a_tag_is_not_a_tag | pass | yes |
| REQ-ARC-002.N6 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N6_unrecognised_tag_still_routes_by_the_touched_id | pass | yes |

Findings:
- F1 (spec gap, rule 4) "Ends with" in REQ-ARC-002 (the `$` in `GAP_TAG`) has no scenario, and breaking it leaves all 459 tests green. With the mutant, "- Output (cli) is not localized" would be archived as "- Output (<change-id>)" into cli only, so the gap text is cut short. No scenario puts a tag-shaped "(name)" mid-line with text after it; N3 puts it at the start, and the `\S` before the space already blocks that. The code is correct today. → asked the operator: A) amend now: add REQ-ARC-002.N7 (gap "- Output (cli) is not localized" → duration's and cli's Known gaps each have it whole), a task and a `## Mutations` entry for the anchor; B) accept as a known gap.
- F2 (spec gap, regression) Archive now loops over touched prefixes, not capability files. So when two prefixes of a change share one capability spec, each routed gap and the change history line are written twice. Repro: `sdd.py new x --capability duration=DUR --capability duration=DU2` (accepted), REQ-DUR-001 and REQ-DU2-001, one untagged gap, then verified and archive. duration's spec gets "- Output is not localized (0001-dup)" twice and the "0001-dup — Dup …" history line twice. The pinned tool writes each once. Scope says the history line stays as it is, and no scenario covers this. → asked the operator: A) amend now: add a boundary scenario (one capability declared under two prefixes: each gap and the history line once) and a task, for example by iterating capability files and collecting their prefixes; or reject one name with two prefixes in `new` and `check`, in a separate change; B) accept as a known gap.

Verdict: GAPS — 2 findings (F1, F2 awaiting the operator; no gap tasks added)

### Round 2
- Date: 2026-10-21 · Verifier: subagent (strong)
- Tests: `python3 -m unittest tests.test_sdd` → 461 passed
- Check: `sdd.py check --stage verify` (pinned) → OK; 14 warnings, all for pre-existing tasks (T2–T8, T10–T15, T21)
- Replay: `sdd.py replay --base HEAD` (dev) → replay: 22 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` (dev) → mutate: 10 caught, 0 survived or invalid
- Hand mutations (scratch copy):
  - Caught: M9 by hand (drop `$`) by REQ-ARC-002.N7 · B3 by hand (the round-1 per-prefix loop) by REQ-ARC-001.B3, with "AssertionError: 2 != 1" · H1 by N5 · H2 by B2 · H3 by B1
  - Survived the full suite (461 OK): a loop that keeps only one prefix per capability file (`prefixes = {[…][-1]}`) → finding F3
- Coverage: not available
- New tests:
  - REQ-ARC-002.N7 asserts both Known gaps lines and no "- Output (<change-id>)" line → yes. T21 (pre-existing) is sound: it passes at the base and fails without the `$` anchor.
  - REQ-ARC-001.B3 asserts the gap exactly once, the history line exactly once, and no other folder → yes. T22's red "(after T1): 2 != 1" is reproduced by restoring the round-1 per-prefix loop. The per-file loop fixes it, and its output matches the pinned tool's (one gap line, one history line).
- Fixture: `archive_with(second=…)` defaults to `cli=CLI`, and its replacements are no-ops then, so the earlier 20 tests run unchanged.
- Rule 5 (re-run after the loop change): the same legacy probe archives byte-for-byte the same with the dev and pinned tools, with all 3 untagged gaps in both duration and cli.
- F1 closed: N7 and M9 catch the anchor. F2 closed: one capability under two prefixes gets each gap and the history line once.

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-ARC-001.S1–S2, B1–B2, N1–N4 | as in round 1 | pass | yes |
| REQ-ARC-001.B3 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_B3_one_capability_under_two_prefixes_gets_each_line_once | pass | yes (see F3) |
| REQ-ARC-002.S1–S3, B1–B3, N1–N6 | as in round 1 | pass | yes |
| REQ-ARC-002.N7 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_002_N7_tag_shaped_name_mid_line_is_not_a_tag | pass | yes |

Findings:
- F3 (spec gap on REQ-ARC-001.B3, second round on this scenario) The per-file loop unions every prefix of the file, but B3's gap names no ID, so it goes to every prefix and can't tell a union from a single prefix.
  - Mutant: keeping only the file's last prefix (DU2) leaves all 461 tests green.
  - Effect: "- REQ-DUR-001 is slow", in a change declaring duration=DUR and duration=DU2, would land nowhere.
  - Today's code writes it once into duration (checked by hand).
  - The "don't loop forever" rule applies, so no task was added and the pattern is reported to the operator.
  - Options: A) amend now: add a scenario with that ID-named gap, a task and a mutation entry; B) accept it as a known gap: an unusual input (one capability under two prefixes) whose code is correct today.

Verdict: GAPS — 1 finding (F3 awaiting the operator; F1, F2 closed; no gap tasks added)

### Round 3
- Date: 2026-10-21 · Verifier: subagent (strong)
- Production code: `sdd.py` is byte-identical to round 2 (compared with a saved copy)
- Tests: `python3 -m unittest tests.test_sdd` → 462 passed
- Check: `sdd.py check --stage verify` (pinned) → OK; 15 warnings, all for pre-existing tasks (T2–T8, T10–T15, T21, T23)
- Replay: `sdd.py replay --base HEAD` (dev) → replay: 23 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` (dev) → mutate: 11 caught, 0 survived or invalid
- Hand mutations (scratch copy):
  - Caught: M11 by hand (keep the file's last prefix, `[-1]`) by REQ-ARC-001.B4, with "AssertionError: 0 != 1"; the full suite fails too
  - Survived the full suite (462 OK): its mirror, keeping the file's first prefix (`[0]`) → finding F4
- Coverage: not available
- New test: REQ-ARC-001.B4 sets up the DUR + DU2 change with the gap "- REQ-DUR-001 is slow", archives, and asserts the line exactly once and no folder but duration → yes. T23 (pre-existing) is sound: it passes at the base (replay), where every gap goes to every file, and fails under M11.
- F3 closed: dropping DUR, as M11 does, is now caught.

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-ARC-001.S1–S2, B1–B3, N1–N4 | as in rounds 1–2 | pass | yes |
| REQ-ARC-001.B4 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_B4_gap_naming_one_of_two_prefixes_of_a_capability_lands_once | pass | yes (see F4) |
| REQ-ARC-002.S1–S3, B1–B3, N1–N7 | as in rounds 1–2 | pass | yes |

Findings:
- F4 (spec gap, third round on the two-prefix scenarios B3/B4; reported as a pattern, no task added) B4 pins only that DUR is kept.
  - Mutant: keeping only the first prefix (DUR) leaves all 462 tests green.
  - Effect: a gap "- REQ-DU2-001 is slow" in the same change would land nowhere.
  - Today's code writes it once into duration (checked by hand).
  - Pattern: each round's scenario pins one example of the rule "a file is reached through all of its prefixes", and the next mutant drops a different prefix.
  - The operator's decision covers the whole rule:
    - A) amend once more with a scenario that names both prefixes in separate gaps ("- REQ-DUR-001 …" and "- REQ-DU2-001 …", each exactly once), which pins the union from both ends;
    - B) accept it as a known gap: one capability under two prefixes is an unusual input, and the code is correct today.
    - The operator could also forbid one name with two prefixes in `new` and `check`, in a separate change.

Verdict: GAPS — 1 finding (F4 awaiting the operator, a pattern on the two-prefix scenarios; F1–F3 closed; no gap tasks added)

### Round 4
- Date: 2026-10-22 · Verifier: subagent (strong)
- Production code: `sdd.py` is byte-identical to rounds 2–3 (compared with a saved copy)
- Tests: `python3 -m unittest tests.test_sdd` → 463 passed
- Check: `sdd.py check --stage verify` (pinned) → OK; 16 warnings, all for pre-existing tasks (T2–T8, T10–T15, T21, T23, T24)
- Replay: `sdd.py replay --base HEAD` (dev) → replay: 24 confirmed, 0 mismatch, 0 skipped
- Mutate: `sdd.py mutate` (dev) → mutate: 12 caught, 0 survived or invalid
- Hand mutations (scratch copy):
  - M11 by hand (keep the last prefix): REQ-ARC-001.B5 fails with "AssertionError: 0 != 1", and the full suite has 2 failures (B4, B5)
  - M12 by hand (keep the first prefix): B5 fails with "AssertionError: 0 != 1", and the full suite has 1 failure (B5)
  - Extra: requiring all of a file's prefixes (`prefixes & to` → `prefixes <= to`) is caught by the class (2 failures)
- Coverage: not available
- New test: REQ-ARC-001.B5 sets up the DUR + DU2 change with both gaps, archives, and asserts each line exactly once in duration and no folder but duration → yes. T24 (pre-existing) is sound: it passes at the base (replay) and fails under both M11 and M12.
- F4 closed: dropping either prefix of a two-prefix capability is now caught.
- No further gap seen on the two-prefix scenarios, or elsewhere.

| Scenario | Test | Result | Then fully asserted |
| --- | --- | --- | --- |
| REQ-ARC-001.S1–S2, B1–B4, N1–N4 | as in rounds 1–3 | pass | yes |
| REQ-ARC-001.B5 | tests/test_sdd.py::ArchiveGapRoutingTests.test_REQ_ARC_001_B5_gaps_naming_each_of_two_prefixes_land_once_each | pass | yes |
| REQ-ARC-002.S1–S3, B1–B3, N1–N7 | as in rounds 1–2 | pass | yes |

Findings: none open (F1–F4 closed by amendments A1–A3)

Verdict: PASS

## Open questions
- Q1 Is a tag followed by a period, "- Output is not localized (cli).", a tag? → yes: the tag is dropped and the period kept (operator, 2026-10-21)
- Q2 What does archive do with a tag on a wrapped gap's continuation line? → a gap is one line: the tag must be on the bullet line, documented, plus a known gap (operator, 2026-10-21)

## Clarifications
<!-- Spec Critic: one round per review, started with `sdd.py round`. Format:
method/format.md. Required before the gate at production and above. -->

### Round 1 — 2026-10-21 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-ARC-001 | issues | F1, F2, F3, F4 |
| REQ-ARC-002 | issues | F5, F6, F7, F8 |

- F1 [ambiguity] REQ-ARC-001: "whose requirement ID prefix the gap names" and "names no such prefix" don't say what counts. Is it only a full ID token (`REQ-<PREFIX>-<3+ digits>`, as in requirement headings, case-sensitive), or also a bare "DUR", "REQ-DUR", "DUR-001" or "req-dur-001"? "No such prefix" can also be read as "no requirement ID at all", which would send N1's REQ-APR-001 gap nowhere. Fix: define the token in the statement, say "no touched capability's prefix", and add a row showing that a bare "DUR" or a lowercase ID does not route. → fixed: the statement defines the ID token (capitals, optional scenario suffix) and says "no touched capability's prefix"; N4 shows that bare and lowercase forms don't route
- F2 [ambiguity] REQ-ARC-001: "touched capability" (holds at least one of the change's requirements, removed ones included) is defined only in Scope. Scope is not carried into the living archive spec, so after archive the requirement uses an undefined term. Fix: put the definition in the statement. → fixed: the definition of a touched capability is in the REQ-ARC-001 statement
- F3 [coverage] REQ-ARC-001: no scenario covers a capability touched only by a `[REMOVED]` requirement. Scope and the design notes rely on removals counting as touching, for both ID routing and tags, but no test proves it (e.g. the change removes REQ-APR-001 and the gap "- REQ-APR-001 is gone" goes to approvals only). → fixed: REQ-ARC-001.B2 and REQ-ARC-002.B3 cover a capability touched only by a removal
- F4 [untestable] REQ-ARC-001: N2's Then says "each have the line" without giving the exact text. Write "- REQ-ZZZ-001 is out of reach (<change-id>)" so the test asserts concrete data. → fixed: N2's Then gives the exact line
- F5 [ambiguity] REQ-ARC-002: the tag syntax is not pinned down. Open cases: no space after the comma "(duration,cli)", extra spaces "( cli )", a duplicate "(cli, cli)", an empty "()", uppercase "(CLI)", trailing whitespace, a gap that is only "(cli)", and above all a period after the tag, "… (cli).", which fits the house style (every carried gap and the 0003 gap "(REQ-ANL-006)." end with a period). Fix: pin each case in the statement or format.md, add one boundary row for spacing, and see Q1 for the period. → fixed: the statement pins the tag (text before it, comma with at most one space, optional period); S3 (period, Q1), B2 (no spaces, duplicate), N4 (capitals) and N5 (tag only) added; "( cli )" and "()" are a known gap
- F6 [ambiguity] REQ-ARC-002: "ends with a capability tag" is undefined for a gap wrapped over several lines. `cmd_archive` keeps only the bullet lines (`^\s*[-*]\s+\S`), so a tag on a continuation line is never seen and the gap goes to every touched capability without its tag. See Q2. → Q2
- F7 [contradiction] REQ-ARC-002: Known gaps bullet 1 says a gap with an unrecognised tag goes "as an untagged gap, to every touched capability". Under REQ-ARC-001, an untagged gap that names a touched ID goes only to that capability: "- REQ-DUR-001 is slow (approvals)" goes to duration only. Fix: say "routed as an untagged gap (REQ-ARC-001)" and add an N row combining an unrecognised tag with a touched ID. → fixed: known gap 1 says "routed as an untagged gap (REQ-ARC-001)"; N6 added
- F8 [ambiguity] REQ-ARC-002: the rule 5 line in Scope says a gap written by an earlier version "has no tag". That isn't guaranteed: an in-flight gap whose prose happens to end with a touched capability's name in parentheses, e.g. "… shared with (orchestration)", is now read as a tag, stripped and narrowed. Fix: say so in the backward-compatibility line or in Known gaps. → fixed: the Scope backward-compatibility line says such a gap is now read as a tag
- Q1 A gap ending in a tag followed by a period, "- Output is not localized (cli).": is that a tag? A) no: ")" must be the last character, and the gap is carried as untagged with its text B) yes: archive drops the tag and keeps the period, giving "- Output is not localized. (<change-id>)" — recommended: B (house style ends gaps with a period, and a silent fallback to every capability is the problem this change fixes)
  - Answer: B — yes: drop the tag, keep the period (operator, 2026-10-21)
- Q2 A gap wrapped over several lines, with the tag on a continuation line: what does archive do? A) a gap is one line: document in format.md that the tag must be on the bullet line, and add a Known gap B) archive joins indented continuation lines into the gap before routing (this also changes today's behavior, which drops continuation text) — recommended: A (B fixes a separate existing defect and belongs in its own change)
  - Answer: A — a gap is one line; document it and add a known gap (operator, 2026-10-21)

<!-- Findings: - F1 [type] REQ-…: <problem> → fixed: … | accepted: … | rejected: <reason> | Q1
Questions (at most 5): - Q1 <question> A) … B) … — recommended: …
  - Answer: pending -->

## Amendments
<!-- Spec changes after approval, one line each, then `sdd.py approve amend`:
- A1 2026-10-07: <reason> → <what changed> -->
- A1 2026-10-21: verification round 1 (GAPS) F1, F2; operator chose A for both → REQ-ARC-002.N7 (a tag-shaped "(cli)" mid-line is not a tag) and REQ-ARC-001.B3 (one capability spec reached through two prefixes gets each gap and the history line once) added; tasks T21, T22 and mutation M9 added; design notes: the gap loop iterates capability files
- A2 2026-10-21: verification round 2 (GAPS) F3; operator chose A → REQ-ARC-001.B4 added (one capability spec under two prefixes gets a gap naming REQ-DUR-001 exactly once); task T23 and mutation M11 (keep only a file's last prefix) added; design notes: routed through any of its prefixes
- A3 2026-10-21: verification round 3 (GAPS) F4, the two-prefix pattern; operator chose A once more → REQ-ARC-001.B5 added (one capability spec under two prefixes gets gaps naming REQ-DUR-001 and REQ-DU2-001 exactly once each); task T24 and mutation M12 (keep only a file's first prefix, the mirror of M11) added; design notes cite B5

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
| plan | 2026-10-21 | Operator in Claude Code chat, 2026-10-21: "/sdd approve" (spec and plan of 0004-archive-gap-routing as presented at the plan gate, after Critic round 1 and answers Q1=B, Q2=A) |
| amend | 2026-10-21 | Operator in Claude Code chat, 2026-10-21: "approve" (amendment A1 of 0004: REQ-ARC-002.N7 and REQ-ARC-001.B3, tasks T21-T22, mutation M9), after deciding "Amend now for F1 and F2" |
| amend | 2026-10-21 | Operator in Claude Code chat, 2026-10-21: "Approve amendment A2 for 0004. Record it, implement T23, then re-verify." (A2: REQ-ARC-001.B4, task T23, mutation M11) |
| amend | 2026-10-22 | Operator in Claude Code chat, 2026-10-22: "Approve amendment A3 for 0004. Record it, implement T24, then run the final re-verify." (A3: REQ-ARC-001.B5, task T24, mutation M12) |
