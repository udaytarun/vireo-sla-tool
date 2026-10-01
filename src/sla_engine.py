from pathlib import Path
import sys

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

# Allow importing cleaning.py from src/
sys.path.append(str(BASE_DIR / "src"))

from cleaning import clean_tickets


# ============================================================
# SLA POLICY
# ============================================================

SLA_TARGETS_MINUTES = {
    "chat": 15,
    "voice": 120,
    "social": 240,
    "email": 480,
}


# ============================================================
# CALCULATE RESPONSE TIME
# ============================================================

def calculate_response_time(df):
    """
    Calculate first-response time in minutes.

    response_time = first_response_at - created_at
    """

    df = df.copy()

    df["response_time_minutes"] = (
        (
            df["first_response_at"]
            - df["created_at"]
        )
        .dt.total_seconds()
        / 60
    )

    return df


# ============================================================
# ASSIGN SLA TARGET
# ============================================================

def assign_sla_target(df):
    """
    Assign SLA target in minutes based on channel.
    """

    df = df.copy()

    df["sla_target_minutes"] = (
        df["channel"]
        .map(SLA_TARGETS_MINUTES)
    )

    return df


# ============================================================
# CALCULATE BREACH
# ============================================================

def calculate_breach(df):
    """
    A ticket breaches SLA when its first response
    is later than the channel-specific SLA target.

    Exactly equal to the target is NOT a breach.
    """

    df = df.copy()

    # Check for unknown channels first
    unknown_channels = df.loc[
        df["sla_target_minutes"].isna(),
        "channel"
    ].unique()

    if len(unknown_channels) > 0:
        raise ValueError(
            f"Unknown channels found: {unknown_channels}"
        )

    df["sla_breach"] = (
        df["response_time_minutes"]
        > df["sla_target_minutes"]
    )

    return df


# ============================================================
# COMPLETE SLA PIPELINE
# ============================================================

def calculate_sla():

    print("=" * 60)
    print("VIREO SLA ENGINE")
    print("=" * 60)

    # --------------------------------------------------------
    # Load and clean tickets
    # --------------------------------------------------------

    df = clean_tickets()

    # --------------------------------------------------------
    # Calculate response time
    # --------------------------------------------------------

    df = calculate_response_time(df)

    # --------------------------------------------------------
    # Assign SLA target
    # --------------------------------------------------------

    df = assign_sla_target(df)

    # --------------------------------------------------------
    # Calculate breach
    # --------------------------------------------------------

    df = calculate_breach(df)

    return df


# ============================================================
# SUMMARY
# ============================================================

def print_summary(df):

    total_tickets = len(df)

    breached_tickets = int(
        df["sla_breach"].sum()
    )

    breach_rate = (
        breached_tickets / total_tickets
        if total_tickets > 0
        else 0
    )

    estimated_credit = (
        breached_tickets * 350
    )

    print("\n" + "=" * 60)
    print("SLA SUMMARY")
    print("=" * 60)

    print(
        f"Canonical tickets : {total_tickets:,}"
    )

    print(
        f"SLA breaches     : {breached_tickets:,}"
    )

    print(
        f"Breach rate      : {breach_rate:.2%}"
    )

    print(
        f"Estimated credits: ₹{estimated_credit:,.2f}"
    )


# ============================================================
# BREAKDOWN BY CHANNEL
# ============================================================

def print_channel_summary(df):

    print("\n" + "=" * 60)
    print("CHANNEL BREAKDOWN")
    print("=" * 60)

    summary = (
        df.groupby("channel")
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("sla_breach", "sum"),
            avg_response_minutes=(
                "response_time_minutes",
                "mean",
            ),
        )
    )

    summary["breach_rate"] = (
        summary["breaches"]
        / summary["tickets"]
    )

    print(summary.to_string())


# ============================================================
# SAMPLE TICKETS
# ============================================================

def print_sample(df):

    print("\n" + "=" * 60)
    print("SAMPLE SLA CALCULATIONS")
    print("=" * 60)

    columns = [
        "ticket_id",
        "channel",
        "created_at",
        "first_response_at",
        "response_time_minutes",
        "sla_target_minutes",
        "sla_breach",
    ]

    print(
        df[columns]
        .head(15)
        .to_string(index=False)
    )


# ============================================================
# MAIN
# ============================================================

def main():

    df = calculate_sla()

    print_summary(df)

    print_channel_summary(df)

    print_sample(df)


if __name__ == "__main__":
    main()