"""Set the status of one Codebeamer item (Lab 5.7).

    python3 ci/set_status.py "Transfer between my own accounts" Done

The item is found by its exact name with cbQL, then its Status field is set.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cb_client import Codebeamer  # noqa: E402


def main(name, status, project="NETBANK-DEMO"):
    cb = Codebeamer()
    found = cb.query("project.name = '%s' AND summary = '%s'" % (project, name.replace("'", "''")))
    if len(found) != 1:
        sys.exit("Expected 1 item named '%s', found %d" % (name, len(found)))
    item = found[0]
    print("%s  %s  status %s" % (item["id"], item["name"], item["status"]["name"]))
    cb.put("/items/%d/fields" % item["id"], {"fieldValues": [{
        "fieldId": 7, "name": "Status", "type": "ChoiceFieldValue",
        "values": [{"name": status, "type": "ChoiceOptionReference"}]}]})
    print("  is now", cb.get("/items/%d" % item["id"])["status"]["name"])
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
