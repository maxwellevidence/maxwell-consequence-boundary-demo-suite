SHELL := /bin/bash
PYTHON ?= python

DEMO_DIRS := $(sort $(wildcard demos/*))
FLAGSHIP := demos/02-effect-gate-public-preview

.PHONY: help suite-check package-check demo-lint demo-run demo-verify demo-adversarial demo-test demo-core-check scenario-extra-checks adversarial-harness flagship-fuzz flagship-mutation flagship-deep-check decoy-proof launch-check ci-full clean

help:
	@echo "Available targets:"
	@echo "  make suite-check            Validate suite metadata and required release assets"
	@echo "  make package-check          Run every demo public-package checker"
	@echo "  make demo-lint              Run each demo lint/compile check"
	@echo "  make demo-run               Run make demo in all ten demos"
	@echo "  make demo-verify            Run make verify in all ten demos"
	@echo "  make demo-adversarial       Run make adversarial in all ten demos"
	@echo "  make demo-test              Run make test in all ten demos"
	@echo "  make scenario-extra-checks  Run reconstruction/replay extra checks"
	@echo "  make adversarial-harness    Run the suite adversarial harness"
	@echo "  make flagship-fuzz          Run Demo 02 fail-closed fuzz quick set"
	@echo "  make flagship-mutation      Run Demo 02 planted-mutant smoke harness"
	@echo "  make decoy-proof            Prove a known fail-open patch is caught"
	@echo "  make launch-check           Run launch gate checks"
	@echo "  make ci-full                Run the GitHub public CI gate"

suite-check:
	$(PYTHON) tools/suite_spec_check.py .

package-check:
	@set -euo pipefail; \
	for d in $(DEMO_DIRS); do \
	  echo "== package-check: $$d"; \
	  ($(MAKE) -C "$$d" package-check); \
	done

demo-lint:
	@set -euo pipefail; \
	for d in $(DEMO_DIRS); do \
	  echo "== lint: $$d"; \
	  ($(MAKE) -C "$$d" lint); \
	done

demo-run:
	@set -euo pipefail; \
	for d in $(DEMO_DIRS); do \
	  echo "== demo: $$d"; \
	  ($(MAKE) -C "$$d" demo); \
	done

demo-verify:
	@set -euo pipefail; \
	for d in $(DEMO_DIRS); do \
	  echo "== verify: $$d"; \
	  ($(MAKE) -C "$$d" verify); \
	done

demo-adversarial:
	@set -euo pipefail; \
	for d in $(DEMO_DIRS); do \
	  echo "== adversarial: $$d"; \
	  ($(MAKE) -C "$$d" adversarial); \
	done

demo-test:
	@set -euo pipefail; \
	for d in $(DEMO_DIRS); do \
	  echo "== test: $$d"; \
	  ($(MAKE) -C "$$d" test); \
	done

# A public CI gate that proves the visible demo commands run for every demo.
# It intentionally verifies generated effects before tests/package-check clean them.
demo-core-check: demo-lint demo-run demo-verify demo-adversarial demo-test

scenario-extra-checks:
	$(MAKE) -C demos/05-incident-reconstruction demo verify reconstruct tamper-demo
	$(MAKE) -C demos/06-policy-replay demo verify replay

adversarial-harness:
	$(PYTHON) tools/adversarial_harness.py . --json reports/adversarial_harness_report.json

flagship-fuzz:
	$(MAKE) -C $(FLAGSHIP) fuzz-quick

flagship-mutation:
	$(MAKE) -C $(FLAGSHIP) mutation-smoke

flagship-deep-check:
	$(MAKE) -C $(FLAGSHIP) lint demo verify samples adversarial test fuzz-quick mutation-smoke package-check

decoy-proof:
	$(PYTHON) tools/decoy_fail_open_proof.py . --report-dir reports/decoy_fail_open

launch-check: suite-check package-check adversarial-harness flagship-fuzz flagship-mutation decoy-proof

ci-full: suite-check demo-core-check scenario-extra-checks adversarial-harness flagship-deep-check package-check decoy-proof

clean:
	@set -euo pipefail; \
	for d in $(DEMO_DIRS); do \
	  echo "== clean: $$d"; \
	  ($(MAKE) -C "$$d" clean); \
	done
	rm -rf .pytest_cache .mypy_cache .ruff_cache .hypothesis htmlcov .coverage coverage.xml build dist
