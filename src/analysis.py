from pathlib import Path
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR / "src"))

from report import build_analysis_dataset


# ============================================================
# AGENT SUMMARY
# ============================================================

def agent_summary(df):

    result = (
        df.groupby(
            ["agent_id", "name", "site", "team", "shift"],
            dropna=False,
        )
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("sla_breach", "sum"),
        )
        .reset_index()
    )

    result["breach_rate"] = (
        result["breaches"]
        / result["tickets"]
    )

    result = result.sort_values(
        ["breaches", "breach_rate"],
        ascending=False,
    )

    return result


# ============================================================
# SHIFT SUMMARY
# ============================================================

def shift_summary(df):

    result = (
        df.groupby("shift")
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("sla_breach", "sum"),
        )
        .reset_index()
    )

    result["breach_rate"] = (
        result["breaches"]
        / result["tickets"]
    )

    return result.sort_values(
        "breach_rate",
        ascending=False,
    )


# ============================================================
# WEEKLY SHIFT SUMMARY
# ============================================================

def weekly_shift_summary(df):

    df = df.copy()

    df["week"] = (
        df["created_at_ist"]
        .dt.strftime("%G-W%V")
    )

    result = (
        df.groupby(
            ["week", "shift"]
        )
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("sla_breach", "sum"),
        )
        .reset_index()
    )

    result["breach_rate"] = (
        result["breaches"]
        / result["tickets"]
    )

    return result


# ============================================================
# WEEKLY AGENT SUMMARY
# ============================================================

def weekly_agent_summary(df):

    df = df.copy()

    df["week"] = (
        df["created_at_ist"]
        .dt.strftime("%G-W%V")
    )

    result = (
        df.groupby(
            [
                "week",
                "agent_id",
                "name",
                "site",
                "team",
                "shift",
            ],
            dropna=False,
        )
        .agg(
            tickets=("ticket_id", "count"),
            breaches=("sla_breach", "sum"),
        )
        .reset_index()
    )

    result["breach_rate"] = (
        result["breaches"]
        / result["tickets"]
    )

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("VIREO SUPPORT SLA ANALYSIS")
    print("=" * 60)

    df = build_analysis_dataset()

    # --------------------------------------------------------
    # Agent analysis
    # --------------------------------------------------------

    agents = agent_summary(df)

    print("\n" + "=" * 60)
    print("TOP AGENTS BY BREACH COUNT")
    print("=" * 60)

    print(
        agents.head(15).to_string(index=False)
    )

    # --------------------------------------------------------
    # Shift analysis
    # --------------------------------------------------------

    shifts = shift_summary(df)

    print("\n" + "=" * 60)
    print("SHIFT SUMMARY")
    print("=" * 60)

    print(
        shifts.to_string(index=False)
    )

    # --------------------------------------------------------
    # Weekly shift analysis
    # --------------------------------------------------------

    weekly_shifts = weekly_shift_summary(df)

    print("\n" + "=" * 60)
    print("WEEKLY SHIFT SUMMARY")
    print("=" * 60)

    print(
        weekly_shifts.head(30)
        .to_string(index=False)
    )

    # --------------------------------------------------------
    # Weekly agent analysis
    # --------------------------------------------------------

    weekly_agents = weekly_agent_summary(df)

    print("\n" + "=" * 60)
    print("TOP WEEKLY AGENT RESULTS")
    print("=" * 60)

    print(
        weekly_agents
        .sort_values(
            ["breaches", "breach_rate"],
            ascending=False,
        )
        .head(30)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()