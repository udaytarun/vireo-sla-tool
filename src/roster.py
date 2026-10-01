from pathlib import Path
import pandas as pd
import sys


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

sys.path.append(str(BASE_DIR / "src"))

from cleaning import clean_tickets


# ============================================================
# LOAD ROSTER
# ============================================================

def load_roster():

    path = DATA_DIR / "agents.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Could not find agents file: {path}"
        )

    roster = pd.read_csv(path)

    # Convert roster dates
    roster["from_date"] = pd.to_datetime(
        roster["from_date"]
    )

    roster["to_date"] = pd.to_datetime(
        roster["to_date"]
    )

    return roster


# ============================================================
# MATCH TICKET TO ROSTER
# ============================================================

def assign_roster(tickets, roster):

    tickets = tickets.copy()

    # Ticket creation date in IST
    tickets["ticket_date"] = (
        tickets["created_at_ist"]
        .dt.tz_localize(None)
        .dt.normalize()
    )

    # Start with empty columns
    roster_columns = [
        "name",
        "site",
        "team",
        "shift",
        "tier",
    ]

    for column in roster_columns:
        tickets[column] = None

    # --------------------------------------------------------
    # Match each ticket against the correct assignment
    # --------------------------------------------------------

    for index, ticket in tickets.iterrows():

        agent_id = ticket["agent_id"]
        ticket_date = ticket["ticket_date"]

        matches = roster[
            (roster["agent_id"] == agent_id)
            &
            (roster["from_date"] <= ticket_date)
            &
            (
                roster["to_date"].isna()
                |
                (roster["to_date"] >= ticket_date)
            )
        ]

        if len(matches) == 1:

            assignment = matches.iloc[0]

            tickets.at[index, "name"] = assignment["name"]
            tickets.at[index, "site"] = assignment["site"]
            tickets.at[index, "team"] = assignment["team"]
            tickets.at[index, "shift"] = assignment["shift"]
            tickets.at[index, "tier"] = assignment["tier"]

        elif len(matches) == 0:

            # No roster assignment found
            tickets.at[index, "shift"] = "UNKNOWN"

        else:

            # More than one assignment matched
            tickets.at[index, "shift"] = "AMBIGUOUS"

    return tickets


# ============================================================
# VALIDATION
# ============================================================

def validate_roster_assignment(df):

    print("\n" + "=" * 60)
    print("ROSTER VALIDATION")
    print("=" * 60)

    print(
        "\nShift distribution:"
    )

    print(
        df["shift"]
        .value_counts(dropna=False)
        .to_string()
    )

    unknown = (
        df["shift"] == "UNKNOWN"
    ).sum()

    ambiguous = (
        df["shift"] == "AMBIGUOUS"
    ).sum()

    print(
        f"\nUnknown assignments : {unknown:,}"
    )

    print(
        f"Ambiguous assignments: {ambiguous:,}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("VIREO ROSTER MAPPING")
    print("=" * 60)

    # Load cleaned tickets
    tickets = clean_tickets()

    # Load roster
    roster = load_roster()

    print(
        f"\nTickets : {len(tickets):,}"
    )

    print(
        f"Roster assignments : {len(roster):,}"
    )

    # Match roster
    tickets = assign_roster(
        tickets,
        roster
    )

    # Validate
    validate_roster_assignment(
        tickets
    )

    # Show sample
    print("\n" + "=" * 60)
    print("SAMPLE MAPPINGS")
    print("=" * 60)

    columns = [
        "ticket_id",
        "agent_id",
        "created_at_ist",
        "name",
        "site",
        "team",
        "shift",
        "tier",
    ]

    print(
        tickets[columns]
        .head(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()