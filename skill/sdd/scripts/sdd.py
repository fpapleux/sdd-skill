#!/usr/bin/env python3
"""sdd.py — deterministic helper for the SDD skill (Python 3 standard library only).

Agents call this script for everything that must not depend on judgment:
IDs, status transitions, approvals, coverage checks and archiving. It runs the
same way from Claude Code, Codex, a git hook or a terminal.

    python3 sdd.py init --assurance internal
    python3 sdd.py new parse-duration --title "Parse durations" --capability duration=DUR
    python3 sdd.py status [--json]
    python3 sdd.py check [--stage spec|plan|implement|verify]
    python3 sdd.py analyze [--change ID] [--json]
    python3 sdd.py next [--change ID]
    python3 sdd.py approve plan --evidence "Operator in chat: 'approve'"
    python3 sdd.py advance implementing
    python3 sdd.py archive
    python3 sdd.py next-req DUR
    python3 sdd.py use 0002-other-change
    python3 sdd.py sort-failures failed.txt
    python3 sdd.py defect add --test test_REQ_DUR_001_S1_parses --severity major
    python3 sdd.py defect decide D1 fix-now --evidence "Operator in chat: 'fix it now'"
    python3 sdd.py defect close D1 --evidence "T4 green: 1 passed"
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import io
import json
import os
import posixpath
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
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
STANDARD_FILES = ["proposal.md", "spec-delta.md", "clarifications.md", "design.md", "tasks.md",
                  "verification.md"]
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
TIERS = ["light", "mid", "strong"]
INDEPENDENT_RUNNERS = ("fresh session", "subagent (strong)")  # at production and above

REQ_HEAD = re.compile(
    r"^### (REQ-([A-Z][A-Z0-9]{1,5})-(\d{3,}))(?:\s+\[(MODIFIED|REMOVED)\])?\s*(.*)$")
REQ_TOKEN = re.compile(r"REQ-([A-Z][A-Z0-9]{1,5})-(\d{3,})")
FENCE = re.compile(r"^\s*(```|~~~)")
BULLET = re.compile(r"^\s*[-*] ")
FM_ENTRY = re.compile(r"^(FM(\d+)|None)(?=[ :—]|$)")
INTERFACE_LINE = re.compile(r"^\s*[-*]\s+interface\s*:(.*)$", re.I)
CONTRACT_ENTRY = re.compile(r"^###(?!#)(.*)$")
CLAUSE_WORD = re.compile(r"[A-Za-z]{5,}")
LETTERS = re.compile(r"[A-Za-z]+")
NA_OUTCOME = re.compile(r"^N/A\s*[:—]\s*(.*)$", re.I)
SCENARIO_REF = re.compile(r"REQ-[A-Z][A-Z0-9]{1,5}-\d{3,}\.[A-Z]\d+")
TASK_LINE = re.compile(r"^\s*[-*]\s*\[( |x|X)\]\s*(.*)$")
TASK_ID = re.compile(r"^(T\d+)\b(.*)$")
EVIDENCE_LINE = re.compile(r"^\s+[-*]\s*(test|red|green)\s*:\s*(.*)$", re.I)
TIER_LINE = re.compile(r"^\s+[-*]\s*tier\s*:\s*(.*)$", re.I)
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
UNCOUNTED_SECTIONS = ("Clarifications", "Tasks", "Mutations", "Verification", "Amendments", "Approvals")
FINDING_TYPES = ["ambiguity", "contradiction", "untestable", "coverage", "weak-negative",
                 "conflict", "scope"]
MUTATION_LINE = re.compile(r"^\s*[-*]\s*(M\d+)\b\s*(.*)$")
MUTATION_TEXT = re.compile(r"^\s+[-*]\s*(find|replace)\s*:(.*)$", re.I)
ROUND_HEAD = re.compile(r"^### Round (\d+)\b(.*)$")
FINDING_LINE = re.compile(r"^\s*[-*]\s*(F\d+)\s*\[([A-Za-z-]+)\]\s*(.*)$")
QUESTION_LINE = re.compile(r"^\s*[-*]\s*(Q\d+)\b\s*(.*)$")
ANSWER_LINE = re.compile(r"^\s+[-*]\s*Answer\s*:\s*(.*)$", re.I)
UNANSWERED = {"", "pending", "?", "tbd", "todo"}
LOCKED_SECTIONS = ("Intent", "Defect", "Scope", "Requirements", "Known gaps")
DEFECT_FIELDS = ("Symptom", "Reproduce", "Current behavior", "Expected behavior", "Violates")
DEFECT_FIELD = re.compile(r"^\s*[-*]\s*([A-Za-z][A-Za-z ]*?)\s*:\s*(.*)$")
AMENDMENT_ENTRY = re.compile(r"^\s*[-*]\s*A\d+\b")
LOCK_ERROR = "the spec changed since it was approved"
CONSTITUTION_ERROR = "the constitution changed since approval"
CONSTITUTION_BOOKKEEPING = ("approved", "fingerprint", "approved_level")
ROW_FINGERPRINT = re.compile(
    r"· fingerprint ([0-9a-f]{12}) · level ([a-z]+)(?: · assurance lowered [a-z]+ → [a-z]+)?\s*$")
VERDICT_LINE = re.compile(r"^\s*(?:(?:[-*+]|\d+[.)])\s+)?[*_]*verdict[*_]*\s*:[*_\s]*([A-Za-z]*)(.*)$", re.I)
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
    """Cap spec/design length; exclude comments, task bookkeeping and review records."""
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


def design_text(path: Path) -> str:
    """The design a rule reads: design.md of a standard change, the Design notes of a mini one."""
    if read_front_matter(path.read_text()).get("size") == "standard":
        design = path.parent / "design.md"
        return strip_comments(design.read_text()) if design.exists() else ""
    return sections(strip_comments(path.read_text())).get("Design notes", "")


def test_component(design: str) -> str:
    """The design's component test command template ("" when absent), for the method and later tools."""
    match = re.search(r"^\s*[-*]\s*Test component\s*:[ \t]*(.*)$", design, re.M)
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
                          "test": "", "red": "", "green": "", "tiers": []})
            continue
        tier = TIER_LINE.match(line)
        if tier and tasks:
            tasks[-1]["tiers"].append(tier.group(1).strip())
            continue
        evidence = EVIDENCE_LINE.match(line)
        if evidence and tasks:
            tasks[-1][evidence.group(1).lower()] = evidence.group(2).strip()
    return tasks, problems


def parse_mutations(section_text: str) -> list:
    """Planned mutations: '- M1 <scenario> <file>' with find: and replace: lines."""
    mutations = []
    for line in section_text.splitlines():
        entry = MUTATION_LINE.match(line)
        if entry:
            words = entry.group(2).split()
            mutations.append({"id": entry.group(1), "scenario": words[0] if words else "",
                              "file": words[1] if len(words) > 1 else ""})
            continue
        text = MUTATION_TEXT.match(line)
        if text and mutations:
            raw = text.group(2)
            first, last = raw.find("`"), raw.rfind("`")
            mutations[-1][text.group(1).lower()] = raw[first + 1:last] if last > first else None
    return mutations


def unsafe_path(rel: str) -> bool:
    """True when a mutation's file would lie outside the project."""
    path = rel.replace("\\", "/")
    if path.startswith("/") or re.match(r"^[A-Za-z]:", path):
        return True
    return posixpath.normpath(path).split("/")[0] == ".."


def check_mutations(mutations, scenario_refs, err):
    seen = set()
    for m in mutations:
        if m["id"] in seen:
            err(f"{m['id']}: duplicate mutation ID")
        seen.add(m["id"])
        if m["scenario"] not in scenario_refs:
            err(f"{m['id']}: {m['scenario'] or 'no scenario'} is not a scenario of this change")
        if not m["file"]:
            err(f"{m['id']}: missing file (write '- {m['id']} REQ-….S1 path/to/file')")
        elif unsafe_path(m["file"]):
            err(f"{m['id']}: file {m['file']} is outside the project (use a path relative to its root)")
        for field in ("find", "replace"):
            if field not in m:
                err(f"{m['id']}: missing {field} (write '  - {field}: `text`')")
            elif m[field] is None:
                err(f"{m['id']}: the {field} text must be written between backticks")
        if m.get("find") is not None and m.get("find") == m.get("replace"):
            err(f"{m['id']} changes nothing: its replace text equals its find text")


def parse_rounds(section_text: str) -> list:
    """Spec Critic rounds: audit verdicts, findings with outcomes, and answered questions."""
    rounds, current, in_table = [], None, False
    for line in section_text.splitlines():
        head = ROUND_HEAD.match(line)
        if head:
            mode = re.search(r"Critic:\s*(same session|fresh session|subagent(?:\s*\([^)]*\))?)",
                             head.group(2), re.I)
            current = {"number": int(head.group(1)),
                       "mode": " ".join(mode.group(1).lower().split()) if mode else "",
                       "audit": {}, "findings": [], "questions": []}
            rounds.append(current)
            in_table = False
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = table_cells(stripped)
            if [c.lower() for c in cells[:2]] == ["req", "verdict"]:
                in_table = True
            elif in_table and cells and not is_separator(cells) and len(cells) >= 2:
                current["audit"][cells[0]] = cells[1].lower()
            continue
        in_table = False
        answer = ANSWER_LINE.match(line)
        if answer and current["questions"]:
            current["questions"][-1]["answer"] = answer.group(1).strip()
            continue
        finding = FINDING_LINE.match(line)
        if finding:
            body = finding.group(3)
            text, _, outcome = body.rpartition("→") if "→" in body else (body, "", "")
            current["findings"].append({"id": finding.group(1), "type": finding.group(2).lower(),
                                        "text": text.strip(), "outcome": outcome.strip()})
            continue
        question = QUESTION_LINE.match(line)
        if question:
            current["questions"].append({"id": question.group(1), "text": question.group(2), "answer": ""})
    return rounds


def answered(question: dict) -> bool:
    return question["answer"].strip().lower() not in UNANSWERED


def critic_required(size: str, level: str) -> bool:
    """Size decides whether the Critic runs; assurance can demand it at any size."""
    if level not in LEVELS:
        return False
    return (size == "standard" and level != "prototype") or \
        LEVELS.index(level) >= LEVELS.index("production")


def critic_gate_errors(reqs: list, rounds: list, size: str, level: str) -> list:
    if not critic_required(size, level):
        return []
    if not rounds:
        return ["a Critic round is required before this gate at this size and assurance level: "
                "run sdd clarify"]
    last = rounds[-1]
    return [f"{r.id}: not audited in the latest Critic round (round {last['number']}); "
            "run another round: sdd clarify"
            for r in reqs if r.tag != "REMOVED" and last["audit"].get(r.id) not in ("ok", "issues")]


def check_rounds(rounds: list, level: str, req_ids: set, err, warn) -> int:
    """Validate every round; return the number of unanswered questions."""
    unanswered = 0
    for rnd in rounds:
        name = f"Round {rnd['number']}"
        for rid, verdict in rnd["audit"].items():
            if verdict not in ("ok", "issues"):
                err(f"{name}: {rid} has no verdict (write ok or issues)")
            elif rid not in req_ids:
                warn(f"{name}: audits {rid}, which isn't a requirement of this change")
        if len(rnd["questions"]) > 5:
            err(f"{name} has {len(rnd['questions'])} questions: at most 5 per round "
                "(ask the most important first, then start a new round)")
        answers = {q["id"]: answered(q) for q in rnd["questions"]}
        unanswered += sum(1 for ok in answers.values() if not ok)
        for f in rnd["findings"]:
            if f["type"] not in FINDING_TYPES:
                err(f"{name}: {f['id']} has unknown type '{f['type']}' (use: {', '.join(FINDING_TYPES)})")
            outcome = f["outcome"]
            link = re.match(r"^(Q\d+)\b", outcome)
            resolved = re.match(r"^(fixed|accepted|rejected)\s*:\s*(\S.*)$", outcome, re.I)
            if link:
                if not answers.get(link.group(1), False):
                    err(f"{name}: {f['id']} is open: it waits on {link.group(1)}, which has no answer yet")
            elif not resolved:
                err(f"{name}: {f['id']} is open: end it with → fixed: … / accepted: … / "
                    "rejected: <reason>, or → Q<n> for a question")
    if rounds and LEVELS.index(level) >= LEVELS.index("production") \
            and rounds[-1]["mode"] not in INDEPENDENT_RUNNERS:
        last = rounds[-1]
        if last["mode"].startswith("subagent"):
            warn(f"Round {last['number']}'s runner ({last['mode']}) is not independent: at production "
                 "and above the Critic runs as a strong subagent or in a fresh session")
        else:
            warn(f"Round {last['number']} ran in the same session; at production and above the "
                 "Critic should run in a fresh session or a strong subagent (enforced in a later version)")
    return unanswered


def latest_verdict(section_text: str):
    """(word, rest) of the last verdict line, ignoring fenced code, comments and tables."""
    found, in_fence = None, False
    for line in strip_comments(section_text).splitlines():
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith("|"):
            continue
        match = VERDICT_LINE.match(line)
        if match:
            found = (match.group(1), match.group(2).rstrip())
    return found


def latest_verifier(section_text: str):
    """The text after 'Verifier:' on the last line that has it, ignoring comments and fenced code."""
    found, in_fence = None, False
    for line in strip_comments(section_text).splitlines():
        if line.strip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.search(r"verifier\s*:\s*(.*)$", line, re.I)
        if match:
            found = match.group(1).strip()
    return found


def verdict_problem(change: str):
    """None when the Verifier's latest verdict is PASS; otherwise why it can't be verified."""
    found = latest_verdict(sections(strip_comments(change)).get("Verification", ""))
    if found is None:
        return "no verdict in the Verification section (the Verifier ends it with 'Verdict: PASS' or 'Verdict: GAPS')"
    word, rest = found
    if word.upper() == "PASS":
        return None
    if word.upper() == "GAPS":
        return f"the latest verdict is '{word}{rest}'"
    return f"verdict '{word or '(empty)'}' is neither PASS nor GAPS"


def constitution_fingerprint(text: str) -> str:
    """12 hex digits over the rules; bookkeeping keys, Approvals, comments and spacing excluded."""
    match = FRONT_MATTER.match(text)
    head, body = ([], text) if not match else (
        [l for l in match.group(1).splitlines()
         if l.split(":", 1)[0].strip() not in CONSTITUTION_BOOKKEEPING], text[match.end():])
    body = re.sub(r"^## Approvals\n.*?(?=^## |\Z)", "", strip_comments(body), flags=re.S | re.M)
    lines = [" ".join(line.split()) for line in head + body.splitlines() if line.strip()]
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()[:12]


def approval_rows(text: str) -> list:
    rows = []
    for line in sections(strip_comments(text)).get("Approvals", "").splitlines():
        cells = table_cells(line) if line.strip().startswith("|") else []
        if cells and not is_separator(cells) and cells[0].lower() != "gate":
            rows.append(cells)
    return rows


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

    def constitution_state(self) -> dict:
        """Compare the constitution with its newest fingerprinted approval."""
        text = self.constitution.read_text()
        fm = read_front_matter(text)
        current = constitution_fingerprint(text)
        reference = None
        for cells in approval_rows(text):
            match = ROW_FINGERPRINT.search(cells[-1])
            if match:
                reference = (match.group(1), match.group(2))
        if reference is None and re.fullmatch(r"[0-9a-f]{12}", fm.get("fingerprint", "")):
            reference = (fm["fingerprint"], fm.get("approved_level", ""))
        changed = bool(reference) and (current != reference[0] or fm.get("fingerprint") != reference[0])
        approved_level = reference[1] if reference and reference[1] in LEVELS else None
        return {"text": text, "fm": fm, "current": current, "reference": reference,
                "changed": changed, "approved_level": approved_level}

    def level(self) -> str:
        """The project level: the approved one while the constitution has unapproved edits."""
        state = self.constitution_state()
        if state["changed"] and state["approved_level"]:
            return state["approved_level"]
        level = state["fm"].get("assurance", "")
        if level in LEVELS:
            return level
        if state["approved_level"]:
            return state["approved_level"]
        raise SddError(f"the constitution's assurance level '{level or '(missing)'}' is not one of: "
                       f"{', '.join(LEVELS)}")

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
        self.critic = []  # what a gate still needs from the Spec Critic
        self.counts = {}
        self.reqs = []  # the change's parsed requirements
        self.design_errors = []  # errors from the design rules (REQ-ANL-002 to REQ-ANL-005)
        self.round_errors = []  # errors about the Critic rounds (the Clarifications section)
        self.defects = {"open": 0, "critical": 0, "undecided": 0}  # specs/defects.md (REQ-DEF-004); None: invalid

    @property
    def ok(self):
        return not self.errors

    def round_error(self, message):
        """An error about a Critic round: also kept in round_errors."""
        self.errors.append(message)
        self.round_errors.append(message)

    def design_error(self, message):
        """An error from the design rules (REQ-ANL-002 to REQ-ANL-005): also kept in design_errors."""
        self.errors.append(message)
        self.design_errors.append(message)

    def render(self, head=None, scenarios=False) -> str:
        out = [head or f"check {self.change_id} (stage: {self.stage}, assurance: {self.level})"]
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
        if scenarios:
            sc = self.counts["scenarios"]
            out.append(f"scenarios: {sc['happy']} happy, {sc['negative']} negative, {sc['boundary']} boundary")
        if defect_line(self.defects):
            out.append(defect_line(self.defects))
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


def spec_edited_since_approval(fm: dict, text: str) -> bool:
    """Whether the locked sections no longer match the fingerprint recorded when the spec was approved
    (a blocked change counts at the status it was blocked from; an abandoned one is never locked)."""
    status = fm.get("status", "draft")
    effective = fm.get("blocked_from", "draft") if status == "blocked" else status
    locked = fm.get("spec_hash")
    return bool(locked and effective not in UNLOCKED_STATUSES | {"abandoned"} and spec_hash(text) != locked)


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
    if project.constitution_state()["changed"]:
        err(f"{CONSTITUTION_ERROR}: review the edits, then sdd approve (constitution); "
            "the gates refuse until then")
    if spec_edited_since_approval(fm, text):
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
    report.reqs = reqs
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
    for task in tasks:
        if len(task["tiers"]) > 1:
            err(f"{task['id']} has more than one tier line (write one line; escalate with →)")
        for value in task["tiers"]:
            problem = tier_problem(task["id"], value)
            if problem:
                err(problem)
    scenario_refs = [f"{r.id}.{s['id']}" for r in reqs if r.tag != "REMOVED" for s in r.scenarios]
    if STAGES.index(stage) >= STAGES.index("plan"):
        check_plan(clean, tasks, scenario_refs, err, warn)
        check_component_command(design_text(path), err, warn)
        view = design_view(path)
        if view is not None:  # a standard change
            check_contracts(view, report.design_error, warn)
    for task in tasks:
        if task["done"]:
            check_evidence(task, err, warn)
    if stage == "verify":
        for task in tasks:
            if not task["done"]:
                err(f"{task['id']}: not done")
        runner = latest_verifier(secs.get("Verification", ""))
        if LEVELS.index(level) >= LEVELS.index("production") and not " ".join((runner or "").lower().split()).startswith(INDEPENDENT_RUNNERS):
            warn(f"the Verifier should run in a fresh session or a strong subagent "
                 f"(latest Verifier line: {runner or 'none'})")
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
    check_mutations(parse_mutations(secs.get("Mutations", "")), set(scenario_refs), err)
    rounds = parse_rounds(secs.get("Clarifications", ""))
    unanswered = check_rounds(rounds, level, {r.id for r in reqs}, report.round_error, warn)
    report.open_questions = clean.count("[NEEDS CLARIFICATION") + unanswered
    report.critic = critic_gate_errors(reqs, rounds, fm.get("size", "mini"), level)

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
    if tasks:
        report.counts["tiers"] = tier_counts(tasks)
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


def task_tier(task) -> str:
    """The tier a task runs on: the last step of its tier line, or 'untiered'."""
    if not task["tiers"]:
        return "untiered"
    return task["tiers"][0].split("→")[-1].strip()


def tier_problem(tid: str, value: str):
    """Why a tier line is invalid, or None: one tier, or a chain of one-tier steps."""
    if "->" in value:
        return f"{tid}: tier '{value}': an escalation is written with \"→\""
    parts = [part.strip() for part in value.split("→")]
    for part in parts:
        if part not in TIERS:
            return f"{tid}: tier '{value}' is not one of: {', '.join(TIERS)}"
    for low, high in zip(parts, parts[1:]):
        if TIERS.index(high) != TIERS.index(low) + 1:
            return f"{tid}: tier '{value}': each step must go up exactly one tier"
    return None


def tier_counts(tasks) -> dict:
    counts = {}
    for task in tasks:
        tier = task_tier(task)
        counts[tier] = counts.get(tier, 0) + 1
    return {t: counts[t] for t in [*TIERS, "untiered"] if counts.get(t)}


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


def check_component_command(design: str, err, warn) -> None:
    """The design's `- Test component:` line: one per design, with {prefix} and closed quotes."""
    lines = re.findall(r"^\s*[-*]\s*Test component\s*:[ \t]*(.*)$", design, re.M)
    if len(lines) > 1:
        err('the design has more than one "Test component:" line: keep one')
        return
    command = lines[0].strip().strip("`").strip() if lines else ""
    if not command:
        warn('the design has no "Test component:" line (or it is empty): '
             "the component checkpoints will be skipped")
        return
    if "{prefix}" not in command:
        err('the "Test component:" command has no {prefix}: write where the capability\'s requirement '
            'prefix goes, e.g. "- Test component: `python3 -m unittest -k REQ_{prefix}_`"')
    try:
        shlex.split(command)
    except ValueError:
        err(f'the "Test component:" command has a quote that is not closed: {command}')


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
        if not task["tiers"]:
            warn(f"{task['id']}: no tier (add '  - tier: light|mid|strong')")
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
    if project.constitution_state()["changed"]:
        return f"{CONSTITUTION_ERROR}: review it, then sdd approve"
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
        if report.critic:
            return "run a Critic round (required at this assurance level): sdd clarify"
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
        if report.critic:
            return "run a Critic round: sdd clarify"
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
        return "sdd analyze, then ask for plan approval"
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
    block = (TEMPLATES / "agents-section.md").read_text().strip()
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
    state = project.constitution_state()
    constitution = state["fm"]
    effective = project.level()
    pending = constitution.get("assurance") if state["changed"] and \
        constitution.get("assurance") != effective else None
    data = {"initialized": True, "assurance": effective, "assurance_pending": pending,
            "constitution_approved": constitution.get("approved") == "yes",
            "constitution_changed": state["changed"],
            "change": None, "in_flight": project.in_flight(), "notes": [],
            "capabilities": [{"name": info["name"], "prefix": prefix, "requirements": len(info["reqs"])}
                             for prefix, info in sorted(project.registry().items(),
                                                        key=lambda kv: kv[1]["name"])]}
    if not data["constitution_approved"]:
        data["notes"].append("constitution not approved yet (sdd approve)")
    if state["changed"]:
        data["notes"].append(f"{CONSTITUTION_ERROR}: review the edits, then sdd approve")
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
    log = read_defect_log(project)  # the log belongs to the project, not to a change
    data["defects"] = defect_counts(log)
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    shown = data["assurance"] + (f" ({pending} pending approval)" if pending else "")
    print(f"project assurance: {shown}"
          + ("" if data["constitution_approved"] else " (constitution not approved)"))
    if state["changed"]:
        print(f"{CONSTITUTION_ERROR}: review the edits, then sdd approve")
    change = data["change"]
    if change:
        sc, tk = change["scenarios"], change["tasks"]
        print(f"active change: {change['id']} — {change['title']}")
        print(f"  {change['type']} · size {change['size']} · assurance {change['assurance']}"
              f" · status {change['status']}")
        print(f"  {change['requirements']} requirements · scenarios: {sc['happy']} happy, "
              f"{sc['negative']} negative, {sc['boundary']} boundary · tasks {tk['done']}/{tk['total']}"
              f" · {change['known_gaps']} known gaps · {change['lines']}/{change['cap']} lines")
        if change.get("tiers"):
            print("  tiers: " + ", ".join(f"{n} {t}" for t, n in change["tiers"].items()))
        ck = change["check"]
        print(f"  check ({ck['stage']}): {ck['errors']} errors, {ck['warnings']} warnings"
              f" · {change['open_questions']} open questions")
    else:
        print("active change: none")
    if log.problem:
        print(f"defect log: {log.problem}")
    elif defect_line(data["defects"]):
        print(defect_line(data["defects"]))
    if data["capabilities"]:
        print("living spec: " + ", ".join(
            f"{c['name']} ({c['prefix']}, {c['requirements']} requirement{'' if c['requirements'] == 1 else 's'})"
            for c in data["capabilities"]))
    others = [c for c in data["in_flight"] if not change or c["id"] != change["id"]]
    if others:
        print("other changes: " + ", ".join(f"{c['id']} ({c['status']})" for c in others))
    print(f"next: {data['next']}")
    return 0


def report_json(report: Report) -> dict:
    return {"ok": report.ok, "stage": report.stage, "errors": report.errors,
            "warnings": report.warnings, "coverage": report.coverage,
            "open_questions": report.open_questions, **report.counts, "defects": report.defects}


def defect_findings(project: Project, report: Report) -> None:
    """The defect log's counts on the report, and its problem as an error at verify, else a warning
    (REQ-DEF-004, REQ-DEF-006); analyze() itself, which the gates call, never reads the log."""
    log = read_defect_log(project)
    report.defects = defect_counts(log)
    if log.problem:
        (report.errors if report.stage == "verify" else report.warnings).append(log.problem)


def cmd_check(project: Project, args) -> int:
    project.require_init()
    report = analyze(project, project.current(args.change), args.stage)
    defect_findings(project, report)
    if args.json:
        print(json.dumps(report_json(report), indent=2))
    else:
        print(report.render())
    return 0 if report.ok else 1


def design_view(path: Path):
    """design.md without comments, fenced code blanked line by line; None for a mini change."""
    if read_front_matter(path.read_text()).get("size") != "standard":
        return None
    path = path.parent / "design.md"
    if not path.exists():
        return ""
    text = strip_comments(path.read_text())
    out, fence = [], None
    for line in text.splitlines():
        if FENCE.match(line):
            marker = FENCE.match(line).group(1)[0]
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            out.append("")
        else:
            out.append("" if fence else line)
    return "\n".join(out)


def design_rules_apply(fm: dict) -> bool:
    """A standard change at designed or later; blocked counts as blocked_from, abandoned never."""
    if fm.get("size") != "standard":
        return False
    status = fm.get("status", "draft")
    status = fm.get("blocked_from") if status == "blocked" else status
    if status == "abandoned":
        return False
    return status in STATUS_ORDER and STATUS_ORDER.index(status) >= STATUS_ORDER.index("designed")


def design_findings(project: Project, path: Path, report: Report, err, warn):
    """The design rules of a standard change at designed or later: trace, failure modes, presence."""
    fm = read_front_matter(path.read_text())
    if not design_rules_apply(fm):
        return
    view = design_view(path) or ""
    known_ids = known_requirement_ids(project, report.reqs)
    check_design_trace(view, report, known_ids, err, warn)
    check_failure_modes(view, known_ids, counting_scenarios(project, report.reqs), err)
    level = report.level if report.level in LEVELS else project.level()  # as analyze() falls back
    check_failure_modes_present(view, level, err, warn)


def known_requirement_ids(project: Project, reqs: list) -> set:
    """Every requirement that exists: the change's (any tag) and the living spec's."""
    return {r.id for r in reqs} | {rid for info in project.registry().values() for rid in info["reqs"]}


def living_scenarios(project: Project) -> dict:
    """REQ ID -> scenario IDs, parsed from each capability's ## Requirements."""
    result = {}
    for info in project.registry().values():
        text = strip_comments(info["path"].read_text())
        reqs, _ = parse_requirements(sections(text).get("Requirements", ""))
        for req in reqs:
            result[req.id] = [s["id"] for s in req.scenarios]
    return result


def counting_scenarios(project: Project, reqs: list) -> set:
    """Scenario references that count: the change's (not removed), plus the living spec's for
    requirements the change neither modifies nor removes."""
    modified_ids = {r.id for r in reqs if r.tag == "MODIFIED"}
    removed_ids = {r.id for r in reqs if r.tag == "REMOVED"}
    result = {f"{r.id}.{s['id']}" for r in reqs if r.tag != "REMOVED" for s in r.scenarios}
    for rid, ids in living_scenarios(project).items():
        if rid in modified_ids or rid in removed_ids:
            continue
        result |= {f"{rid}.{i}" for i in ids}
    return result


def check_design_trace(view: str, report: Report, known_ids: set, err, warn):
    """REQ-ANL-002: design.md names only requirements that exist, and names every one of the change's."""
    named = list(dict.fromkeys(m.group(0) for m in REQ_TOKEN.finditer(view)))
    for rid in named:
        if rid not in known_ids:
            err(f"design.md names {rid}, which doesn't exist (in this change or the living spec)")
    for req in report.reqs:
        if req.id not in named and req.tag != "REMOVED":
            warn(f"{req.id} is not named in design.md: trace each component to its requirements")


def failure_mode_bullets(view: str) -> list:
    """The text of each bullet under design.md's ## Failure modes, marker and outer spaces removed."""
    body = sections(view).get("Failure modes", "")
    return [line[BULLET.match(line).end():].strip() for line in body.splitlines() if BULLET.match(line)]


def check_failure_modes(view: str, known_ids: set, scenario_ids: set, err):
    """REQ-ANL-003: each bullet under ## Failure modes is a well-formed entry."""
    bullets = failure_mode_bullets(view)
    entries, nones = [], []
    for text in bullets:
        m = FM_ENTRY.match(text)
        if not m:
            err(f'Failure modes: "{text}" is neither a failure-mode entry nor a None line')
        elif m.group(2):
            entries.append(text)
            check_fm_entry(m.group(1), text[m.end():], known_ids, scenario_ids, err)
        else:
            nones.append(text)
            check_none_line(text[m.end():], err)
    if nones and (entries or len(nones) > 1):
        err("Failure modes: a None line can't sit next to entries")
    check_fm_numbers(bullets, err)


def failure_mode_entries(view: str) -> list:
    """The bullets under ## Failure modes that are entries (FM<n> or None first), well formed or not."""
    return [text for text in failure_mode_bullets(view) if FM_ENTRY.match(text)]


def check_failure_modes_present(view: str, level: str, err, warn):
    """REQ-ANL-004: design.md has an entry under ## Failure modes; an error at production and above,
    a warning below."""
    if failure_mode_entries(view):
        return
    emit = err if LEVELS.index(level) >= LEVELS.index("production") else warn
    emit('design.md has no failure modes: list each as "- FM<n> <what fails> → <scenario>", '
         'or write "- None — <reason>"')


def check_fm_numbers(bullets: list, err):
    """An FM number is used once; numbers compare as integers, and each repeat is reported once."""
    seen_numbers, reported = set(), set()
    for text in bullets:
        m = FM_ENTRY.match(text)
        if not (m and m.group(2)):
            continue
        number = int(m.group(2))
        if number in seen_numbers:
            if number not in reported:
                err(f"Failure modes: FM{number} is repeated")
                reported.add(number)
        seen_numbers.add(number)


def check_none_line(body: str, err):
    """A None line: ':' or '—' then a reason of at least three words."""
    if body.strip() and not re.match(r"\s*[:—]", body):
        err('Failure modes: the None line needs ":" or "—" before its reason')
        return
    none_reason = re.sub(r"^\s*[:—]\s*", "", body)
    if len(none_reason.split()) < 3:
        err("Failure modes: the None line needs a reason of at least 3 words")


def check_fm_entry(label: str, body: str, known_ids: set, scenario_ids: set, err):
    """One FM<n> entry: its body (after the label) holds text, an arrow and an outcome."""
    if "→" not in body:
        err(f"Failure modes: {label} has no outcome (end the line with → <scenarios> or → N/A: <reason>)")
        return
    text, outcome = (part.strip() for part in body.rsplit("→", 1))
    if not re.sub(r"^[:—]\s*", "", text):
        err(f"Failure modes: {label} has no text before its arrow")
        return
    na = NA_OUTCOME.match(outcome)
    if na:
        na_reason = na.group(1).strip()
        if len(na_reason.split()) < 3:
            err(f"Failure modes: {label}'s N/A needs a real reason (at least 3 words)")
        return
    refs = [part.strip() for part in outcome.split(",")]
    for part in refs:
        if not SCENARIO_REF.fullmatch(part):
            err(f"Failure modes: {label}'s outcome is neither scenario references nor N/A: {outcome}")
            return
    check_fm_refs(label, refs, known_ids, scenario_ids, err)


def check_fm_refs(label: str, refs: list, known_ids: set, scenario_ids: set, err):
    """Each reference names a scenario that counts; one whose requirement doesn't exist is left to
    the design trace (REQ-ANL-002), so it is reported once."""
    for ref in refs:
        if ref.split(".")[0] not in known_ids:
            continue
        if ref not in scenario_ids:
            err(f"Failure modes: {label} names {ref}, which doesn't exist: a failure mode the spec "
                "doesn't cover needs an amendment (sdd amend)")


def split_contracts(view: str) -> tuple:
    """(the view's lines outside ## Contracts, the lines inside it)."""
    outside, inside, current = [], [], None
    for line in view.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
        (inside if current == "Contracts" else outside).append(line)
    return outside, inside


def contract_name(name: str) -> str:
    """A name as written, trimmed of spaces, then of surrounding backticks."""
    return name.strip().strip("`")


def interface_names(lines: list) -> list:
    """The name on each interface line, in order ("" for a line with no name)."""
    return [contract_name(m.group(1)) for m in map(INTERFACE_LINE.match, lines) if m]


def contract_entries(lines: list) -> list:
    """The name of each ### entry, in order ("" for an entry with no name)."""
    return [contract_name(m.group(1)) for m in map(CONTRACT_ENTRY.match, lines) if m]


def check_contracts(view: str, err, warn):
    """REQ-ANL-005: each interface listed outside ## Contracts has a ### entry inside it."""
    outside, inside = split_contracts(view)
    interfaces, entries = interface_names(outside), contract_entries(inside)
    for name in interfaces:
        if not name:
            err("an interface line has no name")
    for name in entries:
        if not name:
            err("a contract entry under ## Contracts has no name")
    for name in dict.fromkeys(n for n in interfaces if n):
        if name not in entries:
            err(f'the interface "{name}" has no contract entry (add "### {name}" under ## Contracts)')
    seen_entries = set()
    for name in filter(None, entries):
        if name in seen_entries:
            err(f'the contract entry "{name}" is repeated')
        seen_entries.add(name)
    listed = set(interfaces)
    for name in dict.fromkeys(n for n in entries if n):
        if name not in listed:
            warn(f'the contract entry "{name}" has no interface line')


def clause_words(clause: str) -> set:
    """A clause's words: runs of five or more ASCII letters, lowercased."""
    return {word.lower() for word in CLAUSE_WORD.findall(clause)}


def distinctive_words(clauses: list) -> list:
    """For each clause, the words no other clause of the statement has."""
    words = [clause_words(clause) for clause in clauses]
    return [own - set().union(*(other for j, other in enumerate(words) if j != i))
            for i, own in enumerate(words)]


def scenario_words(req) -> set:
    """The lowercased letter runs of the Given, When and Then cells of the requirement's scenarios."""
    return {word.lower() for s in req.scenarios for cell in (s["given"], s["when"], s["then"])
            for word in LETTERS.findall(cell)}


def check_requirement_clauses(req, warn):
    """REQ-ANL-006: warn about each clause of the statement whose distinctive words no scenario has."""
    clauses = [c.strip() for c in req.text.split(";") if c.strip()]
    if len(clauses) < 2:
        return
    mentioned = scenario_words(req)
    for clause, distinct in zip(clauses, distinctive_words(clauses)):
        if distinct and not distinct & mentioned:
            shown = clause[:-1] if clause.endswith(".") else clause
            warn(f'{req.id}: no scenario exercises the clause "{shown}" (heuristic)')


def check_balance(report: Report, warn):
    """REQ-ANL-007: warn when happy scenarios outnumber every non-happy one (boundary included)."""
    sc = report.counts["scenarios"]
    happy, negative, boundary, level = sc["happy"], sc["negative"], sc["boundary"], report.level
    if happy > negative + boundary and level != "prototype":
        warn(f"{happy} happy scenarios outweigh {negative + boundary} non-happy ones")


def cross_artifact(project: Project, path: Path, report: Report):
    """Analyze-only findings, appended to check's report; design errors also land in design_errors."""
    design_findings(project, path, report, report.design_error, report.warnings.append)
    for req in (r for r in report.reqs if r.tag != "REMOVED"):
        check_requirement_clauses(req, report.warnings.append)
    check_balance(report, report.warnings.append)


def full_analysis(project: Project, path: Path) -> Report:
    """check's plan-stage report; the cross-artifact findings are appended to it."""
    report = analyze(project, path, "plan")
    cross_artifact(project, path, report)
    return report


def render_analysis(report: Report) -> str:
    """analyze's text report: check's, headed for analyze, with the scenarios line."""
    return report.render(head=f"analyze {report.change_id} (assurance: {report.level})", scenarios=True)


def cmd_analyze(project: Project, args) -> int:
    project.require_init()
    report = full_analysis(project, project.current(args.change))
    defect_findings(project, report)
    if args.json:
        print(json.dumps(report_json(report), indent=2))
    else:
        print(render_analysis(report))
    return 1 if report.errors else 0


GATE_LINES = {
    "spec": "gate: the operator approves the spec (sdd approve spec)",
    "plan": "gate: the operator approves the plan (sdd approve plan)",
    "results": "gate: the operator approves the results (sdd approve results)",
    "review": "gate: the operator reviews the verification, then sdd archive",
    "gaps": "gate: the operator decides on the gaps (amend or accept), then sdd verify",
    "amend": "gate: the operator approves the amendment (sdd approve amend)",
    "none": "gate: none",
}


def next_lines(project: Project, path: Path) -> list:
    """What sdd.py next prints: the numbered steps to the next gate, then the gate line."""
    fm = read_front_matter(path.read_text())
    early = early_lines(project, path, fm)
    if early is not None:
        return early
    steps, gate = next_plan(project, path, fm)
    return [f"{n}. sdd {step}" for n, step in enumerate(steps, 1)] + [GATE_LINES[gate]]


def amendment_logged(whole: str) -> bool:
    """Whether an edit is logged under ## Amendments and not yet approved: more entries than amend approvals."""
    logged = sum(1 for line in sections(strip_comments(whole)).get("Amendments", "").splitlines()
                 if AMENDMENT_ENTRY.match(line))
    return logged > approvals(whole).count("amend")


def early_lines(project: Project, path: Path, fm: dict):
    """The one line (or amend step and gate) that replaces everything else, or None, in design.md's
    order: an abandoned change, a changed constitution, an edited approved spec (its amend gate alone
    once the edit is logged), a blocked change."""
    if fm.get("status") == "abandoned":
        return ["nothing to run: the change is abandoned"]
    changed = project.constitution_state()["changed"]
    if changed:
        return [f"{CONSTITUTION_ERROR}: review it, then sdd approve (constitution)"]
    whole = change_text(path)
    if spec_edited_since_approval(fm, whole):
        if not amendment_logged(whole):
            return ["1. sdd amend", GATE_LINES["amend"]]
        return [GATE_LINES["amend"]]
    if fm.get("status") == "blocked":
        return ["blocked: resolve the blocker, then sdd status"]
    return None


def next_plan(project: Project, path: Path, fm: dict) -> tuple:
    """(steps, gate) by size and status, as in design.md's table for sdd.py next."""
    status, size = fm.get("status", "draft"), fm.get("size", "mini")
    if size == "standard" and status in ("draft", "clarifying"):
        return spec_stage_steps(project, path), "spec"
    if size == "standard" and status in ("spec-approved", "designed"):
        return plan_stage_steps(project, path, status), "plan"
    if size == "mini" and status == "draft":
        return mini_draft_steps(project, path), "plan"
    if status in ("planned", "implementing"):
        return implement_stage_steps(status, path), results_gate(size)
    if status == "verifying":
        return verify_stage_steps(path), verify_stage_gate(path, size)
    if status == "verified" and size == "mini":
        return [], "review"
    if status == "verified":
        return ["archive"], "none"
    raise SddError(f'cannot list steps: unknown status "{status}"')


def results_gate(size: str) -> str:
    """The gate after verify: the operator approves the results (standard) or reviews them (mini)."""
    return "results" if size == "standard" else "review"


def implement_stage_steps(status: str, path: Path) -> list:
    """A change between the plan gate and its results gate: implement while it is planned or a task
    is unticked, then verify."""
    tasks, _ = parse_tasks(sections(strip_comments(change_text(path))).get("Tasks", ""))
    unticked = sum(1 for task in tasks if not task["done"])
    steps = ["implement"] if status == "planned" or unticked else []
    return steps + ["verify"]


def verifier_verdict(path: Path):
    """(word, rest) of the change's latest Verifier verdict, or None."""
    return latest_verdict(sections(strip_comments(change_text(path))).get("Verification", ""))


def verify_stage_steps(path: Path) -> list:
    """A change at verifying: verify until the Verifier has written a verdict."""
    return ["verify"] if verifier_verdict(path) is None else []


def verify_stage_gate(path: Path, size: str) -> str:
    """The results gate, or the gaps gate when the latest verdict is not PASS."""
    found = verifier_verdict(path)
    return "gaps" if found and found[0].upper() != "PASS" else results_gate(size)


def spec_stage_steps(project: Project, path: Path) -> list:
    """A standard change before the spec gate: specify while the spec has a problem, then clarify
    while it applies."""
    report = analyze(project, path, "spec")
    steps = []
    if spec_needs_work(report):
        steps.append("specify")
    if clarify_applies(report):
        steps.append("clarify")
    return steps


def spec_needs_work(report: Report) -> bool:
    """No requirements yet, or a spec error that is not about a Critic round: specify fixes it."""
    return report.counts["requirements"] == 0 or bool(spec_errors_outside_rounds(report))


def mini_draft_steps(project: Project, path: Path) -> list:
    """A mini draft, which has one gate (plan): specify, tasks, then clarify, each while it applies."""
    report = analyze(project, path, "spec")
    wanted = [
        ("specify", spec_needs_work(report)),
        ("tasks", needs_tasks(project, path, report)),
        ("clarify", clarify_applies(report)),
    ]
    return [step for step, applies in wanted if applies]


def needs_tasks(project: Project, path: Path, report: Report) -> bool:
    """No tasks yet, or a plan-stage error that the spec stage does not report (tasks fixes those)."""
    return not report.counts["tasks"]["total"] or bool(plan_errors_only(project, path, report))


def plan_errors_only(project: Project, path: Path, spec_report: Report) -> list:
    """The plan-stage errors the spec stage does not report, other than the design errors (REQ-ANL-002 to 005)."""
    full = full_analysis(project, path)
    return [error for error in full.errors if error not in spec_report.errors and error not in full.design_errors]


def spec_errors_outside_rounds(report: Report) -> list:
    """The spec-stage errors that are not about a Critic round (those are for clarify to fix)."""
    return [error for error in report.errors if error not in report.round_errors]


def clarify_applies(report: Report) -> bool:
    """Whether the Spec Critic's round still has work: a gate error, an open question or a finding."""
    return bool(report.critic or report.open_questions)


def plan_stage_steps(project: Project, path: Path, status: str) -> list:
    """A standard change between the spec and plan gates: design, tasks, analyze; at designed, design
    only while a design rule (REQ-ANL-002 to REQ-ANL-005) reports an error, tasks only while there
    are none or a plan error (other than a design error) is reported."""
    if status == "spec-approved":
        return ["design", "tasks", "analyze"]
    report = full_analysis(project, path)
    steps = []
    if report.design_errors:
        steps.append("design")
    if needs_tasks(project, path, analyze(project, path, "spec")):
        steps.append("tasks")
    return steps + ["analyze"]


def cmd_next(project: Project, args) -> int:
    project.require_init()
    for line in next_lines(project, project.current(args.change)):
        print(line)
    return 0


def cmd_approve(project: Project, args) -> int:
    project.require_init()
    evidence = args.evidence.strip()
    if not evidence:
        raise SddError("approval needs --evidence: the operator's words and where they were given")
    if args.gate == "constitution":
        state = project.constitution_state()
        text, fm = state["text"], state["fm"]
        level = fm.get("assurance", "")
        if level not in LEVELS:
            raise SddError(f"the constitution's assurance level '{level or '(missing)'}' is not one of: "
                           f"{', '.join(LEVELS)}")
        if state["reference"] and not state["changed"]:
            raise SddError("nothing changed since approval: the constitution matches its last approval")
        again = fm.get("approved") == "yes"
        note = f"· fingerprint {state['current']} · level {level}"
        previous = state["approved_level"]
        if previous and LEVELS.index(level) < LEVELS.index(previous):
            note += f" · assurance lowered {previous} → {level}"
        for key, value in (("approved", "yes"), ("fingerprint", state["current"]), ("approved_level", level)):
            text = set_front_matter(text, key, value)
        project.constitution.write_text(text)
        append_approval(project.constitution, "constitution (re-approval)" if again else "constitution",
                        f"{evidence} {note}")
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
        if report.critic:
            raise SddError("spec approval refused: " + "; ".join(report.critic))
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
        problem = verdict_problem(change_text(path))
        if problem:
            raise SddError(f"results approval refused: {problem}")
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
        report = full_analysis(project, path)
        if report.errors:
            print(render_analysis(report))
            raise SddError("plan approval refused: fix the analyze errors first")
        if report.open_questions:
            raise SddError(f"plan approval refused: {report.open_questions} open question(s) "
                           "must be answered first")
        if size != "standard" and report.critic:  # standard met this at the spec gate
            raise SddError("plan approval refused: " + "; ".join(report.critic))
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
    if not amendment_logged(whole):
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
        problem = verdict_problem(change_text(path))
        if problem:
            raise SddError(f"cannot mark verified: {problem}")
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
    pending, actions, touched = {}, {}, {}
    for req in reqs:
        info = registry.get(req.prefix)
        if info is None:
            name = declared[req.prefix]
            info = registry[req.prefix] = {"name": name, "reqs": set(),
                                           "path": project.capabilities / name / "spec.md"}
        cap_path = info["path"]
        touched[req.prefix] = (info["name"], cap_path)  # removed requirements touch too
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
    routed = [route_gap(g, touched) for g in gaps]
    for cap_path, done in actions.items():  # per file: one spec may hold several prefixes
        prefixes = {prefix for prefix, (_, path) in touched.items() if path == cap_path}
        head, blocks = split_capability(pending[cap_path])
        head = insert_in_section(head, "Known gaps",
                                 [f"- {text} ({change_id})" for text, to in routed if prefixes & to])
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


GAP_TAG = re.compile(r"^(.*\S) \(([a-z0-9-]+(?:, ?[a-z0-9-]+)*)\)(\.?)$")


def route_gap(gap: str, touched: dict) -> tuple:
    """(text, prefixes) of the touched capabilities a known gap is written into.

    A trailing "(name, name)" tag naming touched capabilities wins and is removed (a final
    period stays); else the touched capabilities whose requirement IDs the gap names; else all."""
    tag = GAP_TAG.match(gap)
    if tag:
        names = {n.strip() for n in tag.group(2).split(",")}
        by_name = {name: prefix for prefix, (name, _) in touched.items()}
        if names <= set(by_name):
            return tag.group(1) + tag.group(3), {by_name[n] for n in names}
    named = {m for m in re.findall(r"REQ-([A-Z][A-Z0-9]{1,5})-\d{3,}", gap) if m in touched}
    return gap, named or set(touched)


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


def append_to_section(text: str, name: str, new_lines: list, before=("Amendments", "Approvals")) -> str:
    """Append lines at the end of '## name'; create the section (before `before`) if missing."""
    lines = text.rstrip("\n").splitlines()
    if f"## {name}" not in lines:
        at = next((i for i, l in enumerate(lines) if l in [f"## {b}" for b in before]), len(lines))
        lines[at:at] = [f"## {name}", ""]
    start = lines.index(f"## {name}")
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    lines[end:end] = [""] + new_lines
    return "\n".join(lines) + "\n"


def cmd_round(project: Project, args) -> int:
    project.require_init()
    path = project.current(args.change)
    fm = read_front_matter(path.read_text())
    if fm.get("status") not in ("draft", "clarifying"):
        raise SddError(f"change is '{fm.get('status')}': Critic rounds happen before the gate; "
                       "after approval, spec changes go through sdd amend")
    secs = sections(strip_comments(change_text(path)))
    reqs, _ = parse_requirements(secs.get("Requirements", ""))
    current = [r.id for r in reqs if r.tag != "REMOVED"]
    if not current:
        raise SddError("no requirements to review yet: write them first (sdd specify)")
    rounds = parse_rounds(secs.get("Clarifications", ""))
    number = max([r["number"] for r in rounds] or [0]) + 1
    mode = f"subagent ({args.subagent})" if args.subagent else \
        "fresh session" if args.fresh else "same session"
    block = [f"### Round {number} — {today()} · Critic: {mode}", "",
             "| REQ | Verdict | Notes |", "| --- | --- | --- |"]
    block += [f"| {rid} | ? | |" for rid in current]
    block += ["", "<!-- Findings: - F1 [type] REQ-…: <problem> → fixed: … | accepted: … | "
              "rejected: <reason> | Q1", "Questions (at most 5): - Q1 <question> A) … B) … — "
              "recommended: …", "  - Answer: pending -->"]
    target = path.parent / "clarifications.md" if path.name == "proposal.md" else path
    if not target.exists():
        target.write_text(render("standard/clarifications.md"))
    target.write_text(append_to_section(target.read_text(), "Clarifications", block))
    if fm.get("size") == "standard" and fm.get("status") == "draft":
        path.write_text(set_front_matter(path.read_text(), "status", "clarifying"))
    print(f"added Round {number} ({mode}) to {target.relative_to(project.root)}: give each "
          "requirement a verdict (ok or issues), then findings and at most 5 questions")
    return 0


# ---------------------------------------------------------------- scripted evidence (replay, mutate)

def test_one(clean_text: str) -> str:
    """The design's per-test command template; refuses when there is none."""
    match = re.search(r"^\s*[-*]\s*Test one\s*:[ \t]*(.*)$", clean_text, re.M)
    template = match.group(1).strip().strip("`").strip() if match else ""
    if not template:
        raise SddError('no "Test one:" line in the design: add one, e.g. '
                       '"- Test one: `python3 -m unittest {name}`"')
    return template


def expand(template: str, test_line: str):
    """The command for one test, or None when the template needs '::' and the line has none."""
    file, sep, name = test_line.partition("::")
    if not sep and ("{file}" in template or "{name}" in template):
        return None
    values = {"{test}": test_line, "{file}": file, "{name}": name}
    argv = []
    for token in shlex.split(template):
        for key, value in values.items():
            token = token.replace(key, value)
        argv.append(token)
    return argv


def run_test(argv: list, cwd: Path) -> bool:
    """Exit code 0 is a pass; anything else, or a runner that can't start, is a failure."""
    try:
        result = subprocess.run(argv, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        return False
    return result.returncode == 0


@contextlib.contextmanager
def scratch(kind: str):
    folder = Path(tempfile.mkdtemp(prefix=f"sdd-{kind}-"))
    try:
        yield folder
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def require_git(project: Project, command: str):
    try:
        inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=project.root,
                                capture_output=True, text=True)
    except OSError:
        inside = None
    if inside is None or inside.returncode != 0 or inside.stdout.strip() != "true":
        raise SddError(f"{command} needs a git repository (git must be installed and the project "
                       "under version control)")


def git_output(project: Project, *args) -> str:
    return subprocess.run(["git", *args], cwd=project.root, capture_output=True, text=True,
                          check=True).stdout


def base_copy(project: Project, rev: str, folder: Path) -> Path:
    """Extract the base revision into folder; return the project root inside it."""
    prefix = git_output(project, "rev-parse", "--show-prefix").strip()
    archive = subprocess.run(["git", "archive", "--format=tar", rev], cwd=project.root,
                             capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        if hasattr(tarfile, "data_filter"):  # Python 3.12+, and patched earlier releases
            tar.extractall(folder, filter="data")
        else:
            tar.extractall(folder)
    return folder / prefix


def listed_files(project: Project) -> list:
    """Tracked and untracked, not ignored, files that exist, relative to the project root."""
    out = git_output(project, "ls-files", "--cached", "--others", "--exclude-standard")
    return [rel for rel in out.splitlines() if rel and (project.root / rel).is_file()]


def overlay_tests(project: Project, target: Path):
    """Lay every current test file (outside specs/) over a copy of another revision."""
    for rel in listed_files(project):
        if is_test_path(rel) and Path(rel).parts[0] != "specs":
            (target / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(project.root / rel, target / rel)


def cmd_replay(project: Project, args) -> int:
    project.require_init()
    path = project.current(args.change)
    clean = strip_comments(change_text(path))
    template = test_one(clean)
    require_git(project, "replay")
    known = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{args.base}^{{commit}}"],
                           cwd=project.root, capture_output=True)
    if known.returncode != 0:
        raise SddError(f"unknown base revision '{args.base}'")
    tasks, _ = parse_tasks(sections(clean).get("Tasks", ""))
    mismatches, earlier = 0, set()
    with scratch("replay") as folder:
        base_root = base_copy(project, args.base, folder)
        overlay_tests(project, base_root)
        for task in tasks:
            depends = re.search(r"\(after (T\d+)\)", task["red"])
            depends = depends.group(1) if depends and depends.group(1) in earlier else None
            earlier.add(task["id"])
            if not task["done"]:
                print(f"{task['id']} skipped (not ticked)")
                continue
            if not evidence_present(task["test"]):
                mismatches += 1
                print(f"{task['id']} mismatch: no test to run")
                continue
            argv = expand(template, task["test"])
            if argv is None:
                mismatches += 1
                print(f'{task["id"]} mismatch: the test line has no "::"')
                continue
            print(f"run: {' '.join(shlex.quote(a) for a in argv)}")
            if depends:
                if run_test(argv, project.root):
                    print(f"{task['id']} confirmed now (depends on {depends})")
                else:
                    mismatches += 1
                    print(f"{task['id']} mismatch: the test fails now")
                continue
            at_base, now = run_test(argv, base_root), run_test(argv, project.root)
            claims_red = not task["red"].lower().startswith("pre-existing")
            if not now:
                problem = "the test fails now"
            elif claims_red and at_base:
                problem = "red claimed, but the test passes at the base"
            elif not claims_red and not at_base:
                problem = "pre-existing claimed, but the test fails at the base"
            else:
                problem = None
            if problem:
                mismatches += 1
                print(f"{task['id']} mismatch: {problem}")
            else:
                print(f"{task['id']} confirmed")
    ticked = sum(1 for task in tasks if task["done"])
    if not ticked:
        print("nothing to replay: no ticked task")
    else:
        print(f"replay: {ticked - mismatches} confirmed, {mismatches} mismatch, "
              f"{len(tasks) - ticked} skipped")
    return 1 if mismatches else 0


def tree_copy(project: Project, target: Path):
    for rel in listed_files(project):
        (target / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(project.root / rel, target / rel)


def run_mutation(project: Project, m: dict, tasks: list, template: str) -> str:
    """'caught', 'survived' or 'invalid: <why>' for one planned mutation."""
    if m.get("find") is None or m.get("replace") is None:
        return "invalid: the entry is incomplete (run sdd check)"
    tests = [task["test"] for task in tasks
             if m["scenario"] in task["refs"] and evidence_present(task["test"])]
    if not tests:
        return "invalid: no test to run"
    commands = [expand(template, test) for test in tests]
    if None in commands:
        return 'invalid: the test line has no "::"'
    if not m["file"] or unsafe_path(m["file"]):
        return "invalid: the file is missing or outside the project"
    if not (project.root / m["file"]).is_file():
        return "invalid: the file doesn't exist"
    occurrences = (project.root / m["file"]).read_text().count(m["find"])
    if occurrences == 0:
        return "invalid: the find text is not in the file"
    if occurrences > 1:
        return f"invalid: the find text occurs {occurrences} times"
    with scratch("mutate") as folder:
        tree_copy(project, folder)
        if not all(run_test(argv, folder) for argv in commands):
            return "invalid: the test fails without the mutation"
        target = (folder / m["file"]).resolve()
        if folder.resolve() not in target.parents:
            return "invalid: the file is missing or outside the project"
        target.write_text(target.read_text().replace(m["find"], m["replace"], 1))
        after = [run_test(argv, folder) for argv in commands]
    return "survived" if all(after) else "caught"


def cmd_mutate(project: Project, args) -> int:
    project.require_init()
    clean = strip_comments(change_text(project.current(args.change)))
    secs = sections(clean)
    mutations = parse_mutations(secs.get("Mutations", ""))
    if not mutations:
        print("no mutations are planned: nothing to run")
        return 0
    template = test_one(clean)
    require_git(project, "mutate")
    tasks, _ = parse_tasks(secs.get("Tasks", ""))
    failed = 0
    for m in mutations:
        result = run_mutation(project, m, tasks, template)
        failed += result != "caught"
        print(f"{m['id']} {result}")
    print(f"mutate: {len(mutations) - failed} caught, {failed} survived or invalid")
    return 1 if failed else 0


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


# ---------------------------------------------------------------- sort-failures

def change_plan(path: Path) -> tuple:
    """The change's scenario refs (its non-removed requirements) and its tasks, in plan order."""
    secs = sections(strip_comments(change_text(path)))
    reqs, _ = parse_requirements(secs.get("Requirements", ""))
    refs = [f"{r.id}.{s['id']}" for r in reqs if r.tag != "REMOVED" for s in r.scenarios]
    tasks, _ = parse_tasks(secs.get("Tasks", ""))
    return refs, tasks


def cmd_sort_failures(project: Project, args) -> int:
    project.require_init()
    path = project.current(args.change)
    try:
        lines = Path(args.file).read_text().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise SddError(f"cannot read {args.file}: {exc.strerror if isinstance(exc, OSError) else exc}")
    names = list(dict.fromkeys(line.strip() for line in lines if line.strip()))  # file order, first kept
    refs, tasks = change_plan(path)
    counts = {"regression": 0, "expected": 0, "outside": 0}
    for name in names:
        found = sorted((m.start(), ref) for ref in refs for m in [scenario_pattern(ref).search(name)] if m)
        if not found:
            counts["outside"] += 1
            print(f"outside: {name}")
            continue
        ids = [ref for _, ref in found]
        ticked = [(ref, t) for ref in ids for t in tasks if t["done"] and ref in t["refs"]]
        if ticked:
            ref, task = ticked[0]
            counts["regression"] += 1
            print(f"regression: {name} ({ref}, {task['id']} done)")
        else:
            planners = [t["id"] + " not done" for t in tasks if ids[0] in t["refs"]]
            counts["expected"] += 1
            print(f"expected: {name} ({ids[0]}, {planners[0] if planners else 'no task'})")
    print(f"sorted: {counts['regression']} regression, {counts['expected']} expected, "
          f"{counts['outside']} outside the change")
    return 1 if counts["regression"] else 0


# ---------------------------------------------------------------- defect log

DEFECT_COLUMNS = ["ID", "Status", "Severity", "Decision", "Capability", "Change", "Test", "Evidence",
                  "Close evidence"]
DEFECT_HEADER = "| " + " | ".join(DEFECT_COLUMNS) + " |"
DEFECT_SEPARATOR = "| --- " * len(DEFECT_COLUMNS) + "|"
DEFECT_STATUSES = ["open", "closed"]
DEFECT_SEVERITIES = ["critical", "major", "minor"]
DEFECT_DECISIONS = ["fix-now", "later", "wont-fix"]
NAME_REQ = re.compile(r"REQ[-_]([A-Z][A-Z0-9]{1,5})[-_]\d+", re.I)


def defect_row(cells: list) -> str:
    """A row as written: '| ' + cells joined by ' | ' + ' |' (an empty cell is two spaces, a | is \\|)."""
    return "| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |"


class DefectLog:
    """specs/defects.md as written: its text, its lines, its rows (with line numbers) and the first problem."""

    def __init__(self, path: Path):
        self.path = path
        self.exists = path.exists()
        self.text = path.read_text() if self.exists else ""
        self.lines = self.text.splitlines()
        self.rows, self.problem = [], None
        # comments blanked to as many newlines, so that line numbers stay true
        view = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), self.text, flags=re.S)
        self.table = [(number, line) for number, line in enumerate(view.splitlines(), 1) if line.startswith("|")]
        for number, line in self.table[:1]:
            if table_cells(line) != DEFECT_COLUMNS:  # table_cells trims each cell
                self.problem = f"specs/defects.md line {number}: the header must be the cells " + \
                    ", ".join(DEFECT_COLUMNS)
                return
        if len(self.table) == 1:
            self.problem = f"specs/defects.md line {self.table[0][0]}: the header has no separator row after it"
            return
        for number, line in self.table[1:2]:
            if not all(re.fullmatch(r":?-+:?", cell) for cell in table_cells(line)):
                self.problem = f"specs/defects.md line {number}: the second table line must be a separator row"
                return
        for number, line in self.table[2:]:
            cells = table_cells(line)
            padded = cells + [""] * (len(DEFECT_COLUMNS) - len(cells))
            row = {"line": number, "cells": cells, "id": padded[0], "status": padded[1],
                   "severity": padded[2], "decision": padded[3], "test": padded[6]}
            problem = self.row_problem(row)
            first = [r["line"] for r in self.rows if r["id"] == row["id"]]
            if not problem and first:
                problem = f"{row['id']} is repeated (first on line {first[0]})"
            if problem:
                self.problem = f"specs/defects.md line {number}: {problem}"
                break
            self.rows.append(row)

    @staticmethod
    def row_problem(row: dict) -> str:
        """What is wrong with a row ("" when it is valid)."""
        if len(row["cells"]) != len(DEFECT_COLUMNS):
            return f"a row needs {len(DEFECT_COLUMNS)} cells, found {len(row['cells'])}"
        if not re.fullmatch(r"D\d+", row["id"]):
            return f'the ID "{row["id"]}" is not D<n>'
        for name, allowed in (("status", DEFECT_STATUSES), ("severity", DEFECT_SEVERITIES),
                              ("decision", ["undecided"] + DEFECT_DECISIONS)):
            if row[name] not in allowed:
                return f'{name} "{row[name]}" is not {", ".join(allowed[:-1])} or {allowed[-1]}'
        return ""


def read_defect_log(project: Project) -> DefectLog:
    return DefectLog(project.specs / "defects.md")


def defect_counts(log: DefectLog):
    """The open defects, how many critical and how many undecided; None for an invalid log (REQ-DEF-004)."""
    if log.problem:
        return None
    open_rows = [r for r in log.rows if r["status"] == "open"]
    return {"open": len(open_rows), "critical": sum(r["severity"] == "critical" for r in open_rows),
            "undecided": sum(r["decision"] == "undecided" for r in open_rows)}


def defect_line(counts) -> str:
    """The text line for the open defects ("" when there are none)."""
    if not counts or not counts["open"]:
        return ""
    return f"open defects: {counts['open']} ({counts['critical']} critical, {counts['undecided']} undecided)"


def defect_capability(test: str) -> str:
    """The first requirement prefix the test name carries, in capitals."""
    match = NAME_REQ.search(test)
    if not match:
        raise SddError("the test name carries no requirement ID: name the capability with --capability <PREFIX>")
    return match.group(1).upper()


def cmd_defect_add(project: Project, args) -> int:
    project.require_init()
    path = project.current(args.change)
    change_id = path.parent.name
    if not args.test.strip():
        raise SddError("the test name is empty")
    capability = args.capability or defect_capability(args.test)
    declared = parse_capabilities(read_front_matter(path.read_text()).get("capabilities", ""))
    if capability not in project.registry() and capability not in declared:
        raise SddError(f'capability "{capability}" is not a prefix of the living spec or of {change_id}')
    log = read_defect_log(project)
    if log.problem:  # an invalid log is never appended to
        raise SddError(log.problem)
    for r in log.rows:
        if r["test"] == args.test and r["status"] == "open":
            raise SddError(f"{args.test} already has an open defect: {r['id']}")
    number = 1 + max([int(r["id"][1:]) for r in log.rows if re.fullmatch(r"D\d+", r["id"])] or [0])
    row = defect_row([f"D{number}", "open", args.severity, "undecided", capability, change_id, args.test, "", ""])
    table = f"{DEFECT_HEADER}\n{DEFECT_SEPARATOR}\n{row}\n"
    ending = "" if log.text.endswith("\n") else "\n"
    if not log.text.strip():
        log.path.write_text(f"# Defects\n\n{table}")
    else:  # append: the lines already written stay as they are
        with log.path.open("a") as handle:
            handle.write(ending + (row + "\n" if log.table else "\n" + table))
    print(f"D{number} added ({args.severity}, {capability})")
    return 0


def set_cells(line: str, changes: dict) -> str:
    """The row line with cell index → value written as ' value ' (a | as \\|) where the cell's value
    differs; every other segment stays as written."""
    parts = re.split(r"(?<!\\)\|", line)
    for index, value in changes.items():
        if parts[1 + index].strip().replace("\\|", "|") != value:
            escaped = value.replace("|", "\\|")
            parts[1 + index] = f" {escaped} "
    return "|".join(parts)


def one_line(text: str) -> str:
    """Evidence as one cell: line breaks become spaces, surrounding spaces are removed."""
    return re.sub(r"\r\n|\r|\n", " ", text).strip()


def defect_lookup(project: Project, defect_id: str):
    """The log and the row a decide or close names (REQ-DEF-002, REQ-DEF-003)."""
    if not re.fullmatch(r"D\d+", defect_id):
        raise SddError(f'"{defect_id}" is not a defect ID: write D<n>')
    log = read_defect_log(project)
    if not log.exists:
        raise SddError("no defect is logged (specs/defects.md does not exist)")
    if log.problem:  # an invalid log is never rewritten
        raise SddError(log.problem)
    for row in log.rows:
        if row["id"] == defect_id:
            return log, row
    raise SddError(f"no defect {defect_id} in specs/defects.md")


def write_cells(log: DefectLog, row: dict, changes: dict) -> None:
    """Rewrite only the row's line, with its changed cells; every other byte of the log stays as written."""
    with log.path.open(newline="") as handle:
        lines = handle.read().splitlines(keepends=True)
    old = lines[row["line"] - 1]
    content = old.rstrip("\r\n")
    new = set_cells(content, changes)
    if new == content:
        return
    lines[row["line"] - 1] = new + old[len(content):]
    with log.path.open("w", newline="") as handle:
        handle.write("".join(lines))


def cmd_defect_decide(project: Project, args) -> int:
    project.require_init()
    if not (args.evidence or "").strip():
        raise SddError("a decision needs the operator's words: add --evidence \"<what they said>\"")
    log, row = defect_lookup(project, args.id)
    if row["status"] == "closed":
        raise SddError(f"{args.id} is closed: its decision can't change")
    write_cells(log, row, {3: args.decision, 7: one_line(args.evidence)})
    print(f"{args.id}: {args.decision}")
    return 0


def cmd_defect_close(project: Project, args) -> int:
    project.require_init()
    log, row = defect_lookup(project, args.id)
    if row["status"] == "closed":
        raise SddError(f"{args.id} is already closed")
    if row["decision"] == "undecided":
        raise SddError(f"{args.id} has no decision: the operator decides first (sdd.py defect decide)")
    if not (args.evidence or "").strip():
        raise SddError("closing needs --evidence: what fixed the defect, or why it is closed")
    write_cells(log, row, {1: "closed", 8: one_line(args.evidence)})
    print(f"{args.id} closed")
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

    p = sub.add_parser("analyze", help="check's plan report plus the cross-artifact findings")
    p.add_argument("--change")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("next", help="the steps to the next gate, in order (writes nothing)")
    p.add_argument("--change")
    p.set_defaults(func=cmd_next)

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

    p = sub.add_parser("round", help="start a Spec Critic review round on the active change")
    runner = p.add_mutually_exclusive_group()
    runner.add_argument("--fresh", action="store_true", help="the Critic runs in a fresh session")
    runner.add_argument("--subagent", choices=TIERS, help="the Critic runs as a subagent on this tier")
    p.add_argument("--change")
    p.set_defaults(func=cmd_round)

    p = sub.add_parser("replay", help="rerun each ticked task's test at a base revision and now")
    p.add_argument("--base", required=True, help="the revision before the change (e.g. main)")
    p.add_argument("--change")
    p.set_defaults(func=cmd_replay)

    p = sub.add_parser("mutate", help="run the change's planned mutations against their tests")
    p.add_argument("--change")
    p.set_defaults(func=cmd_mutate)

    p = sub.add_parser("next-req", help="next free requirement ID for a prefix")
    p.add_argument("prefix")
    p.set_defaults(func=cmd_next_req)

    p = sub.add_parser("use", help="make another change active")
    p.add_argument("change_id")
    p.set_defaults(func=cmd_use)

    p = sub.add_parser("sort-failures", help="sort failing tests into regressions, expected failures and the rest")
    p.add_argument("file", help="the failing test names, one per line")
    p.add_argument("--change")
    p.set_defaults(func=cmd_sort_failures)

    p = sub.add_parser("defect", help="record a defect in specs/defects.md")
    defect = p.add_subparsers(dest="defect_command", required=True)
    p = defect.add_parser("add", help="add an open, undecided defect for a failing test")
    p.add_argument("--test", required=True)
    p.add_argument("--severity", required=True, choices=DEFECT_SEVERITIES)
    p.add_argument("--capability", metavar="PREFIX")
    p.add_argument("--change")
    p.set_defaults(func=cmd_defect_add)
    p = defect.add_parser("decide", help="record the operator's decision on an open defect")
    p.add_argument("id", help="the defect ID, D<n>")
    p.add_argument("decision", choices=DEFECT_DECISIONS)
    p.add_argument("--evidence", help="the operator's words")
    p.set_defaults(func=cmd_defect_decide)
    p = defect.add_parser("close", help="close a decided defect, with what fixed it or why it is closed")
    p.add_argument("id", help="the defect ID, D<n>")
    p.add_argument("--evidence", help="what fixed the defect, or why it is closed")
    p.set_defaults(func=cmd_defect_close)
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
