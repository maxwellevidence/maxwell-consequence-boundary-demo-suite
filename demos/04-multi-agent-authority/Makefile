PYTHON ?= python
MODULE ?= maxwell_multi_agent_authority
PYTHONPATH ?= src
INPUTS ?= examples/demo_inputs
POLICY ?= policies/multi_agent_authority_policy.yml
OUT ?= artifacts/runs
ZIP_OUT ?= ../maxwell-multi-agent-authority-demo-v0.1.0.zip

.PHONY: adversarial demo verify test lint clean clean-artifacts package-check package samples tree help

help:
	@echo "Available targets:"
	@echo "  make demo           Run all example cases"
	@echo "  make verify         Verify generated run artifacts"
	@echo "  make adversarial    Run adversarial corpus tests"
	@echo "  make test           Run tests"
	@echo "  make clean          Remove generated runs and caches"
	@echo "  make package-check  Check release hygiene"
	@echo "  make package        Create a clean ZIP one directory above this folder"
	@echo "  make samples        Refresh committed sample outputs"

demo:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli demo --inputs $(INPUTS) --policy $(POLICY) --out $(OUT)

verify:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli verify --runs $(OUT)

adversarial:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q tests/adversarial/test_adversarial_corpus.py

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q

lint:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m compileall -q src tests tools

package-check: clean
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tools/public_package_check.py .

package: clean package-check
	$(PYTHON) tools/create_clean_zip.py . $(ZIP_OUT)

samples: demo verify
	rm -rf artifacts/sample_outputs/runs
	mkdir -p artifacts/sample_outputs
	cp -R artifacts/runs artifacts/sample_outputs/runs
	@echo "Sample outputs copied to artifacts/sample_outputs/runs"

clean-artifacts:
	rm -rf artifacts/runs

clean: clean-artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml build dist *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" \) -delete

tree:
	find . -maxdepth 4 -type f | sort
