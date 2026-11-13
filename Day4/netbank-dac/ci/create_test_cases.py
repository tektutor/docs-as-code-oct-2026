"""Create Codebeamer test cases from a CSV file (Lab 5.7).

    python3 ci/create_test_cases.py data/us15-tests.csv

CSV columns: name, pre_action, action, expected. Every row becomes one item in
the Test Cases tracker of NETBANK-DEMO. The script prints the new item IDs.
Run it twice and you get every test case twice: Codebeamer does not check names.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cb_client import Codebeamer  # noqa: E402
from report_test_results import find_tracker  # noqa: E402


def main(path, project="NETBANK-DEMO"):
    cb = Codebeamer()
    tracker_id = find_tracker_by_name(cb, project, "Test Cases")
    for row in csv.DictReader(open(path, encoding="utf-8")):
        body = {"name": row["name"],
                "description": "%s\n\nAction: %s\n\nExpected result: %s" % (
                    row["pre_action"], row["action"], row["expected"]),
                "descriptionFormat": "Wiki"}
        item = cb.post("/trackers/%d/items" % tracker_id, body)
        print("Created %s  %s" % (item["id"], item["name"]))
    return 0


def find_tracker_by_name(cb, project, name):
    os.environ.pop("CB_TEST_RUN_TRACKER", None)
    return find_tracker(cb, project, name)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
