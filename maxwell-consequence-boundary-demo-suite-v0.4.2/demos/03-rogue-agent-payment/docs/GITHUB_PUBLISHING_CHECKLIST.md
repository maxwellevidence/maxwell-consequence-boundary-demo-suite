# GitHub Publishing Checklist

Before publishing this demo:

- [ ] Run `make clean`.
- [ ] Run `make demo`.
- [ ] Run `make verify`.
- [ ] Run `make test`.
- [ ] Run `make package-check`.
- [ ] Confirm no `artifacts/runs/` directory is committed unless intentionally publishing sample outputs.
- [ ] Confirm no `.env`, credentials, real invoices, real vendor data, or real payment files are present.
- [ ] Confirm `LICENSE`, `LICENSE-NOTICE.md`, `SECURITY.md`, and `CLAIMS_AND_LIMITATIONS.md` are present.
- [ ] Confirm the README states that no real payment occurs.
