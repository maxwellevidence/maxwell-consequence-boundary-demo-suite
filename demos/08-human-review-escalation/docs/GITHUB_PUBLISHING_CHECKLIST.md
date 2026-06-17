# GitHub Publishing Checklist

Before publishing this demo:

- Run `make demo`.
- Run `make verify`.
- Run `make test`.
- Run `make package-check`.
- Confirm no `artifacts/runs/` directory is checked in.
- Confirm no `.env`, virtual environment, cache directory, credentials, or real data are present.
- Confirm README and claims documents match the released version.
- Create the ZIP with `make package`.
