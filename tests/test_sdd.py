"""Tests for skill/sdd/scripts/sdd.py (stdlib only: python3 -m unittest)."""

import contextlib
import importlib.util
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True  # keep skill/ free of __pycache__
SCRIPT = Path(__file__).resolve().parents[1] / "skill" / "sdd" / "scripts" / "sdd.py"
_spec = importlib.util.spec_from_file_location("sdd", SCRIPT)
sdd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sdd)


VALID_REQS = """\
### REQ-DUR-001 Parse hours and minutes
When the user passes a duration string such as "1h30m", the parser shall
return the total number of minutes.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| S1 | happy | the string "1h30m" | parse is called | it returns 90 |
| N1 | validation | the string "abc" | parse is called | it raises ValueError · nothing is returned |

- N/A state: the parser is a pure function without state
- N/A dependency: the parser calls no other component or service
"""

VALID_TASKS = """\
- Test command: `python3 -m unittest`

## Tasks
- [ ] T1 REQ-DUR-001.S1 Parse "1h30m"
  - test:
  - red:
  - green:
- [ ] T2 REQ-DUR-001.N1 Reject "abc"
  - test:
  - red:
  - green:
"""

DONE_TASKS = """\
- Test command: `python3 -m unittest`

## Tasks
- [x] T1 REQ-DUR-001.S1 Parse "1h30m"
  - test: tests/test_dur.py::test_REQ_DUR_001_S1
  - red: AssertionError: None != 90
  - green: 1 passed
- [x] T2 REQ-DUR-001.N1 Reject "abc"
  - test: tests/test_dur.py::test_REQ_DUR_001_N1
  - red: AssertionError: ValueError not raised
  - green: 1 passed
"""


def amend(repo, cid, log=True):
    """Simulate an amendment: a new scenario + its task, logged under ## Amendments."""
    path = repo.spec(cid)
    text = path.read_text()
    text = text.replace(
        "| N1 | validation | the string \"abc\" | parse is called | it raises ValueError · nothing is returned |",
        "| N1 | validation | the string \"abc\" | parse is called | it raises ValueError · nothing is returned |\n"
        "| N2 | validation | an empty string | parse is called | it raises ValueError · nothing is returned |", 1)
    text = text.replace("## Verification", "- [ ] T9 REQ-DUR-001.N2 Reject empty\n  - test:\n  - red:\n  - green:\n\n"
                        "## Verification", 1)
    if log:
        text = text.replace("## Amendments\n", "## Amendments\n- A1 2026-10-07: empty strings were not covered → added N2 and T9\n", 1)
    path.write_text(text)


class Repo:
    """A temporary repository driven through sdd.main()."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def close(self):
        self._tmp.cleanup()

    def run(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = sdd.main(["--root", str(self.root), *args])
            except SystemExit as exc:  # argparse errors
                code = exc.code
        return code, out.getvalue() + err.getvalue()

    def ok(self, *args):
        code, output = self.run(*args)
        assert code == 0, f"{args} failed ({code}):\n{output}"
        return output

    def change_dir(self, change_id):
        for base in ("changes", "archive"):
            path = self.root / "specs" / base / change_id
            if path.exists():
                return path
        raise AssertionError(f"no change {change_id}")

    def spec(self, change_id):
        return self.change_dir(change_id) / "spec.md"

    def set_section(self, change_id, name, body):
        """Replace the body of a `## name` section in a change spec."""
        path = self.spec(change_id)
        text = path.read_text()
        pattern = re.compile(rf"(^## {re.escape(name)}\n)(.*?)(?=^## |\Z)", re.S | re.M)
        assert pattern.search(text), f"section {name} missing"
        text = pattern.sub(lambda m: m.group(1) + body + "\n", text, count=1)
        path.write_text(text)

    def fill(self, change_id, reqs=VALID_REQS, gaps="- None\n", design_and_tasks=VALID_TASKS,
             verdict="PASS"):
        self.set_section(change_id, "Requirements", reqs)
        self.set_section(change_id, "Known gaps", gaps)
        if verdict:  # since REQ-APR-001, verified needs the Verifier's PASS verdict
            self.set_section(change_id, "Verification", f"Verdict: {verdict}\n")
        # Design notes section body is followed by the Tasks section we inject.
        path = self.spec(change_id)
        text = path.read_text()
        text = re.sub(r"^## Design notes\n.*?^## Tasks\n.*?(?=^## )",
                      "## Design notes\n" + design_and_tasks + "\n",
                      text, count=1, flags=re.S | re.M)
        path.write_text(text)

    def write(self, rel, content):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path


class Base(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.close)

    def init(self, level="internal"):
        self.repo.ok("init", "--assurance", level)

    def new(self, slug="parse-duration", *extra):
        self.repo.ok("new", slug, "--title", "Parse durations", "--capability", "duration=DUR", *extra)
        return sorted(p.name for p in (self.repo.root / "specs" / "changes").iterdir()
                      if p.is_dir())[-1]


# ---------------------------------------------------------------- init

class InitTests(Base):
    def test_init_creates_skeleton(self):
        self.init()
        specs = self.repo.root / "specs"
        for rel in ("constitution.md", "capabilities", "changes", "archive", ".sdd/active"):
            self.assertTrue((specs / rel).exists(), rel)
        self.assertIn("assurance: internal", (specs / "constitution.md").read_text())

    def test_init_twice_fails_without_force(self):
        self.init()
        code, out = self.repo.run("init", "--assurance", "internal")
        self.assertEqual(code, 1)
        self.assertIn("already initialized", out)

    def test_init_force_keeps_single_agents_block(self):
        self.init()
        self.repo.ok("init", "--assurance", "internal", "--force")
        agents = (self.repo.root / "AGENTS.md").read_text()
        self.assertEqual(agents.count("<!-- sdd:begin -->"), 1)

    def test_init_preserves_existing_agents_and_claude_files(self):
        self.repo.write("AGENTS.md", "# House rules\nBe nice.\n")
        self.repo.write("CLAUDE.md", "# Claude notes\n")
        self.init()
        agents = (self.repo.root / "AGENTS.md").read_text()
        claude = (self.repo.root / "CLAUDE.md").read_text()
        self.assertIn("Be nice.", agents)
        self.assertIn("<!-- sdd:begin -->", agents)
        self.assertIn("# Claude notes", claude)
        self.assertEqual(claude.count("@AGENTS.md"), 1)

    def test_init_rejects_unknown_assurance(self):
        code, _ = self.repo.run("init", "--assurance", "sloppy")
        self.assertNotEqual(code, 0)
        self.assertFalse((self.repo.root / "specs").exists())


# ---------------------------------------------------------------- new

class NewTests(Base):
    def test_new_creates_numbered_change_and_sets_active(self):
        self.init()
        cid = self.new()
        self.assertEqual(cid, "0001-parse-duration")
        text = self.repo.spec(cid).read_text()
        self.assertIn("status: draft", text)
        self.assertIn("assurance: internal", text)
        self.assertIn("capabilities: duration=DUR", text)
        active = (self.repo.root / "specs/.sdd/active").read_text().strip()
        self.assertEqual(active, cid)

    def test_new_requires_init(self):
        code, out = self.repo.run("new", "x", "--title", "X")
        self.assertEqual(code, 1)
        self.assertIn("sdd init", out)

    def test_new_rejects_bad_slug(self):
        self.init()
        code, out = self.repo.run("new", "Bad Slug!", "--title", "X")
        self.assertEqual(code, 1)
        self.assertIn("slug", out)

    def test_new_rejects_sizes_not_available_yet(self):
        self.init()
        code, out = self.repo.run("new", "big", "--title", "Big", "--size", "full")
        self.assertEqual(code, 1)
        self.assertIn("not available", out)

    def test_new_may_raise_but_not_lower_assurance(self):
        self.init("internal")
        self.repo.ok("new", "pay", "--title", "Pay", "--assurance", "critical")
        code, out = self.repo.run("new", "demo", "--title", "Demo", "--assurance", "prototype")
        self.assertEqual(code, 1)
        self.assertIn("waiver", out)

    def test_new_numbers_after_archived_changes(self):
        self.init()
        (self.repo.root / "specs/archive/0007-old").mkdir(parents=True)
        self.assertEqual(self.new("next-thing"), "0008-next-thing")

    def test_new_rejects_prefix_taken_by_other_capability(self):
        self.init()
        self.repo.write("specs/capabilities/timing/spec.md",
                        "---\ncapability: timing\nprefix: DUR\n---\n\n## Requirements\n")
        code, out = self.repo.run("new", "x", "--title", "X", "--capability", "duration=DUR")
        self.assertEqual(code, 1)
        self.assertIn("DUR", out)

    def test_new_rejects_malformed_capability(self):
        self.init()
        code, out = self.repo.run("new", "x", "--title", "X", "--capability", "duration")
        self.assertEqual(code, 1)
        self.assertIn("name=PREFIX", out)


# ---------------------------------------------------------------- check

class CheckTests(Base):
    def setUp(self):
        super().setUp()
        self.init()
        self.cid = self.new()

    def check(self, *extra):
        return self.repo.run("check", *extra)

    def test_valid_internal_spec_passes(self):
        self.repo.fill(self.cid)
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_html_comments_are_ignored(self):
        # The untouched template only has guidance in comments: no requirements yet.
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("no requirements", out)
        self.assertNotIn("REQ-CHK-001", out)

    def test_missing_required_category_fails(self):
        reqs = VALID_REQS.replace("- N/A dependency: the parser calls no other component or service\n", "")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("dependency", out)

    def test_na_with_too_short_reason_fails(self):
        reqs = VALID_REQS.replace("the parser calls no other component or service", "not needed")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("reason", out)

    def test_unknown_category_fails(self):
        reqs = VALID_REQS.replace("| N1 | validation |", "| N1 | weird |")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("weird", out)

    def test_requirement_without_happy_path_fails(self):
        reqs = VALID_REQS.replace("| S1 | happy |", "| S1 | validation |")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("happy", out)

    def test_duplicate_requirement_fails(self):
        dup = VALID_REQS + "\n" + VALID_REQS.replace("Parse hours and minutes", "Again")
        self.repo.fill(self.cid, reqs=dup)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("duplicate", out.lower())

    def test_undeclared_prefix_fails(self):
        self.repo.fill(self.cid, reqs=VALID_REQS.replace("REQ-DUR-001", "REQ-ZZZ-001"),
                       design_and_tasks=VALID_TASKS.replace("REQ-DUR-001", "REQ-ZZZ-001"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("ZZZ", out)

    def test_scenario_without_task_fails(self):
        tasks = VALID_TASKS.split("- [ ] T2")[0]
        self.repo.fill(self.cid, design_and_tasks=tasks)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("REQ-DUR-001.N1", out)

    def test_orphan_task_fails(self):
        tasks = VALID_TASKS + "- [ ] T3 REQ-DUR-001.N9 Ghost\n  - test:\n  - red:\n  - green:\n"
        self.repo.fill(self.cid, design_and_tasks=tasks)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("N9", out)

    def test_task_without_any_scenario_reference_fails(self):
        tasks = VALID_TASKS + "- [ ] T3 Tidy up\n"
        self.repo.fill(self.cid, design_and_tasks=tasks)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("T3", out)

    def test_ticked_task_without_red_evidence_fails(self):
        tasks = DONE_TASKS.replace("  - red: AssertionError: None != 90\n", "  - red:\n")
        self.repo.fill(self.cid, design_and_tasks=tasks)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("red", out)

    def test_open_question_is_reported(self):
        reqs = VALID_REQS.replace("total number of minutes.",
                                  "total number of minutes. [NEEDS CLARIFICATION: seconds too?]")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("1 open question", out)

    def test_single_assertion_negative_then_warns(self):
        reqs = VALID_REQS.replace("it raises ValueError · nothing is returned", "it raises ValueError")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("side effects", out)

    def test_missing_shall_warns(self):
        reqs = VALID_REQS.replace("the parser shall\nreturn", "the parser\nreturns")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("shall", out)

    def test_size_cap_boundary(self):
        self.repo.fill(self.cid)
        path = self.repo.spec(self.cid)
        base = path.read_text()
        lines = sdd.counted_lines(base)

        def padded(n):  # pad the design, which stays subject to the size cap
            return base.replace("## Design notes\n", "## Design notes\n" + "\n" * n, 1)

        path.write_text(padded(200 - lines))
        self.assertEqual(sdd.counted_lines(path.read_text()), 200)
        code, out = self.check()
        self.assertNotIn("size cap", out)
        path.write_text(padded(201 - lines))
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("size cap", out)

    def test_size_cap_excludes_task_checklist_and_completed_evidence(self):
        self.repo.fill(self.cid)
        before = sdd.counted_lines(self.repo.spec(self.cid).read_text())
        evidence = "\n".join("  - detail: recorded assertion output" for _ in range(300))
        self.repo.set_section(self.cid, "Tasks", DONE_TASKS.split("## Tasks\n", 1)[1] + evidence)
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertEqual(sdd.counted_lines(self.repo.spec(self.cid).read_text()), before)
        self.assertNotIn("size cap", out)

    def test_size_cap_counts_sections_following_tasks(self):
        text = "## Tasks\n" + VALID_TASKS.split("## Tasks\n", 1)[1] + "## Design notes\n- counted\n"
        self.assertEqual(sdd.counted_lines(text), 2)

    def test_task_exclusion_keeps_plan_coverage_validation(self):
        self.repo.fill(self.cid)
        self.repo.set_section(self.cid, "Tasks", "- [ ] T1 REQ-DUR-001.S1 Happy path\n  - test:\n  - red:\n  - green:\n")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("REQ-DUR-001.N1: no task plans this scenario", out)

    def test_new_requirement_colliding_with_capability_fails(self):
        self.repo.write("specs/capabilities/duration/spec.md",
                        "---\ncapability: duration\nprefix: DUR\n---\n\n## Requirements\n\n"
                        "### REQ-DUR-001 Existing\nThe parser shall exist.\n")
        self.repo.fill(self.cid)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("already exists", out)

    def test_modified_requirement_must_exist(self):
        reqs = VALID_REQS.replace("### REQ-DUR-001 ", "### REQ-DUR-001 [MODIFIED] ")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("does not exist", out)

    def test_verify_stage_requires_tests_naming_each_scenario(self):
        self.repo.fill(self.cid, design_and_tasks=DONE_TASKS)
        self.repo.write("tests/test_dur.py", "def test_REQ_DUR_001_S1():\n    pass\n")
        code, out = self.check("--stage", "verify")
        self.assertEqual(code, 1)
        self.assertIn("REQ-DUR-001.N1", out)

    def test_verify_stage_passes_with_tests_in_any_naming_style(self):
        self.repo.fill(self.cid, design_and_tasks=DONE_TASKS)
        self.repo.write("tests/test_dur.py", "def test_req_dur_001_s1():\n    pass\n")
        self.repo.write("web/dur.test.js", "it('REQ-DUR-001.N1 rejects abc', () => {})\n")
        code, out = self.check("--stage", "verify")
        self.assertEqual(code, 0, out)

    def test_verify_stage_does_not_count_mentions_inside_specs(self):
        self.repo.fill(self.cid, design_and_tasks=DONE_TASKS)
        code, out = self.check("--stage", "verify")
        self.assertEqual(code, 1)
        self.assertIn("no test", out)

    def test_verify_stage_requires_all_tasks_ticked(self):
        self.repo.fill(self.cid)
        self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")
        code, out = self.check("--stage", "verify")
        self.assertEqual(code, 1)
        self.assertIn("not done", out)


class AssuranceLevelTests(Base):
    def test_prototype_needs_only_happy_path_and_known_gaps(self):
        self.init("prototype")
        cid = self.new()
        reqs = VALID_REQS.split("| N1 |")[0].rstrip() + "\n"
        tasks = VALID_TASKS.split("- [ ] T2")[0]
        self.repo.fill(cid, reqs=reqs, gaps="- Invalid strings are not rejected\n",
                       design_and_tasks=tasks)
        code, out = self.repo.run("check")
        self.assertEqual(code, 0, out)

    def test_prototype_requires_known_gaps_list(self):
        self.init("prototype")
        cid = self.new()
        reqs = VALID_REQS.split("| N1 |")[0].rstrip() + "\n"
        tasks = VALID_TASKS.split("- [ ] T2")[0]
        self.repo.fill(cid, reqs=reqs, gaps="", design_and_tasks=tasks)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("Known gaps", out)

    def test_production_requires_boundary_and_access(self):
        self.init("production")
        cid = self.new()
        self.repo.fill(cid)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("boundary", out)
        self.assertIn("access", out)

    def test_raised_change_level_applies(self):
        self.init("internal")
        self.repo.ok("new", "pay", "--title", "Pay", "--capability", "duration=DUR",
                     "--assurance", "critical")
        cid = "0001-pay"
        self.repo.fill(cid)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("concurrency", out)


# ---------------------------------------------------------------- approve / advance

class LifecycleTests(Base):
    def setUp(self):
        super().setUp()
        self.init()
        self.cid = self.new()

    def status_of(self):
        return re.search(r"^status: (\S+)", self.repo.spec(self.cid).read_text(), re.M).group(1)

    def test_approve_plan_moves_to_planned_and_records_evidence(self):
        self.repo.fill(self.cid)
        self.repo.ok("approve", "plan", "--evidence", "Operator in chat: 'approve'")
        self.assertEqual(self.status_of(), "planned")
        self.assertIn("Operator in chat: 'approve'", self.repo.spec(self.cid).read_text())

    def test_approve_plan_refuses_when_check_fails(self):
        code, out = self.repo.run("approve", "plan", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertEqual(self.status_of(), "draft")

    def test_approve_plan_refuses_with_open_questions(self):
        reqs = VALID_REQS.replace("minutes.", "minutes. [NEEDS CLARIFICATION: seconds?]")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.repo.run("approve", "plan", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("open question", out)
        self.assertEqual(self.status_of(), "draft")

    def test_approve_requires_nonempty_evidence(self):
        self.repo.fill(self.cid)
        code, out = self.repo.run("approve", "plan", "--evidence", "   ")
        self.assertEqual(code, 1)
        self.assertIn("evidence", out)
        self.assertEqual(self.status_of(), "draft")

    def test_approve_plan_twice_fails(self):
        self.repo.fill(self.cid)
        self.repo.ok("approve", "plan", "--evidence", "ok")
        code, out = self.repo.run("approve", "plan", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("planned", out)

    def test_approve_evidence_with_pipe_does_not_break_table(self):
        self.repo.fill(self.cid)
        self.repo.ok("approve", "plan", "--evidence", "a | b")
        self.assertEqual(self.status_of(), "planned")
        self.assertIn("a \\| b", self.repo.spec(self.cid).read_text())

    def test_approve_constitution(self):
        self.repo.ok("approve", "constitution", "--evidence", "Operator: looks good")
        text = (self.repo.root / "specs/constitution.md").read_text()
        self.assertIn("approved: yes", text)
        self.assertIn("Operator: looks good", text)

    def test_approve_amend_keeps_status(self):
        self.repo.fill(self.cid)
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.repo.ok("advance", "implementing")
        amend(self.repo, self.cid)
        self.repo.ok("approve", "amend", "--evidence", "Operator: accept new rule")
        self.assertEqual(self.status_of(), "implementing")

    def test_advance_illegal_transition_fails(self):
        code, out = self.repo.run("advance", "implementing")
        self.assertEqual(code, 1)
        self.assertIn("draft", out)
        self.assertEqual(self.status_of(), "draft")

    def test_advance_to_verified_requires_clean_verify_check(self):
        self.repo.fill(self.cid, design_and_tasks=DONE_TASKS)
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.repo.ok("advance", "implementing")
        self.repo.ok("advance", "verifying")
        code, out = self.repo.run("advance", "verified")
        self.assertEqual(code, 1)
        self.assertEqual(self.status_of(), "verifying")
        self.repo.write("tests/test_dur.py", "test_REQ_DUR_001_S1 test_REQ_DUR_001_N1")
        self.repo.ok("advance", "verified")
        self.assertEqual(self.status_of(), "verified")

    def test_verifying_can_return_to_implementing(self):
        self.repo.fill(self.cid)
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.repo.ok("advance", "implementing")
        self.repo.ok("advance", "verifying")
        self.repo.ok("advance", "implementing")
        self.assertEqual(self.status_of(), "implementing")

    def test_abandon_clears_active(self):
        self.repo.ok("advance", "abandoned")
        self.assertEqual((self.repo.root / "specs/.sdd/active").read_text().strip(), "")


# ---------------------------------------------------------------- archive

class ArchiveTests(Base):
    def setUp(self):
        super().setUp()
        self.init()

    def verified_change(self, slug, reqs, tasks, tests):
        cid = self.new(slug)
        self.repo.fill(cid, reqs=reqs, design_and_tasks=tasks)
        self.repo.write(f"tests/test_{slug}.py", tests)
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.repo.ok("advance", "implementing")
        self.repo.ok("advance", "verifying")
        self.repo.ok("advance", "verified")
        return cid

    def test_archive_requires_verified(self):
        cid = self.new()
        code, out = self.repo.run("archive")
        self.assertEqual(code, 1)
        self.assertIn("verified", out)
        self.assertTrue((self.repo.root / "specs/changes" / cid).exists())

    def test_archive_creates_capability_and_moves_change(self):
        cid = self.verified_change("first", VALID_REQS, DONE_TASKS,
                                   "REQ_DUR_001_S1 REQ_DUR_001_N1")
        out = self.repo.ok("archive")
        cap = (self.repo.root / "specs/capabilities/duration/spec.md").read_text()
        self.assertIn("prefix: DUR", cap)
        self.assertIn("### REQ-DUR-001 Parse hours and minutes", cap)
        self.assertFalse((self.repo.root / "specs/changes" / cid).exists())
        archived = self.repo.root / "specs/archive" / cid / "spec.md"
        self.assertIn("status: archived", archived.read_text())
        self.assertEqual((self.repo.root / "specs/.sdd/active").read_text().strip(), "")
        self.assertIn("REQ-DUR-001", out)

    def test_archive_applies_modified_and_removed(self):
        self.verified_change("first", VALID_REQS, DONE_TASKS, "REQ_DUR_001_S1 REQ_DUR_001_N1")
        self.repo.ok("archive")
        second = VALID_REQS.replace("REQ-DUR-001", "REQ-DUR-002").replace(
            "Parse hours and minutes", "Parse seconds")
        self.verified_change("seconds", second, DONE_TASKS.replace("REQ-DUR-001", "REQ-DUR-002"),
                             "REQ_DUR_002_S1 REQ_DUR_002_N1")
        self.repo.ok("archive")

        modified = VALID_REQS.replace("### REQ-DUR-001 Parse hours and minutes",
                                      "### REQ-DUR-001 [MODIFIED] Parse hours, minutes and days")
        removed = "### REQ-DUR-002 [REMOVED] Parse seconds\nReason: seconds are out of scope now.\n"
        self.verified_change("days", modified + "\n" + removed, DONE_TASKS,
                             "REQ_DUR_001_S1 REQ_DUR_001_N1")
        self.repo.ok("archive")
        cap = (self.repo.root / "specs/capabilities/duration/spec.md").read_text()
        self.assertIn("### REQ-DUR-001 Parse hours, minutes and days", cap)
        self.assertNotIn("[MODIFIED]", cap)
        self.assertNotIn("### REQ-DUR-002", cap)
        self.assertIn("removed REQ-DUR-002", cap)  # the history keeps the trace
        self.assertEqual(cap.count("### REQ-DUR-001"), 1)

    def test_removed_requirement_needs_reason(self):
        self.verified_change("first", VALID_REQS, DONE_TASKS, "REQ_DUR_001_S1 REQ_DUR_001_N1")
        self.repo.ok("archive")
        cid = self.new("drop")
        self.repo.fill(cid, reqs="### REQ-DUR-001 [REMOVED] Parse hours and minutes\n",
                       design_and_tasks="- Test command: `true`\n\n## Tasks\n")
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("Reason", out)


# ---------------------------------------------------------------- next-req / status / use

class InfoTests(Base):
    def test_next_req_scans_changes_and_capabilities(self):
        self.init()
        self.repo.write("specs/capabilities/duration/spec.md",
                        "---\ncapability: duration\nprefix: DUR\n---\n### REQ-DUR-004 X\n")
        cid = self.new()
        self.repo.fill(cid, reqs=VALID_REQS.replace("REQ-DUR-001", "REQ-DUR-009"))
        out = self.repo.ok("next-req", "DUR")
        self.assertEqual(out.strip(), "REQ-DUR-010")

    def test_next_req_unknown_prefix_starts_at_001(self):
        self.init()
        self.assertEqual(self.repo.ok("next-req", "NEW").strip(), "REQ-NEW-001")

    def test_next_req_rejects_bad_prefix(self):
        self.init()
        code, out = self.repo.run("next-req", "lower")
        self.assertEqual(code, 1)

    def test_status_uninitialized(self):
        code, out = self.repo.run("status")
        self.assertEqual(code, 1)
        self.assertIn("sdd init", out)

    def test_status_without_active_change_suggests_quick(self):
        self.init()
        out = self.repo.ok("status")
        self.assertIn("sdd quick", out)

    def test_status_json_reports_counts_and_next_step(self):
        self.init()
        cid = self.new()
        self.repo.fill(cid)
        data = json.loads(self.repo.ok("status", "--json"))
        self.assertEqual(data["change"]["id"], cid)
        self.assertEqual(data["change"]["requirements"], 1)
        self.assertEqual(data["change"]["scenarios"], {"happy": 1, "negative": 1, "boundary": 0})
        self.assertEqual(data["change"]["tasks"], {"done": 0, "total": 2})
        self.assertIn("approve", data["next"])

    def test_use_switches_active_change(self):
        self.init()
        first = self.new("one")
        self.new("two")
        self.repo.ok("use", first)
        self.assertEqual((self.repo.root / "specs/.sdd/active").read_text().strip(), first)

    def test_use_unknown_change_fails(self):
        self.init()
        code, out = self.repo.run("use", "9999-nope")
        self.assertEqual(code, 1)


# ---------------------------------------------------------------- fixes from the first dogfood run

IF_THEN_REQ = """\
### REQ-DUR-002 Reject invalid durations
If the string is not a valid duration, then the parser shall raise ValueError.

| ID | Category | Given | When | Then |
| --- | --- | --- | --- | --- |
| N1 | validation | the string "abc" | parse is called | it raises ValueError · nothing is returned |
"""


class DogfoodFixTests(Base):
    def setUp(self):
        super().setUp()
        self.init()
        self.cid = self.new()

    def status_of(self):
        return re.search(r"^status: (\S+)", self.repo.spec(self.cid).read_text(), re.M).group(1)

    def to_verifying(self, tasks=DONE_TASKS):
        self.repo.fill(self.cid, design_and_tasks=tasks)
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.repo.ok("advance", "implementing")
        self.repo.ok("advance", "verifying")

    # B1: a failed archive must leave everything as it was.
    def test_archive_with_existing_destination_changes_nothing(self):
        self.to_verifying()
        self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")
        self.repo.ok("advance", "verified")
        (self.repo.root / "specs/archive" / self.cid).mkdir(parents=True)
        code, out = self.repo.run("archive")
        self.assertEqual(code, 1)
        self.assertIn("already exists", out)
        self.assertEqual(self.status_of(), "verified")
        self.assertFalse((self.repo.root / "specs/capabilities/duration/spec.md").exists())

    # B2: 'blocked' must not be a way around the plan gate.
    def test_blocked_draft_cannot_jump_to_implementing(self):
        self.repo.ok("advance", "blocked")
        code, out = self.repo.run("advance", "implementing")
        self.assertEqual(code, 1)
        self.assertIn("draft", out)
        self.repo.ok("advance", "draft")
        self.assertEqual(self.status_of(), "draft")

    def test_blocked_returns_to_the_status_it_came_from(self):
        self.repo.fill(self.cid)
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.repo.ok("advance", "implementing")
        self.repo.ok("advance", "blocked")
        code, _ = self.repo.run("advance", "verifying")
        self.assertEqual(code, 1)
        self.repo.ok("advance", "implementing")
        self.assertEqual(self.status_of(), "implementing")

    # B3a: only test files count as proof.
    def test_verify_ignores_mentions_outside_test_files(self):
        self.to_verifying()
        self.repo.write("README.md", "TODO: REQ-DUR-001.S1 REQ-DUR-001.N1")
        self.repo.write("durations.py", "# REQ_DUR_001_S1 REQ_DUR_001_N1\n")
        code, out = self.repo.run("check", "--stage", "verify")
        self.assertEqual(code, 1)
        self.assertIn("no test", out)

    def test_verify_ignores_test_like_files_inside_specs(self):
        self.to_verifying()
        self.repo.write("specs/tests/test_fake.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")
        code, out = self.repo.run("check", "--stage", "verify")
        self.assertEqual(code, 1)
        self.assertIn("no test", out)

    def test_verify_accepts_common_test_file_layouts(self):
        self.to_verifying()
        self.repo.write("src/__tests__/dur.js", "it('REQ-DUR-001.S1', () => {})")
        self.repo.write("pkg/dur_test.go", "func TestREQ_DUR_001_N1(t *testing.T) {}")
        code, out = self.repo.run("check", "--stage", "verify")
        self.assertEqual(code, 0, out)

    # B3b: red evidence must show a failure.
    def test_red_evidence_must_show_a_failure(self):
        tasks = DONE_TASKS.replace("red: AssertionError: None != 90", "red: 1 passed")
        self.repo.fill(self.cid, design_and_tasks=tasks)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("does not show a failure", out)

    def test_pre_existing_behavior_is_accepted_and_reported(self):
        tasks = DONE_TASKS.replace("red: AssertionError: None != 90",
                                   "red: pre-existing — parse_duration already handled this")
        self.repo.fill(self.cid, design_and_tasks=tasks)
        code, out = self.repo.run("check")
        self.assertEqual(code, 0, out)
        self.assertIn("pre-existing", out)

    def test_pre_existing_needs_a_reason(self):
        tasks = DONE_TASKS.replace("red: AssertionError: None != 90", "red: pre-existing")
        self.repo.fill(self.cid, design_and_tasks=tasks)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("reason", out)

    # B4: a status past draft needs a recorded plan approval.
    def test_status_past_draft_requires_plan_approval_record(self):
        self.repo.fill(self.cid, design_and_tasks=DONE_TASKS)
        path = self.repo.spec(self.cid)
        path.write_text(path.read_text().replace("status: draft", "status: verifying"))
        self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")
        code, out = self.repo.run("advance", "verified")
        self.assertEqual(code, 1)
        self.assertIn("no plan approval", out)
        self.assertEqual(self.status_of(), "verifying")

    # B5: approving the constitution again is labelled as such.
    def test_constitution_reapproval_is_labelled(self):
        self.repo.ok("approve", "constitution", "--evidence", "first")
        c = self.repo.root / "specs/constitution.md"  # since REQ-APR-002, re-approval needs a change
        c.write_text(c.read_text().replace("## Approvals", "10. A new rule.\n\n## Approvals", 1))
        out = self.repo.ok("approve", "constitution", "--evidence", "second")
        self.assertIn("re-approval", out)
        text = (self.repo.root / "specs/constitution.md").read_text()
        self.assertIn("| constitution (re-approval) |", text)

    # F1: an If…then requirement is all failure behavior.
    def test_if_then_requirement_needs_no_happy_path(self):
        reqs = VALID_REQS.replace(
            "| N1 | validation | the string \"abc\" | parse is called | it raises ValueError · nothing is returned |\n", ""
        ).replace("- N/A state:", "- N/A validation: covered by REQ-DUR-002\n- N/A state:") + "\n" + IF_THEN_REQ
        tasks = VALID_TASKS.replace("REQ-DUR-001.N1", "REQ-DUR-002.N1")
        self.repo.fill(self.cid, reqs=reqs, design_and_tasks=tasks)
        code, out = self.repo.run("check")
        self.assertEqual(code, 0, out)

    def test_if_then_requirement_needs_a_failure_scenario(self):
        bad = IF_THEN_REQ.replace("| N1 | validation |", "| S1 | happy |")
        self.repo.fill(self.cid, reqs=VALID_REQS + "\n" + bad)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("If…then", out)

    def test_na_covered_by_unknown_requirement_fails(self):
        reqs = VALID_REQS.replace("the parser calls no other component or service",
                                  "covered by REQ-DUR-077")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("REQ-DUR-077", out)

    # F8: the size cap counts the spec, not the Verifier's report or approvals.
    def test_size_cap_excludes_verification_and_approvals(self):
        self.repo.fill(self.cid)
        self.repo.set_section(self.cid, "Verification", "| row |\n" * 300)
        code, out = self.repo.run("check")
        self.assertNotIn("size cap", out)

    # F11: tightened side-effect heuristic: a comma is not a second assertion.
    def test_comma_is_not_a_second_assertion(self):
        reqs = VALID_REQS.replace("it raises ValueError · nothing is returned",
                                  "it raises ValueError, as expected")
        self.repo.fill(self.cid, reqs=reqs)
        code, out = self.repo.run("check")
        self.assertIn("side effects", out)


class ArchiveCarryOverTests(Base):
    # F9: known gaps and history reach the living spec.
    def test_archive_carries_known_gaps_and_history(self):
        self.init()
        cid = self.new()
        self.repo.fill(cid, gaps="- Non-UTF-8 files crash the command\n", design_and_tasks=DONE_TASKS)
        self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")
        self.repo.ok("approve", "plan", "--evidence", "ok")
        for status in ("implementing", "verifying", "verified"):
            self.repo.ok("advance", status)
        self.repo.ok("archive")
        cap = (self.repo.root / "specs/capabilities/duration/spec.md").read_text()
        self.assertIn(f"- Non-UTF-8 files crash the command ({cid})", cap)
        self.assertRegex(cap, rf"- {cid} — Parse durations \(\d{{4}}-\d\d-\d\d\): added REQ-DUR-001")
        self.assertLess(cap.index("## Known gaps"), cap.index("## Requirements"))
        self.assertLess(cap.index("## Change history"), cap.index("### REQ-DUR-001"))

    def test_none_is_not_carried_as_a_gap(self):
        self.init()
        cid = self.new()
        self.repo.fill(cid, design_and_tasks=DONE_TASKS)
        self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")
        self.repo.ok("approve", "plan", "--evidence", "ok")
        for status in ("implementing", "verifying", "verified"):
            self.repo.ok("advance", status)
        self.repo.ok("archive")
        cap = (self.repo.root / "specs/capabilities/duration/spec.md").read_text()
        self.assertNotIn("- None (", cap)

    # F11: status shows the living spec.
    def test_status_lists_living_spec(self):
        self.init()
        self.repo.write("specs/capabilities/duration/spec.md",
                        "---\ncapability: duration\nprefix: DUR\n---\n## Requirements\n"
                        "### REQ-DUR-001 A\n### REQ-DUR-002 B\n")
        out = self.repo.ok("status")
        self.assertIn("duration (DUR, 2 requirements)", out)


# ---------------------------------------------------------------- v1 increment 1: amend

class AmendTests(Base):
    def setUp(self):
        super().setUp()
        self.init()
        self.cid = self.new()
        self.repo.fill(self.cid)
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.repo.ok("advance", "implementing")

    def test_approval_locks_the_spec(self):
        self.assertRegex(self.repo.spec(self.cid).read_text(), r"(?m)^spec_hash: [0-9a-f]{12}$")
        self.repo.ok("check")

    def test_spec_edit_after_approval_fails_check(self):
        amend(self.repo, self.cid)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("changed since it was approved", out)

    def test_known_gaps_edit_is_also_locked(self):
        self.repo.set_section(self.cid, "Known gaps", "- Huge numbers overflow\n")
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("changed since it was approved", out)

    def test_task_and_design_edits_are_not_locked(self):
        path = self.repo.spec(self.cid)
        text = path.read_text().replace("- Test command:", "- Approach: regex\n- Test command:", 1)
        text = text.replace("## Verification", "- [ ] T7 REQ-DUR-001.S1 Extra check\n\n## Verification", 1)
        path.write_text(text)
        self.repo.ok("check")

    def test_approved_amendment_unlocks_and_relocks(self):
        amend(self.repo, self.cid)
        out = self.repo.ok("approve", "amend", "--evidence", "Operator: yes, cover empty strings")
        self.assertIn("amendment", out)
        self.repo.ok("check")
        self.assertIn("Operator: yes, cover empty strings", self.repo.spec(self.cid).read_text())

    def test_amend_requires_a_spec_change(self):
        code, out = self.repo.run("approve", "amend", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("nothing to amend", out)

    def test_amend_requires_a_log_entry(self):
        amend(self.repo, self.cid, log=False)
        code, out = self.repo.run("approve", "amend", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("## Amendments", out)

    def test_second_amendment_needs_a_second_log_entry(self):
        amend(self.repo, self.cid)
        self.repo.ok("approve", "amend", "--evidence", "first")
        self.repo.set_section(self.cid, "Known gaps", "- Huge numbers overflow\n")
        code, out = self.repo.run("approve", "amend", "--evidence", "second")
        self.assertEqual(code, 1)
        self.assertIn("## Amendments", out)

    def test_amend_refuses_an_amended_spec_that_fails_check(self):
        amend(self.repo, self.cid)
        path = self.repo.spec(self.cid)
        path.write_text(path.read_text().replace("- [ ] T9 REQ-DUR-001.N2 Reject empty", "- [ ] T9 Reject empty", 1))
        code, out = self.repo.run("approve", "amend", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("REQ-DUR-001.N2", out)
        self.assertEqual(path.read_text().count("| amend |"), 0)
        code, out = self.repo.run("check")  # still locked: nothing was accepted
        self.assertIn("changed since it was approved", out)

    def test_changes_approved_before_locking_are_not_flagged(self):
        path = self.repo.spec(self.cid)
        path.write_text(re.sub(r"(?m)^spec_hash: .*\n", "", path.read_text()))
        amend(self.repo, self.cid)
        self.repo.ok("check")


# ---------------------------------------------------------------- v1 increment 1: bug

DEFECT = """\
- Symptom: "1h 30m" returns 60 instead of 90
- Reproduce: parse_duration("1h 30m")
- Current behavior: returns 60
- Expected behavior: returns 90; spaces between parts are allowed
- Violates: REQ-DUR-001
- Root cause:
"""

MODIFIED_WITH_REGRESSION = VALID_REQS.replace(
    "### REQ-DUR-001 Parse hours and minutes", "### REQ-DUR-001 [MODIFIED] Parse hours and minutes"
).replace(
    "| N1 | validation |",
    "| R1 | happy | the string \"1h 30m\" | parse is called | it returns 90 |\n| N1 | validation |")

REGRESSION_TASKS = VALID_TASKS + "- [ ] T3 REQ-DUR-001.R1 Spaces between parts\n  - test:\n  - red:\n  - green:\n"


class BugTests(Base):
    def setUp(self):
        super().setUp()
        self.init()
        self.repo.write("specs/capabilities/duration/spec.md",
                        "---\ncapability: duration\nprefix: DUR\n---\n\n## Requirements\n\n" + VALID_REQS)
        self.repo.ok("new", "fix-spaces", "--title", "Spaces in durations", "--type", "defect",
                     "--capability", "duration=DUR")
        self.cid = "0001-fix-spaces"

    def fill_defect(self, defect=DEFECT, reqs=MODIFIED_WITH_REGRESSION, tasks=REGRESSION_TASKS):
        self.repo.set_section(self.cid, "Defect", defect)
        self.repo.fill(self.cid, reqs=reqs, design_and_tasks=tasks)

    def test_defect_change_has_a_defect_section(self):
        text = self.repo.spec(self.cid).read_text()
        self.assertIn("type: defect", text)
        for field in ("Symptom", "Reproduce", "Current behavior", "Expected behavior", "Violates", "Root cause"):
            self.assertIn(f"- {field}:", text)

    def test_feature_change_has_no_defect_section(self):
        self.repo.ok("new", "feature", "--title", "F", "--capability", "duration=DUR")
        self.assertNotIn("## Defect", self.repo.spec("0002-feature").read_text())

    def test_valid_code_defect_passes(self):
        self.fill_defect()
        code, out = self.repo.run("check")
        self.assertEqual(code, 0, out)

    def test_defect_fields_are_required(self):
        self.fill_defect(defect=DEFECT.replace("- Current behavior: returns 60", "- Current behavior:"))
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("Current behavior", out)

    def test_defect_needs_a_regression_scenario(self):
        self.fill_defect(reqs=MODIFIED_WITH_REGRESSION.replace("| R1 |", "| S2 |"),
                         tasks=REGRESSION_TASKS.replace("REQ-DUR-001.R1", "REQ-DUR-001.S2"))
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("needs a regression scenario", out)

    def test_violated_requirement_must_exist(self):
        self.fill_defect(defect=DEFECT.replace("Violates: REQ-DUR-001", "Violates: REQ-DUR-042"))
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("REQ-DUR-042", out)

    def test_violated_requirement_must_be_restated_with_the_regression(self):
        second = (VALID_REQS.replace("REQ-DUR-001", "REQ-DUR-002")
                  .replace("| N1 | validation |",
                           "| R1 | happy | the string \"1h 30m\" | parse is called | it returns 90 |\n| N1 | validation |"))
        tasks = VALID_TASKS.replace("REQ-DUR-001", "REQ-DUR-002") + \
            "- [ ] T3 REQ-DUR-002.R1 Spaces\n  - test:\n  - red:\n  - green:\n"
        self.fill_defect(reqs=second, tasks=tasks)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("[MODIFIED]", out)

    def test_spec_gap_defect_with_new_requirement_passes(self):
        gap = DEFECT.replace("Violates: REQ-DUR-001", "Violates: spec gap — nothing says what spaces do")
        new_req = (VALID_REQS.replace("REQ-DUR-001", "REQ-DUR-002").replace("Parse hours and minutes", "Spaces")
                   .replace("| N1 | validation |",
                            "| R1 | happy | the string \"1h 30m\" | parse is called | it returns 90 |\n| N1 | validation |"))
        tasks = VALID_TASKS.replace("REQ-DUR-001", "REQ-DUR-002") + \
            "- [ ] T3 REQ-DUR-002.R1 Spaces\n  - test:\n  - red:\n  - green:\n"
        self.fill_defect(defect=gap, reqs=new_req, tasks=tasks)
        code, out = self.repo.run("check")
        self.assertEqual(code, 0, out)

    def test_violates_must_be_a_requirement_or_spec_gap(self):
        self.fill_defect(defect=DEFECT.replace("Violates: REQ-DUR-001", "Violates: the parser"))
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("spec gap", out)

    def test_root_cause_is_required_before_verified(self):
        self.fill_defect(tasks=REGRESSION_TASKS.replace("- [ ]", "- [x]").replace(
            "  - test:\n  - red:\n  - green:\n",
            "  - test: tests/test_dur.py::t\n  - red: AssertionError: 60 != 90\n  - green: 1 passed\n"))
        self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1 REQ_DUR_001_R1")
        code, out = self.repo.run("check", "--stage", "verify")
        self.assertEqual(code, 1)
        self.assertIn("Root cause", out)
        self.repo.set_section(self.cid, "Defect", DEFECT.replace("- Root cause:", "- Root cause: the regex ignored spaces"))
        code, out = self.repo.run("check", "--stage", "verify")
        self.assertEqual(code, 0, out)


# ---------------------------------------------------------------- v1 increment 2: standard size

STD_TASKS = """\
- [ ] T1 REQ-DUR-001.S1 Parse "1h30m"
  - test:
  - red:
  - green:
- [ ] T2 REQ-DUR-001.N1 Reject "abc"
  - test:
  - red:
  - green:
"""
STD_DONE_TASKS = DONE_TASKS.split("## Tasks\n", 1)[1]


def set_file_section(path, name, body):
    text = path.read_text()
    pattern = re.compile(rf"(^## {re.escape(name)}\n)(.*?)(?=^## |\Z)", re.S | re.M)
    assert pattern.search(text), f"section {name} missing in {path.name}"
    path.write_text(pattern.sub(lambda m: m.group(1) + body + "\n", text, count=1))


class StandardTests(Base):
    def setUp(self):
        super().setUp()
        self.init()
        self.repo.ok("new", "durations", "--title", "Parse durations", "--size", "standard",
                     "--capability", "duration=DUR")
        self.cid = "0001-durations"
        self.dir = self.repo.root / "specs/changes" / self.cid

    def f(self, name):
        return self.dir / name

    def status_of(self):
        return re.search(r"^status: (\S+)", self.f("proposal.md").read_text(), re.M).group(1)

    def spec(self, reqs=VALID_REQS, gaps="- None\n", critic=True):
        set_file_section(self.f("spec-delta.md"), "Requirements", reqs)
        set_file_section(self.f("spec-delta.md"), "Known gaps", gaps)
        if critic:  # since increment 3, standard changes at internal+ need a Critic round
            set_file_section(self.f("clarifications.md"), "Clarifications", ROUND_DONE)

    def design(self, command="`python3 -m unittest`"):
        set_file_section(self.f("design.md"), "Approach", "- A regex over the string\n")
        set_file_section(self.f("design.md"), "Test strategy", f"- Unit tests\n- Test command: {command}\n")

    def tasks(self, body=STD_TASKS):
        set_file_section(self.f("tasks.md"), "Tasks", body)

    def to_designed(self):
        self.spec()
        self.repo.ok("approve", "spec", "--evidence", "Operator: spec ok")
        self.design()
        self.repo.ok("advance", "designed")

    def to_verifying(self, tests=True):
        self.to_designed()
        self.tasks(STD_DONE_TASKS)
        self.repo.ok("approve", "plan", "--evidence", "Operator: plan ok")
        self.repo.ok("advance", "implementing")
        self.repo.ok("advance", "verifying")
        if tests:
            self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")
        # since REQ-APR-001, the results gate needs the Verifier's PASS verdict
        set_file_section(self.f("verification.md"), "Verification", "Verdict: PASS\n")

    # layout
    def test_new_standard_creates_a_change_folder(self):
        for name in ("proposal.md", "spec-delta.md", "design.md", "tasks.md", "verification.md"):
            self.assertTrue(self.f(name).exists(), name)
        self.assertFalse(self.f("spec.md").exists())
        text = self.f("proposal.md").read_text()
        self.assertIn("size: standard", text)
        self.assertIn("status: draft", text)
        self.assertEqual((self.repo.root / "specs/.sdd/active").read_text().strip(), self.cid)

    def test_full_size_is_still_not_available(self):
        code, out = self.repo.run("new", "big", "--title", "Big", "--size", "full")
        self.assertEqual(code, 1)
        self.assertIn("not available", out)

    def test_defect_section_goes_into_the_proposal(self):
        self.repo.ok("new", "fix", "--title", "Fix", "--size", "standard", "--type", "defect")
        self.assertIn("## Defect", (self.repo.root / "specs/changes/0002-fix/proposal.md").read_text())

    # check across files
    def test_check_reads_the_change_across_files(self):
        self.spec()
        self.design()
        self.tasks()
        code, out = self.repo.run("check")
        self.assertEqual(code, 0, out)
        self.assertIn("REQ-DUR-001", out)

    def test_check_finds_coverage_gaps_in_spec_delta(self):
        self.spec(reqs=VALID_REQS.replace("- N/A dependency: the parser calls no other component or service\n", ""))
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("dependency", out)

    def test_standard_size_cap_is_400_lines(self):
        self.spec()
        filler = "".join(f"- note {i}\n" for i in range(330))
        set_file_section(self.f("design.md"), "Approach", filler)
        code, out = self.repo.run("check")
        self.assertNotIn("size cap", out)
        set_file_section(self.f("design.md"), "Approach", filler + "".join(f"- more {i}\n" for i in range(80)))
        code, out = self.repo.run("check")
        self.assertIn("size cap", out)
        self.assertIn("400", out)

    def test_standard_size_cap_excludes_task_file(self):
        self.spec()
        self.design()
        self.tasks()
        _, before = self.repo.run("status", "--json")
        self.tasks(STD_TASKS + "  - detail: recorded assertion output\n" * 450)
        code, out = self.repo.run("check", "--stage", "plan")
        self.assertEqual(code, 0, out)
        self.assertNotIn("size cap", out)
        _, after = self.repo.run("status", "--json")
        self.assertEqual(json.loads(after)["change"]["lines"],
                         json.loads(before)["change"]["lines"])

    # gate 1: spec
    def test_spec_gate_locks_the_spec(self):
        self.spec()
        self.repo.ok("approve", "spec", "--evidence", "Operator: spec ok")
        self.assertEqual(self.status_of(), "spec-approved")
        self.assertRegex(self.f("proposal.md").read_text(), r"(?m)^spec_hash: [0-9a-f]{12}$")
        set_file_section(self.f("spec-delta.md"), "Known gaps", "- Overflow\n")
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("changed since it was approved", out)

    def test_spec_gate_does_not_need_tasks_or_design(self):
        self.spec()
        self.repo.ok("approve", "spec", "--evidence", "ok")

    def test_spec_gate_refuses_check_errors(self):
        code, out = self.repo.run("approve", "spec", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertEqual(self.status_of(), "draft")

    def test_spec_gate_refuses_open_questions(self):
        self.spec(reqs=VALID_REQS.replace("minutes.", "minutes. [NEEDS CLARIFICATION: seconds?]"))
        code, out = self.repo.run("approve", "spec", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("open question", out)

    def test_spec_gate_is_for_standard_only(self):
        self.repo.ok("new", "small", "--title", "Small", "--capability", "duration=DUR")
        self.repo.fill("0002-small")
        code, out = self.repo.run("approve", "spec", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("approve plan", out)

    def test_clarifying_is_a_draft_step_before_the_spec_gate(self):
        self.spec()
        self.repo.ok("advance", "clarifying")
        self.assertEqual(self.status_of(), "clarifying")
        self.repo.ok("approve", "spec", "--evidence", "ok")
        self.assertEqual(self.status_of(), "spec-approved")

    # design
    def test_design_and_tasks_stay_editable_after_the_spec_gate(self):
        self.spec()
        self.repo.ok("approve", "spec", "--evidence", "ok")
        self.design()
        self.tasks()
        self.repo.ok("check")

    def test_designed_requires_a_test_command(self):
        self.spec()
        self.repo.ok("approve", "spec", "--evidence", "ok")
        self.design(command="")
        code, out = self.repo.run("advance", "designed")
        self.assertEqual(code, 1)
        self.assertIn("Test command", out)
        self.assertEqual(self.status_of(), "spec-approved")

    # gate 2: plan
    def test_plan_gate_comes_after_design(self):
        self.spec()
        self.repo.ok("approve", "spec", "--evidence", "ok")
        self.design()
        self.tasks()
        code, out = self.repo.run("approve", "plan", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("designed", out)

    def test_plan_gate_after_design(self):
        self.to_designed()
        self.tasks()
        self.repo.ok("approve", "plan", "--evidence", "Operator: plan ok")
        self.assertEqual(self.status_of(), "planned")

    def test_plan_gate_refuses_a_spec_changed_since_its_gate(self):
        self.to_designed()
        self.tasks()
        set_file_section(self.f("spec-delta.md"), "Known gaps", "- Overflow\n")
        code, out = self.repo.run("approve", "plan", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("changed since it was approved", out)

    def test_amend_works_while_designing(self):
        self.to_designed()
        set_file_section(self.f("spec-delta.md"), "Known gaps", "- Overflow\n")
        set_file_section(self.f("proposal.md"), "Amendments", "- A1 2026-10-08: overflow found → known gap\n")
        self.repo.ok("approve", "amend", "--evidence", "Operator: accept the gap")
        self.assertEqual(self.status_of(), "designed")
        self.repo.ok("check")

    # gate 3: results
    def test_verified_needs_the_results_gate(self):
        self.to_verifying()
        code, out = self.repo.run("advance", "verified")
        self.assertEqual(code, 1)
        self.assertIn("approve results", out)
        self.repo.ok("approve", "results", "--evidence", "Operator: verification accepted")
        self.assertEqual(self.status_of(), "verified")

    def test_results_gate_refuses_a_failing_verify_check(self):
        self.to_verifying(tests=False)
        code, out = self.repo.run("approve", "results", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("no test", out)
        self.assertEqual(self.status_of(), "verifying")

    def test_results_gate_is_for_standard_only(self):
        self.repo.ok("new", "small", "--title", "Small", "--capability", "duration=DUR")
        code, out = self.repo.run("approve", "results", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("advance verified", out)

    # integrity
    def test_each_passed_gate_needs_its_approval_record(self):
        self.spec()
        self.design()
        self.tasks()
        path = self.f("proposal.md")
        path.write_text(path.read_text().replace("status: draft", "status: planned"))
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("no spec approval", out)
        self.assertIn("no plan approval", out)

    def test_cannot_skip_the_spec_gate_by_advancing(self):
        self.spec()
        code, out = self.repo.run("advance", "designed")
        self.assertEqual(code, 1)
        self.assertIn("approve spec", out)

    # archive and status
    def test_archive_merges_and_moves_the_folder(self):
        self.to_verifying()
        self.repo.ok("approve", "results", "--evidence", "ok")
        self.repo.ok("archive")
        cap = (self.repo.root / "specs/capabilities/duration/spec.md").read_text()
        self.assertIn("### REQ-DUR-001 Parse hours and minutes", cap)
        archived = self.repo.root / "specs/archive" / self.cid
        self.assertTrue((archived / "proposal.md").exists())
        self.assertTrue((archived / "tasks.md").exists())
        self.assertFalse(self.dir.exists())

    def test_status_reports_standard_changes(self):
        self.spec()
        data = json.loads(self.repo.ok("status", "--json"))
        self.assertEqual(data["change"]["size"], "standard")
        self.assertEqual(data["change"]["cap"], 400)
        self.assertIn("approve", data["next"])
        self.assertEqual(data["in_flight"][0]["id"], self.cid)

    def test_next_step_after_each_gate(self):
        self.spec()
        self.repo.ok("approve", "spec", "--evidence", "ok")
        self.assertIn("design", json.loads(self.repo.ok("status", "--json"))["next"])
        self.design()
        self.repo.ok("advance", "designed")
        self.assertIn("tasks", json.loads(self.repo.ok("status", "--json"))["next"])


# ---------------------------------------------------------------- v1 increment 3: clarify + Spec Critic

ROUND_DONE = """\
### Round 1 — 2026-10-08 · Critic: same session

| REQ | Verdict | Notes |
| --- | --- | --- |
| REQ-DUR-001 | issues | F1, F2 |

- F1 [coverage] REQ-DUR-001: no scenario for an empty string → fixed: N2 added
- F2 [ambiguity] REQ-DUR-001: is "90" minutes? → Q1
- Q1 Should "90" (no unit) count as minutes? A) yes B) no, reject — recommended: B
  - Answer: B — reject (operator, 2026-10-08)
"""


class ClarifyMiniTests(Base):
    def setUp(self):
        super().setUp()
        self.init()
        self.cid = self.new()
        self.repo.fill(self.cid)

    def clar(self, body):
        self.repo.set_section(self.cid, "Clarifications", body)

    def test_mini_spec_has_a_clarifications_section(self):
        self.assertIn("## Clarifications", self.repo.spec(self.cid).read_text())

    def test_round_command_lists_every_requirement(self):
        out = self.repo.ok("round")
        self.assertIn("Round 1", out)
        text = self.repo.spec(self.cid).read_text()
        self.assertRegex(text, r"### Round 1 — \d{4}-\d\d-\d\d · Critic: same session")
        self.assertIn("| REQ-DUR-001 | ? |", text)

    def test_round_numbers_increment_and_fresh_is_recorded(self):
        self.repo.ok("round")
        self.repo.ok("round", "--fresh")
        self.assertRegex(self.repo.spec(self.cid).read_text(), r"### Round 2 — .* · Critic: fresh session")

    def test_round_needs_requirements(self):
        self.repo.set_section(self.cid, "Requirements", "")
        code, out = self.repo.run("round")
        self.assertEqual(code, 1)
        self.assertIn("requirements", out)

    def test_round_only_before_the_gate(self):
        self.repo.ok("approve", "plan", "--evidence", "ok")
        code, out = self.repo.run("round")
        self.assertEqual(code, 1)
        self.assertIn("amend", out)

    def test_complete_round_passes_check(self):
        self.clar(ROUND_DONE)
        code, out = self.repo.run("check")
        self.assertEqual(code, 0, out)

    def test_unaudited_requirement_fails_check(self):
        self.repo.ok("round")
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("verdict", out)

    def test_open_finding_fails_check(self):
        self.clar(ROUND_DONE.replace(" → fixed: N2 added", ""))
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("F1", out)

    def test_rejected_finding_needs_a_reason(self):
        self.clar(ROUND_DONE.replace("→ fixed: N2 added", "→ rejected:"))
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("F1", out)

    def test_finding_waiting_on_an_unanswered_question_is_open(self):
        self.clar(ROUND_DONE.replace("  - Answer: B — reject (operator, 2026-10-08)\n", "  - Answer: pending\n"))
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("F2", out)
        self.assertIn("1 open question", out)

    def test_unknown_finding_type_fails(self):
        self.clar(ROUND_DONE.replace("[ambiguity]", "[vibes]"))
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("vibes", out)

    def test_at_most_five_questions_per_round(self):
        extra = "".join(f"- Q{i} Question {i}? A) x B) y — recommended: A\n  - Answer: A (operator)\n"
                        for i in range(2, 7))
        self.clar(ROUND_DONE + extra)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1)
        self.assertIn("at most 5", out)

    def test_clarifications_are_not_locked_or_counted(self):
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.clar(ROUND_DONE + "\n" * 300)
        code, out = self.repo.run("check")
        self.assertEqual(code, 0, out)
        self.assertNotIn("size cap", out)

    def test_internal_mini_plan_gate_needs_no_round(self):
        self.repo.ok("approve", "plan", "--evidence", "ok")


class ClarifyGateTests(Base):
    def standard(self, level="internal"):
        self.init(level)
        self.repo.ok("new", "durations", "--title", "Parse durations", "--size", "standard",
                     "--capability", "duration=DUR")
        self.dir = self.repo.root / "specs/changes/0001-durations"
        set_file_section(self.dir / "spec-delta.md", "Requirements", VALID_REQS)
        set_file_section(self.dir / "spec-delta.md", "Known gaps", "- None\n")

    def test_standard_folder_has_clarifications_file(self):
        self.standard()
        self.assertIn("## Clarifications", (self.dir / "clarifications.md").read_text())

    def test_standard_spec_gate_requires_a_critic_round(self):
        self.standard()
        code, out = self.repo.run("approve", "spec", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("Critic round", out)
        self.assertIn("sdd clarify", out)

    def test_standard_spec_gate_passes_after_a_complete_round(self):
        self.standard()
        set_file_section(self.dir / "clarifications.md", "Clarifications", ROUND_DONE)
        self.repo.ok("approve", "spec", "--evidence", "ok")

    def test_round_moves_a_standard_draft_to_clarifying(self):
        self.standard()
        self.repo.ok("round")
        self.assertIn("status: clarifying", (self.dir / "proposal.md").read_text())
        self.assertIn("| REQ-DUR-001 | ? |", (self.dir / "clarifications.md").read_text())

    def test_requirement_added_after_the_round_needs_a_new_round(self):
        self.standard()
        set_file_section(self.dir / "clarifications.md", "Clarifications", ROUND_DONE)
        second = VALID_REQS.replace("REQ-DUR-001", "REQ-DUR-002").replace("Parse hours and minutes", "Seconds")
        set_file_section(self.dir / "spec-delta.md", "Requirements", VALID_REQS + "\n" + second)
        code, out = self.repo.run("approve", "spec", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("REQ-DUR-002", out)
        self.assertIn("latest Critic round", out)

    def test_prototype_standard_needs_no_round(self):
        self.standard("prototype")
        set_file_section(self.dir / "spec-delta.md", "Requirements",
                         VALID_REQS.split("| N1 |")[0].rstrip() + "\n")
        set_file_section(self.dir / "spec-delta.md", "Known gaps", "- Invalid strings not rejected\n")
        self.repo.ok("approve", "spec", "--evidence", "ok")

    def test_production_mini_plan_gate_requires_a_round(self):
        self.init("production")
        cid = self.new()
        reqs = VALID_REQS.replace("- N/A state:", "- N/A boundary: the parser accepts any length of input\n"
                                  "- N/A access: the parser is a local pure function\n- N/A state:")
        self.repo.fill(cid, reqs=reqs)
        code, out = self.repo.run("approve", "plan", "--evidence", "ok")
        self.assertEqual(code, 1)
        self.assertIn("Critic round", out)
        self.repo.set_section(cid, "Clarifications", ROUND_DONE.replace("same session", "fresh session"))
        self.repo.ok("approve", "plan", "--evidence", "ok")

    def test_same_session_round_at_production_warns(self):
        self.init("production")
        cid = self.new()
        self.repo.fill(cid)
        self.repo.set_section(cid, "Clarifications", ROUND_DONE)
        code, out = self.repo.run("check")
        self.assertIn("fresh session", out)

    def test_status_suggests_clarify_before_the_spec_gate(self):
        self.standard()
        data = json.loads(self.repo.ok("status", "--json"))
        self.assertIn("sdd clarify", data["next"])
        set_file_section(self.dir / "clarifications.md", "Clarifications", ROUND_DONE)
        data = json.loads(self.repo.ok("status", "--json"))
        self.assertIn("approve", data["next"])


# ---------------------------------------------------------------- change 0001-approval-integrity (REQ-APR-*)

def fingerprint_in(text):
    match = re.search(r"(?m)^fingerprint: ([0-9a-f]{12})$", text)
    return match.group(1) if match else None


def last_approval_row(text):
    rows = [l for l in text.split("## Approvals", 1)[1].splitlines()
            if l.startswith("| ") and not l.startswith("| Gate") and not l.startswith("| ---")]
    return rows[-1] if rows else ""


class VerdictStandardTests(Base):
    """REQ-APR-001: the standard results gate reads the Verifier's verdict."""

    def setUp(self):
        super().setUp()
        self.init()
        self.repo.ok("new", "durations", "--title", "Parse durations", "--size", "standard",
                     "--capability", "duration=DUR")
        self.dir = self.repo.root / "specs/changes/0001-durations"
        set_file_section(self.dir / "spec-delta.md", "Requirements", VALID_REQS)
        set_file_section(self.dir / "spec-delta.md", "Known gaps", "- None\n")
        set_file_section(self.dir / "clarifications.md", "Clarifications", ROUND_DONE)
        self.repo.ok("approve", "spec", "--evidence", "ok")
        set_file_section(self.dir / "design.md", "Test strategy", "- Test command: `python3 -m unittest`\n")
        self.repo.ok("advance", "designed")
        set_file_section(self.dir / "tasks.md", "Tasks", STD_DONE_TASKS)
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.repo.ok("advance", "implementing")
        self.repo.ok("advance", "verifying")
        self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")

    def verification(self, body):
        set_file_section(self.dir / "verification.md", "Verification", body)

    def status_of(self):
        return re.search(r"^status: (\S+)", (self.dir / "proposal.md").read_text(), re.M).group(1)

    def results_rows(self):
        return (self.dir / "proposal.md").read_text().count("| results |")

    def accepted(self):
        out = self.repo.ok("approve", "results", "--evidence", "ok")
        self.assertEqual(self.status_of(), "verified")
        self.assertEqual(self.results_rows(), 1)
        return out

    def refused(self, *expected):
        code, out = self.repo.run("approve", "results", "--evidence", "ok")
        self.assertEqual(code, 1, out)
        for text in expected:
            self.assertIn(text, out)
        self.assertEqual(self.status_of(), "verifying")
        self.assertEqual(self.results_rows(), 0)
        return out

    def test_REQ_APR_001_S1_pass_verdict_accepted(self):
        self.verification("- Tests: 2 passed\n\nVerdict: PASS\n")
        self.accepted()

    def test_REQ_APR_001_R1_gaps_verdict_refused(self):
        self.verification("- Tests: 2 passed\n\nVerdict: GAPS — F1 open: weak test for N1\n")
        self.refused("GAPS — F1 open")

    def test_REQ_APR_001_N1_no_verdict_refused(self):
        self.verification("- Tests: 2 passed\n")
        self.refused("no verdict")

    def test_REQ_APR_001_N2_unknown_verdict_refused(self):
        self.verification("Verdict: maybe\n")
        self.refused("PASS", "GAPS", "maybe")

    def test_REQ_APR_001_B1_lowercase_with_trailing_text_accepted(self):
        self.verification("Verdict: pass — 0 findings\n")
        self.accepted()

    def test_REQ_APR_001_B2_emphasised_later_gaps_refused(self):
        self.verification("Verdict: PASS\n\n**Verdict:** GAPS — F3\n")
        self.refused("GAPS")

    def test_REQ_APR_001_B3_verdict_in_code_block_ignored(self):
        self.verification("Verdict: PASS\n\n```\nVerdict: GAPS\n```\n")
        self.accepted()

    def test_REQ_APR_001_B4_numbered_dot_gaps_after_pass_refused(self):
        self.verification("Verdict: PASS\n\n1. Verdict: GAPS — F4\n")
        self.refused("GAPS — F4")

    def test_REQ_APR_001_B5_numbered_paren_gaps_after_pass_refused(self):
        self.verification("Verdict: PASS\n\n1) Verdict: GAPS — F4\n")
        self.refused("GAPS — F4")

    def test_REQ_APR_001_B6_table_row_is_not_a_verdict(self):
        self.verification("Verdict: GAPS — F1\n\n| Verdict | PASS |\n| --- | --- |\n")
        self.refused("GAPS — F1")

    def test_REQ_APR_001_B7_mid_line_mention_is_not_a_verdict(self):
        self.verification("Verdict: GAPS — F1\n\nThe final Verdict: PASS was expected\n")
        self.refused("GAPS — F1")

    def test_REQ_APR_001_B8_commented_verdict_is_not_a_verdict(self):
        self.verification("Verdict: GAPS — F1\n\n<!-- reviewer draft\nVerdict: PASS\nend of draft -->\n")
        self.refused("GAPS — F1")

    def test_REQ_APR_001_N3_latest_gaps_after_pass_refused(self):
        self.verification("Verdict: PASS\n\nVerdict: GAPS — F2\n")
        self.refused("GAPS — F2")

    def test_REQ_APR_001_S2_latest_pass_after_gaps_accepted(self):
        self.verification("Verdict: GAPS\n\nVerdict: PASS\n")
        self.accepted()

    def test_REQ_APR_001_N6_passed_is_an_unknown_verdict(self):
        self.verification("- Tests: 2 passed\n\nVerdict: PASSED\n")
        self.refused("PASS", "GAPS", "PASSED")

    def test_REQ_APR_001_N4_missing_verification_file_refused(self):
        (self.dir / "verification.md").unlink()
        self.refused("no verdict")


class VerdictMiniTests(Base):
    """REQ-APR-001: the mini verified step reads the Verifier's verdict."""

    def setUp(self):
        super().setUp()
        self.init()
        self.cid = self.new()
        self.repo.fill(self.cid, design_and_tasks=DONE_TASKS)
        self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.repo.ok("advance", "implementing")
        self.repo.ok("advance", "verifying")

    def status_of(self):
        return re.search(r"^status: (\S+)", self.repo.spec(self.cid).read_text(), re.M).group(1)

    def refused(self, verification, expected):
        self.repo.set_section(self.cid, "Verification", verification)
        before = self.repo.spec(self.cid).read_text()
        code, out = self.repo.run("advance", "verified")
        self.assertEqual(code, 1, out)
        self.assertIn(expected, out)
        self.assertEqual(self.status_of(), "verifying")
        self.assertEqual(self.repo.spec(self.cid).read_text(), before)

    def test_REQ_APR_001_S3_mini_pass_accepted(self):
        self.repo.set_section(self.cid, "Verification", "Verdict: PASS\n")
        self.repo.ok("advance", "verified")
        self.assertEqual(self.status_of(), "verified")

    def test_REQ_APR_001_R2_mini_gaps_refused(self):
        self.refused("Verdict: GAPS — weak N1\n", "GAPS")

    def test_REQ_APR_001_N5_mini_no_verdict_refused(self):
        self.refused("- Tests: 2 passed\n", "no verdict")


class ConstitutionTests(Base):
    """Shared helpers for REQ-APR-002 and REQ-APR-003."""

    def setUp(self):
        super().setUp()
        self.init()
        self.c = self.repo.root / "specs/constitution.md"

    def approve(self):
        return self.repo.ok("approve", "constitution", "--evidence", "Operator: ok")

    def edit(self, old, new):
        text = self.c.read_text()
        assert old in text, old
        self.c.write_text(text.replace(old, new, 1))

    def add_rule(self):
        self.edit("## Approvals", "10. Anything goes.\n\n## Approvals")

    def status(self):
        return self.repo.ok("status")

    def status_json(self):
        return json.loads(self.repo.ok("status", "--json"))

    def as_earlier_version(self, level="internal"):
        """A constitution approved before fingerprints existed."""
        self.edit("approved: no", "approved: yes")
        if level != "internal":
            self.edit("assurance: internal", f"assurance: {level}")
        self.edit("| --- | --- | --- |", "| --- | --- | --- |\n| constitution | 2026-10-01 | old approval |")

    def mini_ready(self, slug="demo"):
        self.repo.ok("new", slug, "--title", "Demo", "--capability", "duration=DUR")
        cid = sorted(p.name for p in (self.repo.root / "specs/changes").iterdir() if p.is_dir())[-1]
        self.repo.fill(cid)
        return cid

    def assurance_of(self, cid):
        return re.search(r"^assurance: (\S+)", self.repo.spec(cid).read_text(), re.M).group(1)


class ConstitutionFingerprintTests(ConstitutionTests):
    """REQ-APR-002: constitution changes after approval are detected."""

    def test_REQ_APR_002_S1_approval_records_fingerprint(self):
        self.approve()
        text = self.c.read_text()
        fp = fingerprint_in(text)
        self.assertIsNotNone(fp)
        self.assertIn("approved_level: internal", text)
        self.assertTrue(last_approval_row(text).endswith(f"· fingerprint {fp} · level internal |"))
        self.assertNotIn("changed since approval", self.status())

    def test_REQ_APR_002_R1_status_reports_change(self):
        self.approve()
        self.add_rule()
        out = self.status()
        self.assertIn("changed since approval", out)
        self.assertIn("sdd approve", out)
        data = self.status_json()
        self.assertTrue(data["constitution_changed"])
        self.assertTrue(data["constitution_approved"])

    def test_REQ_APR_002_N1_plan_gate_refused_while_changed(self):
        self.approve()
        cid = self.mini_ready()
        self.add_rule()
        before = self.repo.spec(cid).read_text()
        code, out = self.repo.run("approve", "plan", "--evidence", "ok")
        self.assertEqual(code, 1, out)
        self.assertIn("changed since approval", out)
        self.assertEqual(self.repo.spec(cid).read_text(), before)

    def test_REQ_APR_002_N5_check_fails_while_changed(self):
        self.approve()
        self.mini_ready()
        self.add_rule()
        code, out = self.repo.run("check")
        self.assertEqual(code, 1, out)
        self.assertIn("changed since approval", out)

    def test_REQ_APR_002_N6_advance_verified_refused_while_changed(self):
        self.approve()
        cid = self.mini_ready()
        self.repo.fill(cid, design_and_tasks=DONE_TASKS)
        self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.repo.ok("advance", "implementing")
        self.repo.ok("advance", "verifying")
        self.repo.set_section(cid, "Verification", "Verdict: PASS\n")
        self.add_rule()
        code, out = self.repo.run("advance", "verified")
        self.assertEqual(code, 1, out)
        self.assertIn("changed since approval", out)
        self.assertIn("status: verifying", self.repo.spec(cid).read_text())

    def test_REQ_APR_002_S2_reapproval_clears_change(self):
        self.approve()
        self.add_rule()
        self.approve()
        text = self.c.read_text()
        row = last_approval_row(text)
        self.assertIn("| constitution (re-approval) |", row)
        self.assertIn(f"· fingerprint {fingerprint_in(text)} ·", row)
        self.assertNotIn("changed since approval", self.status())

    def test_REQ_APR_002_N2_unchanged_reapproval_refused(self):
        self.approve()
        before = self.c.read_text()
        code, out = self.repo.run("approve", "constitution", "--evidence", "again")
        self.assertEqual(code, 1, out)
        self.assertIn("nothing changed since approval", out)
        self.assertEqual(self.c.read_text(), before)

    def test_REQ_APR_002_N3_edited_fingerprint_reported(self):
        self.approve()
        self.edit(f"fingerprint: {fingerprint_in(self.c.read_text())}", "fingerprint: 000000000000")
        before = self.c.read_text()
        self.assertIn("changed since approval", self.status())
        self.assertEqual(self.c.read_text(), before)

    def test_REQ_APR_002_N7_deleted_fingerprint_reported(self):
        self.approve()
        self.edit(f"fingerprint: {fingerprint_in(self.c.read_text())}\n", "")
        before = self.c.read_text()
        self.assertIn("changed since approval", self.status())
        self.assertEqual(self.c.read_text(), before)

    def test_REQ_APR_002_N8_broken_front_matter_reported(self):
        self.approve()
        lines = self.c.read_text().splitlines(keepends=True)
        self.c.write_text("".join(l for i, l in enumerate(lines) if not (l == "---\n" and i < 8)))
        before = self.c.read_text()
        self.assertIn("changed since approval", self.status())
        self.assertEqual(self.c.read_text(), before)

    def test_REQ_APR_002_B1_blank_lines_and_comments_ignored(self):
        self.approve()
        self.edit("## Approvals", "\n\n<!-- a reviewer's note -->\n\n## Approvals")
        before = self.c.read_text()
        self.assertNotIn("changed since approval", self.status())
        self.assertEqual(self.c.read_text(), before)

    def test_REQ_APR_002_B2_extra_whitespace_ignored(self):
        self.approve()
        self.edit("No production code", "No  production   code")
        before = self.c.read_text()
        self.assertNotIn("changed since approval", self.status())
        self.assertEqual(self.c.read_text(), before)

    def test_REQ_APR_002_B4_rewrapped_rule_is_a_change(self):
        self.approve()
        self.edit("No production code without", "No production code\nwithout")
        before = self.c.read_text()
        self.assertIn("changed since approval", self.status())
        self.assertEqual(self.c.read_text(), before)

    def test_REQ_APR_002_B3_hand_added_row_ignored(self):
        self.approve()
        self.edit("| --- | --- | --- |", "| --- | --- | --- |\n| constitution | 2026-10-12 | hand-written |")
        before = self.c.read_text()
        self.assertNotIn("changed since approval", self.status())
        self.assertEqual(self.c.read_text(), before)

    def test_REQ_APR_002_N4_earlier_version_not_flagged(self):
        self.as_earlier_version()
        self.add_rule()
        before = self.c.read_text()
        self.assertNotIn("changed since approval", self.status())
        self.assertEqual(self.c.read_text(), before)

    def test_REQ_APR_002_S3_earlier_version_gets_fingerprint(self):
        self.as_earlier_version()
        self.approve()
        text = self.c.read_text()
        self.assertIsNotNone(fingerprint_in(text))
        self.assertIn(f"· fingerprint {fingerprint_in(text)} ·", last_approval_row(text))
        self.assertNotIn("changed since approval", self.status())

    def test_REQ_APR_002_N9_quoted_older_note_is_ignored(self):
        self.approve()
        self.edit("assurance: internal", "assurance: production")
        self.repo.ok("approve", "constitution", "--evidence",
                     "Operator: raise it (previous note: · fingerprint 0123456789ab · level prototype)")
        self.assertNotIn("changed since approval", self.status())
        self.assertEqual(self.status_json()["assurance"], "production")
        self.repo.ok("new", "demo", "--title", "Demo")
        self.assertEqual(self.assurance_of("0001-demo"), "production")

    def test_REQ_APR_002_N10_newest_fingerprinted_row_is_the_reference(self):
        self.approve()
        self.edit(f"fingerprint: {fingerprint_in(self.c.read_text())}\n", "")
        self.c.write_text(self.c.read_text().rstrip("\n") + "\n| constitution | 2026-10-12 | hand-written |\n")
        before = self.c.read_text()
        self.assertIn("changed since approval", self.status())
        self.assertEqual(self.c.read_text(), before)

    def test_REQ_APR_002_S5_front_matter_fingerprint_is_the_fallback(self):
        self.approve()
        text = self.c.read_text()
        self.c.write_text("\n".join(l for l in text.splitlines() if "· fingerprint " not in l) + "\n")
        self.edit("assurance: internal", "assurance: prototype")
        out = self.status()
        self.assertIn("changed since approval", out)
        self.assertIn("internal (prototype pending approval)", out)
        self.repo.ok("new", "demo", "--title", "Demo")
        self.assertEqual(self.assurance_of("0001-demo"), "internal")

    def test_REQ_APR_002_S4_never_approved_blocks_nothing(self):
        cid = self.mini_ready()
        self.repo.ok("approve", "plan", "--evidence", "ok")
        self.assertIn("status: planned", self.repo.spec(cid).read_text())


class ApprovedLevelTests(ConstitutionTests):
    """REQ-APR-003: the approved assurance level stays in force."""

    def test_REQ_APR_003_S1_approved_level_applies(self):
        self.approve()
        self.repo.ok("new", "demo", "--title", "Demo")
        self.assertEqual(self.assurance_of("0001-demo"), "internal")

    def test_REQ_APR_003_R1_lowered_level_not_in_force(self):
        self.approve()
        self.edit("assurance: internal", "assurance: prototype")
        self.repo.ok("new", "demo", "--title", "Demo")
        self.assertEqual(self.assurance_of("0001-demo"), "internal")
        self.assertIn("internal (prototype pending approval)", self.status())
        data = self.status_json()
        self.assertEqual(data["assurance"], "internal")
        self.assertEqual(data["assurance_pending"], "prototype")

    def test_REQ_APR_003_N3_explicit_lower_level_refused_while_pending(self):
        self.approve()
        self.edit("assurance: internal", "assurance: prototype")
        code, out = self.repo.run("new", "demo", "--title", "Demo", "--assurance", "prototype")
        self.assertEqual(code, 1, out)
        self.assertIn("lower than the project level 'internal'", out)
        self.assertFalse((self.repo.root / "specs/changes/0001-demo").exists())

    def test_REQ_APR_003_S2_reapproval_records_lowering(self):
        self.approve()
        self.edit("assurance: internal", "assurance: prototype")
        self.approve()
        self.assertTrue(last_approval_row(self.c.read_text())
                        .endswith("· assurance lowered internal → prototype |"))
        self.repo.ok("new", "demo", "--title", "Demo")
        self.assertEqual(self.assurance_of("0001-demo"), "prototype")

    def test_REQ_APR_003_N1_invalid_or_missing_level_refused(self):
        self.approve()
        for broken in ("assurance: sloppy\n", ""):
            with self.subTest(broken=broken or "(deleted)"):
                text = self.c.read_text()
                self.c.write_text(re.sub(r"(?m)^assurance: .*\n", broken, text, count=1))
                before = self.c.read_text()
                code, out = self.repo.run("approve", "constitution", "--evidence", "ok")
                self.assertEqual(code, 1, out)
                for level in ("prototype", "internal", "production", "critical"):
                    self.assertIn(level, out)
                self.assertEqual(self.c.read_text(), before)
                data = self.status_json()
                self.assertEqual(data["assurance"], "internal")
                self.c.write_text(text)

    def test_REQ_APR_003_B1_raised_level_not_in_force(self):
        self.approve()
        self.edit("assurance: internal", "assurance: production")
        self.repo.ok("new", "demo", "--title", "Demo")
        self.assertEqual(self.assurance_of("0001-demo"), "internal")
        self.assertIn("internal (production pending approval)", self.status())

    def test_REQ_APR_003_B2_raised_level_approved_without_note(self):
        self.approve()
        self.edit("assurance: internal", "assurance: production")
        self.approve()
        self.assertNotIn("lowered", last_approval_row(self.c.read_text()))
        self.repo.ok("new", "demo", "--title", "Demo")
        self.assertEqual(self.assurance_of("0001-demo"), "production")

    def test_REQ_APR_003_B3_unchanged_level_approved_without_note(self):
        self.approve()
        self.add_rule()
        self.approve()
        self.assertNotIn("lowered", last_approval_row(self.c.read_text()))

    def test_REQ_APR_003_N2_earlier_version_uses_front_matter_level(self):
        self.as_earlier_version()
        self.edit("assurance: internal", "assurance: prototype")
        before = self.c.read_text()
        self.repo.ok("new", "demo", "--title", "Demo")
        self.assertEqual(self.assurance_of("0001-demo"), "prototype")
        self.assertEqual(self.c.read_text(), before)

    def assert_four_levels(self, out):
        self.assertIn("prodution", out)
        for level in ("prototype", "internal", "production", "critical"):
            self.assertIn(level, out)

    def test_REQ_APR_003_N4_invalid_level_refused_by_new(self):
        self.edit("assurance: internal", "assurance: prodution")
        code, out = self.repo.run("new", "demo", "--title", "Demo")
        self.assertEqual(code, 1, out)
        self.assert_four_levels(out)
        self.assertFalse((self.repo.root / "specs/changes/0001-demo").exists())

    def test_REQ_APR_003_N5_invalid_level_refused_by_status(self):
        self.edit("assurance: internal", "assurance: prodution")
        code, out = self.repo.run("status")
        self.assertEqual(code, 1, out)
        self.assert_four_levels(out)

    def test_REQ_APR_003_N6_invalid_level_refused_by_check(self):
        self.as_earlier_version()
        self.mini_ready()
        self.edit("assurance: internal", "assurance: prodution")
        code, out = self.repo.run("check")
        self.assertEqual(code, 1, out)
        self.assert_four_levels(out)

    def test_REQ_APR_003_N7_missing_level_refused_by_new(self):
        text = self.c.read_text()
        self.assertIn("approved: no", text)
        self.c.write_text(re.sub(r"^assurance: .*\n", "", text, count=1, flags=re.M))
        code, out = self.repo.run("new", "demo", "--title", "Demo")
        self.assertEqual(code, 1, out)
        self.assertIn("(missing)", out)
        for level in ("prototype", "internal", "production", "critical"):
            self.assertIn(level, out)
        self.assertFalse((self.repo.root / "specs/changes/0001-demo").exists())

    def test_REQ_APR_003_S4_earlier_version_first_approval_records_level(self):
        self.as_earlier_version()
        self.edit("assurance: internal", "assurance: prototype")
        self.approve()
        text = self.c.read_text()
        self.assertIsNotNone(fingerprint_in(text))
        self.assertIn("approved_level: prototype", text)
        self.assertNotIn("lowered", last_approval_row(text))


# ---------------------------------------------------------------- change 0002-subagent-fanout (ORC, EVD)

def snapshot(root):
    """Every file under root with its bytes: 'no file is changed' compares two snapshots."""
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(Path(root).rglob("*")) if p.is_file()}


def tier_tasks(*tiers):
    """A design line plus one task per entry; an entry is a tier value, a list of values, or None."""
    lines = ["- Test command: `python3 -m unittest`", "", "## Tasks"]
    for n, tier in enumerate(tiers, 1):
        ref = "REQ-DUR-001.S1" if n != 2 else "REQ-DUR-001.N1"
        lines.append(f"- [ ] T{n} {ref} Task {n}")
        for value in ([] if tier is None else [tier] if isinstance(tier, str) else tier):
            lines.append(f"  - tier: {value}")
        lines += ["  - test:", "  - red:", "  - green:"]
    if len(tiers) < 2:  # every scenario needs a task
        lines += ["- [ ] T9 REQ-DUR-001.N1 Reject", "  - tier: light", "  - test:", "  - red:", "  - green:"]
    return "\n".join(lines) + "\n"


class TierTests(Base):
    """REQ-ORC-001: tasks carry a model tier."""

    def setUp(self):
        super().setUp()
        self.init()
        self.cid = self.new()

    def plan(self, *tiers):
        self.repo.fill(self.cid, design_and_tasks=tier_tasks(*tiers))
        return snapshot(self.repo.root)

    def check(self):
        return self.repo.run("check")

    def test_REQ_ORC_001_S1_three_tiers_pass_and_status_counts_them(self):
        self.plan("light", "mid", "strong")
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertNotIn("tier", out.lower())
        self.assertIn("tiers: 1 light, 1 mid, 1 strong", self.repo.ok("status"))
        data = json.loads(self.repo.ok("status", "--json"))
        self.assertEqual(data["change"]["tiers"], {"light": 1, "mid": 1, "strong": 1})

    def test_REQ_ORC_001_S2_escalation_counts_as_the_higher_tier(self):
        self.plan("light → mid", "light")
        code, out = self.check()
        self.assertEqual(code, 0, out)
        data = json.loads(self.repo.ok("status", "--json"))
        self.assertEqual(data["change"]["tiers"], {"light": 1, "mid": 1})

    def test_REQ_ORC_001_S3_chain_counts_as_its_last_tier(self):
        self.plan("light → mid → strong", "light")
        code, out = self.check()
        self.assertEqual(code, 0, out)
        data = json.loads(self.repo.ok("status", "--json"))
        self.assertEqual(data["change"]["tiers"], {"light": 1, "strong": 1})

    def assert_refused(self, *needles):
        before = snapshot(self.repo.root)
        code, out = self.check()
        self.assertEqual(code, 1, out)
        errors = out.split("errors", 1)[1].split("coverage:")[0] if "errors" in out else ""
        for needle in needles:
            self.assertIn(needle, errors)
        self.assertEqual(snapshot(self.repo.root), before)
        return errors

    def test_REQ_ORC_001_N1_unknown_tier_refused(self):
        self.plan("cheap", "light")
        self.assert_refused("T1", "light, mid, strong")

    def test_REQ_ORC_001_N3_capitalised_tier_refused(self):
        self.plan("Light", "light")
        self.assert_refused("T1", "light, mid, strong")

    def test_REQ_ORC_001_N2_downward_escalation_refused(self):
        self.plan("strong → light", "light")
        self.assert_refused("T1", "each step must go up exactly one tier")

    def test_REQ_ORC_001_N5_two_tier_jump_refused(self):
        self.plan("light → strong", "light")
        self.assert_refused("T1", "each step must go up exactly one tier")

    def test_REQ_ORC_001_B1_same_tier_escalation_refused(self):
        self.plan("mid → mid", "light")
        self.assert_refused("T1", "each step must go up exactly one tier")

    def test_REQ_ORC_001_N6_ascii_arrow_refused(self):
        self.plan("light -> mid", "light")
        self.assert_refused("T1", 'an escalation is written with "→"')

    def test_REQ_ORC_001_N4_two_tier_lines_refused(self):
        self.plan(["light", "mid"], "light")
        self.assert_refused("T1 has more than one tier")

    def test_REQ_ORC_001_B2_missing_tier_warns(self):
        before = self.plan(None, "light")
        code, out = self.check()
        self.assertEqual(code, 0, out)
        warnings = out.split("warnings", 1)[1] if "warnings" in out else ""
        self.assertIn("T1: no tier", warnings)
        self.assertEqual(snapshot(self.repo.root), before)

    def test_REQ_ORC_001_B3_status_counts_untiered_tasks(self):
        before = self.plan("light", None)
        self.assertIn("tiers: 1 light, 1 untiered", self.repo.ok("status"))
        self.assertEqual(snapshot(self.repo.root), before)

    def test_REQ_ORC_001_B4_no_tiers_line_without_tasks(self):
        self.repo.fill(self.cid, design_and_tasks="- Test command: `python3 -m unittest`\n\n## Tasks\n")
        self.assertNotIn("tiers", self.repo.ok("status"))
        self.assertNotIn("tiers", json.loads(self.repo.ok("status", "--json"))["change"])


PROD_REQS = VALID_REQS.replace("- N/A state:", "- N/A boundary: the parser accepts any length of input\n"
                               "- N/A access: the parser is a local pure function\n- N/A state:")


def round_headed(runner, number=1):
    return ROUND_DONE.replace("### Round 1 — 2026-10-08 · Critic: same session",
                              f"### Round {number} — 2026-10-08 · Critic: {runner}")


class CriticRunnerTests(Base):
    """REQ-ORC-002: Critic rounds record a subagent runner."""

    def standard(self, level="production"):
        self.init(level)
        self.repo.ok("new", "durations", "--title", "Parse durations", "--size", "standard",
                     "--capability", "duration=DUR")
        self.dir = self.repo.root / "specs/changes/0001-durations"
        set_file_section(self.dir / "spec-delta.md", "Requirements", PROD_REQS)
        set_file_section(self.dir / "spec-delta.md", "Known gaps", "- None\n")

    def clarifications(self):
        return (self.dir / "clarifications.md").read_text()

    def test_REQ_ORC_002_S1_round_subagent_heads_the_round(self):
        self.standard()
        code, out = self.repo.run("round", "--subagent", "strong")
        self.assertEqual(code, 0, out)
        self.assertIn("· Critic: subagent (strong)", self.clarifications())
        self.assertIn("status: clarifying", (self.dir / "proposal.md").read_text())

    def assert_round_refused(self, code_expected, args, needles):
        before = snapshot(self.repo.root)
        code, out = self.repo.run("round", *args)
        self.assertEqual(code, code_expected, out)
        for needle in needles:
            self.assertIn(needle, out)
        self.assertNotIn("### Round", self.clarifications())
        self.assertEqual(snapshot(self.repo.root), before)

    def test_REQ_ORC_002_N1_unknown_subagent_tier_is_a_usage_error(self):
        self.standard()
        self.assert_round_refused(2, ["--subagent", "cheap"], ["'light', 'mid', 'strong'"])

    def test_REQ_ORC_002_N2_subagent_with_fresh_is_a_usage_error(self):
        self.standard()
        self.assert_round_refused(2, ["--subagent", "strong", "--fresh"],
                                  ["--subagent", "--fresh", "not allowed with"])

    def test_REQ_ORC_002_N3_round_after_spec_gate_points_to_amend(self):
        self.standard()
        set_file_section(self.dir / "clarifications.md", "Clarifications",
                         round_headed("fresh session"))
        self.repo.ok("approve", "spec", "--evidence", "Operator: spec ok")
        before = snapshot(self.repo.root)
        code, out = self.repo.run("round", "--subagent", "strong")
        self.assertEqual(code, 1, out)
        self.assertIn("sdd amend", out)
        self.assertNotIn("### Round 2", self.clarifications())
        self.assertEqual(snapshot(self.repo.root), before)

    def runner_warnings(self, clarifications, level="production"):
        """The check's warnings about the Critic's runner, with the files unchanged."""
        self.standard(level)
        set_file_section(self.dir / "clarifications.md", "Clarifications", clarifications)
        before = snapshot(self.repo.root)
        _, out = self.repo.run("check")
        self.assertEqual(snapshot(self.repo.root), before)
        warnings = out.split("warnings", 1)[1].split("coverage:")[0] if "warnings (" in out else ""
        return [w for w in warnings.splitlines() if "Round" in w]

    def test_REQ_ORC_002_S2_strong_subagent_round_is_independent(self):
        self.assertEqual(self.runner_warnings(round_headed("subagent (strong)")), [])

    def assert_not_independent(self, runner):
        warnings = self.runner_warnings(round_headed(runner))
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("runner", warnings[0])
        self.assertIn("is not independent", warnings[0])

    def test_REQ_ORC_002_N4_hand_written_invalid_tier_not_independent(self):
        self.assert_not_independent("subagent (cheap)")

    def test_REQ_ORC_002_B2_subagent_without_tier_not_independent(self):
        self.assert_not_independent("subagent")

    def test_REQ_ORC_002_B3_mid_subagent_not_independent_at_production(self):
        self.assert_not_independent("subagent (mid)")

    def test_REQ_ORC_002_B1_later_same_session_round_warns(self):
        rounds = round_headed("subagent (strong)") + "\n" + round_headed("same session", 2)
        warnings = self.runner_warnings(rounds)
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("Round 2 ran in the same session", warnings[0])

    def test_REQ_ORC_002_B4_no_runner_warning_below_production(self):
        self.assertEqual(self.runner_warnings(round_headed("subagent (light)"), level="internal"), [])


VERIFIER_WARNING = "the Verifier should run in a fresh session or a strong subagent"


class VerifierRunnerTests(Base):
    """REQ-ORC-003: the Verifier's runner is recorded."""

    def verifying(self, verification, level="production"):
        """A mini change in verifying whose Verification section is `verification`."""
        self.init(level)
        cid = self.new()
        self.repo.fill(cid, reqs=PROD_REQS, design_and_tasks=DONE_TASKS)
        self.repo.set_section(cid, "Clarifications", round_headed("fresh session"))
        self.repo.ok("approve", "plan", "--evidence", "Operator: plan ok")
        self.repo.ok("advance", "implementing")
        self.repo.ok("advance", "verifying")
        self.repo.write("tests/test_dur.py", "REQ_DUR_001_S1 REQ_DUR_001_N1")
        self.repo.set_section(cid, "Verification", verification + "\nVerdict: PASS\n")
        return cid

    def verify_check(self, *args):
        before = snapshot(self.repo.root)
        code, out = self.repo.run("check", *args)
        self.assertEqual(snapshot(self.repo.root), before)
        return code, out

    def test_REQ_ORC_003_N1_same_session_verifier_warns(self):
        self.verifying("- Date: 2026-10-14 · Verifier: same session (production)")
        code, out = self.verify_check("--stage", "verify")
        self.assertIn(VERIFIER_WARNING, out)
        self.assertEqual(code, 0, out)

    def test_REQ_ORC_003_N2_missing_verifier_line_warns(self):
        self.verifying("- Date: 2026-10-14 · ran the suite")
        _, out = self.verify_check("--stage", "verify")
        self.assertIn(VERIFIER_WARNING, out)

    def assert_no_verifier_warning(self, *check_args):
        code, out = self.verify_check(*check_args)
        self.assertNotIn("Verifier", out)
        return code, out

    def test_REQ_ORC_003_S1_strong_subagent_verifier(self):
        self.verifying("- Date: 2026-10-14 · Verifier: subagent (strong)")
        self.assert_no_verifier_warning("--stage", "verify")

    def test_REQ_ORC_003_S2_fresh_session_verifier(self):
        self.verifying("- Date: 2026-10-14 · Verifier: fresh session (production)")
        self.assert_no_verifier_warning("--stage", "verify")

    def test_REQ_ORC_003_B4_verifier_line_in_any_case(self):
        self.verifying("- Date: 2026-10-14 · verifier: Fresh Session")
        self.assert_no_verifier_warning("--stage", "verify")

    def test_REQ_ORC_003_N3_invalid_tier_verifier_warns(self):
        self.verifying("- Date: 2026-10-14 · Verifier: subagent (cheap)")
        _, out = self.verify_check("--stage", "verify")
        self.assertIn(VERIFIER_WARNING, out)

    def test_REQ_ORC_003_N5_mid_subagent_verifier_warns(self):
        self.verifying("- Date: 2026-10-14 · Verifier: subagent (mid)")
        _, out = self.verify_check("--stage", "verify")
        self.assertIn(VERIFIER_WARNING, out)

    def test_REQ_ORC_003_N4_no_verifier_warning_in_draft(self):
        self.init("production")
        cid = self.new()
        self.repo.fill(cid, reqs=PROD_REQS, design_and_tasks=VALID_TASKS, verdict=None)
        self.assert_no_verifier_warning()

    def test_REQ_ORC_003_B1_no_verifier_warning_below_production(self):
        self.verifying("- Date: 2026-10-14 · Verifier: same session (internal)", level="internal")
        self.assert_no_verifier_warning("--stage", "verify")

    def test_REQ_ORC_003_B2_latest_verifier_line_counts(self):
        self.verifying("- Date: 2026-10-12 · Verifier: fresh session (production)\n"
                       "- Date: 2026-10-14 · Verifier: same session (production)")
        _, out = self.verify_check("--stage", "verify")
        self.assertIn(VERIFIER_WARNING, out)

    def test_REQ_ORC_003_B3_verifier_line_in_comment_ignored(self):
        self.verifying("- Date: 2026-10-14 · Verifier: same session (production)\n"
                       "<!-- Verifier: subagent (strong) -->")
        _, out = self.verify_check("--stage", "verify")
        self.assertIn(VERIFIER_WARNING, out)

    def test_REQ_ORC_003_B3_verifier_line_in_fenced_code_ignored(self):
        self.verifying("- Date: 2026-10-14 · Verifier: same session (production)\n"
                       "```\nVerifier: subagent (strong)\n```")
        _, out = self.verify_check("--stage", "verify")
        self.assertIn(VERIFIER_WARNING, out)


MUTATION_OK = """\
- M1 REQ-DUR-001.N1 src/dur.py
  - find: `return 0`
  - replace: `return 1`
"""


class MutationsCheckTests(Base):
    """REQ-EVD-002: the change lists its planned mutations."""

    def setUp(self):
        super().setUp()
        self.init()
        self.cid = self.new()

    def mutations(self, body):
        self.repo.fill(self.cid, design_and_tasks=VALID_TASKS + "\n## Mutations\n" + body)

    def assert_mutation_error(self, body, *needles):
        self.mutations(body)
        before = snapshot(self.repo.root)
        code, out = self.repo.run("check")
        self.assertEqual(code, 1, out)
        errors = out.split("errors", 1)[1].split("coverage:")[0] if "errors (" in out else ""
        line = next((l for l in errors.splitlines() if "M1" in l), "")
        for needle in needles:
            self.assertIn(needle, line, errors)
        self.assertEqual(snapshot(self.repo.root), before)

    def test_REQ_EVD_002_N1_missing_replace_is_an_error(self):
        self.assert_mutation_error(MUTATION_OK.replace("  - replace: `return 1`\n", ""), "M1", "replace")

    def assert_no_mutation_error(self, body):
        self.mutations(body)
        code, out = self.repo.run("check")
        self.assertEqual(code, 0, out)
        self.assertNotIn("M1", out)

    def test_REQ_EVD_002_S1_complete_entry_accepted(self):
        self.assert_no_mutation_error(MUTATION_OK)

    def test_REQ_EVD_002_B3_empty_replace_accepted(self):
        self.assert_no_mutation_error(MUTATION_OK.replace("`return 1`", "``"))

    def test_REQ_EVD_002_N3_missing_file_is_an_error(self):
        self.assert_mutation_error(MUTATION_OK.replace(" src/dur.py", ""), "M1", "file")

    def test_REQ_EVD_002_N7_find_without_backticks_is_an_error(self):
        self.assert_mutation_error(MUTATION_OK.replace("`return 0`", "return 0"), "M1", "find")

    def test_REQ_EVD_002_N2_scenario_outside_the_change_is_an_error(self):
        self.assert_mutation_error(MUTATION_OK.replace("REQ-DUR-001.N1", "REQ-DUR-001.N9"),
                                   "M1", "REQ-DUR-001.N9")

    def test_REQ_EVD_002_N4_duplicate_id_is_an_error(self):
        self.assert_mutation_error(MUTATION_OK + MUTATION_OK.replace("return 1", "return 2"),
                                   "M1", "duplicate")

    def test_REQ_EVD_002_N5_path_leaving_the_project_is_an_error(self):
        self.assert_mutation_error(MUTATION_OK.replace("src/dur.py", "../x.py"), "M1", "../x.py")

    def test_REQ_EVD_002_N6_absolute_path_is_an_error(self):
        self.assert_mutation_error(MUTATION_OK.replace("src/dur.py", "/src/dur.py"), "M1", "/src/dur.py")

    def test_REQ_EVD_002_B2_replace_equal_to_find_is_an_error(self):
        self.assert_mutation_error(MUTATION_OK.replace("`return 1`", "`return 0`"), "M1", "changes nothing")

    def test_REQ_EVD_002_B1_no_mutations_section_no_error(self):
        self.repo.fill(self.cid)
        code, out = self.repo.run("check")
        self.assertEqual(code, 0, out)
        self.assertNotIn("M1", out)

    def test_REQ_EVD_002_B4_mutations_not_counted_toward_the_size_cap(self):
        self.repo.ok("new", "durations", "--title", "Parse durations", "--size", "standard",
                     "--capability", "duration=DUR")
        tasks = self.repo.root / "specs/changes/0002-durations/tasks.md"
        before = json.loads(self.repo.ok("status", "--json"))["change"]["lines"]
        entries = "".join(MUTATION_OK.replace("M1", f"M{n}") for n in range(1, 11))  # 30 lines
        tasks.write_text(tasks.read_text() + "\n## Mutations\n" + entries)
        state = snapshot(self.repo.root)
        self.assertEqual(json.loads(self.repo.ok("status", "--json"))["change"]["lines"], before)
        self.assertEqual(snapshot(self.repo.root), state)



# A test runner for the git fixtures: test NAME passes when src/dur.py contains NAME.
CHECKER = """import sys
from pathlib import Path
source = Path("src/dur.py")
sys.exit(0 if source.exists() and sys.argv[1] in source.read_text() else 1)
"""
GIT = ["git", "-c", "user.name=sdd-test", "-c", "user.email=test@example.invalid"]


def git(root, *args):
    return subprocess.run([*GIT, *args], cwd=root, capture_output=True, text=True, check=True).stdout


def tree_state(root):
    """git status plus every file outside .git: 'the working tree is unchanged' compares two."""
    files = {str(p.relative_to(root)): p.read_bytes() for p in sorted(Path(root).rglob("*"))
             if p.is_file() and ".git" not in p.relative_to(root).parts}
    return git(root, "status", "--porcelain"), files


class GitFixture(Base):
    """A project in a git repository: base commit, then working-tree edits."""

    TEST_ONE = f"{shlex.quote(sys.executable)} -B tests/check.py {{name}}"

    def setUp(self):
        super().setUp()
        self.scratch = Path(tempfile.mkdtemp(prefix="sdd-test-scratch-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(self.scratch, ignore_errors=True))
        patcher = mock.patch.object(tempfile, "tempdir", str(self.scratch))
        patcher.start()
        self.addCleanup(patcher.stop)
        env = mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(self.repo.root.parent)})
        env.start()
        self.addCleanup(env.stop)
        self.init()
        self.cid = self.new()

    def project(self, tasks, base="", now=None, test_one=None, git_repo=True, mutations=None):
        """tasks: (ticked, test_line, red) triples. src/dur.py holds `base` at the base commit
        and `now` in the working tree. Returns the base revision."""
        lines = ["- Test command: `python3 -m unittest`"]
        if test_one is not False:
            lines.append(f"- Test one: `{test_one or self.TEST_ONE}`")
        lines += ["", "## Tasks"]
        for n, (ticked, test_line, red, *ref) in enumerate(tasks, 1):
            ref = ref[0] if ref else "REQ-DUR-001.S1" if n == 1 else "REQ-DUR-001.N1"
            lines += [f"- [{'x' if ticked else ' '}] T{n} {ref} Task {n}", "  - tier: light",
                      f"  - test: {test_line}", f"  - red: {red}", "  - green: 1 passed"]
        if mutations is not None:
            lines += ["", "## Mutations", mutations]
        self.repo.fill(self.cid, design_and_tasks="\n".join(lines) + "\n")
        self.repo.write("tests/check.py", CHECKER)
        self.repo.write("src/dur.py", base)
        rev = None
        if git_repo:
            git(self.repo.root, "init", "-q")
            git(self.repo.root, "add", "-A")
            git(self.repo.root, "commit", "-qm", "base")
            rev = git(self.repo.root, "rev-parse", "HEAD").strip()
        self.repo.write("src/dur.py", base if now is None else now)
        return rev

    def run_tool(self, *args):
        """Run sdd with the tree state captured before and after; scratch must end empty."""
        before = tree_state(self.repo.root) if (self.repo.root / ".git").exists() else None
        code, out = self.repo.run(*args)
        if before is not None:
            self.assertEqual(tree_state(self.repo.root), before, "the working tree changed")
        self.assertEqual(os.listdir(self.scratch), [], "a scratch copy was left")
        return code, out


RED = "AssertionError: rule missing"
PRE = "pre-existing — the rule was already there"


class ReplayTests(GitFixture):
    """REQ-EVD-001: replay the tests against the base revision."""

    def test_REQ_EVD_001_S1_red_task_confirmed(self):
        rev = self.project([(True, "tests/check.py::rule_a", RED)], base="", now="rule_a")
        code, out = self.run_tool("replay", "--base", rev)
        self.assertEqual(code, 0, out)
        self.assertIn("T1 confirmed", out)

    def test_REQ_EVD_001_N1_red_claimed_but_passes_at_base(self):
        rev = self.project([(True, "tests/check.py::rule_a", RED)], base="rule_a", now="rule_a")
        code, out = self.run_tool("replay", "--base", rev)
        self.assertEqual(code, 1, out)
        self.assertIn("T1 mismatch: red claimed, but the test passes at the base", out)

    def test_REQ_EVD_001_N3_test_fails_now(self):
        rev = self.project([(True, "tests/check.py::rule_a", RED)], base="", now="")
        code, out = self.run_tool("replay", "--base", rev)
        self.assertEqual(code, 1, out)
        self.assertIn("T1 mismatch: the test fails now", out)

    def test_REQ_EVD_001_S2_pre_existing_task_confirmed(self):
        rev = self.project([(True, "tests/check.py::rule_a", PRE)], base="rule_a", now="rule_a")
        code, out = self.run_tool("replay", "--base", rev)
        self.assertEqual(code, 0, out)
        self.assertIn("T1 confirmed", out)

    def test_REQ_EVD_001_N2_pre_existing_claimed_but_fails_at_base(self):
        rev = self.project([(True, "tests/check.py::rule_a", PRE)], base="", now="rule_a")
        code, out = self.run_tool("replay", "--base", rev)
        self.assertEqual(code, 1, out)
        self.assertIn("T1 mismatch: pre-existing claimed, but the test fails at the base", out)

    def refused_before_any_test(self, *args):
        with mock.patch.object(sdd, "run_test", wraps=sdd.run_test) as runner:
            code, out = self.run_tool(*args)
        self.assertEqual(code, 1, out)
        self.assertEqual(runner.call_count, 0, out)
        return out

    def test_REQ_EVD_001_N4_no_test_one_line(self):
        rev = self.project([(True, "tests/check.py::rule_a", RED)], now="rule_a", test_one=False)
        self.assertIn('"Test one:"', self.refused_before_any_test("replay", "--base", rev))

    def test_REQ_EVD_001_N5_unknown_base_revision(self):
        self.project([(True, "tests/check.py::rule_a", RED)], now="rule_a")
        out = self.refused_before_any_test("replay", "--base", "nosuchrev")
        self.assertIn("nosuchrev", out)
        self.assertNotIn("Traceback", out)

    def test_REQ_EVD_001_N6_not_a_git_repository(self):
        self.project([(True, "tests/check.py::rule_a", RED)], now="rule_a", git_repo=False)
        before = snapshot(self.repo.root)
        out = self.refused_before_any_test("replay", "--base", "HEAD")
        self.assertIn("replay needs a git repository", out)
        self.assertEqual(snapshot(self.repo.root), before)

    def test_REQ_EVD_001_N7_missing_runner_fails_every_task(self):
        rev = self.project([(True, "tests/check.py::rule_a", RED), (True, "tests/check.py::rule_b", RED)],
                           now="rule_a rule_b", test_one="no-such-runner {test}")
        code, out = self.run_tool("replay", "--base", rev)
        self.assertEqual(code, 1, out)
        self.assertIn("T1 mismatch: the test fails now", out)
        self.assertIn("T2 mismatch: the test fails now", out)

    def mismatch_without_running(self, test_line, reason, test_one=None):
        rev = self.project([(True, test_line, RED)], now="rule_a", test_one=test_one)
        with mock.patch.object(sdd, "run_test", wraps=sdd.run_test) as runner:
            code, out = self.run_tool("replay", "--base", rev)
        self.assertEqual(code, 1, out)
        self.assertIn(f"T1 mismatch: {reason}", out)
        self.assertEqual(runner.call_count, 0, out)

    def test_REQ_EVD_001_N8_ticked_task_without_test_line(self):
        self.mismatch_without_running("", "no test to run")

    def test_REQ_EVD_001_N9_test_line_without_separator(self):
        self.mismatch_without_running("tests/t_x.py", 'the test line has no "::"',
                                      test_one="runner {file} {name}")

    def test_REQ_EVD_001_N10_replay_without_base_is_a_usage_error(self):
        self.project([(True, "tests/check.py::rule_a", RED)], now="rule_a")
        with mock.patch.object(sdd, "run_test", wraps=sdd.run_test) as runner:
            code, out = self.run_tool("replay")
        self.assertEqual(code, 2, out)
        self.assertIn("--base", out)
        self.assertEqual(runner.call_count, 0, out)

    def test_REQ_EVD_001_B1_unticked_task_skipped(self):
        rev = self.project([(True, "tests/check.py::rule_a", RED), (False, "tests/check.py::rule_b", "")],
                           now="rule_a")
        with mock.patch.object(sdd, "run_test", wraps=sdd.run_test) as runner:
            code, out = self.run_tool("replay", "--base", rev)
        self.assertEqual(code, 0, out)
        self.assertIn("T2 skipped", out)
        self.assertEqual(runner.call_count, 2, out)  # T1 at the base and now; T2 never

    def test_REQ_EVD_001_B2_nothing_ticked(self):
        rev = self.project([(False, "tests/check.py::rule_a", "")], now="rule_a")
        code, out = self.run_tool("replay", "--base", rev)
        self.assertEqual(code, 0, out)
        self.assertIn("nothing to replay", out)

    def test_REQ_EVD_001_B3_file_and_name_substituted_and_printed(self):
        rev = self.project([(True, "tests/t_x.py::Cases.test_a", RED)], now="rule_a",
                           test_one="runner {file} {name}")
        _, out = self.run_tool("replay", "--base", rev)
        self.assertIn("runner tests/t_x.py Cases.test_a", out)

    def test_REQ_EVD_001_B4_untracked_fixture_laid_over_base(self):
        self.repo.write("tests/fixture_check.py", CHECKER.replace('"src/dur.py"', '"tests/fixtures/f.json"'))
        rev = self.project([(True, "tests/fixture_check.py::rule_a", PRE)],
                           test_one=f"{shlex.quote(sys.executable)} -B {{file}} {{name}}")
        self.repo.write("tests/fixtures/f.json", '{"rule": "rule_a"}')  # untracked, not ignored
        code, out = self.run_tool("replay", "--base", rev)
        self.assertEqual(code, 0, out)
        self.assertIn("T1 confirmed", out)

    def replay_recording(self, rev):
        """Run replay; return (code, out, [(test name, ran at the base?)])."""
        calls = []
        real = sdd.run_test

        def record(argv, cwd):
            calls.append((argv[-1], Path(cwd).resolve() != self.repo.root.resolve()))
            return real(argv, cwd)
        with mock.patch.object(sdd, "run_test", side_effect=record):
            code, out = self.run_tool("replay", "--base", rev)
        return code, out, calls

    def test_REQ_EVD_001_S3_pre_existing_after_earlier_task(self):
        rev = self.project([(True, "tests/check.py::rule_a", RED),
                            (True, "tests/check.py::rule_b", "pre-existing (after T1) — T1's code already does it")],
                           now="rule_a rule_b")
        code, out, calls = self.replay_recording(rev)
        self.assertEqual(code, 0, out)
        self.assertIn("T2 confirmed now (depends on T1)", out)
        self.assertNotIn(("rule_b", True), calls)

    def test_REQ_EVD_001_N11_dependent_task_fails_now(self):
        rev = self.project([(True, "tests/check.py::rule_a", RED),
                            (True, "tests/check.py::rule_b", "AssertionError (after T1): warning shown")],
                           now="rule_a")
        code, out, _ = self.replay_recording(rev)
        self.assertEqual(code, 1, out)
        self.assertIn("T2 mismatch: the test fails now", out)

    def test_REQ_EVD_001_B5_later_task_is_not_a_dependency(self):
        rev = self.project([(True, "tests/check.py::rule_a", "pre-existing (after T2) — see T2"),
                            (True, "tests/check.py::rule_b", RED)],
                           now="rule_a rule_b")
        code, out, calls = self.replay_recording(rev)
        self.assertEqual(code, 1, out)
        self.assertIn("T1 mismatch: pre-existing claimed, but the test fails at the base", out)
        self.assertIn(("rule_a", True), calls)

    def test_REQ_EVD_001_B6_task_id_without_marker_is_not_a_dependency(self):
        rev = self.project([(True, "tests/check.py::rule_a", RED),
                            (True, "tests/check.py::rule_b", "AssertionError: 'T1 skipped' not found")],
                           base="rule_b", now="rule_a rule_b")
        code, out, calls = self.replay_recording(rev)
        self.assertEqual(code, 1, out)
        self.assertIn("T2 mismatch: red claimed, but the test passes at the base", out)
        self.assertIn(("rule_b", True), calls)

    def test_REQ_EVD_001_S4_red_after_earlier_task(self):
        rev = self.project([(True, "tests/check.py::rule_a", RED),
                            (True, "tests/check.py::rule_b", "AssertionError (after T1): warning shown")],
                           base="rule_b", now="rule_a rule_b")
        code, out, calls = self.replay_recording(rev)
        self.assertEqual(code, 0, out)
        self.assertIn("T2 confirmed now (depends on T1)", out)
        self.assertNotIn(("rule_b", True), calls)



def mutation(find="rule_a", replace="rule_x", scenario="REQ-DUR-001.S1", file="src/dur.py", mid="M1"):
    return f"- {mid} {scenario} {file}\n  - find: `{find}`\n  - replace: `{replace}`\n"


class MutateTests(GitFixture):
    """REQ-EVD-003: run the planned mutations."""

    def test_REQ_EVD_003_S1_mutation_caught(self):
        self.project([(True, "tests/check.py::rule_a", RED)], now="rule_a", mutations=mutation())
        code, out = self.run_tool("mutate")
        self.assertEqual(code, 0, out)
        self.assertIn("M1 caught", out)

    def test_REQ_EVD_003_N1_mutation_survived(self):
        self.project([(True, "tests/check.py::rule_a", RED)], now="rule_a",
                     mutations=mutation(replace="rule_a and more"))
        code, out = self.run_tool("mutate")
        self.assertEqual(code, 1, out)
        self.assertIn("M1 survived", out)

    def test_REQ_EVD_003_N2_test_fails_without_the_mutation(self):
        self.project([(True, "tests/check.py::rule_b", RED)], now="rule_a", mutations=mutation())
        code, out = self.run_tool("mutate")
        self.assertEqual(code, 1, out)
        self.assertIn("M1 invalid: the test fails without the mutation", out)

    def invalid_without_running(self, reason, now="rule_a", tasks=None, **mutation_args):
        self.project(tasks or [(True, "tests/check.py::rule_a", RED)], now=now,
                     mutations=mutation(**mutation_args))
        with mock.patch.object(sdd, "run_test", wraps=sdd.run_test) as runner:
            code, out = self.run_tool("mutate")
        self.assertEqual(code, 1, out)
        self.assertIn(f"M1 invalid: {reason}", out)
        self.assertEqual(runner.call_count, 0, out)

    def test_REQ_EVD_003_N3_find_text_not_in_file(self):
        self.invalid_without_running("the find text is not in the file", find="rule_z")

    def test_REQ_EVD_003_N4_find_text_found_twice(self):
        self.invalid_without_running("the find text occurs 2 times", now="rule_a\nrule_a\n")

    def test_REQ_EVD_003_N5_no_test_one_line(self):
        self.project([(True, "tests/check.py::rule_a", RED)], now="rule_a", test_one=False,
                     mutations=mutation())
        with mock.patch.object(sdd, "run_test", wraps=sdd.run_test) as runner:
            code, out = self.run_tool("mutate")
        self.assertEqual(code, 1, out)
        self.assertIn('"Test one:"', out)
        self.assertEqual(runner.call_count, 0, out)

    def test_REQ_EVD_003_N6_file_does_not_exist(self):
        self.invalid_without_running("the file doesn't exist", file="src/gone.py")

    def test_REQ_EVD_003_N7_task_without_test_line(self):
        self.invalid_without_running("no test to run", tasks=[(True, "", RED)])

    def test_REQ_EVD_003_N9_scenario_no_task_plans(self):
        self.invalid_without_running("no test to run", scenario="REQ-DUR-001.N1",
                                     tasks=[(True, "tests/check.py::rule_a", RED)])

    def test_REQ_EVD_003_N8_not_a_git_repository(self):
        self.project([(True, "tests/check.py::rule_a", RED)], now="rule_a", git_repo=False,
                     mutations=mutation())
        before = snapshot(self.repo.root)
        with mock.patch.object(sdd, "run_test", wraps=sdd.run_test) as runner:
            code, out = self.run_tool("mutate")
        self.assertEqual(code, 1, out)
        self.assertIn("mutate needs a git repository", out)
        self.assertEqual(runner.call_count, 0, out)
        self.assertEqual(snapshot(self.repo.root), before)

    def test_REQ_EVD_003_B1_no_mutations_section(self):
        self.project([(True, "tests/check.py::rule_a", RED)], now="rule_a")
        code, out = self.run_tool("mutate")
        self.assertEqual(code, 0, out)
        self.assertIn("no mutations are planned", out)

    def test_REQ_EVD_003_B2_one_caught_one_survived(self):
        self.project([(True, "tests/check.py::rule_a", RED)], now="rule_a",
                     mutations=mutation() + mutation(replace="rule_a and more", mid="M2"))
        code, out = self.run_tool("mutate")
        self.assertEqual(code, 1, out)
        self.assertIn("M1 caught", out)
        self.assertIn("M2 survived", out)

    def test_REQ_EVD_003_B3_leading_spaces_kept(self):
        self.project([(True, "tests/check.py::x_marker", RED)], now="    x_marker\nx_mark\n",
                     mutations=mutation(find="    x_mark", replace="    y_mark"))
        code, out = self.run_tool("mutate")
        self.assertEqual(code, 0, out)
        self.assertIn("M1 caught", out)

    def test_REQ_EVD_003_B4_scenario_planned_by_two_tasks(self):
        self.project([(True, "tests/check.py::rule_a", RED),
                      (True, "tests/check.py::rule_b", RED, "REQ-DUR-001.S1")],
                     now="rule_a rule_b", mutations=mutation())
        code, out = self.run_tool("mutate")
        self.assertEqual(code, 0, out)
        self.assertIn("M1 caught", out)


if __name__ == "__main__":
    unittest.main()
