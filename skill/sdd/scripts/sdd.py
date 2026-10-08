#!/usr/bin/env python3
"""sdd.py — deterministic helper for the SDD skill (Python 3 standard library only).

Agents call this script for everything that must not depend on judgment:
IDs, status transitions, approvals, coverage checks and archiving. It runs the
same way from Claude Code, Codex, a git hook or a terminal.

    python3 sdd.py init --assurance internal
    python3 sdd.py new parse-duration --title "Parse durations" --capability duration=DUR
    python3 sdd.py status [--json]
    python3 sdd.py check [--stage spec|plan|implement|verify]
    python3 sdd.py approve plan --evidence "Operator in chat: 'approve'"
    python3 sdd.py advance implementing
    python3 sdd.py archive
    python3 sdd.py next-req DUR
    python3 sdd.py use 0002-other-change
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"

LEVELS = ["prototype", "internal", "production", "critical"]
LEVEL_MEANING = {
    "prototype": "Demo, experiment or learning; may be thrown away. Happy-path tests come "
                 "first, and each change keeps a Known gaps list instead of failure cases.",
    "internal": "Used by you or your team, with real data and a small blast radius. Every "
                "scenario is test-first; bad input, wrong state and dependency failures are covered.",
    "production": "External users or business data that must persist. The six core failure "
                  "categories are covered, and review and verification are independent.",
    "critical": "Money, security, safety, regulation or irreversible effects. Production rigor "
                "plus concurrency, rule combinations and invariants.",
}

CATEGORIES = {
    "happy": "Happy path",
    "validation": "Input validation",
    "boundary": "Boundaries",
    "state": "State & sequence",
    "access": "Access",
    "dependency": "Dependency failure",
    "concurrency": "Concurrency",
    "combination": "Rule combinations",
    "invariant": "Invariants",
}
REQUIRED = {
    "prototype": ["happy"],
    "internal": ["happy", "validation", "state", "dependency"],
    "production": ["happy", "validation", "boundary", "state", "access", "dependency"],
    "critical": list(CATEGORIES),
}

SIZE_CAPS = {"mini": 200, "standard": 400, "full": 800}
SIZES_AVAILABLE = ["mini", "standard"]
STANDARD_FILES = ["proposal.md", "spec-delta.md", "design.md", "tasks.md", "verification.md"]
TYPES = ["feature", "defect", "hardening"]
STATUS_ORDER = ["draft", "clarifying", "spec-approved", "designed", "planned",
                "implementing", "verifying", "verified", "archived"]
STATUSES = STATUS_ORDER + ["blocked", "abandoned"]
UNLOCKED_STATUSES = {"draft", "clarifying"}
TERMINAL = {"archived", "abandoned"}
# Moves `advance` may make; gates (approve spec/plan/results) are the only other way forward.
TRANSITIONS = {
    "mini": {
        "planned": {"implementing"},
        "implementing": {"verifying"},
        "verifying": {"implementing", "verified"},
    },
    "standard": {
        "draft": {"clarifying"},
        "clarifying": {"draft"},
        "spec-approved": {"designed"},
        "planned": {"implementing"},
        "implementing": {"verifying"},
        "verifying": {"implementing"},
    },
}
# Every status at or past the first one requires that gate's approval record.
REQUIRED_APPROVALS = {
    "mini": [("planned", "plan")],
    "standard": [("spec-approved", "spec"), ("planned", "plan"), ("verified", "results")],
}
AMENDABLE = {"spec-approved", "designed", "planned", "implementing", "verifying"}
STAGES = ["spec", "plan", "implement", "verify"]

REQ_HEAD = re.compile(
    r"^### (REQ-([A-Z][A-Z0-9]{1,5})-(\d{3,}))(?:\s+\[(MODIFIED|REMOVED)\])?\s*(.*)$")
REQ_TOKEN = re.compile(r"REQ-([A-Z][A-Z0-9]{1,5})-(\d{3,})")
SCENARIO_REF = re.compile(r"REQ-[A-Z][A-Z0-9]{1,5}-\d{3,}\.[A-Z]\d+")
TASK_LINE = re.compile(r"^\s*[-*]\s*\[( |x|X)\]\s*(.*)$")
TASK_ID = re.compile(r"^(T\d+)\b(.*)$")
EVIDENCE_LINE = re.compile(r"^\s+[-*]\s*(test|red|green)\s*:\s*(.*)$", re.I)
NA_LINE = re.compile(r"^\s*[-*]\s*N/A\s+([A-Za-z-]+)\s*(?::|—|–|\s-\s)\s*(.*)$", re.I)
REASON_LINE = re.compile(r"^\s*Reason\s*:\s*(.+)$", re.I)
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CAP_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PREFIX = re.compile(r"^[A-Z][A-Z0-9]{1,5}$")
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
PLACEHOLDERS = {"", "-", "…", "...", "todo", "tbd", "n/a"}
FAILURE_WORDS = re.compile(r"fail|error|assert|expected|exception|traceback|raise|panic|"
                           r"not equal|!=|mismatch|undefined|cannot|missing|not found", re.I)
SETUP_ERRORS = re.compile(r"ImportError|ModuleNotFoundError|SyntaxError|IndentationError|"
                          r"Cannot find module|command not found", re.I)
UNCOUNTED_SECTIONS = ("Verification", "Amendments", "Approvals")
LOCKED_SECTIONS = ("Intent", "Defect", "Scope", "Requirements", "Known gaps")
DEFECT_FIELDS = ("Symptom", "Reproduce", "Current behavior", "Expected behavior", "Violates")
DEFECT_FIELD = re.compile(r"^\s*[-*]\s*([A-Za-z][A-Za-z ]*?)\s*:\s*(.*)$")
AMENDMENT_ENTRY = re.compile(r"^\s*[-*]\s*A\d+\b")
LOCK_ERROR = "the spec changed since it was approved"
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
             ".tox", ".mypy_cache", ".pytest_cache", "target", ".next"}
CHANGE_KEYS = ["id", "title", "type", "size", "assurance", "status", "capabilities", "created"]


class SddError(Exception):
    """A user-facing failure: printed as 'error: ...' with exit code 1."""


# ---------------------------------------------------------------- text helpers

def today() -> str:
    return dt.date.today().isoformat()


def strip_comments(text: str) -> str:
    """Remove HTML comments: template guidance never counts as content."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def counted_lines(text: str) -> int:
    """Spec length for the size cap: comments, Verification and Approvals don't count."""
    clean = strip_comments(text)
    for name in UNCOUNTED_SECTIONS:
        clean = re.sub(rf"^## {name}\n.*?(?=^## |\Z)", "", clean, flags=re.S | re.M)
    return len(clean.splitlines())


def spec_hash(text: str) -> str:
    """Fingerprint of the approved contract: the locked sections, whitespace-normalized."""
    secs = sections(strip_comments(text))
    parts = []
    for name in LOCKED_SECTIONS:
        lines = [" ".join(line.split()) for line in secs.get(name, "").splitlines() if line.strip()]
        parts.append(name + "\n" + "\n".join(lines))
    return hashlib.sha256("\n\n".join(parts).encode()).hexdigest()[:12]


def is_test_path(rel: str) -> bool:
    """True for files that, by common convention, hold tests."""
    parts = rel.replace("\\", "/").split("/")
    name, folders = parts[-1], [p.lower() for p in parts[:-1]]
    stem = name.split(".")[0]
    return (any(f in ("test", "tests", "__tests__", "spec", "testing") for f in folders)
            or name.lower().startswith(("test_", "test."))
            or bool(re.search(r"_(test|spec)$", stem.lower()))
            or bool(re.search(r"\.(test|spec)\.[^.]+$", name.lower()))
            or bool(re.search(r"(Test|Tests|Spec)$", stem)))


def read_front_matter(text: str) -> dict:
    match = FRONT_MATTER.match(text)
    if not match:
        return {}
    data = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def set_front_matter(text: str, key: str, value: str) -> str:
    match = FRONT_MATTER.match(text)
    if not match:
        raise SddError("file has no front matter")
    block = match.group(1)
    line = f"{key}: {value}"
    if re.search(rf"^{re.escape(key)}:.*$", block, re.M):
        block = re.sub(rf"^{re.escape(key)}:.*$", lambda _: line, block, count=1, flags=re.M)
    else:
        block += "\n" + line
    return f"---\n{block}\n---\n" + text[match.end():]


def change_text(path: Path) -> str:
    """The whole change as one document. A standard change is proposal.md plus its
    sibling files (content from their first '## ' heading on), in a fixed order."""
    text = path.read_text()
    if path.name != "proposal.md":
        return text
    parts = [text.rstrip("\n")]
    for name in STANDARD_FILES[1:]:
        extra = path.parent / name
        if extra.exists():
            body = extra.read_text()
            start = re.search(r"^## ", body, re.M)
            parts.append(body[start.start():].rstrip("\n") if start else "")
    return "\n\n".join(parts) + "\n"


def test_command(clean_text: str) -> str:
    match = re.search(r"Test command\s*:[ \t]*(.*)", clean_text)
    return match.group(1).strip().strip("`").strip() if match else ""


def drop_front_matter(text: str, key: str) -> str:
    match = FRONT_MATTER.match(text)
    if not match:
        return text
    block = re.sub(rf"^{re.escape(key)}:.*\n?", "", match.group(1) + "\n", flags=re.M).rstrip("\n")
    return f"---\n{block}\n---\n" + text[match.end():]


def approvals(text: str) -> list:
    """Gate names recorded in the '## Approvals' table."""
    rows = []
    for line in sections(strip_comments(text)).get("Approvals", "").splitlines():
        cells = table_cells(line) if line.strip().startswith("|") else []
        if cells and not is_separator(cells) and cells[0].lower() != "gate":
            rows.append(cells[0])
    return rows


def sections(text: str) -> dict:
    """Map each top-level '## Name' heading to its body (front matter excluded)."""
    body = text[FRONT_MATTER.match(text).end():] if FRONT_MATTER.match(text) else text
    result, name, lines = {}, None, []
    for line in body.splitlines():
        if line.startswith("## "):
            if name is not None:
                result[name] = "\n".join(lines)
            name, lines = line[3:].strip(), []
        elif name is not None:
            lines.append(line)
    if name is not None:
        result[name] = "\n".join(lines)
    return result


def table_cells(line: str) -> list:
    """Split a markdown table row on unescaped pipes."""
    parts = re.split(r"(?<!\\)\|", line.strip())
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip().replace("\\|", "|") for p in parts]


def is_separator(cells: list) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c) for c in cells)


def has_bullet(text: str) -> bool:
    return any(re.match(r"^\s*[-*]\s+\S", line) for line in text.splitlines())


def evidence_present(value: str) -> bool:
    value = value.strip()
    return value.lower() not in PLACEHOLDERS and not value.startswith("<")


def scenario_pattern(ref: str) -> re.Pattern:
    """REQ-DUR-001.S1 matches test_REQ_DUR_001_S1, req_dur_001_s1, 'REQ-DUR-001.S1 ...'."""
    req, scen = ref.split(".")
    _, prefix, number = req.split("-")
    return re.compile(rf"REQ[-_]{prefix}[-_]{number}[-_.]{scen}(?![0-9])", re.I)


# ---------------------------------------------------------------- requirement parsing

class Requirement:
    def __init__(self, rid, prefix, number, tag, title, lines):
        self.id, self.prefix, self.number = rid, prefix, int(number)
        self.tag, self.title = tag, title  # tag: None (added), MODIFIED or REMOVED
        self.statement, self.scenarios, self.na, self.reason = [], [], {}, None
        self.problems = []  # structural errors found while parsing
        self.raw_lines = lines
        self._parse(lines[1:])

    def _parse(self, lines):
        header_seen = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("|"):
                cells = table_cells(stripped)
                if not header_seen:
                    if [c.lower() for c in cells] == ["id", "category", "given", "when", "then"]:
                        header_seen = True
                    else:
                        self.problems.append(
                            "scenario table header must be | ID | Category | Given | When | Then |")
                        header_seen = True  # report once
                    continue
                if is_separator(cells):
                    continue
                if len(cells) != 5:
                    self.problems.append(f"scenario row needs 5 cells: {stripped}")
                    continue
                sid, cat, given, when, then = cells
                self.scenarios.append({"id": sid, "category": cat.lower(),
                                       "given": given, "when": when, "then": then})
                continue
            na = NA_LINE.match(line)
            if na:
                self.na[na.group(1).lower()] = na.group(2).strip()
                continue
            reason = REASON_LINE.match(line)
            if reason:
                self.reason = reason.group(1).strip()
                continue
            if stripped:
                self.statement.append(stripped)

    @property
    def text(self) -> str:
        return " ".join(self.statement)

    @property
    def unwanted(self) -> bool:
        """An EARS 'If <condition>, then … shall …' requirement: all failure behavior."""
        return self.text.lower().startswith("if ")

    def block(self, drop_tag=False) -> str:
        lines = list(self.raw_lines)
        if drop_tag:
            lines[0] = f"### {self.id} {self.title}".rstrip()
        while lines and not lines[-1].strip():
            lines.pop()
        return "\n".join(lines)


def parse_requirements(section_text: str) -> tuple:
    """Return (requirements, problems) for a '## Requirements' section."""
    reqs, problems, current = [], [], None
    for line in section_text.splitlines():
        if line.startswith("### "):
            head = REQ_HEAD.match(line)
            if not head:
                problems.append(f"heading is not a requirement (### REQ-ABC-001 Title): {line}")
                current = None
                continue
            current = [line]
            reqs.append(current)
        elif line.startswith("## "):
            current = None
        elif current is not None:
            current.append(line)
    parsed = []
    for lines in reqs:
        head = REQ_HEAD.match(lines[0])
        parsed.append(Requirement(head.group(1), head.group(2), head.group(3),
                                  head.group(4), head.group(5).strip(), lines))
    return parsed, problems


def parse_tasks(section_text: str) -> tuple:
    tasks, problems = [], []
    for line in section_text.splitlines():
        task = TASK_LINE.match(line)
        if task:
            ident = TASK_ID.match(task.group(2).strip())
            if not ident:
                problems.append(f"task has no ID (- [ ] T1 ...): {line.strip()}")
                continue
            tasks.append({"id": ident.group(1), "done": task.group(1).lower() == "x",
                          "refs": SCENARIO_REF.findall(ident.group(2)),
                          "test": "", "red": "", "green": ""})
            continue
        evidence = EVIDENCE_LINE.match(line)
        if evidence and tasks:
            tasks[-1][evidence.group(1).lower()] = evidence.group(2).strip()
    return tasks, problems


# ---------------------------------------------------------------- project

class Project:
    def __init__(self, root: Path):
        self.root = root
        self.specs = root / "specs"
        self.constitution = self.specs / "constitution.md"
        self.changes = self.specs / "changes"
        self.archive = self.specs / "archive"
        self.capabilities = self.specs / "capabilities"
        self.active_file = self.specs / ".sdd" / "active"

    @classmethod
    def locate(cls, root_arg):
        if root_arg:
            return cls(Path(root_arg).resolve())
        here = Path.cwd().resolve()
        for candidate in [here, *here.parents]:
            if (candidate / "specs" / "constitution.md").exists():
                return cls(candidate)
        return cls(here)

    # -- state

    def require_init(self):
        if not self.constitution.exists():
            raise SddError("this repository is not initialized: run `sdd init` first")

    def level(self) -> str:
        return read_front_matter(self.constitution.read_text()).get("assurance", "internal")

    def active(self):
        if not self.active_file.exists():
            return None
        value = self.active_file.read_text().strip()
        return value or None

    def set_active(self, change_id):
        self.active_file.parent.mkdir(parents=True, exist_ok=True)
        self.active_file.write_text((change_id or "") + "\n")

    def main_file(self, change_id):
        """spec.md for a mini change, proposal.md for a standard one, else None."""
        for name in ("spec.md", "proposal.md"):
            path = self.changes / change_id / name
            if path.exists():
                return path
        return None

    def change_path(self, change_id) -> Path:
        path = self.main_file(change_id)
        if path is None:
            raise SddError(f"no change '{change_id}' in specs/changes/")
        return path

    def current(self, change_arg=None) -> Path:
        change_id = change_arg or self.active()
        if not change_id:
            raise SddError("no active change: start one with `sdd quick \"<idea>\"`")
        return self.change_path(change_id)

    def in_flight(self) -> list:
        if not self.changes.exists():
            return []
        result = []
        for folder in sorted(p for p in self.changes.iterdir() if p.is_dir()):
            path = self.main_file(folder.name)
            if path is None:
                continue
            fm = read_front_matter(path.read_text())
            result.append({"id": folder.name, "status": fm.get("status", "?"),
                           "title": fm.get("title", ""), "size": fm.get("size", "mini")})
        return result

    def next_number(self) -> int:
        numbers = [0]
        for base in (self.changes, self.archive):
            if base.exists():
                for child in base.iterdir():
                    match = re.match(r"^(\d{4})-", child.name)
                    if match and child.is_dir():
                        numbers.append(int(match.group(1)))
        return max(numbers) + 1

    # -- capabilities (the living spec)

    def registry(self) -> dict:
        """prefix -> {'name', 'path', 'reqs': set of REQ ids}"""
        result = {}
        if not self.capabilities.exists():
            return result
        for path in sorted(self.capabilities.glob("*/spec.md")):
            text = path.read_text()
            fm = read_front_matter(text)
            prefix = fm.get("prefix", "")
            reqs = {m.group(1) for m in map(REQ_HEAD.match, strip_comments(text).splitlines()) if m}
            result[prefix] = {"name": fm.get("capability", path.parent.name),
                              "path": path, "reqs": reqs}
        return result


def parse_capabilities(value: str) -> dict:
    """'duration=DUR, auth=AUTH' -> {'DUR': 'duration', 'AUTH': 'auth'}"""
    result = {}
    for item in [v.strip() for v in value.split(",") if v.strip()]:
        if "=" not in item:
            raise SddError(f"capability '{item}' must be written name=PREFIX (e.g. checkout=CHK)")
        name, prefix = [p.strip() for p in item.split("=", 1)]
        if not CAP_NAME.match(name):
            raise SddError(f"capability name '{name}' must use lowercase letters, digits and hyphens")
        if not PREFIX.match(prefix):
            raise SddError(f"capability prefix '{prefix}' must be 2–6 uppercase letters/digits")
        result[prefix] = name
    return result


# ---------------------------------------------------------------- analysis

class Report:
    def __init__(self, change_id, stage, level):
        self.change_id, self.stage, self.level = change_id, stage, level
        self.errors, self.warnings, self.coverage = [], [], []
        self.open_questions = 0
        self.counts = {}

    @property
    def ok(self):
        return not self.errors

    def render(self) -> str:
        out = [f"check {self.change_id} (stage: {self.stage}, assurance: {self.level})"]
        if self.errors:
            out.append(f"errors ({len(self.errors)}):")
            out += [f"  - {e}" for e in self.errors]
        if self.warnings:
            out.append(f"warnings ({len(self.warnings)}):")
            out += [f"  - {w}" for w in self.warnings]
        if self.coverage:
            out.append("coverage:")
            out += [f"  {line}" for line in self.coverage]
        if self.open_questions:
            plural = "s" if self.open_questions != 1 else ""
            out.append(f"{self.open_questions} open question{plural} ([NEEDS CLARIFICATION])")
        out.append("result: " + ("OK" if self.ok else "FAIL"))
        return "\n".join(out)


def auto_stage(status: str, has_tasks: bool) -> str:
    if status in ("draft", "clarifying", "spec-approved", "designed"):
        return "plan" if has_tasks else "spec"  # the plan gate always asks for "plan" itself
    if status in ("implementing",):
        return "implement"
    if status in ("verifying", "verified"):
        return "verify"
    return "plan"


def analyze(project: Project, path: Path, stage: str = "auto") -> Report:
    text = change_text(path)
    fm = read_front_matter(text)
    clean = strip_comments(text)
    secs = sections(clean)
    change_id = path.parent.name
    level = fm.get("assurance", project.level())
    tasks, task_problems = parse_tasks(secs.get("Tasks", ""))
    stage = auto_stage(fm.get("status", "draft"), bool(tasks)) if stage == "auto" else stage
    report = Report(change_id, stage, level)
    err, warn = report.errors.append, report.warnings.append

    # Front matter: the fields every phase and the status machine rely on.
    for key in CHANGE_KEYS:
        if key not in fm:
            err(f"front matter is missing '{key}'")
    checks = {"type": TYPES, "size": list(SIZE_CAPS), "assurance": LEVELS, "status": STATUSES}
    for key, allowed in checks.items():
        if key in fm and fm[key] not in allowed:
            err(f"front matter {key} '{fm[key]}' is not one of: {', '.join(allowed)}")
    if level in LEVELS and LEVELS.index(level) < LEVELS.index(project.level()):
        err(f"assurance '{level}' is lower than the project level '{project.level()}' "
            "(lowering needs a recorded operator waiver)")
    if level not in LEVELS:
        level = project.level()
    status = fm.get("status", "draft")
    size = fm.get("size", "mini") if fm.get("size") in REQUIRED_APPROVALS else "mini"
    effective = fm.get("blocked_from", "draft") if status == "blocked" else status
    recorded = approvals(text)
    if effective in STATUS_ORDER:
        for first, gate in REQUIRED_APPROVALS[size]:
            if STATUS_ORDER.index(effective) >= STATUS_ORDER.index(first) and gate not in recorded:
                err(f"status is '{status}' but no {gate} approval is recorded in ## Approvals "
                    f"(only `sdd.py approve {gate}` may pass that gate)")
    locked = fm.get("spec_hash")
    if locked and effective not in UNLOCKED_STATUSES | {"abandoned"} and spec_hash(text) != locked:
        err(f"{LOCK_ERROR} (Intent, Defect, Scope, Requirements or Known gaps): log it under "
            "## Amendments and get the operator's approval (sdd amend)")

    try:
        declared = parse_capabilities(fm.get("capabilities", ""))
    except SddError as exc:
        err(str(exc))
        declared = {}
    registry = project.registry()

    # Requirements: structure, IDs and the living-spec delta.
    if "Requirements" not in secs:
        err("missing '## Requirements' section")
    reqs, req_problems = parse_requirements(secs.get("Requirements", ""))
    for problem in req_problems:
        err(problem)
    if not reqs:
        err("no requirements yet: add at least one '### REQ-<PREFIX>-<NNN> Title' block")

    others = {}
    for other in project.in_flight():
        if other["id"] == change_id or other["status"] in TERMINAL:
            continue
        other_text = strip_comments(change_text(project.change_path(other["id"])))
        other_reqs, _ = parse_requirements(sections(other_text).get("Requirements", ""))
        for r in other_reqs:
            if r.tag is None:
                others[r.id] = other["id"]

    seen = set()
    for req in reqs:
        if req.id in seen:
            err(f"{req.id}: duplicate requirement ID in this change")
        seen.add(req.id)
        if req.prefix not in declared and req.prefix not in registry:
            err(f"{req.id}: prefix {req.prefix} is not declared in front matter "
                f"'capabilities' (e.g. name={req.prefix})")
        existing = registry.get(req.prefix, {}).get("reqs", set())
        if req.tag is None and req.id in existing:
            cap = registry[req.prefix]["path"].relative_to(project.root)
            err(f"{req.id}: already exists in {cap}; mark it [MODIFIED] or take a new ID "
                f"(sdd.py next-req {req.prefix})")
        if req.tag is None and req.id in others:
            err(f"{req.id}: also added by in-flight change {others[req.id]}")
        if req.tag in ("MODIFIED", "REMOVED") and req.id not in existing:
            err(f"{req.id} [{req.tag}]: does not exist in the living spec (specs/capabilities/)")
        for problem in req.problems:
            err(f"{req.id}: {problem}")
        if req.tag == "REMOVED":
            if not req.reason:
                err(f"{req.id} [REMOVED]: needs a 'Reason: ...' line")
            continue
        check_requirement(req, level, err, warn, report)
        known_ids = {r.id for r in reqs if r.tag != "REMOVED"} | \
            {rid for info in registry.values() for rid in info["reqs"]}
        for cat, reason in req.na.items():
            for match in REQ_TOKEN.finditer(reason):
                ref = match.group(0)
                if ref not in known_ids:
                    err(f"{req.id}: N/A {cat} refers to {ref}, which doesn't exist")

    if fm.get("type") == "defect":
        check_defect(secs, reqs, registry, stage, err)

    # Known gaps: the prototype's honest substitute for failure cases.
    if level == "prototype" and not has_bullet(secs.get("Known gaps", "")):
        err("Known gaps list is required at prototype: one line per behavior not handled "
            "(write '- None' if there are none)")

    # Tasks: every scenario is planned test-first, and done means proven.
    for problem in task_problems:
        err(problem)
    scenario_refs = [f"{r.id}.{s['id']}" for r in reqs if r.tag != "REMOVED" for s in r.scenarios]
    if STAGES.index(stage) >= STAGES.index("plan"):
        check_plan(clean, tasks, scenario_refs, err, warn)
    for task in tasks:
        if task["done"]:
            check_evidence(task, err, warn)
    if stage == "verify":
        for task in tasks:
            if not task["done"]:
                err(f"{task['id']}: not done")
        files = {rel: c for rel, c in project_text_files(project).items() if is_test_path(rel)}
        for ref in scenario_refs:
            pattern = scenario_pattern(ref)
            if not any(pattern.search(content) for content in files.values()):
                err(f"{ref}: no test names this scenario (e.g. test_{ref.replace('-', '_').replace('.', '_')})")

    # Size and open questions.
    lines = counted_lines(text)
    cap = SIZE_CAPS.get(fm.get("size", "mini"), 200)
    if lines > cap:
        warn(f"size cap: {lines} lines > {cap} for {fm.get('size', 'mini')}; "
             "trim, or split into smaller changes")
    report.open_questions = clean.count("[NEEDS CLARIFICATION")

    happy = sum(1 for r in reqs for s in r.scenarios if s["category"] == "happy")
    boundary = sum(1 for r in reqs for s in r.scenarios if s["category"] == "boundary")
    total = sum(len(r.scenarios) for r in reqs)
    report.counts = {
        "requirements": len(reqs),
        "scenarios": {"happy": happy, "negative": total - happy - boundary, "boundary": boundary},
        "tasks": {"done": sum(1 for t in tasks if t["done"]), "total": len(tasks)},
        "known_gaps": sum(1 for l in secs.get("Known gaps", "").splitlines()
                          if re.match(r"^\s*[-*]\s+\S", l) and l.strip() not in ("- None", "* None")),
        "lines": lines,
        "cap": cap,
    }
    return report


def check_defect(secs, reqs, registry, stage, err):
    """A defect names what it breaks and carries a regression scenario into the living spec."""
    if "Defect" not in secs:
        err("a defect change needs a '## Defect' section (sdd.py new --type defect creates it)")
        return
    fields = {}
    for line in secs["Defect"].splitlines():
        match = DEFECT_FIELD.match(line)
        if match:
            fields[match.group(1).strip().lower()] = match.group(2).strip()
    for name in DEFECT_FIELDS:
        if not fields.get(name.lower()):
            err(f"Defect: '{name}' is empty")
    if stage == "verify" and not fields.get("root cause"):
        err("Defect: 'Root cause' must be filled before verification passes")
    regressions = [(r, s) for r in reqs if r.tag != "REMOVED" for s in r.scenarios
                   if s["id"].startswith("R")]
    if not regressions:
        err("a defect needs a regression scenario (ID R1, R2…) that reproduces the bug")
    violates = fields.get("violates", "")
    if not violates:
        return
    if violates.lower().startswith("spec gap"):
        return
    match = re.match(r"(REQ-[A-Z][A-Z0-9]{1,5}-\d{3,})\b", violates)
    if not match:
        err("Defect: 'Violates' must be a requirement ID (REQ-ABC-001) or 'spec gap'")
        return
    rid = match.group(1)
    living = {i for info in registry.values() for i in info["reqs"]}
    if rid not in living:
        err(f"Defect: violates {rid}, which isn't in the living spec; "
            "if no requirement covers this behavior, write 'spec gap'")
        return
    restated = [r for r in reqs if r.id == rid and r.tag == "MODIFIED"]
    if not restated:
        err(f"Defect: {rid} must be restated here as '### {rid} [MODIFIED] …' "
            "with the regression scenario")
    elif not any(r.id == rid for r, _ in regressions):
        err(f"Defect: the regression scenario must be in {rid}")


def check_requirement(req, level, err, warn, report):
    if not req.text:
        err(f"{req.id}: has no requirement statement")
    elif "shall" not in req.text.lower():
        warn(f"{req.id}: statement has no 'shall' (EARS: When <trigger>, the <system> shall <response>)")
    if not req.scenarios:
        err(f"{req.id}: has no scenarios (| ID | Category | Given | When | Then |)")
    ids = set()
    for s in req.scenarios:
        ref = f"{req.id}.{s['id']}"
        if not re.fullmatch(r"[A-Z]\d+", s["id"]):
            err(f"{ref}: scenario ID must be a letter and a number (S1, N1, B1)")
        if s["id"] in ids:
            err(f"{ref}: duplicate scenario ID")
        ids.add(s["id"])
        if s["category"] not in CATEGORIES:
            err(f"{ref}: unknown category '{s['category']}' (use: {', '.join(CATEGORIES)})")
        for part in ("given", "when", "then"):
            if not s[part]:
                err(f"{ref}: empty {part.capitalize()}")
        negative = s["category"] not in ("happy",)
        if negative and level != "prototype" and s["then"] and \
                not re.search(r"·|;|\band\b|\bno\b|\bnothing\b|\bunchanged\b", s["then"], re.I):
            warn(f"{ref}: Then checks one thing; a failure test should also check "
                 "that nothing else happened (no side effects)")
    present = {s["category"] for s in req.scenarios}
    if req.unwanted:
        # The requirement is itself failure coverage for another rule: no happy path, no walk.
        if req.scenarios and present <= {"happy"}:
            err(f"{req.id}: an If…then requirement describes failure behavior; "
                "it needs at least one non-happy scenario")
        hits = " · ".join(f"{c} {','.join(s['id'] for s in req.scenarios if s['category'] == c)}"
                          for c in CATEGORIES if c in present)
        report.coverage.append(f"{req.id}  (If…then) {hits}")
        return
    if req.scenarios and "happy" not in present:
        err(f"{req.id}: needs at least one happy-path scenario")
    for cat, reason in req.na.items():
        if cat not in CATEGORIES:
            err(f"{req.id}: N/A for unknown category '{cat}' (use: {', '.join(CATEGORIES)})")
        elif cat in present:
            warn(f"{req.id}: N/A {cat} but the requirement also has {cat} scenarios")
    for cat in REQUIRED[level]:
        if cat == "happy" or cat in present:
            continue
        if cat in req.na:
            if len(req.na[cat].split()) < 3:
                err(f"{req.id}: N/A {cat} needs a real reason (at least 3 words)")
            continue
        err(f"{req.id}: missing {cat} coverage ({CATEGORIES[cat]}): add a scenario or "
            f"'- N/A {cat}: <reason>'")
    cells = []
    for cat in CATEGORIES:
        hits = [s["id"] for s in req.scenarios if s["category"] == cat]
        if hits:
            cells.append(f"{cat} {','.join(hits)}")
        elif cat in req.na:
            cells.append(f"{cat} N/A")
        elif cat in REQUIRED[level]:
            cells.append(f"{cat} MISSING")
    report.coverage.append(f"{req.id}  " + " · ".join(cells))


def check_evidence(task, err, warn):
    """A ticked task proves a real red → green, or declares pre-existing behavior."""
    tid, red = task["id"], task["red"].strip()
    for kind in ("red", "green"):
        if not evidence_present(task[kind]):
            err(f"{tid}: ticked without {kind} evidence "
                f"(record the {'failing' if kind == 'red' else 'passing'} run)")
    if not evidence_present(red):
        return
    if red.lower().startswith("pre-existing"):
        reason = re.sub(r"^pre-existing\s*[—–:-]*\s*", "", red, flags=re.I)
        if len(reason.split()) < 3:
            err(f"{tid}: 'pre-existing' needs a reason (at least 3 words)")
        else:
            warn(f"{tid}: pre-existing behavior, no red run: {reason}")
        return
    if not FAILURE_WORDS.search(red):
        err(f"{tid}: red evidence does not show a failure ('{red}'); record the failing run, "
            "or 'pre-existing — <reason>' if the behavior already existed")
    elif SETUP_ERRORS.search(red):
        warn(f"{tid}: red looks like a setup error, not a failing assertion ('{red}')")


def check_plan(clean, tasks, scenario_refs, err, warn):
    if not test_command(clean):
        warn("no 'Test command:' line in the design; the Implementer and Verifier need it")
    if not tasks:
        err("no tasks yet: add one '- [ ] T1 REQ-...S1 ...' task per scenario")
    ids = set()
    referenced = set()
    known = set(scenario_refs)
    for task in tasks:
        if task["id"] in ids:
            err(f"{task['id']}: duplicate task ID")
        ids.add(task["id"])
        if not task["refs"]:
            err(f"{task['id']}: references no scenario (e.g. REQ-ABC-001.S1)")
        for ref in task["refs"]:
            if ref not in known:
                err(f"{task['id']}: references unknown scenario {ref}")
            referenced.add(ref)
    if tasks:
        for ref in scenario_refs:
            if ref not in referenced:
                err(f"{ref}: no task plans this scenario")


def project_text_files(project: Project) -> dict:
    """All text files outside specs/ (where tests live), keyed by relative path."""
    paths = None
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                             cwd=project.root, capture_output=True, text=True, check=True)
        paths = [project.root / p for p in out.stdout.splitlines() if p]
    except (OSError, subprocess.CalledProcessError):
        paths = []
        for dirpath, dirnames, filenames in os.walk(project.root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            paths += [Path(dirpath) / f for f in filenames]
    files = {}
    for path in paths:
        rel = path.relative_to(project.root)
        if rel.parts and rel.parts[0] == "specs":
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            files[str(rel)] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    return files


def next_step(project: Project, fm: dict, report: Report) -> str:
    status = fm.get("status", "draft")
    counts = report.counts
    if fm.get("size") == "standard":
        step = next_step_standard(status, counts, report)
        if step:
            return step
    if status == "draft":
        if counts["requirements"] == 0:
            return "sdd specify"
        if counts["tasks"]["total"] == 0:
            return "sdd tasks"
        if not report.ok:
            return "fix the check errors (sdd.py check), then ask for approval"
        if report.open_questions:
            return "answer the open questions, then ask for approval"
        return "awaiting operator approval: sdd approve"
    if any(LOCK_ERROR in e for e in report.errors):
        return "a spec amendment is pending: show the operator the change, then sdd approve"
    if status == "planned":
        return "sdd implement"
    if status == "implementing":
        done, total = counts["tasks"]["done"], counts["tasks"]["total"]
        return "sdd implement next" if done < total else "sdd verify"
    if status == "verifying":
        if fm.get("size") == "standard":
            return "sdd verify, then the operator approves the results (sdd approve)"
        return "sdd verify"
    if status == "verified":
        return "sdd archive"
    if status == "blocked":
        return "resolve the blocker, then sdd status"
    return "sdd quick \"<idea>\""


def next_step_standard(status, counts, report):
    """Steps before the plan gate; later statuses share the mini path."""
    if status in ("draft", "clarifying"):
        if counts["requirements"] == 0:
            return "sdd specify"
        if not report.ok:
            return "fix the check errors (sdd.py check), then ask for spec approval"
        if report.open_questions:
            return "answer the open questions, then ask for spec approval"
        return "awaiting operator approval of the spec: sdd approve"
    if any(LOCK_ERROR in e for e in report.errors):
        return "a spec amendment is pending: show the operator the change, then sdd approve"
    if status == "spec-approved":
        return "sdd design"
    if status == "designed":
        if counts["tasks"]["total"] == 0:
            return "sdd tasks"
        if not report.ok:
            return "fix the check errors (sdd.py check), then ask for plan approval"
        return "awaiting operator approval of the plan: sdd approve"
    return None


# ---------------------------------------------------------------- commands

def render(template: str, **values) -> str:
    text = (TEMPLATES / template).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def append_approval(path: Path, gate: str, evidence: str):
    text = path.read_text()
    row = f"| {gate} | {today()} | {evidence.replace('|', chr(92) + '|').replace(chr(10), ' ')} |"
    lines = text.rstrip("\n").splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## Approvals")
    except StopIteration:
        lines += ["", "## Approvals", "| Gate | Date | Evidence |", "| --- | --- | --- |"]
        start = len(lines) - 3
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    insert_at = end
    while insert_at > start + 1 and not lines[insert_at - 1].strip():
        insert_at -= 1
    lines.insert(insert_at, row)
    path.write_text("\n".join(lines) + "\n")


def cmd_init(project: Project, args) -> int:
    if project.constitution.exists() and not args.force:
        raise SddError("already initialized (specs/constitution.md exists); "
                       "use --force to refresh the folders and AGENTS.md/CLAUDE.md only")
    for folder in (project.capabilities, project.changes, project.archive):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / ".gitkeep").touch()
    if not project.active_file.exists():
        project.set_active(None)
    created = not project.constitution.exists()
    if created:
        project.constitution.write_text(render(
            "constitution.md", assurance=args.assurance, assurance_meaning=LEVEL_MEANING[args.assurance]))

    # AGENTS.md carries the SDD rules for Codex; CLAUDE.md imports it for Claude Code.
    block = (TEMPLATES / "agents-md-section.md").read_text().strip()
    agents = project.root / "AGENTS.md"
    current = agents.read_text() if agents.exists() else ""
    marked = re.compile(r"<!-- sdd:begin -->.*?<!-- sdd:end -->", re.S)
    if marked.search(current):
        current = marked.sub(lambda _: block, current, count=1)
    else:
        current = (current.rstrip() + "\n\n" if current.strip() else "") + block + "\n"
    agents.write_text(current)
    claude = project.root / "CLAUDE.md"
    claude_text = claude.read_text() if claude.exists() else ""
    if not any(line.strip() == "@AGENTS.md" for line in claude_text.splitlines()):
        claude.write_text((claude_text.rstrip() + "\n\n" if claude_text.strip() else "") + "@AGENTS.md\n")

    level = read_front_matter(project.constitution.read_text()).get("assurance")
    print(f"initialized specs/ (assurance: {level})")
    if created:
        print("created specs/constitution.md (approval pending: sdd approve)")
    print("updated AGENTS.md (SDD section) and CLAUDE.md (@AGENTS.md)")
    return 0


def cmd_new(project: Project, args) -> int:
    project.require_init()
    if not SLUG.match(args.slug):
        raise SddError(f"invalid slug '{args.slug}': use lowercase letters, digits and hyphens")
    if args.size not in SIZES_AVAILABLE:
        raise SddError(f"size '{args.size}' is not available yet (available: {', '.join(SIZES_AVAILABLE)})")
    base = project.level()
    level = args.assurance or base
    if LEVELS.index(level) < LEVELS.index(base):
        raise SddError(f"assurance '{level}' is lower than the project level '{base}': "
                       "lowering needs a recorded operator waiver (not available yet)")
    declared = parse_capabilities(", ".join(args.capability or []))
    registry = project.registry()
    for prefix, name in declared.items():
        if prefix in registry and registry[prefix]["name"] != name:
            raise SddError(f"prefix {prefix} is already used by capability '{registry[prefix]['name']}'")
        for other_prefix, info in registry.items():
            if info["name"] == name and other_prefix != prefix:
                raise SddError(f"capability '{name}' already uses prefix {other_prefix}")
    change_id = f"{project.next_number():04d}-{args.slug}"
    folder = project.changes / change_id
    folder.mkdir(parents=True)
    caps = ", ".join(f"{name}={prefix}" for prefix, name in declared.items())
    defect = (TEMPLATES / "defect-section.md").read_text() if args.type == "defect" else ""
    values = dict(id=change_id, title=args.title, type=args.type, assurance=level,
                  capabilities=caps, date=today(), defect=defect)
    if args.size == "standard":
        for name in STANDARD_FILES:
            (folder / name).write_text(render(f"standard/{name}", **values))
        created = f"specs/changes/{change_id}/ ({', '.join(STANDARD_FILES)})"
    else:
        (folder / "spec.md").write_text(render("mini-spec.md", **values))
        created = f"specs/changes/{change_id}/spec.md"
    previous = project.active()
    project.set_active(change_id)
    print(f"created {created} (size: {args.size}, assurance: {level})")
    print(f"active change: {change_id}")
    if previous and project.main_file(previous):
        status = read_front_matter(project.main_file(previous).read_text()).get("status")
        if status not in TERMINAL:
            print(f"note: {previous} is still '{status}'; switch back with `sdd.py use {previous}`")
    return 0


def cmd_status(project: Project, args) -> int:
    project.require_init()
    constitution = read_front_matter(project.constitution.read_text())
    data = {"initialized": True, "assurance": constitution.get("assurance"),
            "constitution_approved": constitution.get("approved") == "yes",
            "change": None, "in_flight": project.in_flight(), "notes": [],
            "capabilities": [{"name": info["name"], "prefix": prefix, "requirements": len(info["reqs"])}
                             for prefix, info in sorted(project.registry().items(),
                                                        key=lambda kv: kv[1]["name"])]}
    if not data["constitution_approved"]:
        data["notes"].append("constitution not approved yet (sdd approve)")
    active = project.active()
    if active and project.main_file(active):
        path = project.main_file(active)
        fm = read_front_matter(path.read_text())
        report = analyze(project, path)
        data["change"] = {"id": active, "title": fm.get("title"), "type": fm.get("type"),
                          "size": fm.get("size"), "assurance": fm.get("assurance"),
                          "status": fm.get("status"), **report.counts,
                          "open_questions": report.open_questions,
                          "check": {"stage": report.stage, "errors": len(report.errors),
                                    "warnings": len(report.warnings)}}
        data["next"] = next_step(project, fm, report)
    else:
        data["next"] = "sdd quick \"<idea>\" (or sdd propose \"<idea>\")"
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print(f"project assurance: {data['assurance']}"
          + ("" if data["constitution_approved"] else " (constitution not approved)"))
    change = data["change"]
    if change:
        sc, tk = change["scenarios"], change["tasks"]
        print(f"active change: {change['id']} — {change['title']}")
        print(f"  {change['type']} · size {change['size']} · assurance {change['assurance']}"
              f" · status {change['status']}")
        print(f"  {change['requirements']} requirements · scenarios: {sc['happy']} happy, "
              f"{sc['negative']} negative, {sc['boundary']} boundary · tasks {tk['done']}/{tk['total']}"
              f" · {change['known_gaps']} known gaps · {change['lines']}/{change['cap']} lines")
        ck = change["check"]
        print(f"  check ({ck['stage']}): {ck['errors']} errors, {ck['warnings']} warnings"
              f" · {change['open_questions']} open questions")
    else:
        print("active change: none")
    if data["capabilities"]:
        print("living spec: " + ", ".join(
            f"{c['name']} ({c['prefix']}, {c['requirements']} requirement{'' if c['requirements'] == 1 else 's'})"
            for c in data["capabilities"]))
    others = [c for c in data["in_flight"] if not change or c["id"] != change["id"]]
    if others:
        print("other changes: " + ", ".join(f"{c['id']} ({c['status']})" for c in others))
    print(f"next: {data['next']}")
    return 0


def cmd_check(project: Project, args) -> int:
    project.require_init()
    report = analyze(project, project.current(args.change), args.stage)
    if args.json:
        print(json.dumps({"ok": report.ok, "stage": report.stage, "errors": report.errors,
                          "warnings": report.warnings, "coverage": report.coverage,
                          "open_questions": report.open_questions, **report.counts}, indent=2))
    else:
        print(report.render())
    return 0 if report.ok else 1


def cmd_approve(project: Project, args) -> int:
    project.require_init()
    evidence = args.evidence.strip()
    if not evidence:
        raise SddError("approval needs --evidence: the operator's words and where they were given")
    if args.gate == "constitution":
        again = read_front_matter(project.constitution.read_text()).get("approved") == "yes"
        text = set_front_matter(project.constitution.read_text(), "approved", "yes")
        project.constitution.write_text(text)
        append_approval(project.constitution, "constitution (re-approval)" if again else "constitution",
                        evidence)
        print("constitution re-approval recorded" if again else "constitution approved")
        return 0
    path = project.current(args.change)
    fm = read_front_matter(path.read_text())
    status, size = fm.get("status"), fm.get("size", "mini")
    if args.gate == "spec":
        if size != "standard":
            raise SddError("mini changes have a single gate: sdd.py approve plan")
        if status not in ("draft", "clarifying"):
            raise SddError(f"change is '{status}': spec approval applies to a draft change")
        report = analyze(project, path, "spec")
        if not report.ok:
            print(report.render())
            raise SddError("spec approval refused: fix the check errors first")
        if report.open_questions:
            raise SddError(f"spec approval refused: {report.open_questions} open question(s) "
                           "must be answered first")
        append_approval(path, "spec", evidence)
        text = set_front_matter(path.read_text(), "status", "spec-approved")
        path.write_text(text)
        path.write_text(set_front_matter(text, "spec_hash", spec_hash(change_text(path))))
        print(f"{path.parent.name}: spec approved → spec-approved (the spec is now locked)")
        return 0
    if args.gate == "results":
        if size != "standard":
            raise SddError("mini changes have no results gate: use sdd.py advance verified")
        if status != "verifying":
            raise SddError(f"change is '{status}': results approval applies to a verifying change")
        report = analyze(project, path, "verify")
        if not report.ok:
            print(report.render())
            raise SddError("results approval refused: the verify check fails")
        append_approval(path, "results", evidence)
        path.write_text(set_front_matter(path.read_text(), "status", "verified"))
        print(f"{path.parent.name}: results approved → verified")
        return 0
    if args.gate == "plan":
        expected = "designed" if size == "standard" else "draft"
        if status != expected:
            if size == "standard":
                raise SddError(f"plan approval comes after design: the change is '{status}', "
                               "not 'designed' (sdd.py advance designed)")
            raise SddError(f"change is '{status}': plan approval applies to a draft change")
        report = analyze(project, path, "plan")
        if not report.ok:
            print(report.render())
            raise SddError("plan approval refused: fix the check errors first")
        if report.open_questions:
            raise SddError(f"plan approval refused: {report.open_questions} open question(s) "
                           "must be answered first")
        append_approval(path, "plan", evidence)
        text = set_front_matter(path.read_text(), "status", "planned")
        path.write_text(text)
        if size != "standard":  # standard locked its spec at the spec gate
            path.write_text(set_front_matter(text, "spec_hash", spec_hash(change_text(path))))
        print(f"{path.parent.name}: plan approved → planned")
        return 0
    # amend: the operator accepts a spec change made after approval; status is unchanged.
    if status not in AMENDABLE:
        raise SddError(f"change is '{status}': amendments apply to an approved, unfinished change")
    text = path.read_text()
    whole = change_text(path)
    current = spec_hash(whole)
    if read_front_matter(text).get("spec_hash") == current:
        raise SddError("nothing to amend: the spec hasn't changed since it was last approved")
    logged = sum(1 for line in sections(strip_comments(whole)).get("Amendments", "").splitlines()
                 if AMENDMENT_ENTRY.match(line))
    if logged < approvals(whole).count("amend") + 1:
        raise SddError("log the amendment first under ## Amendments: "
                       "'- A<n> <date>: <reason> → <what changed>'")
    path.write_text(set_front_matter(text, "spec_hash", current))
    report = analyze(project, path)
    if not report.ok:
        path.write_text(text)
        print(report.render())
        raise SddError("amendment refused: fix the check errors first (nothing was recorded)")
    append_approval(path, "amend", evidence)
    print(f"{path.parent.name}: amendment approved; the spec is locked again (status stays '{status}')")
    return 0


def cmd_advance(project: Project, args) -> int:
    project.require_init()
    path = project.current(args.change)
    text = path.read_text()
    status, size = read_front_matter(text).get("status"), read_front_matter(text).get("size", "mini")
    moves = TRANSITIONS.get(size, TRANSITIONS["mini"])
    target = args.status
    if status in TERMINAL:
        raise SddError(f"change is '{status}' and cannot move")
    if target == "abandoned":
        pass
    elif target == "blocked":
        if status == "blocked":
            raise SddError("change is already blocked")
        text = set_front_matter(text, "blocked_from", status)
    elif status == "blocked":
        back = read_front_matter(text).get("blocked_from", "draft")
        if target != back:
            raise SddError(f"change is blocked (it was '{back}'): it can only return to '{back}'")
        text = drop_front_matter(text, "blocked_from")
    elif size == "standard" and target == "verified":
        raise SddError("standard changes need the operator's results approval: sdd.py approve results")
    elif status in ("draft", "clarifying") and target not in moves.get(status, set()):
        gate = "spec approval first (sdd.py approve spec)" if size == "standard" \
            else "plan approval first (sdd approve)"
        raise SddError(f"change is '{status}': it needs {gate}")
    elif target not in moves.get(status, set()):
        allowed = ", ".join(sorted(moves.get(status, set()) | {"blocked", "abandoned"}))
        raise SddError(f"cannot go from '{status}' to '{target}' (allowed: {allowed})")
    if target == "designed" and not test_command(strip_comments(change_text(path))):
        raise SddError("design.md needs a 'Test command:' line before the change is designed")
    if target == "verified":
        report = analyze(project, path, "verify")
        if not report.ok:
            print(report.render())
            raise SddError("cannot mark verified: the verify check fails")
    path.write_text(set_front_matter(text, "status", target))
    if target == "abandoned" and project.active() == path.parent.name:
        project.set_active(None)
    print(f"{path.parent.name}: {status} → {target}")
    return 0


def cmd_archive(project: Project, args) -> int:
    project.require_init()
    path = project.current(args.change)
    text = change_text(path)
    fm = read_front_matter(text)
    change_id = path.parent.name
    if fm.get("status") != "verified":
        raise SddError(f"archive needs a verified change (status is '{fm.get('status')}')")
    report = analyze(project, path, "verify")
    if not report.ok:
        print(report.render())
        raise SddError("archive refused: the verify check fails")
    destination = project.archive / change_id
    if destination.exists():
        raise SddError(f"specs/archive/{change_id} already exists; nothing was changed")

    # Build every capability's new text in memory first, so a failure changes nothing.
    declared = parse_capabilities(fm.get("capabilities", ""))
    registry = project.registry()
    secs = sections(strip_comments(text))
    reqs, _ = parse_requirements(secs.get("Requirements", ""))
    pending, actions = {}, {}
    for req in reqs:
        info = registry.get(req.prefix)
        if info is None:
            name = declared[req.prefix]
            info = registry[req.prefix] = {"name": name, "reqs": set(),
                                           "path": project.capabilities / name / "spec.md"}
        cap_path = info["path"]
        if cap_path not in pending:
            pending[cap_path] = (cap_path.read_text() if cap_path.exists()
                                 else render("capability-spec.md", name=info["name"], prefix=req.prefix))
        head, blocks = split_capability(pending[cap_path])
        if req.tag == "REMOVED":
            blocks.pop(req.id, None)
        else:
            blocks[req.id] = req.block(drop_tag=True)
        pending[cap_path] = join_capability(head, blocks)
        verb = {"MODIFIED": "modified", "REMOVED": "removed"}.get(req.tag, "added")
        actions.setdefault(cap_path, []).append(f"{verb} {req.id}")

    # Known gaps and the change history travel with the requirements.
    gaps = [re.sub(r"^\s*[-*]\s+", "", line).strip()
            for line in secs.get("Known gaps", "").splitlines() if re.match(r"^\s*[-*]\s+\S", line)]
    gaps = [g for g in gaps if g.lower().rstrip(".") != "none"]
    for cap_path, done in actions.items():
        head, blocks = split_capability(pending[cap_path])
        head = insert_in_section(head, "Known gaps", [f"- {g} ({change_id})" for g in gaps])
        head = insert_in_section(head, "Change history",
                                 [f"- {change_id} — {fm.get('title', '')} ({today()}): {', '.join(done)}"])
        pending[cap_path] = join_capability(head, blocks)

    for cap_path, new_text in pending.items():
        cap_path.parent.mkdir(parents=True, exist_ok=True)
        cap_path.write_text(new_text)
    path.write_text(set_front_matter(path.read_text(), "status", "archived"))
    project.archive.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path.parent), str(destination))
    if project.active() == change_id:
        project.set_active(None)
    for cap_path, done in actions.items():
        print(f"{cap_path.relative_to(project.root)}: " + ", ".join(done))
    if gaps:
        print(f"carried {len(gaps)} known gap(s) into the living spec")
    print(f"archived {change_id} → specs/archive/{change_id}")
    return 0


def insert_in_section(head: str, name: str, new_lines: list) -> str:
    """Append lines at the end of '## name' in a capability header (created before Requirements)."""
    if not new_lines:
        return head
    lines = head.splitlines()
    if f"## {name}" not in lines:
        at = lines.index("## Requirements") if "## Requirements" in lines else len(lines)
        lines[at:at] = [f"## {name}", ""]
    start = lines.index(f"## {name}")
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    insert_at = end
    while insert_at > start + 1 and not lines[insert_at - 1].strip():
        insert_at -= 1
    lines[insert_at:insert_at] = new_lines
    if insert_at + len(new_lines) < len(lines) and lines[insert_at + len(new_lines)].strip():
        lines.insert(insert_at + len(new_lines), "")
    return "\n".join(lines)


def split_capability(text: str) -> tuple:
    """Split a capability spec into its header and {REQ id: block text}."""
    lines = text.splitlines()
    head, blocks, current = [], {}, None
    for line in lines:
        match = REQ_HEAD.match(line)
        if match:
            current = match.group(1)
            blocks[current] = [line]
        elif current and (line.startswith("## ") or line.startswith("### ")):
            current = None
            head.append(line)
        elif current:
            blocks[current].append(line)
        else:
            head.append(line)
    return "\n".join(head), {k: "\n".join(v).rstrip() for k, v in blocks.items()}


def join_capability(head: str, blocks: dict) -> str:
    def number(rid):
        return int(rid.rsplit("-", 1)[1])
    ordered = [blocks[k] for k in sorted(blocks, key=number)]
    return head.rstrip() + "\n\n" + "\n\n".join(ordered) + "\n" if ordered else head.rstrip() + "\n"


def cmd_next_req(project: Project, args) -> int:
    project.require_init()
    if not PREFIX.match(args.prefix):
        raise SddError(f"prefix '{args.prefix}' must be 2–6 uppercase letters/digits")
    highest = 0
    for path in project.specs.rglob("*.md"):
        for match in REQ_TOKEN.finditer(strip_comments(path.read_text())):
            if match.group(1) == args.prefix:
                highest = max(highest, int(match.group(2)))
    print(f"REQ-{args.prefix}-{highest + 1:03d}")
    return 0


def cmd_use(project: Project, args) -> int:
    project.require_init()
    project.change_path(args.change_id)
    project.set_active(args.change_id)
    print(f"active change: {args.change_id}")
    return 0


# ---------------------------------------------------------------- entry point

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sdd.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", help="repository root (default: nearest folder with specs/)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create specs/, constitution, AGENTS.md/CLAUDE.md wiring")
    p.add_argument("--assurance", required=True, choices=LEVELS)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("new", help="create a change and make it active")
    p.add_argument("slug")
    p.add_argument("--title", required=True)
    p.add_argument("--type", default="feature", choices=TYPES)
    p.add_argument("--size", default="mini")
    p.add_argument("--assurance", choices=LEVELS)
    p.add_argument("--capability", action="append", metavar="name=PREFIX")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("status", help="where things stand and the next step")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("check", help="validate the active change")
    p.add_argument("--stage", default="auto", choices=["auto", *STAGES])
    p.add_argument("--change")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("approve", help="record an operator approval")
    p.add_argument("gate", choices=["constitution", "spec", "plan", "results", "amend"])
    p.add_argument("--evidence", required=True)
    p.add_argument("--change")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("advance", help="move the active change to its next status")
    p.add_argument("status", choices=["draft", "clarifying", "spec-approved", "designed", "planned",
                                      "implementing", "verifying", "verified",
                                      "blocked", "abandoned"])
    p.add_argument("--change")
    p.set_defaults(func=cmd_advance)

    p = sub.add_parser("archive", help="merge a verified change into the living spec")
    p.add_argument("--change")
    p.set_defaults(func=cmd_archive)

    p = sub.add_parser("next-req", help="next free requirement ID for a prefix")
    p.add_argument("prefix")
    p.set_defaults(func=cmd_next_req)

    p = sub.add_parser("use", help="make another change active")
    p.add_argument("change_id")
    p.set_defaults(func=cmd_use)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    project = Project.locate(args.root)
    try:
        return args.func(project, args)
    except SddError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
