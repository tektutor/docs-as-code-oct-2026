# netbank-dac: NetBank Docs-as-Code repository

Companion repository for the NETBANK-DEMO labs (Day 4 and Day 5).

| Folder | What it holds |
|---|---|
| `src/netbank` | Python model of the NetBank rules (limits, OTP, lockout, statements) |
| `tests/acceptance` | 28 pytest tests, one per Codebeamer test case (AT-1.1 to AT-20.1) |
| `data/netbank.json` | Requirements, epics, HLD, stories, LLD and test scenarios |
| `diagrams` | 70 PlantUML files: 6 HLD, 64 LLD (class, sequence, activity, state) |
| `docs` | `build_docs.py`, Jinja2 templates, CSS, IBM Plex fonts, PlantUML settings |
| `ci` | Codebeamer client, practice server, result reporter, status puller, Lab 5.7 scripts, Jenkins image |
| `import` | Excel files for Labs 4.6 and 4.11 (17 user stories, 26 test cases) |
| `Jenkinsfile` | The CI/CD pipeline |
| `app.py` | NetBank demo web application for manual tests (standard library only) |

## Quick start (no Jenkins, no Codebeamer)

    sudo apt install python3-venv plantuml graphviz fonts-ibm-plex
    ci/run_pipeline_locally.sh none

The PDFs appear in `build/docs`. One test (AT-9.1) fails on purpose: Lab 5.9 fixes it.

## Test by hand in the browser

    python3 app.py            # then open http://localhost:8000

Log in with customer ID `10023456` and password `Secret#2026`. OTPs and alerts
appear in the "Demo phone" box; the "Demo clock" buttons move time forward to
test OTP expiry, session timeout, lockout, and the beneficiary cooling period.
The app uses the same code in `src/netbank` as the tests, so the AT-9.1 bug
shows as a mini statement with 9 rows.

## With the practice Codebeamer server

    ci/run_pipeline_locally.sh practice

The practice server copies a small part of the Codebeamer REST API v3 on
http://localhost:8090/api/v3 (user `trainee`, password `netbank`, or token
`nb-practice-token`). It keeps everything in memory.

## With a real Codebeamer server

    export CB_URL=https://your-server/cb/api/v3
    export CB_USER=your.name CB_PASSWORD=...      # or CB_TOKEN=...
    python3 ci/cb_client.py                       # lists your projects

Your account needs the "Rest / Remote API - Access" permission. The free
trial at trial.codebeamer.com does not give it, so use the practice server there.

## Jenkins

    cd ci/jenkins && docker compose up -d --build     # Jenkins on http://localhost:8080

Create a Pipeline job that reads `Jenkinsfile` from this repository. See Lab 5.9 of the lab manual.
