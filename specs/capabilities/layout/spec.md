---
capability: layout
prefix: LAY
---

# Capability: layout

<!-- Living spec: the current, approved behavior of this capability.
Maintained by `sdd.py archive`. Do not edit by hand. -->

## Known gaps
<!-- Behavior deliberately not handled yet, carried from archived changes. -->
- On main after a merge, the branch folders sit side by side and main's own folder (`.sdd/main/`) does not see them, until `sdd integrate` exists. (0011-per-branch-specs)
- Each branch folder numbers its changes from 0001, so a change ID is unique only within its branch. (0011-per-branch-specs)
- Renaming a branch disconnects its folder; the operator renames the folder or sets SDD_SPECS. (0011-per-branch-specs)
- Branches `feat/a-b` and `feat-a/b` share `.sdd/feat-a-b/`, as do `Feat/A` and `feat/a` on a case-insensitive file system. (0011-per-branch-specs)
- A never-approved `specs/constitution.md` is copied with its own level; its approval stays pending on the branch. (0011-per-branch-specs)
- Each folder holds a copy of the one constitution; editing a copy doesn't change the others until `sdd integrate`. (0011-per-branch-specs)
- A branch cut from a main with no constitution can't see one set on another branch; the `internal` floor is the only guard. (0011-per-branch-specs)
- Tests kept under a `.sdd/` folder are no longer found by check (evidence). (0011-per-branch-specs)
- With the marker and `SDD_SPECS` both set, `init` accepts `prototype` for the `SDD_SPECS` folder: the `internal` floor covers branch folders only. (0011-per-branch-specs)
- No test proves that `specs/` is skipped while another folder is in use (evidence). (0011-per-branch-specs)

## Change history
- 0011-per-branch-specs — Per-branch SDD folders (2026-11-18): added REQ-LAY-001, added REQ-LAY-002, added REQ-LAY-006, added REQ-LAY-003, added REQ-LAY-004, added REQ-LAY-005

## Requirements

### REQ-LAY-001 Per-branch mode keeps the specs in the branch's folder
While the marker exists and `SDD_SPECS` is not set or empty, sdd.py shall read
and write the project's specs in `.sdd/<branch>/` under the project root, where
`<branch>` is the current git branch with each `/` replaced by `-`, and never
in `specs/`.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | the marker, branch `feat/a` initialized in `.sdd/feat-a/` | `new x --title X --capability x=XX` | `.sdd/feat-a/changes/0001-x/spec.md` exists · `.sdd/feat-a/.sdd/active` holds `0001-x` · the output holds "created .sdd/feat-a/changes/0001-x/spec.md" · no `specs/` folder |
| S2 | happy | the marker, `.sdd/feat-a/` with change `0001-x`, `.sdd/feat-b/` with change `0001-y`, branch `feat/b` checked out | `status` | the output lists `0001-y` · it does not list `0001-x` |
| B1 | boundary | the marker, branch `main` initialized in `.sdd/main/` | `status` | exit 0 · the output names the project level from `.sdd/main/constitution.md` |
| B2 | boundary | the marker, branch `feat/a/b` | `init --assurance internal` | `.sdd/feat-a-b/constitution.md` exists · no `specs/` folder |
| B3 | boundary | the marker, branch `feat/a` initialized, `SDD_SPECS` set to an empty string | `status` | exit 0 · the output is the one `.sdd/feat-a/` gives |
| B4 | boundary | the marker, branch `feat/a` initialized, run from the subfolder `pkg/` without `--root` | `new x --title X --capability x=XX` | `.sdd/feat-a/changes/0001-x/spec.md` exists in the project root · no `pkg/.sdd/` |
| N1 | state | the marker, a detached HEAD | `init --assurance internal` | exit 1 · error "per-branch mode needs a git branch: check out a branch or set SDD_SPECS" · `.sdd/` holds only the marker · no `specs/` |
| N2 | dependency | the marker, a folder that is not a git repository | `init --assurance internal` | exit 1 · error "per-branch mode needs a git repository (git must be installed and the project under version control)" · `.sdd/` holds only the marker · no `specs/` |
| N3 | dependency | the marker, git not found on the PATH | `init --assurance internal` | exit 1 · the error of N2 · `.sdd/` holds only the marker · no `specs/` |
| N4 | state | the marker, branch `feat/c` with no `.sdd/feat-c/`, an initialized `specs/` | `status` | exit 1 · error "this repository is not initialized: run `sdd init` first" · `specs/` unchanged |
| N5 | validation | no marker, an initialized `specs/`, an empty `.sdd/` folder | `status` | exit 0 · the output is the one `specs/` gives |

- N/A access: sdd.py is a local tool run by the operator; it has no users or roles

### REQ-LAY-002 init --per-branch turns the mode on
When the operator runs `init --assurance <level> --per-branch`, sdd.py shall
create the marker as an empty file, initialize `.sdd/<branch>/`, print "initialized
.sdd/<branch>/ (assurance: <level>)" with the real folder, and write each
`specs/` path of the AGENTS.md section as the literal text `.sdd/<branch>/`,
with one line saying that `<branch>` is the current git branch with each `/`
replaced by `-` and that `sdd.py where` prints the folder.
Every `init` while the marker exists writes the section the same way. With no
constitution to adopt (REQ-LAY-006), the level must be `internal` or higher. A
refused `init` writes nothing.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | a git repository on branch `feat/a`, no marker, no `specs/` | `init --assurance production --per-branch` | `.sdd/.per-branch` exists and is empty · `.sdd/feat-a/constitution.md` exists · the output holds "initialized .sdd/feat-a/ (assurance: production)" and "created .sdd/feat-a/constitution.md (approval pending: sdd approve)" · AGENTS.md holds "`.sdd/<branch>/changes/`" and "sdd.py where" and not "`specs/changes/`" · no `specs/` folder |
| S2 | happy | the marker, branch `feat/b` with no `.sdd/feat-b/`, an initialized `.sdd/feat-a/` | `init --assurance internal` | `.sdd/feat-b/constitution.md` exists · the output holds "initialized .sdd/feat-b/ (assurance: internal)" · AGENTS.md holds "`.sdd/<branch>/changes/`" · `.sdd/feat-a/` unchanged |
| B2 | boundary | the marker, branch `feat/a` initialized, AGENTS.md without an SDD section | `init --assurance internal --per-branch --force` | exit 0 · AGENTS.md holds "`.sdd/<branch>/changes/`" · `.sdd/feat-a/constitution.md` unchanged |
| B3 | boundary | a git repository with no commit yet, on the unborn branch `main` | `init --assurance internal --per-branch` | `.sdd/main/constitution.md` exists · no `specs/` folder |
| N1 | state | the marker, branch `feat/a` initialized | `init --assurance internal --per-branch` | exit 1 · error "already initialized (.sdd/feat-a/constitution.md exists); use --force to refresh the folders and AGENTS.md/CLAUDE.md only" · no file changed |
| N2 | state | no marker, `.sdd/feat-a/constitution.md` exists, branch `feat/a` | `init --assurance internal --per-branch` | exit 1 · the error of N1 · no marker · no file changed |
| N3 | state | a detached HEAD, no marker | `init --assurance internal --per-branch` | exit 1 · the error of REQ-LAY-001.N1 · no marker · no file written |
| N4 | dependency | a folder that is not a git repository, no marker | `init --assurance internal --per-branch` | exit 1 · the error of REQ-LAY-001.N2 · no marker · no file written |
| N6 | validation | branch `feat/a`, no marker, no `specs/` | `init --assurance prototype --per-branch` | exit 1 · error "per-branch mode is for several developers: the assurance level must be internal or higher" · no marker · no `.sdd/feat-a/` |
| N5 | validation | branch `feat/a`, no marker, `SDD_SPECS=records` | `init --assurance internal --per-branch` | exit 1 · error "init --per-branch can't be used while SDD_SPECS is set" · no marker · no `records/` |

- N/A access: sdd.py is a local tool run by the operator; it has no users or roles

### REQ-LAY-003 SDD_SPECS names the specs folder
When `SDD_SPECS` is set to a non-empty relative path, sdd.py shall use that
folder, relative to the project root, as the specs folder, with or without the marker.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | the marker, branch `feat/a`, an initialized `specs/`, `SDD_SPECS=specs` | `status` | exit 0 · the output is the one `specs/` gives |
| S2 | happy | no marker, `SDD_SPECS=records`, an initialized `records/` | `new x --title X --capability x=XX` | `records/changes/0001-x/spec.md` exists · no `specs/` folder |
| S3 | happy | no marker, `SDD_SPECS=records`, no `records/` | `init --assurance internal` | `records/constitution.md` exists · the output holds "initialized records/ (assurance: internal)" and "created records/constitution.md (approval pending: sdd approve)" · AGENTS.md holds "`specs/changes/`" · no `specs/` folder |
| B3 | boundary | the marker, branch `feat/a`, `SDD_SPECS=records`, no `records/` | `init --assurance internal` | `records/constitution.md` exists · the output holds "initialized records/ (assurance: internal)" · AGENTS.md holds "`.sdd/<branch>/changes/`" · no `.sdd/feat-a/` |
| B1 | boundary | an initialized `specs/`, `SDD_SPECS` set to an empty string | `status` | exit 0 · the output is the one `specs/` gives |
| B2 | boundary | the marker, a detached HEAD, `SDD_SPECS=records`, an initialized `records/` | `status` | exit 0 · the output is the one `records/` gives |
| N1 | validation | `SDD_SPECS` set to the absolute path of `records` inside the project root | `init --assurance internal` | exit 1 · error "SDD_SPECS must name a folder inside the repository" · no file written |
| N2 | validation | `SDD_SPECS=../other` | `init --assurance internal` | exit 1 · the error of N1 · no file written |
| N3 | validation | `SDD_SPECS=.` | `init --assurance internal` | exit 1 · the error of N1 · no file written |
| N4 | validation | `SDD_SPECS=notes.txt`, an existing file `notes.txt` | `init --assurance internal` | exit 1 · the error of N1 · `notes.txt` unchanged |
| N5 | validation | `SDD_SPECS=link`, `link` a symlink to a folder outside the project root | `init --assurance internal` | exit 1 · the error of N1 · nothing written through the link |

- N/A state: the variable is read once per command and keeps no state
- N/A dependency: SDD_SPECS needs no git and calls no other component
- N/A access: sdd.py is a local tool run by the operator; it has no users or roles

### REQ-LAY-004 where prints the specs folder in use
When the operator runs `where`, sdd.py shall print the specs folder relative
to the project root, normalized and ending in `/`, then the reason in
parentheses, whether or not the folder is initialized.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | no marker, no `SDD_SPECS` | `where` | exit 0 · output "specs/ (default)" |
| S2 | happy | the marker, branch `feat/a`, no `.sdd/feat-a/` | `where` | exit 0 · output ".sdd/feat-a/ (per-branch: feat/a)" |
| S3 | happy | the marker, `SDD_SPECS=specs` | `where` | exit 0 · output "specs/ (SDD_SPECS)" |
| B1 | boundary | `SDD_SPECS=./records//` | `where` | exit 0 · output "records/ (SDD_SPECS)" |
| N1 | state | the marker, a detached HEAD | `where` | exit 1 · the error of REQ-LAY-001.N1 · no output on stdout |
| N2 | dependency | the marker, a folder that is not a git repository | `where` | exit 1 · the error of REQ-LAY-001.N2 · no output on stdout |
| N3 | validation | `SDD_SPECS=../other` | `where` | exit 1 · the error of REQ-LAY-003.N1 · no output on stdout |

- N/A access: sdd.py is a local tool run by the operator; it has no users or roles

### REQ-LAY-005 SDD records are never test evidence
When `check --stage verify` searches the test files for a scenario's test,
sdd.py shall skip every file under the project root's `specs/` and `.sdd/`,
and under the `SDD_SPECS` folder when it is set.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | the marker, branch `tests`, a change in `.sdd/tests/` whose tasks name `test_REQ_DUR_001_S1_parses`, no other file naming it | `check --stage verify` | exit 1 · the output says REQ-DUR-001.S1 has no test |
| S2 | happy | the marker, branch `feat/a` with a change planning REQ-DUR-001.S1, `.sdd/testing/notes.md` naming `test_REQ_DUR_001_S1_parses` | `check --stage verify` | exit 1 · the output says REQ-DUR-001.S1 has no test |
| S3 | happy | `SDD_SPECS=tests/records`, a change there whose tasks name `test_REQ_DUR_001_S1_parses`, no other file naming it | `check --stage verify` | exit 1 · the output says REQ-DUR-001.S1 has no test |
| B2 | boundary | no marker, an initialized `specs/` with a change planning REQ-DUR-001.S1, `.sdd/tests/old.md` naming `test_REQ_DUR_001_S1_parses` | `check --stage verify` | exit 1 · the output says REQ-DUR-001.S1 has no test |
| B1 | boundary | the change of S1, plus `tests/test_dur.py` defining `test_REQ_DUR_001_S1_parses` | `check --stage verify` | the output does not say REQ-DUR-001.S1 has no test |

- N/A validation: the search takes no input beyond the files in the repository
- N/A state: the search keeps no state between commands
- N/A dependency: the git lookup is covered by REQ-LAY-001.N2
- N/A access: sdd.py is a local tool run by the operator; it has no users or roles

### REQ-LAY-006 A new branch folder starts from the project's constitution
When `init` writes a branch folder's constitution while the project root's
`specs/constitution.md` exists, sdd.py shall copy that file unchanged, with its
approvals, as the folder's constitution (a branch folder or the `SDD_SPECS`
folder), take its level in force as the folder's level, and print "copied
specs/constitution.md (assurance: <level>); specs/ is not read on this branch".

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | `specs/` approved at `production`, no marker, branch `feat/a` | `init --assurance production --per-branch` | `.sdd/feat-a/constitution.md` equals `specs/constitution.md` byte for byte · the output holds "copied specs/constitution.md (assurance: production); specs/ is not read on this branch" and no "approval pending" line · `specs/` unchanged |
| S2 | happy | `specs/` approved at `production`, the marker, branch `feat/b` with no `.sdd/feat-b/` | `init --assurance production` | `.sdd/feat-b/constitution.md` equals `specs/constitution.md` · `status` on `feat/b` shows no pending constitution approval |
| B1 | boundary | `specs/` approved at `production`, no marker, branch `feat/a` | `init --assurance critical --per-branch` | the copy equals `specs/constitution.md` · the output holds "initialized .sdd/feat-a/ (assurance: production)" and "the copied constitution keeps production: edit it and run sdd approve constitution to raise it" |
| N1 | state | `specs/` approved at `production`, no marker, branch `feat/a` | `init --assurance internal --per-branch` | exit 1 · error "specs/constitution.md is at production: a branch can't start lower" · no marker · no `.sdd/feat-a/` |
| N2 | state | `specs/` approved at `production`, the marker, branch `feat/b` with no `.sdd/feat-b/` | `init --assurance internal` | exit 1 · the error of N1 · no `.sdd/feat-b/` |
| N3 | validation | `specs/constitution.md` with `assurance: draft`, no marker, branch `feat/a` | `init --assurance internal --per-branch` | exit 1 · error "specs/constitution.md: the assurance level 'draft' is not one of: prototype, internal, production, critical" · no marker · no `.sdd/feat-a/` |
| B2 | boundary | `specs/constitution.md` at `internal`, never approved, no marker, branch `feat/a` | `init --assurance internal --per-branch` | the copy equals `specs/constitution.md` · the output holds "initialized .sdd/feat-a/ (assurance: internal)" |
| S3 | happy | `specs/` approved at `production`, no marker, `SDD_SPECS=records` | `init --assurance production` | `records/constitution.md` equals `specs/constitution.md` · the output holds "copied specs/constitution.md (assurance: production)" |

- N/A dependency: the copy reads one local file that `init` has just found to exist
- N/A access: sdd.py is a local tool run by the operator; it has no users or roles
