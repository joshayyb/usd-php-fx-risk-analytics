# Stress rerun safeguards — 11 November 2026

The original stress-testing methodology and scenario set remain unchanged. These are execution controls, not a new financial model. The original notebook is archived in backups/stress_safeguards_20261111; reports/stress_testing_v1 remains byte-preserved. Its original checksum manifest references the old notebook, which is now resolved through that archived copy when reviewing the original execution.

## Prescribed inputs and evidence

The approved-input manifest pins the ledger, exact workbook path/hash, existing source documents and archived endpoint evidence, contract, database and frozen VaR manifest. Ledger/contract/database hashes match the retained verified v1 records; audit/source-file hashes bind the reused evidence to this execution. The module pins the approved-input manifest hash. Hashes establish identity, not truth of a source by themselves.

Working BPI metadata is copied without alteration into data/reference/bpi/bpi_provenance_approved.json. The original provenance record remains in the preserved v1 bundle. Missing/contradictory working BPI metadata or PDF withholds BPI calculations but does not block USD-only completion. Approved entity, reporting date, units, assets/liabilities, positive signed net and comparator fields are checked explicitly. Original publication date remains unknown.

Exactly USD1,000,000 and -5/-3/-1/+1/+3/+5% are enforced. Exact historical selection includes all original intervals with the existing tie rule. Literal known answers, exported zero-shock controls and explicit ending USD valuations supplement same-input arithmetic checks. Chart labels are generated from validated records.

## New run publication

Each run writes to reports/stress_runs/.incomplete-<unique-id>. It validates exact values and rechecks all protected inputs before creating SUCCESS.json. A checksum manifest authenticates outputs. Only after validation is the directory atomically renamed to its unique published name. Failure leaves a clearly incomplete directory with FAILURE.json, never an old successful checks.json beside partially overwritten results. Existing runs and v1 outputs are never overwritten. This is application-level immutability, not a filesystem security boundary against deliberate external edits; verify_run detects subsequent byte changes.

## Acceptance and scope

Controlled tests must cover prescribed inputs, literal known answers, zero output, label consistency, historical ties, BPI fallback and staged-export failures. A fresh notebook kernel must complete the normal run; a separate isolated fixture must publish USD-only results when BPI eligibility fails. No production input is mutated during failure tests. Existing financial results must reconcile exactly.

A successful run supports arithmetic, provenance binding and reproducibility under the tested conditions. It does not certify bank risk adequacy, actual BPI losses, historical publication timing or an operational limit. No third-party reviewed skill is installed or executed.
