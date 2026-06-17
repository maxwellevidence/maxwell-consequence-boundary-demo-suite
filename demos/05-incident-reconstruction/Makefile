PYTHON ?= python
MODULE ?= maxwell_incident_reconstruction
PYTHONPATH ?= src
INPUTS ?= examples/demo_inputs
POLICY ?= policies/incident_reconstruction_policy.yml
OUT ?= artifacts/runs
RECON_OUT ?= artifacts/reconstruction
TAMPER_OUT ?= artifacts/tamper_demo
ZIP_OUT ?= ../maxwell-incident-reconstruction-demo-v0.1.0.zip

.PHONY: adversarial demo verify reconstruct tamper-demo test lint clean clean-artifacts package-check package samples tree help

help:
	@echo "Available targets: demo verify reconstruct tamper-demo test lint clean package-check package samples"

demo: clean-runs
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli demo --inputs $(INPUTS) --policy $(POLICY) --out $(OUT)

verify:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli verify --runs $(OUT)

reconstruct:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli reconstruct --runs $(OUT) --out $(RECON_OUT)

tamper-demo: demo
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli tamper-demo --runs $(OUT) --out $(TAMPER_OUT)

test: clean-artifacts
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q

lint:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m compileall -q src tests tools

package-check: clean
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tools/public_package_check.py .

package: clean package-check
	$(PYTHON) tools/create_clean_zip.py . $(ZIP_OUT)

samples:
	rm -rf artifacts/sample_outputs/runs artifacts/sample_outputs/reconstruction artifacts/sample_outputs/tamper_demo
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli demo --inputs $(INPUTS) --policy $(POLICY) --out artifacts/sample_outputs/runs
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli verify --runs artifacts/sample_outputs/runs
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli reconstruct --runs artifacts/sample_outputs/runs --out artifacts/sample_outputs/reconstruction
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli tamper-demo --runs artifacts/sample_outputs/runs --out artifacts/sample_outputs/tamper_demo
	@echo "Sample outputs copied to artifacts/sample_outputs/"

clean-runs:
	rm -rf $(OUT)

clean-artifacts:
	rm -rf $(OUT) $(RECON_OUT) $(TAMPER_OUT)

clean: clean-artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml build dist *.egg-info src/*.egg-info
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('*.egg-info')]"
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" \) -delete

tree:
	find . -maxdepth 4 -type f | sort

adversarial:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q tests/adversarial/test_adversarial_corpus.py
