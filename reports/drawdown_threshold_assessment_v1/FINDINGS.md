# Drawdown threshold comparison

Assessment date: 10 November 2026. Frozen source coverage: 2 January 2020–30 September 2026, fixed long USD1 million, PHP valuation. This exploratory assessment reuses saved observations; it does not validate a bank risk limit.

## Review workload

| Drawdown threshold | New alerts | Flagged observations / 1,647 | Share flagged | Distinct peak-to-recovery periods | Median episode length (observations) |
|---|---:|---:|---:|---:|---:|
| 2% | 20 | 891 | 54.10% | 7 | 6.5 |
| 3% | 15 | 733 | 44.51% | 4 | 6 |
| 4% | 12 | 591 | 35.88% | 3 | 10 |

Each new alert is a first observed crossing or re-entry after a threshold exit. Continuing flagged observations remain compact ongoing summaries. Higher thresholds flag a subset of observations but do not mathematically guarantee fewer separate episodes; the counts above are this sample's results. Distinct peak-to-recovery periods are not proven statistically independent.

The 3% rule remains active for 733 observations, including one episode lasting 337 observations. A persistent warning alone is therefore not a precise forecast of an imminent loss. The episode layout helps control repeated cards but cannot establish threshold usefulness.

## What happened after the crossing?

The following explicitly retrospective outcomes inspect the next 20 available observations after each new alert. All windows are complete and span 28–35 calendar days, depending on the threshold/window. Five-observation sensitivity is also saved in forward_summary.csv. Neither horizon was calibrated to a risk officer's review process.

| Threshold | Alerts followed by any further decline within 20 observations | Value lower at the 20th observation | Median worst additional valuation loss from crossing |
|---|---:|---:|---:|
| 2% | 17 / 20 | 8 / 20 | PHP394,500 |
| 3% | 12 / 15 | 8 / 15 | PHP596,000 |
| 4% | 11 / 12 | 8 / 12 | PHP819,000 |

“Any further decline” means at least one later observed value below the crossing value. It can occur even if the position subsequently recovers. “Lower at the 20th observation” compares only the crossing value with the window ending value. Worst additional loss is crossing value minus the lowest value in the window, with zero included at the crossing. It is a valuation decline, not necessarily a realised sale loss, and excludes the drawdown already accumulated before the alert.

These are different sets of dates. A larger post-crossing loss or higher historical proportion cannot be used to declare a threshold better. The windows can overlap; repeated alerts share drawdowns; no comparison against ordinary non-alert dates or untouched future sample was performed. The proportions are not forecast probabilities. No independence test, causal effect, avoided loss or effectiveness of a risk officer's action is established.

## Same downturn, different warning dates

For the decline from the October 2022 peak, the first observed crossings were:

| Threshold | First observed crossing |
|---|---|
| 2% | 14 November 2022 |
| 3% | 24 November 2022 |
| 4% | 1 December 2022 |

The 2% line was reached earlier because it required a smaller decline. The 4% line required a larger decline before review. Later knowledge of the trough must not appear on an earlier report date. These dates do not demonstrate that an intervention would have prevented subsequent losses.

## Recommendation and decision still needed

The historical data support the workload/timing tradeoff, but do not establish 3% as superior or optimal. Do not describe it as a standard, calibrated risk limit, statistically validated warning, or bank policy. Do not select a threshold by maximizing later losses in this already examined sample.

Choose the review objective first: an earlier review with more alerts, or a later review with fewer alerts. If earlier review is the agreed prototype priority, 2% is a reasonable candidate among these three because it flags smaller drawdowns; its 20 alerts and persistent flagged periods must be acceptable. If 3% is retained as a workload compromise, that is an explicit design preference informed by descriptive evidence, not a proof of optimality. An actual bank would also need loss appetite, materiality, workflow capacity and operational timing evidence.

No replacement threshold is approved by this assessment. The existing report is preserved and episode acceptance is paused pending that decision. The report should continue to expose drawdown amounts even without a numerical trigger; no flag does not establish no risk.

## Outputs and checks

- DRAWDOWN_THRESHOLD_ASSESSMENT.md records rules and the fact that preliminary data had already been examined.
- threshold_summary.csv: workload, episode lengths and distinct underwater periods.
- episodes.csv: original crossing endpoints, gap groups and observed exits for all 47 threshold episodes.
- forward_outcomes.csv: exact 5/20-observation outcomes for all 94 windows, including calendar spans.
- forward_summary.csv: both exploratory horizons and completeness counts.
- threshold_workload.png: workload comparison.
- checks.json: exact peak/drawdown reconciliation, existing 3% result reproduction, source continuity and protected-file checks.

All 27 frozen VaR files verified unchanged. Existing report and indicator specification were preserved during the calculation. Source dates and mixed calendar gaps remain qualified; no new source audit was required because the saved inputs were unchanged.
