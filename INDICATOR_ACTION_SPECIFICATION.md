# Approved investigation indicators and actions

Approved 10 November 2026. Fixed hypothetical unhedged long USD1 million; PHP reporting. Guided historical report, not automatic trading.

VaR: reuse exact signed 99% 250/higher main results. Flag strictly when subsequent signed loss exceeds prior signed VaR. Preserve exact ties and original endpoints. Display P&L, loss, prior VaR and exceedance. Review inputs, gap and surrounding observations; no causal assumption.

Drawdown: running peak starts at first numeric study valuation, uses no future values and never resets yearly. Drawdown=(value-peak)/peak; flag at or below -3%, an illustrative review trigger, not calibrated risk limit. Distinguish first crossing from continuing flag. Keep 2022 within-year chart separate. On tied peaks retain first attainment date.

Data status per indicator: Available / Available with qualification / Unavailable. Missing VaR due to warm-up or excluded review intervals is not zero or no flag. Expected calendar nonpublication is context, not automatically an error. Preserve original dates and gap group on every flag. All calculated results carry unverified economic-date/publication-timing qualifications.

One card per original interval, combining triggers. Fields: trigger, impact, original interval/gap, evidence to check and blank reviewer/date/evidence/findings/follow-up note. Existing source checks may be marked complete; substantive review is not completed until recorded. No flag means only no trigger in evaluated rules; unavailable means not evaluated. No automatic action or numerical escalation levels.

Stress is display-only, separately dated 30Sep2026 baseline; BPI supporting illustration dated31Dec2025. Do not interpret fixed stress references as contemporaneous earlier forecasts or combine with VaR exception counts.

Approved sample: Aug4–5,2025; gap1; rates58.392→57.514; P&L -PHP878000; priorVaR PHP425719.97; loss beyondVaR PHP452280.03. Endpoints source-matched in existing audit, rows17391→17392. Review surrounding observations; no macro cause inferred. Drawdown to be calculated separately below.

## Approved episode layout and rules — 10 November 2026

New-item cards show VaR exceptions and new observed -3% drawdown crossings, combined into one card per original interval. Continuing drawdown is a compact ongoing-episode summary, not a new drawdown card. The complete original-interval table remains supporting detail.

An episode is a consecutive sequence of available numeric-endpoint observations with drawdown <=-3%. A subsequent observed drawdown >-3% ends the threshold episode. Equality remains flagged. The first crossing is first OBSERVED crossing, not reconstructed intraday timing. Calendar gaps remain visible, and days between endpoints are elapsed calendar span, not proven continuous time below threshold. VaR exclusions do not remove available drawdown observations.

Track first-crossing interval/gap, running peak at episode start, current/latest interval/gap, latest drawdown, deepest drawdown so far, count of flagged observations and observed threshold exit. Retain the earliest occurrence on tied deepest drawdowns. Daily/as-of summaries may use only observations up to that date; later exit/trough/recovery dates are never shown as if known earlier. Retrospective summaries must be labelled explicitly.

Recovery to the peak recorded at first crossing is a separate first-observed event (value >= that peak); threshold exit does not establish peak recovery. Multiple threshold episodes can share the same reference peak. Unobserved exits/recoveries remain unknown within the study, not assumed never to occur. Review notes are blank; automatic trigger ending never completes a review. No trading or numerical escalation action.

## Threshold sensitivity display — 10 November 2026

The full guided report displays the saved 2%, 3%, and 4% full-study comparison with alert counts, active-flag observations and review tradeoffs. It is explicitly retrospective; figures through September 2026 must not be treated as known on an earlier selected report date. The existing selected-date episode logic continues to use an illustrative 3% example. The 3% choice is not calibrated, optimal, a BPI Group policy or a bank risk limit. No preferred operational threshold is selected. Selecting one would require a defined review objective, acceptable workload, loss appetite and operational timing evidence. The BPI Group stress illustration does not establish its appetite. Source: reports/drawdown_threshold_assessment_v1/FINDINGS.md.

## Visual report v2 — 11 November 2026

User approved four answer tiles, aligned loss/VaR, position/peak and episode timelines, evidence beside notes and separate supporting tabs. Default plots only numeric endpoints up to the selected source date; Show later observations explicitly enables muted, labelled later context. Chart windows share the same calendar-date axis. No aggregation or sketch series is substituted for saved financial values. Episode starts/reference peaks/exits are clipped to the viewing cutoff; future information remains in explicitly retrospective supporting views. The selected-date 3% episode display is illustrative, not a recommendation. All2/3/4% comparison totals remain equally visible in the full-study tab. Source details and note context remain traceable. User data stays under the existing browser storage key.
