PYTHON ?= python
MODULE ?= maxwell_prompt_injection_boundary
PYTHONPATH ?= src
INPUTS ?= examples/demo_inputs
POLICY ?= policies/prompt_injection_boundary_policy.yml
OUT ?= artifacts/runs
ZIP_OUT ?= ../maxwell-prompt-injection-boundary-demo-v0.1.0.zip

.PHONY: adversarial help demo verify test lint clean-runs clean-artifacts clean package-check package samples tree

help:
	@echo "Available targets: demo verify test lint clean package-check package samples"

demo: clean-runs
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli demo --inputs $(INPUTS) --policy $(POLICY) --out $(OUT)

verify:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli verify --runs $(OUT)

test: clean-artifacts
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q

lint:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m compileall -q src tests tools

package-check: clean
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tools/public_package_check.py .

package: clean package-check
	$(PYTHON) tools/create_clean_zip.py . $(ZIP_OUT)

samples:
	rm -rf artifacts/sample_outputs/runs
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli demo --inputs $(INPUTS) --policy $(POLICY) --out artifacts/sample_outputs/runs
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli verify --runs artifacts/sample_outputs/runs
	@echo "Sample outputs copied to artifacts/sample_outputs/runs"

clean-runs:
	rm -rf $(OUT)

clean-artifacts:
	rm -rf $(OUT)

clean: clean-artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml build dist *.egg-info src/*.egg-info
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('*.egg-info')]"
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" \) -delete

tree:
	find . -maxdepth 4 -type f | sort

adversarial:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q tests/adversarial/test_adversarial_corpus.py
