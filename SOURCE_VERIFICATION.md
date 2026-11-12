# BSP source reconciliation and initial validation

Verified on 31 October 2026. Read-only research: no workbook values, scripts in the project, or database tables were changed. This report records source matching and structural checks; it does not certify all observations or finalize the financial interpretation of the historical series.

## Important correction to the earlier explanation

The broad weighted-average reference-rate metadata cannot yet be assigned to Column B of this entire cross-rate workbook. The two actual 2020 bulletins distinguish the USD row's PHIL. PESO EQUIVALENT, a separately labelled BSP Reference Rate, and a PDS Closing Rate. Their values differ. The workbook matches the first of these on the samples checked. Preserve that exact identity instead of silently substituting another rate series.

## Direct reconciliation

| Workbook / bulletin date | Workbook Column B | USD-row PHP equivalent | Difference at four decimals | Separate BSP Reference Rate | Separate PDS Closing Rate |
|---|---:|---:|---:|---:|---:|
| 2020-01-02 | 50.802 | 50.8020 | 0.0000 | 50.650 | 50.635 (market date 2019-12-27) |
| 2020-01-03 | 50.646 | 50.6460 | 0.0000 | 50.700 | 50.685 (market date 2020-01-02) |

Workbook locations: peso cross daily!A15350:B15351. Each source PDF was downloaded from a link exposed by BSP's historical archive; its complete page was text-extracted and visually checked.

- [Official January 2 bulletin](https://www.bsp.gov.ph/Lists/RERB/Attachments/719/02Jan2020.pdf)
- [Official January 3 bulletin](https://www.bsp.gov.ph/Lists/RERB/Attachments/720/03Jan2020.pdf)
- [BSP archive with date selector](https://www.bsp.gov.ph/SitePages/Statistics/DailyRERB.aspx)

At four decimal places the checked numeric values match exactly; a trailing zero is a formatting difference. This is a same-provider cross-publication consistency check, not an independent market-price validation.

## Date interpretation supported by this sample

On these two samples, the workbook label matches the bulletin's date. The January 2 bulletin footer refers to Reuters forex closing prices as of NY time January 1, with separate notes/dates for other fields and a January 2 run timestamp of 09:57 AM. The January 3 bulletin footer refers to NY time January 2 and a January 3 run timestamp of 08:44 AM. PDS market dates are separately printed and are not the dates we should automatically assign to the matched USD row.

Do not treat run timestamps as proven public availability times. Do not infer that every currency row uses the same fixing convention merely from a general footer. Do not shift the entire workbook one day based only on general reference-rate metadata. The exact construction of this USD row and continuity across years still need reconciliation with specific documentation or clarification from BSP.

## Structural validation: 2020-01-01 through 2026-09-30

- Calendar rows: 2465; expected calendar dates: 2465.
- Unique dates: 2465; duplicate extra rows: 0; absent calendar dates: 0.
- Positive finite numeric rates: 1648.
- Invalid numeric rates (zero, negative, nonfinite): 0.
- Nonnumeric markers: {'..': 817}.
- Nonnumeric weekend entries: 704; nonnumeric weekday entries: 113.
- Numeric weekend entries: 0.

Weekday missingness is an investigation population, not a count of errors. Holiday explanations require a verified release/trading calendar. Structural validity does not establish price correctness, correct economic dating, or a consistent historical methodology.

Source snapshot: data/raw/dailycrossrates.xlsx
SHA-256: 3cf2fd962d1fbd9c4ecc59f56bb71204aa5a29d5f0ee666faa956835532c6848

## Validation plan before final risk modeling

1. Broaden bulletin matching across years, Monday/holiday boundaries, and recent 2026 dates. Record field identity, exact differences, date mapping, and evidence links for every selected sample. Choose dates by a documented rule, not only after seeing convenient matches.
2. Establish the source method for the historical USD-row PHIL. PESO EQUIVALENT, including any definition/platform changes. General reference-rate metadata alone is insufficient.
3. Classify missingness against verified calendars; investigate unexpected gaps without zero-filling or assuming a holiday.
4. Flag unusually large moves and compare them with original bulletins; do not delete them merely because they are extreme.
5. Before backtesting, define observation dates, economic measurement dates, availability dates, and eligible forecast intervals. Represent unknown metadata explicitly.
6. After future ingestion, reconcile counts, dates, raw markers, and values back to this frozen snapshot; that pipeline reconciliation has not yet been performed.

## Next manageable task

Extend the source-match sample beyond these two adjacent 2020 dates, beginning with a Monday and then a later-year bulletin. Current status: two exact field/date matches; structural study-period checks completed; rate-construction and full date semantics unresolved. No change to learner mastery is implied by mentor-run checks.

## Follow-up verification — 31 October 2026

Current reconciliation now contains four exact same-date workbook/bulletin USD-row matches: January 2/3, 2020, and September 28/30, 2026. This includes a Monday and the latest observation in the supplied workbook.

| Bulletin/workbook date | USD-row rate | Explicit USD-row description | Separate BSP Reference Rate | Separate PDS Closing Rate |
|---|---:|---|---:|---|
| 2026-09-28 | 62.6030 | Weighted average rate in the USD/PHP Market in the last trading day | 62.450 | 62.465, dated 2026-09-25 |
| 2026-09-30 | 62.4850 | Weighted average rate in the USD/PHP Market in the last trading day | 62.550 | 62.565, dated 2026-09-29 |

Both 2026 documents put an asterisk on the USD row that maps to the description above. Their complete pages were text-extracted and visually inspected. This is direct definition evidence for these samples, not merely general metadata. The sampled publication labels match the workbook labels; the underlying last-trading-day basis differs from that label. Preserve the original label and store an economic market date separately only where supported.

- [September 28 official bulletin](https://www.bsp.gov.ph/Lists/RERB/Attachments/2365/28Sep2026.pdf)
- [September 30 official bulletin](https://www.bsp.gov.ph/Lists/RERB/Attachments/2367/30Sep2026.pdf)

The September 30 bulletin separately dates the PDS close and general LSEG source context to September 29. The Monday September 28 bulletin dates these to September 25. These are corroborating context; the PDS close is still a different measure and must not be substituted for the weighted average.

The earlier 2020 PDFs do not print this same USD-specific footnote. That is a documentation difference, not proof of a calculation-method change. Current findings therefore support a weighted-average interpretation for the checked 2026 USD observations while historical methodological continuity remains to be documented.

An official BAP 2020 summary was discoverable in search indexing with a prior-day weighted-average value consistent with the January 3 BSP figure, but direct retrieval returned 404. It is a lead, not an additional fully inspected original-document match, and is excluded from the four-match tally.

Public release availability and revision histories remain distinct from bulletin dates and document run timestamps. Do not claim verified intraday publication time for each historical record. Use a retrospective published-rate study framing until those limits are resolved.

Next task: review DATA_DICTIONARY.md and complete the outstanding historical-definition/calendar/availability evidence. No date shifting, alternate-series substitution, new ingestion or model execution was performed. These checks do not complete business-understanding or data-collection sign-off.

## Cross-year worklist and new match — 1 November 2026
SOURCE_VALIDATION_PLAN.md and the verification workbook record 11 selected dates: four prior checks plus seven annual anchors chosen as the first valid observation on/after July 1. New anchor 2023-07-03 matched 55.368 in workbook row 16628 to original bulletin USD-row PHP equivalent 55.3680. Complete source page text-extracted and visually inspected. Different fields: BSP Reference Rate and PDS Closing Rate both 55.200; PDS date 2023-06-30. No USD-specific weighted-average footnote printed, so value matching does not resolve historical definition continuity. Official PDF: https://www.bsp.gov.ph/Lists/RERB/Attachments/1573/03Jul2023.pdf
Current totals: five exact value matches; six selected annual checks pending. Missing calendar/release/method evidence is not automatically cleared. Original PDF and expanded reconciliation CSV preserved in chat outputs/source-verification/. No source data changed or ingested.

## Source-check update — 2 November 2026
Verified 2021-07-01: workbook row 15896 rate 48.704 matches the original BSP bulletin USD-row PHIL. PESO EQUIVALENT of 48.7040. Separate BSP Reference Rate and PDS Closing Rate both 48.800; PDS market date 2021-06-30. Full original page extracted and visually inspected; no USD-specific weighted-average footnote. Numeric and bulletin-label matching does not establish historical method continuity or exact economic/public-availability dates.
Official PDF: https://www.bsp.gov.ph/Lists/RERB/Attachments/1083/01Jul2021.pdf
Current worklist: six exact value matches, zero mismatches, five pending annual anchors. Next selected check: 2022-07-01. Preserved original PDF and updated reconciliation CSV and verification workbook. No new ingestion, risk model or learner-mastery assessment completed. Updated workbook is a local deliverable; existing Google Sheets copies are not automatically synchronized.

## Batch completion — 2 November 2026 (latest checkpoint)
All five remaining predetermined annual anchors were retrieved from the BSP archive, text-extracted and visually inspected in full. Each value was independently reconciled with the unchanged original workbook (hash retained).

| Source/bulletin date | Workbook PHP/USD | Original bulletin USD-row PHP equivalent | Difference at 4 decimals | Original source |
|---|---:|---:|---:|---|
| 2020-07-01 | 49.790 | 49.7900 | 0.0000 | [BSP bulletin](https://www.bsp.gov.ph/Lists/RERB/Attachments/840/01Jul2020.pdf) |
| 2022-07-01 | 54.970 | 54.9700 | 0.0000 | [BSP bulletin](https://www.bsp.gov.ph/Lists/RERB/Attachments/1330/01Jul2022.pdf) |
| 2024-07-01 | 58.658 | 58.6580 | 0.0000 | [BSP bulletin](https://www.bsp.gov.ph/Lists/RERB/Attachments/1814/01Jul2024.pdf) |
| 2025-07-01 | 56.378 | 56.3780 | 0.0000 | [BSP bulletin](https://www.bsp.gov.ph/Lists/RERB/Attachments/2060/01Jul2025.pdf) |
| 2026-07-01 | 61.290 | 61.2900 | 0.0000 | [BSP bulletin](https://www.bsp.gov.ph/Lists/RERB/Attachments/2304/01Jul2026.pdf) |

Current total: **11/11 selected value comparisons match, zero mismatches, zero pending samples**. All seven annual anchors 2020–2026 are covered. This completes the selected sample-value worklist, not validation of every observation or all source semantics.

All five newly inspected bulletins lack the USD-specific weighted-average footnote, including July 2026. The inspected September 2026 bulletins contain that footnote. This is an observed documentation difference; its timing/cause and any methodological change are unverified. Do not generalize a September footnote to the full period without qualification. Each bulletin also reports separate BSP Reference Rate and PDS Closing Rate values; these were recorded separately and not substituted. The July 2024 PDS date is June 28; other new PDS dates are June 30 of the respective years. These labels provide context, not proof of the USD economic fixing date. Run timestamps are not verified public availability times.

**Next action:** review a bounded source-handling specification: preserve original source dates, exact field and units, retain raw missing markers, do not zero-fill or automatically forward-fill returns, retain unknown economic/release dates, and define eligible return intervals before one-day VaR/backtesting claims. Review readiness for raw ingestion separately from readiness for risk modeling. No ingestion or model run was performed. Do not automatically add more sample dates.

Original PDFs, reconciliation CSV and the updated two-tab local verification workbook are preserved in outputs. Existing Google Sheets copies have not been synchronized. Learner understanding or independent mastery has not been inferred from adviser-run checks.

## Publication-calendar evidence — 2 November 2026 (latest)
PUBLICATION_CALENDAR_REVIEW.md records the official BSP RERB nonpublication rule (weekends/non-working holidays) and working-day 9:30 a.m. schedule. Of 817 '..' markers, 704 are weekends and 106 weekdays match verified proclaimed national non-working dates; treating these as expected gaps applies the published rule retrospectively, not individual proof of historical absence. Seven other weekdays remain unresolved. All 817 have no matching item in the retrieved archive inventory, but three numeric-rate dates also lack an item (2021-09-03, 2022-06-16, 2022-11-04), so an empty archive result cannot certify nonpublication. Archive inventory labels are not extra PDF value comparisons. Eleven inspected value matches remain the tally.
Evidence and per-date review CSVs saved under outputs/publication-calendar. No source values/dates changed, no ingestion or risk run. Retain seven unresolved causes and three archive-control questions visibly; they do not prevent faithful raw capture. The release calendar lists Philippine Peso Cross Rates monthly, but exact dailycrossrates.xlsx refresh/version history is not thereby proven.

## Seven-date investigation — 2 November 2026 (latest)
SEVEN_DATE_INVESTIGATION.md and Seven_Date_Investigation.csv record a completed bounded context review: all seven unusual weekday markers have documented emergency-disruption context. ISDA supports 17 March 2020 USD/PHP market disruption; CTBC explicitly lists FX service unavailable on 1 September 2023. Other cases have date-specific government work and/or settlement suspension evidence. These findings do not certify exact RERB cancellation or prove the marker's causal explanation. Original calendar counts remain 704 weekend / 106 national non-working weekdays / 7 other weekdays; seven now carry investigated_with_qualification status and publication_cause_status unconfirmed.
Control: MC83 applies to 13 November 2020, when the workbook contains 48.291, so government work suspension is not an automatic no-rate rule. MC82 is the correct directive for 12 November. PNB PDF retrieval failed 403; BAP summary retrieval failed 404; neither is reported as fully inspected. Original raw values remain unchanged. Three positive-rate/archive gaps remain a separate question. No messages to institutions, ingestion, model run or learner-mastery assessment occurred.
Next bounded task: frozen raw ingestion and typed staging with these evidence flags. No need to repeat broad searches before raw capture; exact economic-date/method and interval eligibility still limit affected one-day risk claims.
