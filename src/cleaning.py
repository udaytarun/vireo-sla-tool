from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


# ============================================================
# LOAD DATA
# ============================================================

def load_tickets():
    """
    Load raw ticket data from tickets.csv.
    """
    path = DATA_DIR / "tickets.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Could not find tickets file: {path}"
        )

    return pd.read_csv(path)


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate_tickets(df):
    """
    Remove migration duplicates.

    The export contains tickets that appear in both:
        - helpdesk
        - legacy_fd

    When the same ticket_id exists in both systems,
    the helpdesk record is retained as the canonical record.
    """

    df = df.copy()

    raw_count = len(df)

    # Identify duplicate ticket IDs
    duplicate_mask = df["ticket_id"].duplicated(keep=False)
    duplicate_rows = df[duplicate_mask]

    print(f"Raw rows: {raw_count:,}")
    print(f"Duplicate rows: {len(duplicate_rows):,}")

    # Give each source system a priority.
    # Lower number = higher priority.
    source_priority = {
        "helpdesk": 0,
        "legacy_fd": 1,
    }

    df["_source_priority"] = (
        df["source_system"]
        .map(source_priority)
        .fillna(99)
    )

    # Put preferred source first for each ticket
    df = df.sort_values(
        by=["ticket_id", "_source_priority"]
    )

    # Keep exactly one canonical record per ticket
    df = df.drop_duplicates(
        subset=["ticket_id"],
        keep="first",
    )

    # Remove temporary column
    df = df.drop(
        columns=["_source_priority"]
    )

    print(f"Canonical rows: {len(df):,}")

    return df


# ============================================================
# TIMESTAMP NORMALIZATION
# ============================================================

def normalize_timestamps(df):
    """
    Parse timestamps from the helpdesk export.

    The source export stores timestamps in UTC.

    We retain the UTC timestamps and additionally create
    IST versions for operational reporting and shift matching.
    """

    df = df.copy()

    timestamp_columns = [
        "created_at",
        "first_response_at",
        "resolved_at",
    ]

    # --------------------------------------------------------
    # Parse timestamps as UTC
    # --------------------------------------------------------

    for column in timestamp_columns:

        df[column] = pd.to_datetime(
            df[column],
            utc=True,
            errors="coerce",
        )

    # --------------------------------------------------------
    # Convert timestamps to IST
    # --------------------------------------------------------

    df["created_at_ist"] = (
        df["created_at"]
        .dt.tz_convert("Asia/Kolkata")
    )

    df["first_response_at_ist"] = (
        df["first_response_at"]
        .dt.tz_convert("Asia/Kolkata")
    )

    df["resolved_at_ist"] = (
        df["resolved_at"]
        .dt.tz_convert("Asia/Kolkata")
    )

    return df


# ============================================================
# DATA QUALITY CHECKS
# ============================================================

def check_timestamp_quality(df):
    """
    Check whether timestamp conversion produced unexpected
    missing values.
    """

    print("\n" + "=" * 60)
    print("TIMESTAMP QUALITY")
    print("=" * 60)

    timestamp_columns = [
        "created_at",
        "first_response_at",
        "resolved_at",
    ]

    for column in timestamp_columns:

        missing = df[column].isna().sum()

        print(
            f"{column:<20} missing: {missing:,}"
        )


# ============================================================
# MAIN CLEANING PIPELINE
# ============================================================

def clean_tickets():

    print("=" * 60)
    print("VIREO TICKET CLEANING PIPELINE")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Load raw tickets
    # --------------------------------------------------------

    tickets = load_tickets()

    print(
        f"\nLoaded tickets: {len(tickets):,}"
    )

    # --------------------------------------------------------
    # 2. Remove migration duplicates
    # --------------------------------------------------------

    tickets = deduplicate_tickets(tickets)

    # --------------------------------------------------------
    # 3. Normalize timestamps
    # --------------------------------------------------------

    tickets = normalize_timestamps(tickets)

    # --------------------------------------------------------
    # 4. Data quality checks
    # --------------------------------------------------------

    check_timestamp_quality(tickets)

    return tickets


# ============================================================
# TEST / DEVELOPMENT RUN
# ============================================================

def main():

    tickets = clean_tickets()

    print("\n" + "=" * 60)
    print("TIMESTAMP CONVERSION SAMPLE")
    print("=" * 60)

    print(
        tickets[
            [
                "ticket_id",
                "created_at",
                "created_at_ist",
                "first_response_at",
                "first_response_at_ist",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\n" + "=" * 60)
    print("FINAL DATASET")
    print("=" * 60)

    print(
        f"Canonical tickets: {len(tickets):,}"
    )

    print(
        f"Columns: {len(tickets.columns)}"
    )


if __name__ == "__main__":
    main()