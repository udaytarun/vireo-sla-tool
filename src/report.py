from pathlib import Path
import sys

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(BASE_DIR / "src"))

from cleaning import clean_tickets
from sla_engine import (
    calculate_response_time,
    assign_sla_target,
    calculate_breach,
)
from roster import (
    load_roster,
    assign_roster,
)


# ============================================================
# BUILD ANALYTICS DATASET
# ============================================================

def build_analysis_dataset():

    print("=" * 60)
    print("BUILDING ANALYSIS DATASET")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Clean tickets
    # --------------------------------------------------------

    tickets = clean_tickets()

    # --------------------------------------------------------
    # 2. Calculate SLA
    # --------------------------------------------------------

    tickets = calculate_response_time(tickets)

    tickets = assign_sla_target(tickets)

    tickets = calculate_breach(tickets)

    # --------------------------------------------------------
    # 3. Load roster
    # --------------------------------------------------------

    roster = load_roster()

    # --------------------------------------------------------
    # 4. Assign historical roster
    # --------------------------------------------------------

    tickets = assign_roster(
        tickets,
        roster,
    )

    return tickets


# ============================================================
# CREATE WEEK
# ============================================================

def add_week_column(df):

    df = df.copy()

    # Use IST creation timestamp
    df["week"] = (
        df["created_at_ist"]
        .dt.strftime("%G-W%V")
    )

    return df


# ============================================================
# WEEKLY AGENT REPORT
# ============================================================

def create_weekly_agent_report(df):

    df = add_week_column(df)

    report = (
        df
        .groupby(
            [
                "week",
                "agent_id",
                "name",
                "site",
                "shift",
            ],
            dropna=False,
        )
        .agg(
            tickets=(
                "ticket_id",
                "count",
            ),
            breaches=(
                "sla_breach",
                "sum",
            ),
        )
        .reset_index()
    )

    report["breach_rate"] = (
        report["breaches"]
        / report["tickets"]
    )

    return report


# ============================================================
# WEEKLY SHIFT REPORT
# ============================================================

def create_weekly_shift_report(df):

    df = add_week_column(df)

    report = (
        df
        .groupby(
            [
                "week",
                "shift",
            ],
            dropna=False,
        )
        .agg(
            tickets=(
                "ticket_id",
                "count",
            ),
            breaches=(
                "sla_breach",
                "sum",
            ),
        )
        .reset_index()
    )

    report["breach_rate"] = (
        report["breaches"]
        / report["tickets"]
    )

    return report


# ============================================================
# PRINT REPORT
# ============================================================

def main():

    df = build_analysis_dataset()

    # --------------------------------------------------------
    # Agent report
    # --------------------------------------------------------

    agent_report = create_weekly_agent_report(df)

    print("\n" + "=" * 60)
    print("WEEKLY AGENT SLA REPORT")
    print("=" * 60)

    print(
        agent_report
        .head(30)
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # Shift report
    # --------------------------------------------------------

    shift_report = create_weekly_shift_report(df)

    print("\n" + "=" * 60)
    print("WEEKLY SHIFT SLA REPORT")
    print("=" * 60)

    print(
        shift_report
        .head(30)
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # Overall numbers
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("OVERALL")
    print("=" * 60)

    print(
        f"Tickets: {len(df):,}"
    )

    print(
        f"Breaches: {int(df['sla_breach'].sum()):,}"
    )

    print(
        f"Breach rate: "
        f"{df['sla_breach'].mean():.2%}"
    )


if __name__ == "__main__":
    main()