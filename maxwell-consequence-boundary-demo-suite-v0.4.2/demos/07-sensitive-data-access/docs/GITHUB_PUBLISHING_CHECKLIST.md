# GitHub Publishing Checklist

Before publishing this package:

- Run `make demo`.
- Run `make verify`.
- Run `make test`.
- Run `make package-check`.
- Confirm no `.env`, `.venv`, `__pycache__`, `.pytest_cache`, generated `artifacts/runs/`, or real data are present.
- Confirm sample outputs are clearly labeled synthetic.
- Confirm the license notice matches the intended public-preview posture.
