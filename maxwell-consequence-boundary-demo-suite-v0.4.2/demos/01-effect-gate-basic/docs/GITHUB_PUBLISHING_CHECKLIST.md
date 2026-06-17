# GitHub Publishing Checklist

Before publishing this demo:

- Run `make clean`.
- Run `make demo`.
- Run `make verify`.
- Run `make test`.
- Run `make package-check`.
- Confirm no `.env`, `.venv`, `__pycache__`, `.pytest_cache`, credentials, real data, or accidental generated runs are included.
- Confirm the root `LICENSE`, `LICENSE-NOTICE.md`, `SECURITY.md`, and `CLAIMS_AND_LIMITATIONS.md` language matches your intended public-preview boundary.
- Attach the ZIP to a GitHub Release, but keep the source folders visible in the repository.
