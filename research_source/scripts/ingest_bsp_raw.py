"""Load the verified frozen BSP study window without filling or replacing rates.

Requires the project's existing duckdb and openpyxl packages. This deliberately
accepts only the verified snapshot; a later source refresh needs a reviewed loader.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import shutil

import duckdb
import openpyxl

SNAPSHOT_SHA256 = "3cf2fd962d1fbd9c4ecc59f56bb71204aa5a29d5f0ee666faa956835532c6848"
SHEET = "peso cross daily"
FIRST_DATA_ROW, LAST_DATA_ROW = 9, 17813  # Verified snapshot data region; footer/notes are outside it.
START, END = dt.date(2020, 1, 1), dt.date(2026, 9, 30)
TABLE = "raw.bsp_usd_php"
COLUMNS = [
    "snapshot_sha256", "source_file", "snapshot_file", "source_sheet",
    "source_row", "source_date", "source_date_raw", "source_date_cell_type",
    "usd_php_raw", "usd_php_cell_type", "usd_php_number_format", "ingested_at",
]
DDL = """
CREATE TABLE IF NOT EXISTS raw.bsp_usd_php (
    snapshot_sha256 VARCHAR NOT NULL,
    source_file VARCHAR NOT NULL,
    snapshot_file VARCHAR NOT NULL,
    source_sheet VARCHAR NOT NULL,
    source_row INTEGER NOT NULL,
    source_date DATE NOT NULL,
    source_date_raw VARCHAR NOT NULL,
    source_date_cell_type VARCHAR NOT NULL,
    usd_php_raw VARCHAR,
    usd_php_cell_type VARCHAR NOT NULL,
    usd_php_number_format VARCHAR NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (snapshot_sha256, source_sheet, source_row)
)
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_source(path: Path, snapshot_name: str) -> tuple[list[tuple], dict]:
    if sha256(path) != SNAPSHOT_SHA256:
        raise ValueError("Source hash differs from the verified frozen snapshot; no load performed.")
    book = openpyxl.load_workbook(path, read_only=True, data_only=False)
    try:
        sheet = book[SHEET]
        headers = list(sheet.iter_rows(min_row=5, max_row=6, max_col=2, values_only=True))
        if headers[0] != ("Period", "US") or headers[1][1] != "dollar":
            raise ValueError("Unexpected source headers; no load performed.")
        records, dates, positive, markers, weekend_markers = [], [], 0, 0, 0
        for row_number, cells in enumerate(sheet.iter_rows(min_row=FIRST_DATA_ROW, max_row=LAST_DATA_ROW, max_col=2), FIRST_DATA_ROW):
            date_cell, rate_cell = cells
            value = date_cell.value
            # This fixed, hash-verified workbook uses real Excel date cells.
            if not isinstance(value, (dt.datetime, dt.date)):
                raise ValueError(f"Unexpected date at A{row_number}; inspect source before loading.")
            if isinstance(value, dt.datetime) and value.time() != dt.time():
                raise ValueError(f"Unexpected time component at A{row_number}.")
            date = value.date() if isinstance(value, dt.datetime) else value
            if not START <= date <= END:
                continue  # Explicit study scope; the complete workbook remains archived.
            rate = rate_cell.value
            if isinstance(rate, (int, float)) and not isinstance(rate, bool) and math.isfinite(rate) and rate > 0:
                positive += 1
            elif rate == "..":
                markers += 1
                weekend_markers += date.weekday() >= 5
            else:
                raise ValueError(f"Unexpected rate/type at B{row_number}; preserve source and investigate.")
            dates.append(date)
            records.append((
                SNAPSHOT_SHA256, "dailycrossrates.xlsx", snapshot_name, SHEET,
                row_number, date, value.isoformat(), date_cell.data_type,
                str(rate) if rate is not None else None,
                rate_cell.data_type, rate_cell.number_format,
            ))
        expected_dates = {START + dt.timedelta(days=i) for i in range((END - START).days + 1)}
        if len(dates) != len(set(dates)) or set(dates) != expected_dates:
            raise ValueError("Duplicate or missing study-window dates; no load performed.")
        if (len(records), positive, markers, weekend_markers) != (2465, 1648, 817, 704):
            raise ValueError("Source controls differ from the verified study window; no load performed.")
        return records, {"rows": len(records), "positive_numeric_rates": positive,
                         "source_missing_markers": markers, "weekend_markers": weekend_markers,
                         "weekday_markers": markers - weekend_markers}
    finally:
        book.close()


def ingest(source: Path, database: Path, snapshot_dir: Path, samples: Path) -> dict:
    source, database, snapshot_dir, samples = (p.expanduser().resolve() for p in (source, database, snapshot_dir, samples))
    snapshot_name = f"dailycrossrates_{SNAPSHOT_SHA256}.xlsx"
    records, controls = read_source(source, snapshot_name)
    with samples.open(newline="", encoding="utf-8") as stream:
        expected_samples = list(csv.DictReader(stream))
    if len(expected_samples) != 11 or len({r["workbook_date"] for r in expected_samples}) != 11:
        raise ValueError("Expected exactly 11 distinct verified sample controls.")
    by_date = {r[5].isoformat(): r for r in records}
    for sample in expected_samples:
        record = by_date[sample["workbook_date"]]
        if record[4] != int(sample["excel_row"]) or round(float(record[8]) - float(sample["usd_row_php_equivalent"]), 4) != 0:
            raise ValueError(f"Source sample mismatch: {sample['workbook_date']}")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    archived = snapshot_dir / snapshot_name
    if archived.exists():
        if sha256(archived) != SNAPSHOT_SHA256:
            raise ValueError("Existing archive has unexpected contents; it was not overwritten.")
    else:
        temporary = archived.with_suffix(".xlsx.tmp")
        shutil.copyfile(source, temporary)
        if sha256(temporary) != SNAPSHOT_SHA256:
            raise ValueError("Snapshot copy failed its hash check.")
        os.replace(temporary, archived)
    database.parent.mkdir(parents=True, exist_ok=True)
    imported_at = dt.datetime.now(dt.timezone.utc)
    with duckdb.connect(str(database)) as con:
        con.execute("BEGIN TRANSACTION")
        try:
            con.execute("CREATE SCHEMA IF NOT EXISTS raw")
            con.execute(DDL)
            actual_columns = [r[0] for r in con.execute(f"DESCRIBE {TABLE}").fetchall()]
            if actual_columns != COLUMNS:
                raise ValueError("Existing raw table has a different schema; it was not replaced.")
            previous_count = con.execute(f"SELECT count(*) FROM {TABLE} WHERE snapshot_sha256 = ?", [SNAPSHOT_SHA256]).fetchone()[0]
            if not previous_count:
                placeholders = ",".join("?" for _ in COLUMNS)
                con.executemany(f"INSERT INTO {TABLE} ({','.join(COLUMNS)}) VALUES ({placeholders})",
                                [r + (imported_at,) for r in records])
            # Exact field-by-field round trip, also protecting safe reruns.
            loaded = con.execute(f"SELECT {','.join(COLUMNS[:-1])} FROM {TABLE} WHERE snapshot_sha256 = ? ORDER BY source_row",
                                 [SNAPSHOT_SHA256]).fetchall()
            if loaded != records:
                raise ValueError("Raw round-trip mismatch; transaction rolled back. No existing rows were overwritten.")
            sample_results = []
            for sample in expected_samples:
                date = sample["workbook_date"]
                observed = con.execute(f"SELECT source_row, usd_php_raw FROM {TABLE} WHERE snapshot_sha256 = ? AND source_date = CAST(? AS DATE)",
                                       [SNAPSHOT_SHA256, date]).fetchone()
                if observed is None or observed[0] != int(sample["excel_row"]) or round(float(observed[1]) - float(sample["usd_row_php_equivalent"]), 4) != 0:
                    raise ValueError(f"Loaded sample mismatch: {date}")
                sample_results.append({"date": date, "source_row": observed[0], "raw_value": observed[1], "match": True})
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
    return {
        "table": TABLE, "database": str(database), "snapshot_file": str(archived),
        "snapshot_sha256": SNAPSHOT_SHA256, "source_sheet": SHEET,
        "study_start": START.isoformat(), "study_end": END.isoformat(),
        "action": "already_loaded_verified" if previous_count else "inserted",
        "inserted_rows": 0 if previous_count else len(records), "controls": controls,
        "exact_raw_round_trip": True, "sample_checks": sample_results,
        "verification_time_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "loader_version": "1.0", "duckdb_version": duckdb.__version__, "openpyxl_version": openpyxl.__version__,
        "limitations": "Raw study-window capture only. No filling, external-rate substitution, date shift, staging, calendar inference or risk calculation.",
    }


def main() -> None:
    project = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--database", type=Path, default=project / "traded_risk.duckdb")
    parser.add_argument("--snapshot-dir", type=Path, default=project / "data/raw/bsp")
    parser.add_argument("--samples", type=Path, default=project / "data/reference/bsp_verified_samples.csv")
    parser.add_argument("--report", type=Path, default=project / "reports/raw_ingestion.json")
    args = parser.parse_args()
    result = ingest(args.source, args.database, args.snapshot_dir, args.samples)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.report.with_suffix(args.report.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, args.report)
    print(json.dumps({key: result[key] for key in ["table", "action", "inserted_rows", "controls", "exact_raw_round_trip"]}, indent=2))


if __name__ == "__main__":
    main()
