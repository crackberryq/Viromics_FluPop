# Virologix → FluPop contract, draft v1

Pipeline ID: `flupop`. Version: `0.1.0a1`. Repository: `crackberryq/Viromics_FluPop`.

Virologix must install a versioned checkout and the separate `flupop-snake` environment. It owns sample selection, the run ID, configuration, process launch, cancellation, stdout/stderr capture and saved-run history. FluPop owns validation, cFASTA serialization, report generation, stage logs, benchmarks and provenance. The manager must not import FluPop to execute workflow logic inside `viromics`.

Launch an argv list without a shell:

```
<flupop-python> -m snakemake --snakefile <checkout>/workflow/Snakefile --directory <run-directory> --configfile <run-directory>/config.yaml --cores <allocated-cores> --rerun-incomplete
```

Write absolute input paths and an output_dir underneath the new run directory. Set synthetic_demo explicitly. Use the pipeline exit code for success/failure; do not infer success merely from the presence of an old HTML report. Capture process output. Do not kill unrelated Snakemake or WSL processes.

On success, reports are at `<output_dir>/<sample>/report/viral-cloud.html`; the complete report directory must be kept together for relative download links. Logs and benchmarks are siblings of the report directory. Existing Virologix preview runs remain separate legacy records and should stay readable.

The initial manifest is `pipeline.json`. It declares capabilities and result paths, not a promise that the manager already consumes it. No raw-read analysis capability is advertised.
