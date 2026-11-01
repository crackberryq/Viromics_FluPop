# FluPop

**Human Link GenoMix · Viromics_FluPop · 0.1.0a1**

FluPop is an independent Snakemake pipeline. **Virologix is its manager**, responsible for installation, configuration, launching jobs and showing their results. **Viral Cloud** is the report name.

This initial executable workflow validates supplied consensus and reviewed haplotype records, writes cFASTA, and generates the Viral Cloud report. It does not reconstruct haplotypes from raw reads, perform variant calling or validate biological linkage. Included data are synthetic software fixtures.

## Quick start

From a checkout of this repository in Ubuntu/WSL:

```bash
conda env create -f environment.yml
conda activate flupop-snake
snakemake --snakefile workflow/Snakefile --profile profiles/default
```

Open `results/DEMO/report/viral-cloud.html`. The manager environment remains `viromics`; the workflow uses `flupop-snake`. Snakemake is pinned to 9.27.0. Conda setup itself is not yet tested on Windows; the workflow is tested on Linux/Python 3.12.

Alternatively install Snakemake 9.27.0 into an isolated Python environment and run the same command. Stage scripts load bundled FluPop code directly and have no Virologix dependency.

## Stages and outputs

| Stage | Outputs |
|---|---|
| Validate supplied records | `validated.json`, input hashes and software provenance |
| Create cFASTA | `population.cfasta` |
| Viral Cloud report | HTML, JSON, cFASTA and consensus FASTA exports, evidence and checksum manifest |

Each sample also has `logs/` and stage `benchmarks/` containing elapsed time, user/system CPU time and process peak RSS on Linux/WSL. Output folders are keyed by sample; the manager must select a unique run root to preserve separate runs.

```bash
# Inspect planned jobs
snakemake -s workflow/Snakefile --cores 1 --dry-run
# Resume; completed, unchanged stages are skipped
snakemake -s workflow/Snakefile --cores 1 --rerun-incomplete
# Custom run
snakemake -s workflow/Snakefile --cores 2 --configfile /absolute/path/run.yaml
```

Configure samples in `config/config.yaml`. Custom config must set `synthetic_demo: false` for actual supplied records. Evidence JSON is optional; omit its key or use an empty string. Paths are relative to the execution directory; manager-generated configs should use absolute paths. Sample IDs may contain letters, digits, dots, underscores and hyphens, beginning with a letter or digit.

The TSV columns must be `segment`, `id`, `abundance`, `confidence`, `support`, `resolution`, `span`, `edits`, in that order. See the example files and [input semantics](docs/records.md). Confidence labels and evidence methods are supplied assertions. Independent local groups are never pooled, and unresolved abundance is not a sequence claim.

## Manager boundary

See [the integration contract](docs/manager-contract.md). Virologix 0.1.0a8 installs this repository into a separate versioned environment and launches Snakemake externally. Use Pipelines → Install FluPop, then Run synthetic demo. The manager no longer bundles cFASTA or Viral Cloud processing code; older preview reports remain accessible.

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Tests exercise record validation and an actual Snakemake run, unchanged rerun, missing-output recovery, optional evidence, paths with spaces and invalid inputs. CI uploads the synthetic output bundle for inspection. This is software validation, not biological validation.
