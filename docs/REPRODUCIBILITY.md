# Reproducibility scopes

## Portable numerical replay — executable here

From the repository root run `python3 scripts/replay_saved_study.py`. The standard-library script uses the bundled original-interval extract and exact result CSVs. For each main target it selects250 earlier candidate changes, scales their percentage returns by the starting hypothetical USD1m PHP value, computes99% higher VaR and compares the subsequent exact signed loss. It checks all1,390 targets/22 exceptions and14 stress P&Ls. It also checks the original historical selection. No source file is modified.

This verifies numerical reproduction from the attributed analytical inputs. It does not establish the truth, publication timing or licensing of raw observations, rerun all exploratory sensitivities, or reauthenticate the excluded BPI PDF.

## Original research workflow — inspection copies

The notebooks and scripts in research_source preserve the learning/research workflow, with output cells removed and local root paths normalized. They are not promised to Run All in this reduced folder. Full-workspace execution requires the original database, exact frozen workbook and source/audit artifacts, memberships/manifests, approved-input hashes and working BPI PDF/provenance. The ingestion loader deliberately rejects different snapshots. Obtain source files from the cited providers and verify their SHA-256; a newer download is not automatically equivalent.

Original BSP snapshot SHA-256: `3cf2fd962d1fbd9c4ecc59f56bb71204aa5a29d5f0ee666faa956835532c6848`.
Original matched BPI PDF SHA-256: `eef18463a2b4d28a7c8d873d1c40f9911cfb043af605db3d6cf03d3c37d19aa9`.

The source study used Python3.14.10, DuckDB and the versions in ORIGINAL_ENVIRONMENT.json. Clean notebook source does not carry the old output-cell hashes. The full original evidence remains in the private/local workspace; it was not silently rewritten to fit this public candidate.

## Dashboard

Open the generated index.html within its directory tree. Charts stop at the selected endpoint by default; later observations require a labelled toggle. Notes use browser-local storage and are not bundled or transferred when sharing this folder. Use synthetic notes in a fresh profile when testing. Evidence CSV/Markdown targets may open or download depending on browser settings.

`node scripts/check_guided_report_presentation.cjs` exercises mocked DOM/storage handlers, not actual browser dialogs or layout. The owner-reported native tests are separately bounded; second-browser and actual denied-storage behavior remain open.
