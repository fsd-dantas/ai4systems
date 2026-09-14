PYTHON ?= python

.PHONY: install test cli-smoke check

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

cli-smoke:
	aisg --version
	aisg --lang en diagnose --case rf_interference
	aisg --lang en route --compare
	aisg --lang en pipeline --case congestion
	aisg --lang en blackboard --scenario dual-outage

check: test cli-smoke
