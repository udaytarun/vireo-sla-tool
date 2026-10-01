from pathlib import Path
import pandas as pd


# Project root
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def inspect_file(filename):
    path = DATA_DIR / filename

    print("\n" + "=" * 70)
    print(f"FILE: {filename}")
    print("=" * 70)

    if not path.exists():
        print(f"ERROR: File not found: {path}")
        return

    df = pd.read_csv(path)

    print(f"\nShape: {df.shape}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nFirst 5 rows:")
    print(df.head().to_string())

    print("\nMissing values:")
    print(df.isna().sum().to_string())

    print("\nData types:")
    print(df.dtypes.to_string())


def main():
    files = [
        "tickets.csv",
        "agents.csv",
        "customers.csv",
        "orders.csv",
        "products.csv",
    ]

    for filename in files:
        inspect_file(filename)


if __name__ == "__main__":
    main()