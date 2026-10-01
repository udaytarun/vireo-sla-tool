from pathlib import Path
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR / "src"))

from cleaning import clean_tickets
from sla_engine import (
    calculate_response_time,
    assign_sla_target,
    calculate_breach,
)


def independent_validation():

    print("=" * 60)
    print("INDEPENDENT SLA VALIDATION")
    print("=" * 60)

    # Load canonical tickets
    df = clean_tickets()

    # Recalculate directly
    df["response_minutes_check"] = (
        (
            df["first_response_at"]
            - df["created_at"]
        )
        .dt.total_seconds()
        / 60
    )

    sla_targets = {
        "chat": 15,
        "voice": 120,
        "social": 240,
        "email": 480,
    }

    df["target_check"] = df["channel"].map(
        sla_targets
    )

    df["breach_check"] = (
        df["response_minutes_check"]
        > df["target_check"]
    )

    # --------------------------------------------------------
    # Validation results
    # --------------------------------------------------------

    total = len(df)

    breaches = int(
        df["breach_check"].sum()
    )

    rate = breaches / total

    print(f"\nTickets : {total:,}")
    print(f"Breaches: {breaches:,}")
    print(f"Rate    : {rate:.2%}")

    # --------------------------------------------------------
    # Data quality checks
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("DATA QUALITY")
    print("=" * 60)

    print(
        "Missing response timestamps:",
        df["first_response_at"].isna().sum()
    )

    print(
        "Negative response times:",
        (
            df["response_minutes_check"] < 0
        ).sum()
    )

    print(
        "Unknown channels:",
        df["target_check"].isna().sum()
    )

    # --------------------------------------------------------
    # Channel validation
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("CHANNEL VALIDATION")
    print("=" * 60)

    channel_check = (
        df.groupby("channel")
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("breach_check", "sum"),
        )
    )

    channel_check["breach_rate"] = (
        channel_check["breaches"]
        / channel_check["tickets"]
    )

    print(
        channel_check.to_string()
    )


if __name__ == "__main__":
    independent_validation()