# Research integrity audit

The approved modelling, stress and indicator contracts govern their respective calculations and display assumptions. Frozen results and original notebook findings establish measured outcomes. The design and focused RRL establish intent and rationale. The README is a guide. Its date does not override an approved definition.

| Objective / question | Method and checkable evidence | Answer and interpretive boundary |
|---|---|---|
| Establish reliable inputs for every question | SOURCE_VERIFICATION.md, DATA_PIPELINE.md and data/processed/bsp_usd_php_interval_ledger_v1.csv | 1,648 numeric endpoints form 1,647 original intervals. Seven review intervals retain unresolved source-gap evidence. Timing and methodology continuity remain qualified. |
| RQ1, market behaviour | EDA notebook sections on rolling volatility and annual comparison | The 2022 20-change windows ranged from 0.160868 to 0.487180 percentage points of dispersion. 2023 had slightly higher full-year volatility. The sample does not identify a market cause. |
| RQ2, position impact | Fixed quantity times rate change, saved main target and endpoint audit | 4–5 August 2025 produced a hypothetical ₱878,000 loss. Valuation P&L excludes trades and costs. |
| RQ3, prior VaR and coverage | Main 250/higher target archive and exact exceedances | 22/1,390 overall, 12/1,069 single-day, 10/321 multi-day. Calendar groups do not establish equal economic horizons. |
| RQ5, timing and robustness | Common-target CSVs, exception spacing, frozen diagnostic summary | Main/common uses 15/1,140. Window and quantile alternatives yielded 18 and 17. Full inclusion yielded 22/1,397. The nine-interval span diagnostic was exploratory. |
| RQ4, stress and supporting BPI question | Stress contract, seven dated shocks per case, exact scenario_results.csv, BPI provenance | September 2026 baseline gives ₱3,124,250 loss at −5%. The separate December 2025 BPI net is +₱814m in peso equivalent. Linear shock P&L cannot establish total earnings or risk appetite. |
| RQ6, investigation workflow | Indicator specification, saved dashboard, existing tests and owner walkthrough | Selected-date charts, original-interval evidence and distinct notes implement review. Wider operational usefulness and independent novice comprehension remain open. |

## Reconciled differences

- Retained the workbook's checked PHIL. PESO EQUIVALENT field and original source sequence. General reference-rate descriptions alone cannot define this entire series.
- The preliminary design discusses confidence-level sensitivity. The implemented comparisons hold 99% constant and vary window, quantile method and review-interval inclusion.
- The 2022 EDA drawdown uses an annual starting point. The dashboard uses the full-study running peak. A threshold exit differs from recovery.
- ₱878,000 describes the original hypothetical interval. ₱939,543.60 describes a replay on a different starting value.
- Source publication year for BPI's annual report is unestablished. 31 December 2025 is its exposure reporting date.
- Sample quantiles, historical comparisons and software checks are presented within their verified scopes. The local candidate excludes the complete raw-source environment.

Editorial review used previously saved outputs. No new inference test, causal investigation, financial estimator or risk limit was introduced.
