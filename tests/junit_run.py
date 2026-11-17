"""Run unittest and write the outcome of each test to build/junit.xml (stdlib only).

This repository's JUnit adapter for `sdd.py test`, run from the repository root:

    python3 -m tests.junit_run tests.test_sdd
    python3 -m tests.junit_run tests.test_sdd -k REQ_ORC_

It prints unittest's normal output and exits 0 when the run was successful, else 1.
"""

import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

REPORT = Path("build") / "junit.xml"


def first_line(text: str) -> str:
    lines = str(text).strip().splitlines()
    return lines[0] if lines else ""


class JUnitResult(unittest.TextTestResult):
    """A text result that also keeps each test's outcome, in run order."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = {}  # test id -> (outcome, message, text)

    def record(self, test, outcome, message="", text=""):
        current = self.cases.get(test.id())
        if current and current[0] in ("failure", "error") and outcome == "passed":
            return  # a failed subtest keeps the test failed
        if current and current[0] == "error" and outcome == "failure":
            return
        self.cases[test.id()] = (outcome, message, text)

    def problem(self, test, outcome, err):
        detail = first_line(err[1])
        message = f"{err[0].__name__}: {detail}" if detail else err[0].__name__
        self.record(test, outcome, message, self._exc_info_to_string(err, test))

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.problem(test, "failure", err)

    def addError(self, test, err):
        super().addError(test, err)
        self.problem(test, "error", err)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "skipped", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.record(test, "passed")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.record(test, "failure", "unexpected success")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            kind = "failure" if issubclass(err[0], test.failureException) else "error"
            self.problem(test, kind, err)


def write_report(cases: dict, path: Path = REPORT) -> None:
    counts = {kind: sum(1 for c in cases.values() if c[0] == kind) for kind in ("failure", "error", "skipped")}
    suites = ET.Element("testsuites")
    suite = ET.SubElement(suites, "testsuite", name="unittest", tests=str(len(cases)),
                          failures=str(counts["failure"]), errors=str(counts["error"]),
                          skipped=str(counts["skipped"]))
    for test_id, (outcome, message, text) in cases.items():
        classname, _, name = test_id.rpartition(".")
        case = ET.SubElement(suite, "testcase", classname=classname, name=name)
        if outcome != "passed":
            child = ET.SubElement(case, outcome, message=message)
            child.text = text or None
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suites).write(path, encoding="utf-8", xml_declaration=True)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    runner = unittest.TextTestRunner(resultclass=JUnitResult)
    program = unittest.main(module=None, argv=["python3 -m tests.junit_run", *argv],
                            testRunner=runner, exit=False)
    write_report(program.result.cases)
    return 0 if program.result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
