# Supplied record semantics

## Input contract

Consensus FASTA: one unique segment identifier per record, uppercase A/C/G/T/N, nonempty sequence. Identifiers use letters, digits, `_ . : -`. Sample is supplied with `--sample`.

The tab-separated table must have these columns in this exact order:

| Column | Meaning |
|---|---|
| segment | Matching consensus record ID |
| id | Unique supplied row ID within a segment |
| abundance | Supplied fraction, 0–1 |
| confidence | Supplied HIGH, MED or LOW label; no calibration implied |
| support | Nonnegative integer supplied support count |
| resolution | Existing draft GLOBAL, LOCAL, FRAGMENT or INFERRED label |
| span | One-based inclusive interval, such as 1-40 |
| edits | Existing draft edit notation, or `.` for no edits within the declared span |

The copied draft parser checks coordinates, edit structure and reference consistency. `GLOBAL` requires the full consensus span. The format is project-specific, not a claimed community standard. The package does not invent an H0 row from the consensus. A no-edit local row only describes its declared span.

Optional evidence JSON follows the example's `viralcloud-evidence-v0.1` schema. Each comparison group declares sample, segment, ID, common span, method (`observed`, `inferred`, `not_supplied`), counting unit, positive denominator, frequency basis, source and member IDs. A row belongs to at most one group. `observed` is an upstream assertion, not something this program proves.

For `count_fraction`, support divided by denominator must match abundance within 0.001; exclusive member support must not exceed the denominator. For `model_estimate`, abundance need not equal a count ratio. Group abundance plus declared unresolved fraction cannot exceed one beyond the same numerical tolerance. Unknown or overlapping biological categories cannot be made exclusive by this validation.

Unresolved abundance is a group-level residual, not an invented sequence. Unassigned abundance is reported separately. Frequencies from independent local groups are never pooled or used to infer full-length or cross-segment linkage. Ungrouped rows remain visible without a pooled total.

## Outputs

- `population.cfasta`: serialized supplied records.
- `consensus.fasta`: ordinary consensus FASTA export.
- `viral-cloud.html`: offline blue report with expandable evidence tables.
- `viral-cloud.json`: machine-readable report with caveats.
- `evidence.json`: supplied evidence, or JSON null if omitted.
- `manifest.json`: software version and SHA-256 input/output checksums.

Keep the output directory together so report download links work. No network requests are required by the report. No real patient or research data is included.

