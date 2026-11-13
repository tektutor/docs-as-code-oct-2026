#!/usr/bin/env bash
# Runs the same commands as the Jenkinsfile, in the same order, without Jenkins.
# Use it to check the repository before you set up Jenkins.
#   ci/run_pipeline_locally.sh practice     (default) start the practice server
#   ci/run_pipeline_locally.sh none         no Codebeamer at all
set -e
MODE=${1:-practice}
export BUILD_NUMBER=${BUILD_NUMBER:-local}
cd "$(dirname "$0")/.."

echo "== Set up Python"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt

if [ "$MODE" = practice ]; then
  echo "== Start practice server"
  python3 ci/practice_server.py 8090 > build-practice-server.log 2>&1 &
  PID=$!; trap 'kill $PID' EXIT; sleep 2
  export CB_URL=http://localhost:8090/api/v3 CB_TOKEN=nb-practice-token
  echo "== Pull status from Codebeamer"
  python3 ci/pull_status.py data/netbank.json
else
  export CB_URL=
fi

echo "== Acceptance tests"
mkdir -p build/test-results
python3 -m pytest --junitxml=build/test-results/junit.xml || echo "Some tests failed: the build would be UNSTABLE"

echo "== Report results to Codebeamer"
python3 ci/report_test_results.py build/test-results/junit.xml "NetBank build $BUILD_NUMBER"

echo "== Diagrams and PDF documents"
python3 docs/build_docs.py
ls -l build/docs
