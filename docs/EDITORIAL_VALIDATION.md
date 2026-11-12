# Editorial validation

The portable replay reproduced the exact historical VaR on 1,390 scored intervals, including 22 exceptions, and reproduced all 14 stress scenario P&Ls. It starts from the bundled interval extract. The source workbook, private research environment and proprietary source PDFs are outside that replay.

| Check | Result and scope |
|---|---|
| Research evidence | Headline loss, prior VaR, gap-group counts, alternative model denominators, stress cases and drawdown scope were checked against the saved study. The random-placement result links directly to the saved aggregate diagnostic. See [research integrity](RESEARCH_INTEGRITY_AUDIT.md). |
| Companion dashboard | All 54 offline presentation checks passed in an isolated copy, including selected-date cutoffs across 1,647 original intervals. These checks exercise the dashboard logic. |
| Article layout | Chromium rendered the article at 1,440 × 960 and 390 × 844 pixels. The reading column measured 710 and 335 pixels respectively. All four figures loaded in both views, with no page-wide horizontal overflow. This check used the local assets inlined into the browser for rendering. |
| Packaging | SHA-256 hashes identify the included files. The package verifier checks local HTML links and image targets and scans for specified private artifacts. An additional check covers the article stylesheet, internal anchors, archive membership and byte equality after extraction. |
| Research preservation | Compared existing research artifacts against the prior local ZIP, including the dashboard, processed ledger, notebook reading copies and exact model and stress archives. The editorial changes concern the article, its presentation and handoff documentation. |

The legacy BIS stress-principles URL was unavailable during reference review. The article uses the verified official publication record. [Reference audit](REFERENCE_AUDIT.md)

The editorial checks did not exercise a physical phone, a screen reader, another browser engine, or a print preview of this edition. No new reader study or raw-source acquisition was performed. The available evidence supports local owner review. Public release requires the decisions in [publication readiness](PUBLICATION_READINESS.md).
