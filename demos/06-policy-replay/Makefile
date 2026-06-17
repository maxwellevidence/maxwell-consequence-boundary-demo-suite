PYTHON ?= python
MODULE ?= maxwell_policy_replay
PYTHONPATH ?= src
INPUTS ?= examples/demo_inputs
POLICY_ORIGINAL ?= policies/policy_v1.yml
POLICY_REPLAY ?= policies/policy_v2.yml
OUT ?= artifacts/runs
REPLAY_OUT ?= artifacts/replay
ZIP_OUT ?= ../maxwell-policy-replay-demo-v0.1.0.zip

.PHONY: adversarial help demo verify replay test lint clean-runs clean-artifacts clean package-check package samples tree

help:
	@echo "Available targets: demo verify replay test lint clean package-check package samples"

demo: clean-runs
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli demo --inputs $(INPUTS) --policy $(POLICY_ORIGINAL) --out $(OUT)

verify:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli verify --runs $(OUT)

replay: demo
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli replay --runs $(OUT) --target-policy $(POLICY_REPLAY) --out $(REPLAY_OUT)

test: clean-artifacts
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q

lint:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m compileall -q src tests tools

package-check: clean
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) tools/public_package_check.py .

package: clean package-check
	$(PYTHON) tools/create_clean_zip.py . $(ZIP_OUT)

samples:
	rm -rf artifacts/sample_outputs/runs artifacts/sample_outputs/replay
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli demo --inputs $(INPUTS) --policy $(POLICY_ORIGINAL) --out artifacts/sample_outputs/runs
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli verify --runs artifacts/sample_outputs/runs
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m $(MODULE).cli replay --runs artifacts/sample_outputs/runs --target-policy $(POLICY_REPLAY) --out artifacts/sample_outputs/replay
	@echo "Sample outputs copied to artifacts/sample_outputs/"

clean-runs:
	rm -rf $(OUT)

clean-artifacts:
	rm -rf $(OUT) $(REPLAY_OUT)

clean: clean-artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml build dist *.egg-info src/*.egg-info
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('*.egg-info')]"
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" \) -delete

tree:
	find . -maxdepth 4 -type f | sort

adversarial:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q tests/adversarial/test_adversarial_corpus.py
