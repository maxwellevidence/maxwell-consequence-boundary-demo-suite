# GitHub Publishing Checklist

Before publishing this demo:

- Run `make lint`.
- Run `make demo`.
- Run `make verify`.
- Run `make test`.
- Run `make package-check`.
- Confirm no `.env`, `.venv`, cache folders, credentials, private keys, or accidental generated run artifacts are included.
- Confirm sample outputs are intentionally under `artifacts/sample_outputs/`.
- Confirm `LICENSE`, `LICENSE-NOTICE.md`, `SECURITY.md`, and `CLAIMS_AND_LIMITATIONS.md` are present.
