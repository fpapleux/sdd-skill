---
id: 0011-per-branch-specs
title: Per-branch SDD folders
type: feature
size: mini
assurance: production
status: planned
capabilities: layout=LAY
created: 2026-11-18
spec_hash: 2a99c9d219a7
---

# 0011-per-branch-specs — Per-branch SDD folders

## Intent
Two branches of one repository both run SDD. Both write `specs/`, so both
number their first change 0001 and their constitution and active pointer
conflict at merge. The product has one constitution. As an interim, each branch keeps its SDD records in its own
folder; bringing them together on main is a later change.

## Scope
- In: a per-branch mode (marker `.sdd/.per-branch`, specs in `.sdd/<branch>/`),
  `init --per-branch`, the `SDD_SPECS` variable, and `sdd.py where`; `init`
  and `new` print the folder in use.
- Changes existing behavior: check's test-file search skipped `specs/` only → it
  also skips the root's `.sdd/` and the `SDD_SPECS` folder, with or without the marker.
- Out: `sdd integrate`, merging the branch folders on main (a later change);
  change numbers unique across branches; other messages that name `specs/`.
- Otherwise, without the marker and `SDD_SPECS`, behavior is unchanged.

## Requirements
The **project root** is the `--root` folder; else the nearest folder, from the
current one upward, that holds `.sdd/.per-branch`, `specs/constitution.md` or,
when `SDD_SPECS` is set, `<SDD_SPECS>/constitution.md`; else the current folder.
The marker is `.sdd/.per-branch` in the project root.

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

## Known gaps
- On main after a merge, the branch folders sit side by side and main's own folder (`.sdd/main/`) does not see them, until `sdd integrate` exists.
- Each branch folder numbers its changes from 0001, so a change ID is unique only within its branch.
- Renaming a branch disconnects its folder; the operator renames the folder or sets SDD_SPECS.
- Branches `feat/a-b` and `feat-a/b` share `.sdd/feat-a-b/`, as do `Feat/A` and `feat/a` on a case-insensitive file system.
- A never-approved `specs/constitution.md` is copied with its own level; its approval stays pending on the branch.
- Each folder holds a copy of the one constitution; editing a copy doesn't change the others until `sdd integrate`.
- A branch cut from a main with no constitution can't see one set on another branch; the `internal` floor is the only guard.
- Tests kept under a `.sdd/` folder are no longer found by check (evidence).

## Design notes
- Files: `skill/sdd/scripts/sdd.py`, `tests/test_sdd.py` (new `LayoutTests`).
  Reviewed, not tested (rule 1): `method/format.md` Test naming, one line in
  `SKILL.md` ("`specs/` means the folder `SDD where` prints"), `method/overview.md`
  Files, README, release notes, version 0.21.0.
- `specs_folder(root) -> (Path, reason)`: a non-empty `SDD_SPECS` first (refused
  when absolute, or unless it resolves, symlinks followed, to a folder strictly
  inside the root); then the marker, with `git symbolic-ref --short -q HEAD` in
  the root (OSError or no repository → repository error; no symbolic ref →
  branch error); else `specs`. `Project.__init__` takes `self.specs` from it.
- `Project.locate` walks up for `.sdd/.per-branch`, a `SDD_SPECS` constitution or
  `specs/constitution.md`; `main` calls it inside its `try`, so folder errors
  exit 1 before any command runs.
- `init`: resolve the folder, refuse (already initialized, lower level), copy
  `specs/constitution.md` (`shutil.copyfile`), then write the marker. The
  AGENTS.md block swaps `specs/` for `.sdd/<branch>/` while the marker exists.
- `where` prints `<folder>/ (<reason>)` on stdout, without `require_init`.
- `is_records_path(project, rel)` replaces the literal `"specs"` test in
  `project_text_files` and `overlay_tests` (overlay's use isn't observable, so
  it's reviewed).
- Tests: real git repositories in the `Repo` temp folder, `mock.patch.dict(os.environ)`.
- Test command: `python3 -m unittest tests.test_sdd`
- Test one: `python3 -m unittest tests.test_sdd.{name}`
- Test component: `python3 -m unittest tests.test_sdd -k REQ_{prefix}_`

## Tasks
- [ ] T1 REQ-LAY-001.S1 new writes into the branch folder
  - tier: strong
  - test:
  - red:
  - green:
- [ ] T2 REQ-LAY-001.N1 a detached HEAD is refused before any write
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T3 REQ-LAY-001.N2 outside git is refused
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T4 REQ-LAY-001.N3 git not on the PATH is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T5 REQ-LAY-001.N4 a missing branch folder is not initialized, specs/ ignored
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T6 REQ-LAY-001.N5 without the marker, specs/ as before
  - tier: light
  - test:
  - red:
  - green:
- [ ] T7 REQ-LAY-001.S2 another branch's folder is not seen
  - tier: light
  - test:
  - red:
  - green:
- [ ] T8 REQ-LAY-001.B1 REQ-LAY-001.B2 branch names without and with slashes
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T9 REQ-LAY-001.B3 an empty SDD_SPECS keeps the branch folder
  - tier: light
  - test:
  - red:
  - green:
- [ ] T10 REQ-LAY-001.B4 run from a subfolder finds the project root
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T11 REQ-LAY-002.S1 init --per-branch writes the marker, the folder and AGENTS.md
  - tier: strong
  - test:
  - red:
  - green:
- [ ] T12 REQ-LAY-002.N1 init on an initialized branch folder is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T13 REQ-LAY-002.N2 init --per-branch on an existing branch folder writes no marker
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T14 REQ-LAY-002.N3 init --per-branch on a detached HEAD writes nothing
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T15 REQ-LAY-002.N4 init --per-branch outside git writes nothing
  - tier: light
  - test:
  - red:
  - green:
- [ ] T16 REQ-LAY-002.N6 per-branch init below internal is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T17 REQ-LAY-002.N5 init --per-branch with SDD_SPECS set is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T18 REQ-LAY-002.S2 init with the marker on a new branch
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T19 REQ-LAY-002.B3 init on an unborn branch
  - tier: light
  - test:
  - red:
  - green:
- [ ] T20 REQ-LAY-002.B2 init --per-branch --force rewrites AGENTS.md only
  - tier: light
  - test:
  - red:
  - green:
- [ ] T21 REQ-LAY-006.S1 init --per-branch copies the approved constitution
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T22 REQ-LAY-006.N1 a lower level than the approved one is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T23 REQ-LAY-006.N2 init with the marker refuses a lower level too
  - tier: light
  - test:
  - red:
  - green:
- [ ] T24 REQ-LAY-006.N3 an invalid level in specs/constitution.md is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T25 REQ-LAY-006.S2 init with the marker copies it too
  - tier: light
  - test:
  - red:
  - green:
- [ ] T26 REQ-LAY-006.B1 a higher level keeps the copied one, with a note
  - tier: light
  - test:
  - red:
  - green:
- [ ] T27 REQ-LAY-006.B2 a never-approved constitution is adopted at its level
  - tier: light
  - test:
  - red:
  - green:
- [ ] T28 REQ-LAY-006.S3 an SDD_SPECS folder adopts it too
  - tier: light
  - test:
  - red:
  - green:
- [ ] T29 REQ-LAY-003.S1 REQ-LAY-003.S2 SDD_SPECS names the folder
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T30 REQ-LAY-003.S3 init with SDD_SPECS initializes that folder
  - tier: light
  - test:
  - red:
  - green:
- [ ] T31 REQ-LAY-003.B3 init with the marker and SDD_SPECS
  - tier: light
  - test:
  - red:
  - green:
- [ ] T32 REQ-LAY-003.N1 an absolute SDD_SPECS is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T33 REQ-LAY-003.N2 an SDD_SPECS leading outside is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T34 REQ-LAY-003.N3 SDD_SPECS naming the root is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T35 REQ-LAY-003.N4 SDD_SPECS naming a file is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T36 REQ-LAY-003.N5 SDD_SPECS through a symlink outside is refused
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T37 REQ-LAY-003.B1 an empty SDD_SPECS counts as unset
  - tier: light
  - test:
  - red:
  - green:
- [ ] T38 REQ-LAY-003.B2 SDD_SPECS works on a detached HEAD
  - tier: light
  - test:
  - red:
  - green:
- [ ] T39 REQ-LAY-004.S1 REQ-LAY-004.S2 REQ-LAY-004.S3 where prints the folder and the reason
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T40 REQ-LAY-004.N1 where on a detached HEAD is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T41 REQ-LAY-004.N2 where outside git is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T42 REQ-LAY-004.N3 where with an invalid SDD_SPECS is refused
  - tier: light
  - test:
  - red:
  - green:
- [ ] T43 REQ-LAY-004.B1 where normalizes the SDD_SPECS path
  - tier: light
  - test:
  - red:
  - green:
- [ ] T44 REQ-LAY-005.S1 REQ-LAY-005.S2 REQ-LAY-005.S3 SDD records are not test evidence
  - tier: mid
  - test:
  - red:
  - green:
- [ ] T45 REQ-LAY-005.B2 the root's .sdd/ is skipped without the marker
  - tier: light
  - test:
  - red:
  - green:
- [ ] T46 REQ-LAY-005.B1 a real test outside the records still counts
  - tier: light
  - test:
  - red:
  - green:

## Mutations
<!-- Implementer: one entry per new rule once its task is green (project rule 4). -->

## Verification
<!-- Verifier: commands run, results, coverage, findings, verdict. -->

## Open questions
- Per-branch mode with no constitution to adopt: a minimum level? → internal or higher (operator, 2026-11-18, Claude Code chat: "a multi-developer effort should have a minimum level"; internal proposed by the author; operator: "that seems right")
- Round 1 Q1–Q5, round 2 Q1–Q4 and round 3 Q1–Q4 → answered in Clarifications (operator, 2026-11-18, Claude Code chat)

## Clarifications
<!-- Spec Critic: one round per review, started with `sdd.py round`. Format:
method/format.md. Required before the gate at production and above. -->

### Round 1 — 2026-11-18 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-LAY-001 | issues | F5, F6, F7, F8, F9 |
| REQ-LAY-002 | issues | F1, F3, F10, F11, F12 |
| REQ-LAY-003 | issues | F3, F7, F13, F14 |
| REQ-LAY-004 | issues | F15 |
| REQ-LAY-005 | issues | F2, F4, F16 |

- F1 [ambiguity] REQ-LAY-002: the statement says AGENTS.md gets each `specs/` path "written as `.sdd/<branch>/`", where `<branch>` elsewhere in the same sentence is the real folder (`feat-a`), but S1 expects the literal text "`.sdd/<branch>/changes/`". AGENTS.md is one committed file shared by every branch, so writing the real name would make two branches conflict on it at merge (the problem in Intent) and commit a branch name, which may carry a personal name (rule 6). It is also unstated whether S2 (init with the marker, no `--per-branch`) rewrites AGENTS.md, and what `init` without the marker does to an AGENTS.md that holds the per-branch block → fixed: per Q1, LAY-002 writes the literal `.sdd/<branch>/` placeholder, every init while the marker exists writes it (S2 checks it), init without the marker keeps today's section
- F2 [coverage] REQ-LAY-005: only the folder in use is skipped. In per-branch mode the other branches' folders (`.sdd/feat-a/` seen from `feat/b`, and every branch folder on main after a merge, per Known gaps) and a pre-existing `specs/` kept by REQ-LAY-002.B1 are no longer skipped, so their spec.md task lines naming `test_REQ_…` count as test evidence wherever a path part is `tests`, `spec`, etc. Today `specs/` is always skipped, so this also weakens existing behavior → fixed: per Q2, LAY-005 skips `specs/`, all of `.sdd/` and the SDD_SPECS folder; S2 (another branch's folder) and S3 (SDD_SPECS) added
- F3 [contradiction] REQ-LAY-002, REQ-LAY-003: `init --per-branch` with a valid `SDD_SPECS` set: REQ-LAY-002 says it initializes `.sdd/<branch>/` and prints that folder; REQ-LAY-003 says `SDD_SPECS` names the folder "with or without the marker". No scenario decides which wins, nor whether the marker is written → fixed: per Q3, REQ-LAY-002.N5 refuses init --per-branch while SDD_SPECS is set
- F4 [conflict] REQ-LAY-005: the living spec REQ-EVD-001 defines current test files as "the files format.md counts as test files", and format.md says test files "outside `specs/`". Changing the skipped folder modifies evidence behavior, but the change declares only `layout=LAY` and marks nothing `[MODIFIED]`; format.md's Test naming paragraph is not in the Design notes' list of design work → fixed: REQ-EVD-001 defers to format.md and its text doesn't change; Scope records the behavior change, format.md Test naming is listed as design work, and a Known gap tagged evidence
- F5 [coverage] REQ-LAY-001: the marker is the file `.sdd/per-branch`, and a branch named `per-branch` maps to the folder `.sdd/per-branch/`, which can't coexist with it. No scenario or Known gap decides that case (refusal, or a marker name no branch folder can take) → fixed: per Q4, the marker is `.sdd/.per-branch`
- F6 [ambiguity] REQ-LAY-001: every git failure gives "per-branch mode needs a git branch: check out a branch or set SDD_SPECS" (Design notes: "any failure raises the LAY-001.N1 error"), including N2 (not a repository) and git not installed, where "check out a branch" is wrong advice. git missing has no scenario; nothing says whether a repository with no commits yet (an unborn branch, which `git symbolic-ref` resolves) counts as on a branch → fixed: per Q5, a separate repository error (LAY-001.N2) and git missing (N3); an unborn branch counts as on a branch (git symbolic-ref resolves it)
- F7 [weak-negative] REQ-LAY-001, REQ-LAY-003: N1, N2 (LAY-001) and N1, N2 (LAY-003) end in "no file written" after `status`, which writes nothing in any case, so the Then can't fail. The refusal before any write (Design notes: `main` calls `locate` before any command) is only proven with a writing command such as `new` or `init`, checking that no `specs/`, `.sdd/<branch>/` or marker appears → fixed: LAY-001.N1-N3 and LAY-003.N1-N5 run `init`, and check that nothing is written
- F8 [ambiguity] REQ-LAY-001: "`SDD_SPECS` is not set" here, but REQ-LAY-003 and its B1 treat an empty value as unset; with the marker and `SDD_SPECS=""`, REQ-LAY-001 as written does not apply. The statement should say "not set or empty", and no scenario has the marker with an empty `SDD_SPECS` → fixed: LAY-001 says "not set or empty"; B3 added
- F9 [ambiguity] REQ-LAY-001: "the repository root" is not defined when the SDD root (found by `locate`, or `--root`) differs from the git top level, e.g. sdd run from a subfolder of a monorepo; nor is which one the marker is looked up in when the command runs from a subfolder before `.sdd/<branch>/` exists (S2, N3 and REQ-LAY-004.S2 all run in such a state) → fixed: the project root is defined above the requirements; LAY-001.B4 runs from a subfolder
- F10 [coverage] REQ-LAY-002: the refusal order is only proven for a detached HEAD (N2). Two other paths could write the marker before refusing and have no scenario: `init --per-branch` in a folder that isn't a git repository (the N/A points at REQ-LAY-001.N2, which runs `status` with the marker already present, so it can't show the marker isn't written), and `init --per-branch` with no marker while `.sdd/<branch>/constitution.md` exists (N1 has the marker already, so its "no file changed" holds even if the marker were written first) → fixed: LAY-002.N2 (existing branch folder, no marker) and N4 (outside git) added; the statement says a refused init writes nothing
- F11 [coverage] REQ-LAY-002: `init --per-branch --force` (on an initialized branch folder, and on a repository with only `specs/`) has no scenario; the N1 error tells the operator to use `--force`, so what it refreshes in per-branch mode (folders, AGENTS.md block, marker) should be pinned → fixed: LAY-002.B2 pins init --per-branch --force
- F12 [untestable] REQ-LAY-002: S2's Then checks only the constitution and `.sdd/feat-a/`; the init output ("initialized .sdd/feat-b/ …", also required by Scope "init and new print the folder in use") and the AGENTS.md content are unchecked; no scenario checks that `new` prints the folder in use (Scope "In") rather than `specs/` → fixed: LAY-002.S2 checks the output and AGENTS.md; LAY-001.S1 checks new's output
- F13 [coverage] REQ-LAY-003: an `SDD_SPECS` that resolves to the root itself (`.` or `./`) is "inside the repository" yet would make REQ-LAY-005 skip every file (no test is ever found) and put `changes/` and `.sdd/active` at the root; one that names an existing file, or a path through a symlink leading outside, has no scenario either → fixed: LAY-003.N3 (`.`), N4 (a file) and N5 (a symlink outside) added
- F14 [ambiguity] REQ-LAY-003: "relative to the repository root" when the folder isn't initialized yet (e.g. `SDD_SPECS=records init` run from a subfolder): `locate` falls back to the current folder, so `records/` lands in the subfolder. The spec should say which root is used → fixed: SDD_SPECS is relative to the project root, defined above the requirements
- F15 [ambiguity] REQ-LAY-004: the printed form of an `SDD_SPECS` value is not fixed: `records`, `records/`, `./records` and `a//b` could print as given or normalized; only `SDD_SPECS=specs` is shown (S3). A `where` with the marker outside a git repository and with an invalid `SDD_SPECS` rely on scenarios that run `status`, not `where` → fixed: LAY-004 prints the path normalized with a trailing `/` (B1); N2 and N3 run `where`
- F16 [coverage] REQ-LAY-005: the statement names replay and mutate (via `overlay_tests`), but both scenarios run `check --stage verify`; no scenario shows that replay or mutate leaves a spec file in the branch folder (e.g. `.sdd/tests/changes/…/spec.md`) out of the overlaid test files → fixed: LAY-005 names only check's search; overlay uses the same helper, reviewed in the design notes since it isn't observable from the CLI
- Q1 What should the AGENTS.md section say in per-branch mode? A) the literal placeholder `.sdd/<branch>/` (one text for every branch, no merge conflict, no branch name committed), rewritten by every `init` while the marker exists B) the real folder of the branch that ran init (`.sdd/feat-a/`) — recommended: A
  - Answer: A — the literal `.sdd/<branch>/` placeholder (operator, 2026-11-18, Claude Code chat)
- Q2 Which folders should the test-file searches skip? A) only the folder in use, as written B) every SDD records folder: `specs/`, all of `.sdd/`, and the `SDD_SPECS` folder when set — recommended: B
  - Answer: B — skip `specs/`, all of `.sdd/` and the `SDD_SPECS` folder (operator, 2026-11-18, Claude Code chat)
- Q3 What does `init --per-branch` do while a valid `SDD_SPECS` is set? A) refuse with an error and write nothing B) `SDD_SPECS` wins: initialize that folder and still write the marker C) `SDD_SPECS` wins and no marker is written — recommended: A
  - Answer: A — refuse and write nothing (operator, 2026-11-18, Claude Code chat)
- Q4 How should a branch named `per-branch` be handled, since its folder collides with the marker file? A) refuse with an error that suggests SDD_SPECS B) name the marker so no branch folder can take it, e.g. `.sdd/.per-branch` (git forbids branch name parts that start with a dot) — recommended: B
  - Answer: B — the marker is `.sdd/.per-branch` (operator, 2026-11-18, Claude Code chat)
- Q5 Should the git failures have separate errors? A) one error for all, as written B) keep the N1 error for a detached HEAD, and add "per-branch mode needs a git repository (git must be installed and the project under version control)" for no repository or no git, as `replay` already says — recommended: B
  - Answer: B — a separate git repository error (operator, 2026-11-18, Claude Code chat)

### Round 2 — 2026-11-18 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-LAY-001 | issues | F1, F2 |
| REQ-LAY-002 | issues | F3, F4, F5, F6, F10 |
| REQ-LAY-003 | issues | F6, F7, F8 |
| REQ-LAY-004 | ok | |
| REQ-LAY-005 | issues | F9 |

<!-- Round 1 checked: Q1 (literal placeholder, every init with the marker, S1 and S2 check it), Q2 (LAY-005 skips specs/, .sdd/ and SDD_SPECS; S2, S3), Q3 (LAY-002.N5), Q4 (`.sdd/.per-branch` in the statement and scenarios) and Q5 (LAY-001.N2, N3) are applied in the requirements. F7 (writing commands in the N rows), F8 (B3), F9/F14 (project root defined, B4), F10 (LAY-002.N2, N4), F11 (B2), F12, F13 (LAY-003.N3–N5), F15 (LAY-004.B1, N2, N3) and F16 hold. REQ-LAY-004 is sound. -->

- F1 [contradiction] REQ-LAY-001: Q4 is not applied in the Design notes: "`Project.locate` walks up for `.sdd/per-branch`" names the old marker, while the spec's project root and every scenario use `.sdd/.per-branch`. An implementer following the notes builds the collision round 1 removed. Fix the notes. → fixed: the design notes name `.sdd/.per-branch`
- F2 [coverage] REQ-LAY-001: the folder name only maps `/` to `-`, so on a case-insensitive file system (macOS, Windows defaults) branches `Feat/A` and `feat/a` share one folder, as `feat/a-b` and `feat-a/b` do; the Known gaps list only the slash case. Add the case collision to Known gaps. → fixed: a Known gap for case-insensitive file systems
- F3 [conflict] REQ-LAY-002: B1 lets `init --assurance internal --per-branch` start a branch folder at `internal` in a repository whose `specs/constitution.md` is at `production`. The branch's changes are then checked against the new constitution's level, which lowers the project level with no recorded waiver (constitution, Assurance level: "Lowering it needs a recorded operator waiver"), and the approved constitution and project rules 1–9 are not in the branch folder at all. B1's Then checks only that the folder exists and `specs/` is unchanged, and the output says nothing about the existing `specs/` no longer being read → fixed: per Q1, REQ-LAY-006 copies the approved constitution and refuses a lower level (N1)
- F4 [ambiguity] REQ-LAY-002: the content of the marker is not stated. Each branch runs `init --per-branch` and commits its own `.sdd/.per-branch` (S1, S2); the two add the same path, and they merge without a conflict only when the files are byte-identical. If the marker records the branch, a date or the level, the merge the Intent wants to keep clean conflicts. State the content (e.g. an empty file, or one fixed line) and check it in S1's Then. → fixed: the marker is an empty file (LAY-002 statement, S1 checks it)
- F5 [coverage] REQ-LAY-002: round 1 F6 decided that an unborn branch (a repository with no commit yet, the usual state right after `git init`) counts as on a branch, but no scenario has one: B1, B2 and S1 don't say whether a commit exists, and the Design notes make a commit for every test repository. A resolver that runs `git rev-parse --abbrev-ref HEAD` (fails on an unborn branch) passes every row. Add a boundary row: `git init -b main`, no commit, `init --assurance internal --per-branch` → exit 0 · `.sdd/main/constitution.md` exists. → fixed: LAY-002.B3 runs init on an unborn branch
- F6 [ambiguity] REQ-LAY-002, REQ-LAY-003: what `init` writes into AGENTS.md and prints while `SDD_SPECS` is set is not decided. With the marker and `SDD_SPECS=records`, plain `init` initializes `records/` (LAY-003: "with or without the marker"), yet LAY-002 says every init while the marker exists writes `.sdd/<branch>/` into AGENTS.md; without the marker, the section says `specs/` while the folder is `records/`. No scenario runs `init` with a valid `SDD_SPECS`, so the printed "initialized records/ (assurance: …)" (Scope: init prints the folder in use) is unchecked, as is `new`'s "created records/changes/0001-x/spec.md" in LAY-003.S2 → fixed: per Q2, REQ-LAY-003.S3 checks init's output and AGENTS.md with SDD_SPECS
- F7 [coverage] REQ-LAY-003: the branch error (LAY-001.N1) tells the operator to "set SDD_SPECS", but no scenario shows that this works: every SDD_SPECS row is on a branch or without the marker. A resolver that checks the branch before `SDD_SPECS` (the opposite of the Design notes' order) passes every row while the advice fails. Add a row: the marker, a detached HEAD, `SDD_SPECS=records`, an initialized `records/`, `status` → exit 0 · the output is the one `records/` gives (and, for N2's case, the same outside a git repository). → fixed: LAY-003.B2 uses SDD_SPECS with the marker on a detached HEAD
- F8 [untestable] REQ-LAY-003: N1's Given, "an absolute path", has no concrete value. The statement reads the value "relative to the project root" and the Design notes refuse it "unless it resolves … to a folder strictly inside the root"; in Python, `root / "/abs"` is `/abs`, so an absolute path inside the root (e.g. `<root>/records`) would be accepted by the notes and refused by N1 read literally. The test may pick either and pass → fixed: per Q3, LAY-003 takes relative paths only; N1 names an absolute path inside the root
- F9 [contradiction] REQ-LAY-005: Scope says "Without the marker and without `SDD_SPECS`, behavior is unchanged", while Scope's "Changes existing behavior" line and the statement skip all of `.sdd/` in every repository, marker or not (the Known gap "Tests kept under a `.sdd/` folder are no longer found" confirms it). Every scenario that skips `.sdd/` has the marker, so a skip guarded by the marker passes them all. Reword the Scope line to except the evidence search, and add a row without the marker (e.g. no marker, `.sdd/tests/test_dur.py` naming `test_REQ_DUR_001_S1_parses`, `check --stage verify` → says REQ-DUR-001.S1 has no test). Also say whether `.sdd/` means only the root's `.sdd/` or any `.sdd` folder (e.g. `pkg/.sdd/`). → fixed: Scope names the `.sdd/` exception; LAY-005 skips only the project root's `specs/` and `.sdd/`; B2 runs without the marker
- F10 [ambiguity] REQ-LAY-002: the AGENTS.md section is the only place an agent learns where the specs are, and the literal `.sdd/<branch>/` doesn't say what `<branch>` stands for (the branch with `/` replaced by `-`) or that `sdd where` prints it. An agent on `feat/a` may look in `.sdd/feat/a/` or `.sdd/<branch>/` literally → fixed: per Q4, LAY-002 adds the line explaining `<branch>` and `sdd.py where`; S1 checks it
- Q1 What does `init --per-branch` do in a repository whose `specs/` is already initialized? A) as written: start an empty branch folder at the given level, `specs/` is kept and no longer read, with no note B) copy `specs/constitution.md`, approvals included, into the branch folder, ignore a different `--assurance` (or refuse a lower one), and print a note that `specs/` is no longer read C) refuse while `specs/constitution.md` exists — recommended: B
  - Answer: B — copy the constitution with its approvals, refuse a lower level, note that specs/ is not read (operator, 2026-11-18, Claude Code chat)
- Q2 What does `init` write into AGENTS.md while `SDD_SPECS` is set? A) the same as without it: the `.sdd/<branch>/` placeholder with the marker, `specs/` without (SDD_SPECS is a per-session setting, not committed), and the output still names the SDD_SPECS folder B) the SDD_SPECS folder C) refuse `init` while SDD_SPECS is set, as `init --per-branch` does — recommended: A
  - Answer: A — AGENTS.md as without it; the output names the SDD_SPECS folder (operator, 2026-11-18, Claude Code chat)
- Q3 Is an absolute `SDD_SPECS` that points inside the project root accepted? A) no: every absolute path is refused, as N1 reads B) yes: it is accepted and used relative to the root; only paths that resolve outside are refused — recommended: A
  - Answer: A — refuse every absolute path (operator, 2026-11-18, Claude Code chat)
- Q4 Should the per-branch AGENTS.md section say what `<branch>` means? A) no: only the `specs/` paths change B) yes: one added line, e.g. "`<branch>` is the current git branch with `/` replaced by `-`; `sdd where` prints the folder", the same for every branch — recommended: B
  - Answer: B — add the line (operator, 2026-11-18, Claude Code chat)

### Round 3 — 2026-11-18 · Critic: subagent (strong)

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-LAY-001 | ok | |
| REQ-LAY-002 | issues | F2, F3 |
| REQ-LAY-006 | issues | F1, F2, F4, F5, F6 |
| REQ-LAY-003 | issues | F3, F7, F8 |
| REQ-LAY-004 | ok | |
| REQ-LAY-005 | ok | |

<!-- Round 2 checked: F1 (design notes name `.sdd/.per-branch`), F2 (case-insensitive Known gap), F4 (empty marker, S1), F5 (LAY-002.B3 unborn branch), F7 (LAY-003.B2), F8/Q3 (LAY-003.N1 absolute path inside the root), F9 (Scope wording, LAY-005.B2) and F10/Q4 (the `<branch>`/`sdd.py where` line, S1) hold. Q1 is applied as REQ-LAY-006, Q2 as LAY-003.S3. The fingerprint is computed over the content only (constitution_fingerprint), so a byte-for-byte copy keeps its approval on the branch (LAY-006.S2 holds); this also holds for a constitution approved before fingerprints (`approved: yes`, no fingerprint), where level() reads the front matter. REQ-LAY-001, 004 and 005 have nothing new. -->

- F1 [ambiguity] REQ-LAY-006: "approved at production" and "a lower level" don't say which level is compared. `Project.level()` returns the approved level while the constitution has unapproved edits, the front matter `assurance` otherwise, and a never-approved file has no approved level at all. Three cases are undecided: `specs/` approved at production with an unapproved edit raising it to critical (is `--assurance production` lower?); `specs/` never approved, front matter production (refused with an error that says "approved", or allowed, per the Known gap that copies it "with its own level"?); and B1's note "keeps production" in the edited case. → fixed: per Q1, LAY-006 takes the level in force; the error says "is at"; B2 covers a never-approved file
- F2 [contradiction] REQ-LAY-002, REQ-LAY-006: LAY-002 prints "initialized .sdd/<branch>/ (assurance: <level>)", where `<level>` reads as the `--assurance` given, but in LAY-006.B1 (`--assurance critical`, copy at production) the folder is at production. Neither B1 nor S1 checks the "initialized" line, so the test can print either. → fixed: per Q2, the initialized line prints the copied level; B1 and B2 check it
- F3 [weak-negative] REQ-LAY-002, REQ-LAY-003: today `init` also prints "created specs/constitution.md (approval pending: sdd approve)". The spec doesn't say what this line becomes. After a copy, the constitution isn't new and its approval isn't pending (LAY-006.S2), so the line would be wrong. In a fresh branch folder or an `SDD_SPECS` folder it names `specs/`, against Scope ("init and new print the folder in use"). No Then checks that the line is absent after a copy (LAY-006.S1, S2), or that it names `.sdd/<branch>/constitution.md` (LAY-002.S1) or `records/constitution.md` (LAY-003.S3). → fixed: LAY-002.S1 and LAY-003.S3 check the "created <folder>/constitution.md" line; LAY-006.S1 checks no "approval pending" line after a copy
- F4 [ambiguity] REQ-LAY-006: the trigger "when init creates a branch folder" doesn't cover a branch folder that already exists without a constitution, for example `.sdd/feat-b/changes/` left behind, or `init --force` after the constitution was deleted. `cmd_init` writes a new constitution whenever none exists, and the spec doesn't say whether that case copies or writes the template. The trigger should be "when init writes a branch folder's constitution". → fixed: the trigger is "writes a branch folder's constitution"
- F5 [coverage] REQ-LAY-006: the N/A validation reason ("the copy is made unchanged") doesn't cover the copied file as input. A `specs/constitution.md` whose `assurance` is missing or not a level makes `level()` raise. No scenario decides whether init then refuses, and with which error and nothing written, or copies the file anyway. → fixed: per Q4, LAY-006.N3 refuses an invalid level
- F6 [coverage] REQ-LAY-006: the lower-level refusal is only proven without the marker (N1). The marker path (S2's state, plain `init --assurance internal`) has no N row, so a check placed only on the `--per-branch` path passes every row. Add the row: the marker, branch `feat/b` with no `.sdd/feat-b/`, `specs/` approved at production, `init --assurance internal` → exit 1 · the error of N1 · no `.sdd/feat-b/`. → fixed: LAY-006.N2 refuses a lower level with the marker
- F7 [ambiguity] REQ-LAY-003, REQ-LAY-006: with `SDD_SPECS=records` and an approved `specs/constitution.md`, the spec doesn't say whether `init` copies it into `records/` (it is not a "branch folder", and the operator sets the variable for a session) or writes the template at the given level. Without a copy, `records/` can start below the approved level, the gap round 2 Q1 closed for branch folders. → fixed: per Q3, LAY-006 covers the SDD_SPECS folder; S3 checks it
- F8 [coverage] REQ-LAY-003: round 2 Q2 (AGENTS.md as without SDD_SPECS) is proven only without the marker (S3). With the marker and `SDD_SPECS=records`, nothing checks that `init` still writes the `.sdd/<branch>/` placeholder (LAY-002: "every init while the marker exists") and prints "initialized records/". Add the row. → fixed: LAY-003.B3 runs init with the marker and SDD_SPECS
- Q1 Which level does REQ-LAY-006 compare `--assurance` against, and keep in B1's note? A) `level()` of `specs/`: the approved level while unapproved edits exist, else the front matter; a never-approved file counts at its front-matter level, and the error says "specs/constitution.md is at <level>" without "approved" B) only a fingerprinted or `approved: yes` level; a never-approved `specs/constitution.md` imposes no floor C) the front matter `assurance` always — recommended: A
  - Answer: A — the level in force; a never-approved file counts at its own level (operator, 2026-11-18, Claude Code chat: "if there is a constitution, it should adopt it. Constitution is for the product")
- Q2 What does the "initialized" line print when `--assurance` differs from the copied constitution? A) the level of the constitution in the folder (the copied one), as `cmd_init` reads it today, with B1's note after it B) the `--assurance` given — recommended: A
  - Answer: A — the copied level (operator, 2026-11-18, Claude Code chat: "if there is a constitution, it should adopt it. Constitution is for the product")
- Q3 Does `init` with a valid `SDD_SPECS` copy an existing `specs/constitution.md` into that folder? A) yes: the same copy, refusal and note as a branch folder B) no: SDD_SPECS folders start from the template at the given level, and a Known gap records it C) refuse `init` with SDD_SPECS while `specs/constitution.md` exists — recommended: A
  - Answer: A — an SDD_SPECS folder adopts it too (operator, 2026-11-18, Claude Code chat: "if there is a constitution, it should adopt it. Constitution is for the product")
- Q4 What does `init` do when `specs/constitution.md` has a missing or unknown `assurance`? A) refuse with the existing error "the constitution's assurance level '<x>' is not one of: …" (naming specs/constitution.md), nothing written, no marker B) copy it unchanged and skip the level check — recommended: A
  - Answer: A — refuse; an invalid constitution can't be adopted (operator, 2026-11-18, Claude Code chat: "if there is a constitution, it should adopt it. Constitution is for the product")

## Amendments
<!-- Spec changes after approval, one line each, then `sdd.py approve amend`:
- A1 2026-10-07: <reason> → <what changed> -->

## Approvals
| Gate | Date | Evidence |
| --- | --- | --- |
| plan | 2026-11-18 | Operator in Claude Code chat, 2026-11-18: "approved" (spec and plan of 0011 as shown in the review digest, including the hotfix-into-main departure from rule 8, the 0011 number and version 0.21.0) |
