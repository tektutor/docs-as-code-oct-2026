"""Send the JUnit results of the acceptance tests to Codebeamer as one test run.

Usage:
    python3 ci/report_test_results.py build/test-results/junit.xml "NetBank build 42"

Each pytest test is named after its Codebeamer test case, for example
test_AT_14_1_imps_success belongs to the test case whose name starts with
"AT-14.1". The script finds those test cases with cbQL, creates a test run in
the Test Runs tracker, and records PASSED or FAILED for each of them.
It also writes build/test-results/summary.json for the PDF test report.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cb_client import Codebeamer  # noqa: E402

NAME = re.compile(r"test_AT_(\d+)_(\d+)")


def read_junit(path):
    """{'AT-14.1': ('PASSED', ''), 'AT-9.1': ('FAILED', 'assert 9 == 10'), ...}"""
    results = {}
    for case in ET.parse(path).iter("testcase"):
        m = NAME.search(case.get("name", ""))
        if not m:
            continue
        key = "AT-%s.%s" % m.groups()
        failure = case.find("failure")
        if failure is None:
            failure = case.find("error")
        if failure is not None:
            results[key] = ("FAILED", (failure.get("message") or "")[:300])
        elif case.find("skipped") is not None:
            results[key] = ("BLOCKED", "skipped")
        else:
            results[key] = ("PASSED", "")
    return results


def write_summary(results, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({k: {"result": r, "message": m} for k, (r, m) in sorted(results.items())},
              open(path, "w"), indent=1)


def find_tracker(cb, project, tracker):
    """ID of a tracker, found by project name and tracker name."""
    if os.environ.get("CB_TEST_RUN_TRACKER"):
        return int(os.environ["CB_TEST_RUN_TRACKER"])
    pid = next(p["id"] for p in cb.get("/projects") if p["name"] == project)
    for t in cb.get("/projects/%d/trackers" % pid):
        if t["name"] == tracker:
            return t["id"]
    raise SystemExit("No tracker '%s' in project %s" % (tracker, project))


def main(junit, run_name, project="NETBANK-DEMO"):
    results = read_junit(junit)
    write_summary(results, os.path.join(os.path.dirname(junit), "summary.json"))
    print("Read %d results: %d passed, %d failed" % (
        len(results), sum(r == "PASSED" for r, _ in results.values()),
        sum(r == "FAILED" for r, _ in results.values())))
    if os.environ.get("CB_URL", "") == "":
        print("CB_URL is not set: summary written, nothing sent to Codebeamer.")
        return 0

    cb = Codebeamer()
    cases = cb.query("project.name = '%s' AND tracker.name = 'Test Cases'" % project)
    by_key = {}
    for c in cases:
        m = re.match(r"(AT-\d+\.\d+)\b", c["name"])
        if m:
            by_key[m.group(1)] = c["id"]
    missing = sorted(set(results) - set(by_key))
    if missing:
        print("No test case in Codebeamer for: " + ", ".join(missing))
    keys = [k for k in sorted(results) if k in by_key]
    tracker_id = find_tracker(cb, project, "Test Runs")
    ref = lambda k: {"id": by_key[k], "type": "TrackerItemReference"}
    run = cb.post("/trackers/%d/testruns" % tracker_id, {
        "testCaseIds": [ref(k) for k in keys], "runOnlyAcceptedTestCases": False,
        "testRunModel": {"name": run_name, "description": "Automated acceptance tests from Jenkins.",
                         "descriptionFormat": "PlainText"}})
    cb.put("/testruns/%d" % run["id"], {
        "updateRequestModels": [{"testCaseReference": ref(k), "result": results[k][0],
                                 "conclusion": results[k][1] or "Passed in CI.", "runTime": 1}
                                for k in keys],
        "parentResultPropagation": True})
    print("Created test run %d \"%s\" with %d test cases" % (run["id"], run_name, len(keys)))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
