"""Build the reviewed frozen BSP staging snapshot; never modify raw records."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path

import duckdb

SNAPSHOT_SHA256 = "3cf2fd962d1fbd9c4ecc59f56bb71204aa5a29d5f0ee666faa956835532c6848"
START, END = dt.date(2020, 1, 1), dt.date(2026, 9, 30)
STAGING_VERSION = "1.0"
TABLE = "staging.bsp_usd_php"
COLUMNS = [
    "snapshot_sha256", "source_sheet", "source_row", "source_date",
    "usd_php_raw", "usd_php_rate", "rate_status", "is_weekend",
    "calendar_status", "calendar_evidence_source", "calendar_note",
    "event_context", "disruption_evidence_source", "disruption_note",
    "review_status", "publication_cause_status", "evidence_sha256",
    "staging_version", "staged_at",
]
DDL = """
CREATE TABLE IF NOT EXISTS staging.bsp_usd_php (
    snapshot_sha256 VARCHAR NOT NULL,
    source_sheet VARCHAR NOT NULL,
    source_row INTEGER NOT NULL,
    source_date DATE NOT NULL,
    usd_php_raw VARCHAR,
    usd_php_rate DOUBLE,
    rate_status VARCHAR NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    calendar_status VARCHAR NOT NULL,
    calendar_evidence_source VARCHAR,
    calendar_note VARCHAR,
    event_context VARCHAR,
    disruption_evidence_source VARCHAR,
    disruption_note VARCHAR,
    review_status VARCHAR NOT NULL,
    publication_cause_status VARCHAR NOT NULL,
    evidence_sha256 VARCHAR NOT NULL,
    staging_version VARCHAR NOT NULL,
    staged_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (snapshot_sha256, source_sheet, source_row),
    UNIQUE (snapshot_sha256, source_date),
    CHECK (rate_status IN ('valid','source_missing','blank','invalid_input','invalid_numeric')),
    CHECK ((rate_status = 'valid' AND usd_php_rate IS NOT NULL
            AND isfinite(usd_php_rate) AND usd_php_rate > 0)
        OR (rate_status <> 'valid' AND usd_php_rate IS NULL))
)
"""


# Part 1: interpret the raw cell, without changing the original value.
def parse_rate(raw_value: str | None, cell_type: str) -> tuple[float | None, str]:
    if raw_value is None or raw_value == "":
        return None, "blank"
    if raw_value == ".." and cell_type == "s":
        return None, "source_missing"
    if cell_type != "n":  # Do not silently coerce text, booleans or formulas.
        return None, "invalid_input"
    try:
        number = float(raw_value)
    except (ValueError, TypeError, OverflowError):
        return None, "invalid_input"
    if not math.isfinite(number) or number <= 0:
        return None, "invalid_numeric"
    return number, "valid"


# Part 2: attach the evidence already reviewed; do not infer a holiday from weekday alone.
def read_evidence(path: Path) -> tuple[dict, str]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(newline="", encoding="utf-8") as stream:
        entries = list(csv.DictReader(stream))
    by_date = {}
    for entry in entries:
        date = dt.date.fromisoformat(entry["date"])
        if date in by_date:
            raise ValueError(f"Duplicate calendar evidence date: {date}")
        weekend = date.weekday() >= 5
        if entry["raw_marker"] != ".." or entry["actual_bulletin_absence_verified"] != "False":
            raise ValueError("Evidence changed from the reviewed missing-marker qualification.")
        if (entry["calendar_classification"] == "weekend") != weekend:
            raise ValueError(f"Calendar classification conflicts with weekday: {date}")
        if entry["calendar_classification"] == "verified_national_nonworking_day" and not entry["calendar_evidence_source"]:
            raise ValueError(f"Missing holiday evidence link: {date}")
        if entry["calendar_classification"] == "unresolved":
            if entry["review_status"] != "investigated_with_qualification" or entry["publication_cause_status"] != "unconfirmed" or not entry["event_context"] or not entry["disruption_evidence_source"]:
                raise ValueError(f"Missing qualified disruption evidence: {date}")
        by_date[date] = entry
    if Counter(e["calendar_classification"] for e in entries) != {
        "weekend": 704, "verified_national_nonworking_day": 106, "unresolved": 7
    }:
        raise ValueError("Evidence does not match the reviewed 817-date classification.")
    return by_date, digest


def make_record(raw: tuple, evidence: dict, evidence_hash: str) -> tuple:
    snapshot, sheet, row, date, raw_value, cell_type = raw
    numeric_rate, status = parse_rate(raw_value, cell_type)
    weekend = date.weekday() >= 5
    if date in evidence:
        entry = evidence[date]
        if status != "source_missing" or row != int(entry["source_row"]):
            raise ValueError(f"Calendar evidence does not match raw source row/rate: {date}")
        calendar_status = entry["calendar_classification"]
        calendar_source = entry["calendar_evidence_source"] or entry["publication_policy_source"]
        calendar_note = entry["publication_assessment"] + "; " + entry["assessment_basis"]
        event = entry["event_context"] or None
        disruption_source = "\n".join(filter(None, [entry["disruption_evidence_source"], entry["additional_disruption_source"]])) or None
        disruption_note = entry["disruption_finding_limit"] or None
        review = entry["review_status"] or "calendar_reviewed_with_qualification"
        publication_status = entry["publication_cause_status"] or "not_individually_confirmed"
    else:
        calendar_status = "weekend" if weekend else "weekday_not_reviewed"
        calendar_source, event, disruption_source, disruption_note = None, None, None, None
        calendar_note = "No missing-date calendar assessment applied; this is not a trading-calendar certification."
        review, publication_status = "not_assessed", "not_assessed"
    return (snapshot, sheet, row, date, raw_value, numeric_rate, status, weekend,
            calendar_status, calendar_source, calendar_note, event, disruption_source,
            disruption_note, review, publication_status, evidence_hash, STAGING_VERSION)


# Part 3: check the candidate records before saving, then verify the saved table.
def build(database: Path, evidence_file: Path, sample_file: Path) -> dict:
    database, evidence_file, sample_file = (p.expanduser().resolve() for p in (database, evidence_file, sample_file))
    if not database.is_file():
        raise ValueError("Project database does not exist; run the raw loader first.")
    evidence, evidence_hash = read_evidence(evidence_file)
    with sample_file.open(newline="", encoding="utf-8") as stream:
        samples = list(csv.DictReader(stream))
    if len(samples) != 11 or len({s["workbook_date"] for s in samples}) != 11:
        raise ValueError("Expected the 11 distinct verified sample controls.")
    with duckdb.connect(str(database)) as con:
        con.execute("BEGIN TRANSACTION")
        try:
            raw_before = con.execute("SELECT * FROM raw.bsp_usd_php ORDER BY snapshot_sha256,source_sheet,source_row").fetchall()
            raw_rows = con.execute("""SELECT snapshot_sha256,source_sheet,source_row,source_date,
                                          usd_php_raw,usd_php_cell_type
                                     FROM raw.bsp_usd_php WHERE snapshot_sha256 = ? ORDER BY source_row""",
                                   [SNAPSHOT_SHA256]).fetchall()
            dates = [r[3] for r in raw_rows]
            expected_dates = {START + dt.timedelta(days=i) for i in range((END - START).days + 1)}
            if len(dates) != 2465 or len(set(dates)) != 2465 or set(dates) != expected_dates:
                raise ValueError("Raw date scope/count differs from the reconciled snapshot.")
            if {r[3] for r in raw_rows if r[4] == ".."} != set(evidence):
                raise ValueError("Calendar evidence dates differ from raw missing-marker dates.")
            records = [make_record(row, evidence, evidence_hash) for row in raw_rows]
            status_counts = Counter(row[6] for row in records)
            if status_counts != {"valid": 1648, "source_missing": 817}:
                raise ValueError(f"Unexpected source status counts: {dict(status_counts)}; inspect raw before promotion.")
            by_date = {row[3].isoformat(): row for row in records}
            for sample in samples:
                row = by_date[sample["workbook_date"]]
                if row[2] != int(sample["excel_row"]) or row[6] != "valid" or round(row[5] - float(sample["usd_row_php_equivalent"]), 4) != 0:
                    raise ValueError(f"Staging sample mismatch: {sample['workbook_date']}")
            con.execute("CREATE SCHEMA IF NOT EXISTS staging")
            con.execute(DDL)
            if [r[0] for r in con.execute(f"DESCRIBE {TABLE}").fetchall()] != COLUMNS:
                raise ValueError("Existing staging schema differs; no table was replaced.")
            # Rebuild this derived snapshot only. Other snapshots, if any, are preserved.
            con.execute(f"DELETE FROM {TABLE} WHERE snapshot_sha256 = ?", [SNAPSHOT_SHA256])
            staged_at = dt.datetime.now(dt.timezone.utc)
            con.executemany(f"INSERT INTO {TABLE} ({','.join(COLUMNS)}) VALUES ({','.join('?' for _ in COLUMNS)})",
                            [record + (staged_at,) for record in records])
            loaded = con.execute(f"SELECT {','.join(COLUMNS[:-1])} FROM {TABLE} WHERE snapshot_sha256 = ? ORDER BY source_row",
                                 [SNAPSHOT_SHA256]).fetchall()
            if loaded != records:
                raise ValueError("Saved staging records differ from the checked candidate records.")
            raw_after = con.execute("SELECT * FROM raw.bsp_usd_php ORDER BY snapshot_sha256,source_sheet,source_row").fetchall()
            if raw_before != raw_after:
                raise ValueError("Raw records changed unexpectedly; staging transaction rolled back.")
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
    return {"table": TABLE, "database": str(database), "snapshot_sha256": SNAPSHOT_SHA256,
            "rows": len(records), "rate_status_counts": dict(status_counts),
            "null_rates": sum(row[5] is None for row in records),
            "missing_calendar_counts": dict(Counter(e["calendar_classification"] for e in evidence.values())),
            "qualified_disruption_rows": sum(row[14] == "investigated_with_qualification" for row in records),
            "verified_sample_matches": len(samples), "raw_unchanged": True,
            "exact_staging_round_trip": True, "evidence_file": str(evidence_file),
            "evidence_sha256": evidence_hash, "staging_version": STAGING_VERSION,
            "verification_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "duckdb_version": duckdb.__version__,
            "limitations": "Calendar evidence qualifies missing observations, not a complete trading calendar. No date shifts, filling, external rates, market-date reconstruction, one-day eligibility, P&L or risk metrics."}


def main() -> None:
    project = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=project / "traded_risk.duckdb")
    parser.add_argument("--evidence", type=Path, default=project / "data/reference/bsp_missing_calendar_20261102.csv")
    parser.add_argument("--samples", type=Path, default=project / "data/reference/bsp_verified_samples.csv")
    parser.add_argument("--report", type=Path, default=project / "reports/bsp_staging.json")
    args = parser.parse_args()
    result = build(args.database, args.evidence, args.samples)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.report.with_suffix(args.report.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, args.report)
    print(json.dumps({k: result[k] for k in ["table", "rows", "rate_status_counts", "null_rates", "verified_sample_matches", "raw_unchanged"]}, indent=2))


if __name__ == "__main__":
    main()
