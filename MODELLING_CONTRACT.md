# Historical Simulation VaR: Final Methodology Contract

## 1. Purpose and scope

This educational prototype studies historical changes between frozen BSP USD/PHP published observations from January 2020 through September 2026.

The exposure is a fixed, hypothetical, unhedged long USD1,000,000 position valued in PHP. The USD quantity remains fixed; its PHP value changes with the exchange rate.

This is a retrospective published-observation study. It is not verified market-close daily VaR, operational VaR, or a regulatory validation exercise. Explained weekend and holiday gaps do not establish equal economic horizons.

## 2. Data and interval integrity

The reported dataset contains:

- 1,648 numeric observations.
- 1,647 original observation-to-observation intervals.
- 1,640 calendar-candidate intervals.
- Seven review intervals crossing unresolved missing weekdays.

The seven intervals have been investigated, but their exact publication causes remain unconfirmed.

Retain each original interval’s ID, starting observation, ending observation, and return. Do not fill missing values, substitute vendor data, recompute returns across exclusions, or extend a skipped target’s forecast to a later observation.

Define `gap` as the number of calendar days between the recorded endpoint dates. It is not a verified economic holding period.

## 3. Returns, exposure, and losses

Let \(S_a\) and \(S_b\) denote an interval’s starting and ending rates, measured in PHP per USD.

The original simple return is:

\[
r=\frac{S_b}{S_a}-1.
\]

For target interval \(t\), historical return \(r_j\) produces scenario loss:

\[
L_{t,j}=-1{,}000{,}000\,S_{a,t}\,r_j.
\]

The target’s realised loss is:

\[
L_t=-1{,}000{,}000(S_{b,t}-S_{a,t}).
\]

Positive values mean losses; negative values mean gains. VaR is calculated from scenario losses, sorted from smallest to largest.

## 4. Training eligibility and timing

For each target, use the most recent required number of eligible returns whose ending observations are at or before the target’s starting observation.

A training return may end at the target’s starting observation. The target return itself and all later returns must be excluded.

Use full windows only. If insufficient eligible history exists, do not produce a forecast for that target. A window contains 250 or 500 eligible returns, not a fixed number of calendar days.

**Timing assumption and limitation:**

This study assumes, without verifying historical publication timestamps, that the target’s starting observation and all training observations were available before its ending observation became available. Historical underlying market dates are not consistently verified. Recorded sequence is therefore used as a retrospective ordering convention, not proof that the forecasts could have been produced operationally.

If evidence establishes that required inputs became available only with or after the target observation, or that later revisions introduced unavailable information, the affected exercise must be labelled an ex-post calculation or rebuilt using a verified availability sequence.

## 5. Prespecified model variants

| Role | Eligible training returns | Quantile level | Method |
|---|---:|---:|---|
| Main | 250 | 99% | `higher` |
| Window sensitivity | 500 | 99% | `higher` |
| Quantile sensitivity | 250 | 99% | `linear` |

Pool eligible returns across gap lengths. Gap groups are reporting groups, not separately fitted models.

Do not select or replace the main method retrospectively because another variant or subgroup performs better.

For sorted scenario losses \(x_{(1)},\ldots,x_{(n)}\), let \(h=(n-1)\times0.99\).

- `higher` selects \(x_{(\lceil h\rceil+1)}\).
- `linear` interpolates between the surrounding order statistics using the fractional part of \(h\).
- Empirical inverse-CDF selects \(x_{(\lceil0.99n\rceil)}\). It is a distinct convention and is not an additional fitted variant.

The required outputs are:

| Variant | Quantile calculation |
|---|---|
| 250 + `higher` | \(x_{(248)}\) |
| 500 + `higher` | \(x_{(496)}\) |
| 250 + `linear` | \(0.49x_{(247)}+0.51x_{(248)}\) |

## 6. Signed VaR and exception classification

Preserve signed VaR without flooring it at zero. Use the same unrounded signed value in backtesting.

A negative VaR represents a gain at the estimated loss quantile, not a guaranteed gain.

Define \(D_t=L_t-VaR_t\):

- Exception: \(D_t>0\).
- Mathematical tie: \(D_t=0\); a non-exception.
- Other non-exception: \(D_t<0\).

Keep ties in the total evaluated-target denominator and report their count separately.

PHP0.01 is a computational review threshold only. Flag comparisons with \(|D_t|\leq ₱0.01\), then adjudicate them using exact rational arithmetic from the original decimal rate strings and specified quantile weights. A genuine small positive difference remains an exception.

A computational near-tie is not automatically a mathematical tie. Round values only for presentation.

## 7. Exclusion and inclusion sensitivity

Exclude the seven review intervals from both main training and main targets. Freeze their identities independently of backtest outcomes. Exclusion does not assert that their numerical returns are erroneous.

Run a separately labelled inclusion sensitivity using all 1,647 original intervals for both training and targets, subject to full-window availability. Keep all other rules unchanged.

Use three clearly labelled comparisons:

1. **Model variants:** within each eligibility regime, compare the three variants on the intersection of target IDs evaluable by all three.
2. **Exclusion versus inclusion:** for each fixed variant, compare regimes on identical target IDs evaluable under both. This isolates the effect of changing training eligibility.
3. **Full available results:** report each run’s complete eligible target set separately, identifying added targets, dates, counts, and gap composition. Added targets can include earlier ordinary intervals as well as review intervals.

Always disclose the denominator and sample definition used in a result.

## 8. Backtest reporting

Report overall results and separate results for `gap = 1` and `gap > 1`.

Include:

- Evaluated target counts and dates.
- Exception counts and rates.
- Realised losses and excess over VaR for exceptions.
- Mathematical ties and computational near-tie flags.
- Exception timing and clustering.
- Gap composition and uncertainty.

Preserve original interval ordering when describing clusters. Mark excluded or unevaluated intervals; do not silently treat observations separated by skipped intervals as consecutive evaluated outcomes.

Formal coverage or independence tests may supplement descriptive reporting. Disclose their assumptions, sparse-tail limitations, and any independence or constant-probability assumptions used for uncertainty estimates. Passing a test does not establish model adequacy.

Do not infer dependence merely from averaging, or treat the nominal 99% level as a guarantee of a 1% future exception rate.

## 9. What is fixed and what remains investigatory

The data snapshot, interval rules, timing assumption, model variants, quantile definitions, signed-VaR treatment, exception rule, and comparison design are fixed before examining backtest performance.

EDA and later investigation may document extreme observations, repeated returns, dependence, subgroup weaknesses, missing-date causes, and publication limitations. These findings do not automatically change the main method.

If investigation reveals a material data or implementation error, document the correction and version the affected results. Any methodological redesign must be identified separately rather than silently replacing the prespecified study.

## Ready-to-code checklist

### Data audit and EDA

- [ ] Save the frozen source, original decimal values, calendar evidence, and seven review IDs.
- [ ] Reconcile all reported observation and interval counts.
- [ ] Check chronological order, duplicate dates, positive finite rates, and original endpoint integrity.
- [ ] Summarise gap lengths and counts over time.
- [ ] Inspect rates and returns over time, return distributions, zero/repeated returns, and extreme changes with their source rows.
- [ ] Summarise rolling-window calendar spans and historical gap composition.
- [ ] Record unresolved timing and publication questions without treating them as verified.

### Implementation checks

- [ ] Hand-check signs and units for an exchange-rate rise, fall, and unchanged rate.
- [ ] Verify quantile ranks and interpolation using small known examples and the specified 250/500 ranks.
- [ ] Test negative VaR, exact ties, repeated losses, and tiny genuine exceedances.
- [ ] Verify full window sizes and permitted training endpoints for every target.
- [ ] Confirm that changing future observations cannot change earlier forecasts.
- [ ] Confirm exclusions never bridge endpoints or move a forecast to another target.
- [ ] Verify common-target comparisons use identical IDs and denominators.
- [ ] Confirm subgroup counts and exceptions reconcile with overall totals.

### Reproducible reporting

- [ ] Save each target’s endpoints, gap, training interval IDs, variant, eligibility regime, VaR, realised loss, exception status, and tie flags.
- [ ] Save software versions and quantile settings.
- [ ] Label full-sample and common-target results distinctly.
- [ ] Include the timing assumption and mixed-duration limitation beside the interpretation of results.

---

Version: 1.0 — baseline recorded 2026-11-03 (Asia/Manila).
Status: agreed methodology, saved before model implementation/backtest performance review.
Implementation and its acceptance checks remain pending; unchecked boxes below are not claims of completion.
The main text above is the user-supplied final methodology contract, preserved verbatim.
The implementation register following it supplies reproducible identifiers and clarifications.
This contract supersedes conflicting earlier provisional modelling settings, not historical source evidence.

## Implementation register — v1.0

### Frozen inputs and identity

- Study period: 2020-01-01 through 2026-09-30; retain original source-date labels.
- Source: `dailycrossrates.xlsx`, sheet `peso cross daily`, USD column B.
- Archived workbook: `data/raw/bsp/dailycrossrates_3cf2fd962d1fbd9c4ecc59f56bb71204aa5a29d5f0ee666faa956835532c6848.xlsx`.
- Workbook SHA-256: `3cf2fd962d1fbd9c4ecc59f56bb71204aa5a29d5f0ee666faa956835532c6848`.
- Database input: `staging.bsp_usd_php`; raw decimal text and lineage: `raw.bsp_usd_php`.
- Calendar evidence: `data/reference/bsp_missing_calendar_20261102.csv`, with its hash carried by staging/report lineage.
- User-supplied contract attachment SHA-256: `fe81423920ad16979205058be68f56c498b6051286104c09e5c389438415a834`.
- Eligible numeric observation order is ascending original `source_date`; fail on duplicate/invalid endpoints.
- Stable original interval ID: `<snapshot_sha256>:peso cross daily:<start_source_row>-><end_source_row>`.
  The table below abbreviates IDs as `start_source_row->end_source_row`; all use the snapshot and sheet above.

### Frozen seven review intervals

| Row-pair ID | Starting source date | Ending source date | Unresolved intervening source date |
|---|---|---|---|
| `15358->15362` | 2020-01-10 | 2020-01-14 | 2020-01-13 |
| `15424->15426` | 2020-03-16 | 2020-03-18 | 2020-03-17 |
| `15664->15666` | 2020-11-11 | 2020-11-13 | 2020-11-12 |
| `16314->16316` | 2022-08-23 | 2022-08-25 | 2022-08-24 |
| `16345->16349` | 2022-09-23 | 2022-09-27 | 2022-09-26 |
| `16646->16650` | 2023-07-21 | 2023-07-25 | 2023-07-24 |
| `16687->16691` | 2023-08-31 | 2023-09-04 | 2023-09-01 |

These IDs are frozen independently of loss magnitude. Investigated disruption context is not confirmed publication cause. Correct material data errors transparently; new evidence or methodological redesign requires a documented version rather than silent baseline replacement.

### Sensitivity and reporting interpretation

- Main regime: 1,640 calendar candidates, excluding the seven above from both training and targets.
- Inclusion regime: all 1,647 original intervals; score only targets with sufficient prior history.
- The common-main-target comparison of these two regimes is the training-only sensitivity; no duplicate fitted run is required just to display that comparison.
- Show review targets as their own labelled diagnostic subset, outside the main headline denominator. Review IDs without warm-up history are marked `insufficient_history`, not given invented forecasts. Earlier ordinary targets newly available under inclusion must also be identified.
- In the inclusion report, gap groups are exhaustive; the separate review-target subset overlaps gap > 1 and must not be added to those groups again.
- Main headline remains the 250/higher exclusion run. Its standalone history can be shown separately from the common-target intersection used for fair three-variant comparisons.
- `realised loss` in the supplied text means calculated subsequent hypothetical PHP valuation loss from the frozen series, not an executed trade, actual bank loss, or verified market-close P&L.
- Preserve signed VaR. Even a gain can exceed a negative loss quantile; apply the same strict comparison and explain such cases.
- Quantile ranks and interpolation weights are the explicit mathematical definitions above. Use exact 99/100 for audit arithmetic; binary floating-point representation must not decide mathematical ties. Preserve raw decimal inputs; do not use rounded notebook displays.
- Resolve comparisons flagged within PHP0.01 using exact rational arithmetic. This is a review threshold, never an exception allowance. Test that this trigger safely covers numerical error at the observed input scale before trusting unflagged comparisons; use exact arithmetic more broadly if needed.
- Save actual software versions at implementation; observed NumPy environment during contract preparation: 2.5.4. No risk requirements file or model has been implemented by this document save.
- Formal coverage/independence tests are optional supplements to descriptive reporting, not a required pass/fail gate.

### Evidence and remaining work

On 2026-11-03, a read-only contract-preparation check reconfirmed 2,465 unique staging dates, 1,648 numeric observations, 1,647 original intervals, 1,640 calendar candidates and the seven exact endpoint pairs above. This is a data-ledger check, not VaR validation.

Guided notebook outputs reported by the user establish provisional first targets of 2021-01-19 -> 2021-01-20 for 250 candidates (1,390 targets), and 2022-01-20 -> 2022-01-21 for 500 (1,140 targets). The implementation must independently reconcile these, save window membership, and distinguish full from common-target results.

Model code, quantile/sign/boundary/chronology tests, dependence diagnostics, repeated-value checks, all-window calendar composition, numerical near-tie audits, VaR results and backtesting remain pending unless separately evidenced. Existing EDA figures do not establish operational availability or method superiority.

### Authorship and review

The user selected the 2022 exploratory focus, pooled calendar-candidate training with separate gap reporting, 250/higher main model, 500/higher and 250/linear sensitivities, signed VaR, and the exclusion/sensitivity structure. The user supplied the final methodology text. The adviser explained mechanics, reviewed consultation feedback, checked the ledger and prepared this implementation register. Adviser assistance and guided code execution do not establish independent implementation mastery. Do not infer the user's unexpressed reasons.

### Immediate next step

Review this saved contract with the learner, then build the original-interval ledger and eligible rolling-window selection in a separate risk-modelling notebook, one step at a time. Preserve the existing EDA notebook. Do not run a complete unseen model/backtest in place of the guided implementation.
