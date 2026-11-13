"""Copy item IDs and statuses from Codebeamer into data/netbank.json.

Git holds the text of requirements, stories, and tests. Codebeamer holds
their IDs and workflow status. This script brings the Codebeamer side into
the repository before the PDF documents are built, so that every document
shows the current status of every item.

Usage:  python3 ci/pull_status.py [data/netbank.json]
Items are matched by name: "NB-SR8 IMPS transfer", "Send money by IMPS",
"AT-14.1 IMPS success".
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cb_client import Codebeamer  # noqa: E402


def main(path):
    data = json.load(open(path))
    if not os.environ.get("CB_URL"):
        print("CB_URL is not set: keeping the statuses in", path)
        return 0
    cb = Codebeamer()
    p = data["project"]
    found = {}
    for tracker in ("System Requirement Specifications", "User Stories", "Test Cases"):
        for i in cb.query("project.name = '%s' AND tracker.name = '%s'" % (p, tracker)):
            found[i["name"]] = (i["id"], i["status"]["name"])
    hits = 0
    for r in data["requirements"]:
        hit = found.get(r["key"] + " " + r["summary"]) or found.get(r["summary"])
        if hit:
            r["cb_id"], r["status"] = hit
            hits += 1
    for s in data["stories"]:
        hit = found.get(s["summary"])
        if hit:
            s["cb_id"], s["status"] = hit
            hits += 1
        for sc in s["scenarios"]:
            hit = found.get(sc["key"] + " " + sc["name"])
            if hit:
                sc["cb_id"], sc["status"] = hit
                hits += 1
    json.dump(data, open(path, "w"), indent=1)
    print("Updated %d items in %s from %s" % (hits, path, cb.url))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "data/netbank.json"))
