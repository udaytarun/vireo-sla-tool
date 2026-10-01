from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def main():

    path = DATA_DIR / "tickets.csv"

    df = pd.read_csv(path)

    # Find ticket IDs that appear more than once
    duplicate_ids = (
        df["ticket_id"]
        .value_counts()
        .loc[lambda x: x > 1]
        .index
    )

    duplicates = df[
        df["ticket_id"].isin(duplicate_ids)
    ].copy()

    print("=" * 70)
    print("DUPLICATE ANALYSIS")
    print("=" * 70)

    print(f"Raw rows: {len(df):,}")
    print(f"Unique tickets: {df['ticket_id'].nunique():,}")
    print(f"Duplicate rows: {len(df) - df['ticket_id'].nunique():,}")
    print(f"Tickets appearing more than once: {len(duplicate_ids):,}")

    print("\nSource system distribution among duplicates:")
    print(
        duplicates["source_system"]
        .value_counts()
        .to_string()
    )

    print("\nDuplicate source-system combinations:")

    combinations = (
        duplicates
        .groupby("ticket_id")["source_system"]
        .apply(lambda x: " + ".join(sorted(x.unique())))
        .value_counts()
    )

    print(combinations.to_string())

    print("\nSample duplicate tickets:")
    
    sample_ids = list(duplicate_ids[:10])

    sample = (
        duplicates[
            duplicates["ticket_id"].isin(sample_ids)
        ]
        .sort_values(["ticket_id", "source_system"])
        [
            [
                "ticket_id",
                "created_at",
                "first_response_at",
                "agent_id",
                "channel",
                "source_system",
            ]
        ]
    )

    print(sample.to_string(index=False))


if __name__ == "__main__":
    main()