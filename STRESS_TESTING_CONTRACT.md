# Stress-testing contract v1.0

Recorded 10 November 2026 (Asia/Manila), before scenario execution.

## Purpose and fixed scenarios
Fixed unhedged long USD1,000,000, PHP reporting. Hypothetical shocks: -5%, -3%, -1%, +1%, +3%, +5%, expressed as changes in PHP per USD. Negative shocks strengthen PHP and reduce this long USD holding's PHP value. These illustrative severities have no assigned probability, forecast horizon or bank-limit status. No intraday path, transaction costs, tax, interest, liquidity effect, hedge changes or management action is modelled. These are static revaluations, not new VaR forecasts.

Starting valuation rule: latest numeric observation in the unchanged frozen study ledger, expected source date 2026-09-30 and raw rate 62.485 PHP/USD. Reuse the completed same-field bulletin match in SOURCE_VERIFICATION.md; confirm the ledger endpoint and raw workbook cell at execution. Source dates are bulletin/workbook labels, not verified availability or market-close timestamps.

Historical-selection rule: select the minimum EXACT simple return (end/start - 1) across ALL 1,647 original intervals in the frozen 2020-2026-09 snapshot, including review intervals, without bridging or filling. Break ties by earliest end source date, then original interval order. Select by percentage, not peso loss. Preserve both endpoints, gap, eligibility and row IDs. Reuse its completed endpoint audit; if the selected interval lacks evidence, report that gap before interpreting it as verified. Apply its percentage move to the September2026 starting position, not its historical absolute peso movement. This is an ex-post historical replay, not an out-of-sample prediction, worst conceivable case or a causal news attribution.

## BPI separate supporting case
Use the officially matched 2025 report, consolidated USD net on-balance-sheet position +PHP814 million as of 2025-12-31. Assets PHP418686m minus liabilities PHP417872m. Exposure is already peso equivalent, not USD814m. Apply P&L approximately E0*shock with unchanged exposure and linear FX sensitivity. No September2026 valuation rate is applied to BPI. Historical replay on this dated snapshot is hypothetical, not actual historical BPI performance. Complete economic hedges/nonlinearities are not reconstructed. Original publication date remains unknown; this does not assert availability on the reporting date.

Before the seven BPI scenarios, reconcile the separate disclosed +/-1.78% comparator against approximately +/-PHP14m. Tolerance fixed at PHP0.5m for nearest-million reporting; this is a plausibility reconciliation of rounded disclosure, not proof of accounting equivalence. If provenance, scope, sign, units or comparator fails, withhold BPI scenario values and finish USD1m only.

## Arithmetic, display and outputs
Use exact rational arithmetic from decimal strings: S_shocked=S0*(1+r); USD P&L=Q*(S_shocked-S0)=Q*S0*r; signed loss=-P&L. BPI P&L=E0*r. Positive loss means loss; negative loss means gain. Do not floor signs. Export exact numerators/denominators, display PHP to cents, percentages to four decimals. Historical fractions are not rounded before calculation. Include a zero-shock control outside the seven scenarios. Check symmetry, linear scaling, positive shocked rates, independent revaluation and historical endpoint/row preservation. Match source hashes and leave frozen VaR/database unchanged.

User approved scenario set A. Implementation and interpretation are adviser-assisted; no independent learning mastery is inferred. No reviewed third-party skill is installed or used as an execution dependency.
