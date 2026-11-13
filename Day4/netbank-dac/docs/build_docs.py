"""Build the NetBank PDF documents from the files in this repository.

    python3 docs/build_docs.py            all four documents
    python3 docs/build_docs.py srs        only one of: srs design test trace

Inputs
    data/netbank.json                  requirements, epics, HLD, stories, LLD, tests
    diagrams/*.puml                    PlantUML sources (drawn to PNG here)
    build/test-results/summary.json    test results (made by ci/report_test_results.py)
Outputs
    build/docs/NetBank-SRS.pdf
    build/docs/NetBank-Design-Description.pdf
    build/docs/NetBank-Test-Report.pdf
    build/docs/NetBank-Traceability-Matrix.pdf
"""
import datetime
import glob
import json
import os
import subprocess
import sys

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(ROOT, "build", "docs")
PNG = os.path.join(ROOT, "build", "diagrams")

DOCUMENTS = {
    "srs": ("srs.html", "NetBank-SRS.pdf", "System Requirements Specification"),
    "design": ("design.html", "NetBank-Design-Description.pdf", "Software Design Description"),
    "test": ("test-report.html", "NetBank-Test-Report.pdf", "Acceptance Test Report"),
    "trace": ("trace.html", "NetBank-Traceability-Matrix.pdf", "Traceability Matrix"),
}


def draw_diagrams():
    """Draw every .puml file that is newer than its PNG."""
    os.makedirs(PNG, exist_ok=True)
    todo = []
    for src in sorted(glob.glob(os.path.join(ROOT, "diagrams", "*.puml"))):
        png = os.path.join(PNG, os.path.basename(src)[:-5] + ".png")
        if not os.path.exists(png) or os.path.getmtime(png) < os.path.getmtime(src):
            todo.append(src)
    if todo:
        subprocess.run(["plantuml", "-config", os.path.join(DOCS, "plantuml.cfg"),
                        "-tpng", "-failfast2", "-o", PNG] + todo, check=True)
    print("Diagrams: %d drawn, %d up to date" % (len(todo), len(glob.glob(PNG + "/*.png")) - len(todo)))


def load_results():
    path = os.path.join(ROOT, "build", "test-results", "summary.json")
    return json.load(open(path)) if os.path.exists(path) else {}


def context():
    data = json.load(open(os.path.join(ROOT, "data", "netbank.json")))
    results = load_results()
    req = {r["key"]: r for r in data["requirements"]}
    for r in data["requirements"]:
        r["stories"], r["tests"] = [], []
    for s in data["stories"]:
        for k in s["requirements"]:
            req[k]["stories"].append(s)
        for sc in s["scenarios"]:
            sc["result"] = results.get(sc["key"], {}).get("result", "NOT RUN")
            sc["message"] = results.get(sc["key"], {}).get("message", "")
            sc["story"] = s["key"]
            for k in s["requirements"]:
                req[k]["tests"].append(sc)
    for r in data["requirements"]:
        res = [t["result"] for t in r["tests"]]
        r["verdict"] = ("NO TEST" if not res else "FAILED" if "FAILED" in res
                        else "PASSED" if all(x == "PASSED" for x in res) else "PARTLY RUN")
    tests = [sc for s in data["stories"] for sc in s["scenarios"]]
    count = {k: sum(t["result"] == k for t in tests) for k in ("PASSED", "FAILED", "BLOCKED", "NOT RUN")}
    return {
        "d": data, "tests": tests, "count": count,
        "epics": {e["key"]: e for e in data["epics"]},
        "png": lambda name: "file://" + os.path.join(PNG, name + ".png"),
        "has_png": lambda name: os.path.exists(os.path.join(PNG, name + ".png")),
        "build": os.environ.get("BUILD_NUMBER", "local"),
        "commit": (os.environ.get("GIT_COMMIT") or "working copy")[:12],
        "today": datetime.date.today().isoformat(),
        "cb_url": os.environ.get("CB_URL") or "offline snapshot",
    }


def main(which):
    draw_diagrams()
    os.makedirs(OUT, exist_ok=True)
    env = Environment(loader=FileSystemLoader(os.path.join(DOCS, "templates")), autoescape=True)
    ctx = context()
    for key in which:
        template, pdf, title = DOCUMENTS[key]
        html = env.get_template(template).render(title=title, **ctx)
        HTML(string=html, base_url=DOCS + "/templates/").write_pdf(os.path.join(OUT, pdf))
        print("Wrote build/docs/" + pdf)


if __name__ == "__main__":
    args = sys.argv[1:] or list(DOCUMENTS)
    bad = [a for a in args if a not in DOCUMENTS]
    if bad:
        sys.exit("Unknown document %s. Choose from: %s" % (bad, " ".join(DOCUMENTS)))
    main(args)
