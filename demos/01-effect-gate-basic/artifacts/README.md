# Artifacts

`make demo` writes generated run artifacts under:

```text
artifacts/runs/
```

`make verify` adds `verification_report.json` to each run directory.

Generated runs are intentionally excluded from release ZIPs unless copied into `artifacts/sample_outputs/`.
