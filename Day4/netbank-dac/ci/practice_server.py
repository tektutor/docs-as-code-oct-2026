"""Practice server: a small imitation of the Codebeamer REST API v3.

It holds NETBANK-DEMO in memory, loaded from data/netbank.json, so that the
REST API and Jenkins labs work without access to a real Codebeamer server.
Only the calls used in the labs exist. Nothing is saved when it stops.

Start it:   python3 ci/practice_server.py           (port 8090)
Log in as:  user "trainee", password "netbank"  or  token "nb-practice-token"
API root:   http://localhost:8090/api/v3
"""
import base64
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "netbank.json")
USER, PASSWORD, TOKEN = "trainee", "netbank", "nb-practice-token"

PROJECT = {"id": 1190, "name": "NETBANK-DEMO", "type": "ProjectReference"}
TRACKERS = {2001: "System Requirement Specifications", 2002: "Epics", 2003: "User Stories",
            2004: "Test Cases", 2005: "Test Runs", 2006: "Bugs", 2007: "Tasks"}
STATUSES = ["New", "Draft", "Accepted", "ToDo", "In progress", "To verify", "Done",
            "Completed", "Resolved", "Closed", "Finished"]
items = {}
next_id = [3001]


def ref(i):
    return {"id": i["id"], "name": i["name"], "type": "TrackerItemReference"}


def new_item(tracker_id, name, status="New", description="", **extra):
    i = {"id": next_id[0], "name": name, "description": description, "descriptionFormat": "Wiki",
         "tracker": {"id": tracker_id, "name": TRACKERS[tracker_id], "type": "TrackerReference"},
         "status": {"id": STATUSES.index(status) + 1, "name": status, "type": "ChoiceOptionReference"},
         "customFields": []}
    i.update(extra)
    items[i["id"]] = i
    next_id[0] += 1
    return i


def load():
    d = json.load(open(DATA))
    req = {r["key"]: new_item(2001, r["key"] + " " + r["summary"], "Accepted", r["text"])
           for r in d["requirements"]}
    epic = {e["key"]: new_item(2002, e["summary"], "In progress", e["goal"]) for e in d["epics"]}
    for s in d["stories"]:
        st = new_item(2003, s["summary"], s["status"], s["story"], storyPoints=s["points"],
                      release={"name": s["sprint"]} if s["sprint"] else None)
        st["subjects"] = [ref(req[k]) for k in s["requirements"]] + [ref(epic[s["epic"]])]
        for sc in s["scenarios"]:
            tc = new_item(2004, sc["key"] + " " + sc["name"], "Accepted",
                          "Given %s. When %s. Then %s." % (sc["given"], sc["when"], sc["then"]))
            tc["verifies"] = [ref(st)] + [ref(req[k]) for k in s["requirements"]]


# ------------------------------------------------------------------ cbQL subset
CLAUSE = re.compile(r"^\s*([\w.]+)\s*(=|!=|IN|NOT IN|LIKE)\s*(.+?)\s*$", re.I)


def values(text):
    return [v.strip().strip("'\"") for v in text.strip().strip("()").split(",")]


def field_of(item, name):
    name = name.lower()
    return {"project.name": PROJECT["name"], "project.id": str(PROJECT["id"]),
            "tracker.name": item["tracker"]["name"], "tracker.id": str(item["tracker"]["id"]),
            "status": item["status"]["name"], "summary": item["name"], "name": item["name"],
            "release": (item.get("release") or {}).get("name", ""),
            "id": str(item["id"])}.get(name)


def matches(item, cbql):
    for part in re.split(r"\s+AND\s+", cbql, flags=re.I):
        m = CLAUSE.match(part)
        if not m:
            raise ValueError("Cannot read this cbQL condition: " + part)
        f, op, raw = m.group(1), m.group(2).upper(), m.group(3)
        val = field_of(item, f)
        if val is None:
            raise ValueError("Unknown field: " + f)
        vs = values(raw)
        if op == "=" and val != vs[0]:
            return False
        if op == "!=" and val == vs[0]:
            return False
        if op == "IN" and val not in vs:
            return False
        if op == "NOT IN" and val in vs:
            return False
        if op == "LIKE" and not re.fullmatch(vs[0].replace("%", ".*"), val):
            return False
    return True


# ------------------------------------------------------------------ HTTP layer
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.command, self.path))

    def reply(self, code, obj):
        body = json.dumps(obj, indent=1).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        h = self.headers.get("Authorization", "")
        if h == "Bearer " + TOKEN:
            return True
        if h.startswith("Basic "):
            return base64.b64decode(h[6:]).decode() == USER + ":" + PASSWORD
        return False

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n)) if n else {}

    def handle_any(self, method):
        if not self.authorized():
            return self.reply(401, {"message": "Not authenticated"})
        u = urlparse(self.path)
        path, q = u.path.replace("/api/v3", "", 1), {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            return self.route(method, path, q)
        except KeyError as e:
            return self.reply(404, {"message": "Not found: %s" % e})
        except ValueError as e:
            return self.reply(400, {"message": str(e)})

    def route(self, method, path, q):
        if method == "GET" and path == "/projects":
            return self.reply(200, [PROJECT])
        if method == "GET" and path == "/projects/%d/trackers" % PROJECT["id"]:
            return self.reply(200, [{"id": k, "name": v, "type": "TrackerReference"} for k, v in TRACKERS.items()])
        m = re.fullmatch(r"/trackers/(\d+)/items", path)
        if m and method == "GET":
            found = [ref(i) for i in items.values() if i["tracker"]["id"] == int(m.group(1))]
            return self.reply(200, {"page": 1, "pageSize": len(found), "total": len(found), "itemRefs": found})
        if m and method == "POST":
            b = self.body()
            i = new_item(int(m.group(1)), b["name"], "New", b.get("description", ""))
            return self.reply(201, i)
        if method == "GET" and path == "/items/query":
            found = [i for i in items.values() if matches(i, q.get("queryString", ""))]
            page, size = int(q.get("page", 1)), int(q.get("pageSize", 25))
            return self.reply(200, {"page": page, "pageSize": size, "total": len(found),
                                    "items": found[(page - 1) * size:page * size]})
        m = re.fullmatch(r"/items/(\d+)", path)
        if m and method == "GET":
            return self.reply(200, items[int(m.group(1))])
        m = re.fullmatch(r"/items/(\d+)/fields", path)
        if m and method == "PUT":
            i = items[int(m.group(1))]
            for fv in self.body().get("fieldValues", []):
                if fv.get("name") == "Status":
                    name = fv["values"][0]["name"]
                    i["status"] = {"id": STATUSES.index(name) + 1, "name": name, "type": "ChoiceOptionReference"}
                elif fv.get("name") == "Description":
                    i["description"] = fv["value"]
            return self.reply(200, i)
        m = re.fullmatch(r"/trackers/(\d+)/testruns", path)
        if m and method == "POST":
            b = self.body()
            cases = [items[c["id"]] for c in b["testCaseIds"]]
            run = new_item(2005, b["testRunModel"]["name"], "In progress",
                           b["testRunModel"].get("description", ""))
            run["testCases"] = [{"testCase": ref(c), "result": None} for c in cases]
            return self.reply(201, run)
        m = re.fullmatch(r"/testruns/(\d+)", path)
        if m and method == "PUT":
            run = items[int(m.group(1))]
            for u in self.body().get("updateRequestModels", []):
                for tc in run["testCases"]:
                    if tc["testCase"]["id"] == u["testCaseReference"]["id"]:
                        tc["result"] = u["result"]
                        tc["conclusion"] = u.get("conclusion", "")
            results = [tc["result"] for tc in run["testCases"]]
            run["result"] = "FAILED" if "FAILED" in results else "PASSED"
            run["status"] = {"id": STATUSES.index("Finished") + 1, "name": "Finished", "type": "ChoiceOptionReference"}
            return self.reply(200, run)
        m = re.fullmatch(r"/testruns/(\d+)", path)
        if m and method == "GET":
            return self.reply(200, items[int(m.group(1))])
        return self.reply(404, {"message": "No such call in the practice server: %s %s" % (method, path)})

    def do_GET(self):
        self.handle_any("GET")

    def do_POST(self):
        self.handle_any("POST")

    def do_PUT(self):
        self.handle_any("PUT")


if __name__ == "__main__":
    load()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    print("Practice server for NETBANK-DEMO on http://localhost:%d/api/v3 (%d items)" % (port, len(items)))
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
