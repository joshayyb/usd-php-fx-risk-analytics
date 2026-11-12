# Focused RRL matrix

Prepared 31 October 2026. Initial design-oriented review; not exhaustive, not a completed systematic review, and not evidence of learner mastery. Source IDs correspond to PROJECT_DESIGN.md. Search targeted primary sources: BSP, central-bank research, author research, and Basel guidance, using USD/PHP risk, historical simulation, backtesting, and reporting terms. No claim of a novel literature gap follows from this limited search.

| ID / source type | What was examined | Relevant insight | Design implication and critical limit |
|---|---|---|---|
| S1 — Consolacion (2016), BSP-published empirical study | Article text including data, methodology, USD/PHP results, discussion; printed pp. 1–10 | Philippine market data include USD/PHP and a hypothetical USD exposure. Rolling historical and parametric risk measures are compared. | Local anchor for the risk problem and a rolling baseline. Later data and time-consistent evaluation must be tested independently. Do not copy a maximum-loss comparison as the sole test of quantile calibration. |
| S2 — Cassidy & Gizycki (1997), central-bank research | HTML VaR and backtesting sections | Historical simulation revalues a portfolio under historical moves; portfolio changes can contaminate P&L comparisons. | Use a fixed exposure and consistent hypothetical P&L. Foundational methodology, not current regulatory guidance. |
| S3 — Pritsker (2001), methodological research | Official Federal Reserve abstract only | Basic historical approaches can react inadequately to changing conditional risk. | Challenge the baseline with window sensitivity and stress analysis. Full paper review remains needed before detailed claims about alternative estimators. |
| S4 — Christoffersen (1998), peer-reviewed methodological research | Original-paper abstract and summary, with author bibliographic confirmation | Coverage and independence are distinct dimensions of interval-forecast evaluation. | Examine exception frequency and clustering. Sparse exceptions and small samples constrain diagnostic strength. |
| S5 — BCBS (2018), official guidance | Official publication description of stress-testing principles | Objectives, methodology, documentation, and governance belong in a stress framework. | Predefine scenario purpose and severity, record assumptions, and connect results to review. Not an empirical model-comparison finding. |
| S6 — BCBS (2013), official guidance | Official publication overview | Weak risk aggregation/reporting impairs timely risk decisions. | Preserve source-to-output traceability and clear, useful risk reports. Applying selected principles is not compliance certification. |
| S7 — Philippine exchange-rate metadata / BSP, official source documentation | Definitions, preceding-business-day basis, publication timeliness, BSP source page | Reference-rate availability and economic observation timing are not automatically identical. | Verify exact workbook date conventions before forecast alignment. Do not assume metadata for one output establishes another output's methodology. |
| S8 — Fissler, Ziegel & Gneiting (2015/2016), methodological research | Author-submitted abstract | Joint VaR/ES elicitability has implications for ES backtesting. | Qualify S1's categorical ES-backtesting statement; no automatic expansion into ES modeling. |
| S9 — BCBS MAR33, version-specific official standard | Official internal-model capital framework context | ES belongs to contemporary internal-model capital methodology. | Explain why this educational VaR prototype is not a regulatory capital engine. No claim about specific Philippine or HSBC implementation. |

## Synthesis for this project

The literature supports investigating a transparent exposure with historical scenarios and consistent P&L, while checking changing-risk sensitivity, stress vulnerability, and forecast reliability. It does not establish that a 250-return historical model is optimal for our data or that a modern bank's full risk process can be replicated with one public rate series.

Applied contribution: a reproducible recent-period USD/PHP case study that connects validated source observations, explicit hypothetical exposure, forecast evaluation, and interpretable review reporting. This is an extension in application and implementation, not claimed theoretical novelty.

## First guided reading

Read S1 first: printed pp. 1–2 for purpose and context, p. 5 for data/method, and p. 7 for the USD exposure illustration. One session should focus only on: **what problem did the author study, what data were used, and which parts are relevant to our simpler position?** Defer advanced formulas until foundations are ready.

Reading record fields for subsequent sessions: learner explanation; research question; dataset/period; exposure definition; method; validation; limitations; implication for our design; exact source section. Do not mark an article fully reviewed from its title or search snippet.

## Direct sources

- S1: [BSP — Consolacion (2016)](https://www.bsp.gov.ph/Media_And_Research/Publications/BS2016.pdf#page=5)
- S2: [RBA — VaR](https://www.rba.gov.au/publications/rdp/1997/9708/value-at-risk.html); [RBA — Backtesting](https://www.rba.gov.au/publications/rdp/1997/9708/backtesting.html)
- S3: [Federal Reserve — Pritsker (2001)](https://www.federalreserve.gov/pubs/feds/2001/200127/200127abs.html)
- S4: [Christoffersen original paper](https://users.ssc.wisc.edu/~behansen/718/Christoffersen1998.pdf); [author bibliography](https://christoffersen.com/academic-papers/)
- S5: [BCBS — Stress testing principles](https://www.bis.org/publications/201810-guidelines-stress-testing-principles)
- S6: [BCBS — Risk data aggregation/reporting](https://www.bis.org/publications/201301-guidelines-principles-effective-risk-data-aggregation-and-risk-reporting)
- S7: [Country-provided exchange-rate metadata](https://dsbb.imf.org/sdds/dqaf-base/country/PHL/category/EXR00); [BSP exchange rates](https://www.bsp.gov.ph/SitePages/Statistics/exchangerate.aspx)
- S8: [Fissler, Ziegel & Gneiting](https://arxiv.org/abs/1507.00244)
- S9: [BCBS MAR33](https://www.bis.org/committees/bcbs/basel-framework/standard/mar/33/inforce/2023-01-01/published/2020-03-27)

## 2026-10-31 — Source clarification and consultation scope
SOURCE_VERIFICATION.md supplies two direct historical bulletin comparisons: the workbook matches the same-date USD-row PHIL. PESO EQUIVALENT, which differs from each bulletin's BSP Reference Rate/PDS Closing Rate. S7's general reference-rate metadata is contextual and must not be asserted as the definition of the entire workbook. Exact construction and historical continuity remain unresolved. No new RRL finding or learner reading completion is inferred from the external consultation.
The core objective retains VaR/stress/retrospective evaluation. ES remains optional; the local paper's inclusion of ES does not require copying all its measures. See CONSULTATION_REVIEW.md for decisions and evaluation criteria.
