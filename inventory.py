"""Synthetic data-asset catalog and governance metrics.

Every row is invented. Nothing here is a real UT Southwestern dataset.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import duckdb

AS_OF = dt.date(2026, 11, 6)
ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "catalog.duckdb"

ASSETS = [
    ("Encounter fact", "A. Shah", "L. Ortega", "Restricted-PHI", "High", "EHR", "DUA", "2026-06-01", "2026-09-01"),
    ("Lab results", "A. Shah", "L. Ortega", "Restricted-PHI", "High", "LIS", "DUA", "2025-12-01", "2026-08-15"),
    ("Imaging metadata", "R. Cole", "L. Ortega", "Confidential", "High", "PACS", "DUSA", "2027-01-15", "2026-10-01"),
    ("Claims extract", "R. Cole", "M. Iqbal", "Restricted-PHI", "High", "Billing", "DUA", "2026-04-30", "2026-07-20"),
    ("Provider directory", "M. Iqbal", "M. Iqbal", "Internal", "Medium", "Credentialing", "DTA", "2027-03-01", "2026-10-12"),
    ("Facility list", "M. Iqbal", "P. Nguyen", "Public", "Low", "Facilities", None, None, "2026-05-01"),
    ("Appointment slots", "P. Nguyen", "P. Nguyen", "Internal", "Medium", "Scheduling", "DUSA", "2026-11-01", "2026-09-30"),
    ("Referral log", None, "P. Nguyen", "Confidential", "Medium", "EHR", "DUA", "2026-01-10", "2026-06-18"),
    ("Patient portal events", "S. Adler", None, "Restricted-PHI", "Medium", "Portal", "DUA", "2027-08-01", "2026-10-20"),
    ("Device inventory", "S. Adler", "S. Adler", "Internal", "Low", "CMMS", None, None, "2026-04-02"),
    ("Research cohort A", "J. Okonkwo", "J. Okonkwo", "Restricted-PHI", "High", "EDW", "DUSA", "2025-09-01", "2026-03-11"),
    ("Research cohort B", "J. Okonkwo", "J. Okonkwo", "Confidential", "High", "EDW", "DTA", "2027-02-28", "2026-09-09"),
    ("Public quality scores", "C. Brooks", "C. Brooks", "Public", "Low", "Web", None, None, "2026-01-22"),
    ("Staff roster", "C. Brooks", "H. Patel", "Confidential", "Medium", "HR", "DUA", "2026-10-01", "2026-08-01"),
    ("Pharmacy orders", "H. Patel", "H. Patel", "Restricted-PHI", "High", "Pharmacy", "DUA", "2027-05-01", "2026-10-28"),
    ("Supply usage", "H. Patel", None, "Internal", "Low", "ERP", None, None, "2026-02-14"),
    ("Unclassified survey", "N. Flores", "N. Flores", None, "Low", "Qualtrics", None, None, "2025-11-02"),
    ("Unclassified notes export", None, None, None, "Medium", "File share", "DTA", "2026-02-02", "2025-12-12"),
    ("Bed census", "N. Flores", "R. Cole", "Confidential", "High", "ADT", "DUSA", "2026-12-31", "2026-10-05"),
    ("Ambulance turnaround", "L. Ortega", "L. Ortega", "Internal", "Medium", "EMS", "DUA", "2025-08-19", "2026-01-09"),
    ("Community health PDF", "L. Ortega", "C. Brooks", "Public", "Low", "Web", None, None, "2026-06-30"),
    ("Billing denials", "A. Shah", "M. Iqbal", "Confidential", "High", "Billing", "DUA", "2027-04-04", "2026-09-19"),
    ("Legacy access log", None, "S. Adler", None, "Medium", "File share", "DUSA", "2026-03-03", "2026-03-03"),
    ("Student rotation list", "P. Nguyen", "J. Okonkwo", "Confidential", "Medium", "GME", "DTA", "2026-09-15", "2026-07-01"),
]


def build_database(path: Path = DB_PATH) -> Path:
    if path.exists():
        path.unlink()
    con = duckdb.connect(str(path))
    con.execute(
        """
        CREATE TABLE data_assets (
            asset_name VARCHAR,
            owner VARCHAR,
            steward VARCHAR,
            sensitivity VARCHAR,
            criticality VARCHAR,
            source_system VARCHAR,
            agreement_type VARCHAR,
            agreement_expiry DATE,
            last_review_date DATE
        )
        """
    )
    con.executemany(
        "INSERT INTO data_assets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ASSETS,
    )
    con.close()
    return path


def metrics(path: Path = DB_PATH, as_of: dt.date = AS_OF) -> dict:
    con = duckdb.connect(str(path), read_only=True)
    row = con.execute(
        """
        SELECT
            COUNT(*) AS assets,
            COUNT(sensitivity) AS classified,
            COUNT(*) FILTER (WHERE owner IS NULL OR owner = '') AS missing_owner,
            COUNT(*) FILTER (
                WHERE agreement_type IS NOT NULL
                  AND agreement_expiry IS NOT NULL
                  AND agreement_expiry < ?
            ) AS expired_agreements,
            COUNT(*) FILTER (WHERE agreement_type IS NOT NULL) AS with_agreement
        FROM data_assets
        """,
        [as_of],
    ).fetchone()
    con.close()
    assets, classified, missing_owner, expired_agreements, with_agreement = row
    return {
        "as_of": as_of.isoformat(),
        "assets": assets,
        "percent_classified": round(100 * classified / assets, 1),
        "percent_without_owner": round(100 * missing_owner / assets, 1),
        "percent_agreements_expired": round(100 * expired_agreements / with_agreement, 1),
        "classified": classified,
        "missing_owner": missing_owner,
        "expired_agreements": expired_agreements,
        "with_agreement": with_agreement,
    }


def load_frame(path: Path = DB_PATH):
    con = duckdb.connect(str(path), read_only=True)
    frame = con.execute("SELECT * FROM data_assets ORDER BY asset_name").fetchdf()
    con.close()
    return frame


if __name__ == "__main__":
    build_database()
    result = metrics()
    print(
        f"{result['assets']} synthetic assets as of {result['as_of']}: "
        f"{result['percent_classified']}% classified, "
        f"{result['percent_agreements_expired']}% of agreements expired, "
        f"{result['percent_without_owner']}% without an owner."
    )
