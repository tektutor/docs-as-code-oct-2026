# Short commands for the labs. Each target does the same thing as one Jenkins stage.
PY ?= python3

.PHONY: setup test report docs all server clean
setup:            ## create .venv and install the Python packages
	$(PY) -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
test:             ## run the 28 acceptance tests and write JUnit XML
	mkdir -p build/test-results
	-$(PY) -m pytest --junitxml=build/test-results/junit.xml
report: test      ## send results to Codebeamer (needs CB_URL); always writes summary.json
	$(PY) ci/report_test_results.py build/test-results/junit.xml "NetBank local run"
docs: report      ## draw the PlantUML diagrams and build the four PDF documents
	$(PY) docs/build_docs.py
all: docs
server:           ## start the practice Codebeamer server on port 8090
	$(PY) ci/practice_server.py 8090
clean:
	rm -rf build
