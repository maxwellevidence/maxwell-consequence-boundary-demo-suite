PYTHON ?= python
PYTHONPATH ?= src
ZIP_OUT ?= ../maxwell-effect-gate-public-preview-v0.3.0.zip

.PHONY: adversarial demo test verify samples lint fuzz-quick mutation-smoke clean clean-artifacts package-check package tree help

help:
	@echo "Available targets:"
	@echo "  make demo           Run all shape-named demo cases"
	@echo "  make verify         Verify generated artifacts"
	@echo "  make samples        Refresh reviewed sample outputs"
	@echo "  make adversarial    Run adversarial corpus tests"
	@echo "  make test           Run tests"
	@echo "  make lint           Run ruff checks"
	@echo "  make fuzz-quick     Run dependency-light fail-closed input-space fuzz tests"
	@echo "  make mutation-smoke Run bounded planted-mutant credibility harness"
	@echo "  make package-check  Check release hygiene"
	@echo "  make package        Create a clean ZIP one directory above this folder"
	@echo "  make clean          Remove generated runs and caches"

demo:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m maxwell_effect_gate.run_demo

adversarial:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q tests/adversarial/test_adversarial_corpus.py

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q

verify:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m maxwell_effect_gate.verify_artifacts

samples:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m maxwell_effect_gate.export_sample_artifacts

lint:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m ruff check src tests

fuzz-quick:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q tests/fuzz/test_gate_fail_closed_harness.py tests/fuzz/test_fail_closed_input_space.py

mutation-smoke:
	PYTHONUNBUFFERED=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) tools/gate_mutation_smoke.py .

package-check: clean
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tools/public_package_check.py .

package: clean package-check
	$(PYTHON) tools/create_clean_zip.py . $(ZIP_OUT)

clean-artifacts:
	find artifacts -maxdepth 1 -type d -name "*_run" -prune -exec rm -rf {} + 2>/dev/null || true

clean: clean-artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache .hypothesis htmlcov .coverage coverage.xml build dist *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" \) -delete

tree:
	find . -maxdepth 4 -type f | sort
