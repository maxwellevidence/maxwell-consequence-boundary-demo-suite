# Artifacts

Generated demo runs are written to:

```text
artifacts/runs/
```

These run artifacts are intentionally ignored by Git and removed by `make clean`.

Sample outputs created for public review are stored under:

```text
artifacts/sample_outputs/runs/
```

The demo does not store or return real sensitive data. A data-access effect record means the
synthetic policy permitted the access effect; it is not a data payload.
