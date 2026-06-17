# GitHub Publishing Checklist

Before publishing this demo:

- [ ] Run `make demo`.
- [ ] Run `make verify`.
- [ ] Run `make replay`.
- [ ] Run `make test`.
- [ ] Run `make package-check`.
- [ ] Confirm no `.env`, credentials, caches, or private data are present.
- [ ] Confirm sample outputs are intentionally included.
- [ ] Confirm generated `artifacts/runs/` and `artifacts/replay/` are not included except under `artifacts/sample_outputs/`.
