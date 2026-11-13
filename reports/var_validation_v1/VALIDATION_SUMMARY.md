# Validation summary — retrospective BSP published-observation prototype

Fixed hypothetical unhedged long USD1m, PHP reporting. No operational, market-close daily, regulatory adequacy or model-pass claim.

## Reconciled performance

| Sample | Targets | Exceptions | Rate (%) |
|---|---:|---:|---:|
| main_250_higher_full | 1390 | 22 | 1.5827 |
| main_250_higher_common | 1140 | 15 | 1.3158 |
| main_500_higher_common | 1140 | 18 | 1.5789 |
| main_250_linear_common | 1140 | 17 | 1.4912 |
| included_training_250_shared | 1390 | 22 | 1.5827 |
| full_inclusion_250_higher | 1397 | 22 | 1.5748 |

## Interpretation

The main full sample and common-target samples answer different questions. Compare window/quantile variants only on identical common targets; lower thresholds or fewer exceptions alone do not establish superiority.

Gap-group performance is a central descriptive finding. See gap_group_summary.csv for exact sample definitions and denominators. Differences do not establish significance, causality or equal economic horizons.

The 250/higher inclusion sensitivity isolates training effects on shared targets separately from newly scoreable review/earlier ordinary targets. It does not resolve publication uncertainty or establish results for other variants.

The closest-three random-placement diagnostic was formulated after inspecting results and is exploratory. Its simulated frequency is not the probability of independence, model adequacy or future coverage.

## Reproduction and scope

Exact fields use rational strings. Training memberships use original interval-order keys with a frozen ledger checksum. Source files and a code-only notebook snapshot are included. Checksums cover every bundle file except checksums.json itself.

The exporter checked membership, arithmetic, classifications, roundtrip precision and independently recomputed the main 22 exception VaRs using raw rate differences and third-largest heap selection. These are implementation checks, not verification of historical publication availability.

Fresh-kernel reproduction is recorded separately; saving this bundle alone does not establish a clean rerun. No formal coverage p-values, confidence intervals, completed all-exception bulletin audit or stress tests are claimed here. Other-variant inclusion sensitivity remains unimplemented.

Prespecified: main method, window/quantile variants, gap reporting and inclusion design. Exploratory: observed episode/spacing analysis and random-placement diagnostic.

If a rerun changes any bundle bytes, investigate before publishing a separately versioned correction; do not overwrite the baseline or select a method by its backtest result.
