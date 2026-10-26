---
capability: archive
prefix: ARC
---

# Capability: archive

<!-- Living spec: the current, approved behavior of this capability.
Maintained by `sdd.py archive`. Do not edit by hand. -->

## Known gaps
<!-- Behavior deliberately not handled yet, carried from archived changes. -->
- A tag naming a capability the change doesn't touch, or a misspelled one, is not reported: the gap keeps its text and is routed as an untagged gap (REQ-ARC-001). (0004-archive-gap-routing)
- A requirement ID routes a gap by its prefix alone: an ID that doesn't exist in that capability still sends the gap there. (0004-archive-gap-routing)
- `sdd.py check` doesn't look at tags or requirement IDs in Known gaps, so a misrouted gap is seen only in the capability specs archive writes. (0004-archive-gap-routing)
- A gap is its bullet line (Q2): a tag on a continuation line isn't seen, and continuation lines are dropped, as before this change. (0004-archive-gap-routing)
- Spaces inside the parentheses, as in "( cli )", and an empty "()" are not tags; no scenario of their own shows it. (0004-archive-gap-routing)
- The gaps 0002 and 0003 already carried into every capability they touched stay where they are. (0004-archive-gap-routing)

## Change history
- 0004-archive-gap-routing — Archive carries each known gap only to the capability it concerns (2026-10-22): added REQ-ARC-001, added REQ-ARC-002

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
