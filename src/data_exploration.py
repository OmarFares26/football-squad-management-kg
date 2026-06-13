from pathlib import Path

import pandas as pd


# Path to the raw dataset file.
RAW_DATA_PATH = Path("data/raw/players_data_light-2024_2025.csv")

# Folder where we save exploration outputs.
OUTPUT_DIR = Path("outputs/results")


def main() -> None:
    # Create the output folder if it does not exist yet.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Stop early if the dataset file is missing.
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw data file not found: {RAW_DATA_PATH}")

    # Load the CSV dataset.
    df = pd.read_csv(RAW_DATA_PATH)

    # Print basic dataset information.
    print("Dataset loaded successfully")
    print("---------------------------")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print()

    # Print all column names so we know what the dataset really contains.
    print("Column names:")
    for column in df.columns:
        print(f"- {column}")

    print()
    print("First 5 rows:")
    print(df.head())

    # Save a small overview file.
    data_overview = pd.DataFrame(
        {
            "metric": ["rows", "columns"],
            "value": [df.shape[0], df.shape[1]],
        }
    )
    data_overview.to_csv(OUTPUT_DIR / "data_overview.csv", index=False)

    # Save information about each column.
    column_overview = pd.DataFrame(
        {
            "column": df.columns,
            "dtype": [str(df[column].dtype) for column in df.columns],
            "missing_values": [df[column].isna().sum() for column in df.columns],
            "missing_percentage": [
                round(df[column].isna().mean() * 100, 2) for column in df.columns
            ],
            "unique_values": [df[column].nunique(dropna=True) for column in df.columns],
        }
    )
    column_overview.to_csv(OUTPUT_DIR / "column_overview.csv", index=False)

    # Save missing value counts separately because this is useful for the report.
    missing_values = (
        df.isna()
        .sum()
        .reset_index()
        .rename(columns={"index": "column", 0: "missing_values"})
        .sort_values(by="missing_values", ascending=False)
    )
    missing_values.to_csv(OUTPUT_DIR / "missing_values.csv", index=False)

    # These are possible column names for league, team, country, and position.
    # We check them because datasets often use slightly different names.
    possible_categorical_columns = [
        "Comp",
        "Competition",
        "League",
        "Squad",
        "Team",
        "Nation",
        "Pos",
        "Position",
    ]

    # Print and save value counts for useful categorical columns.
    for column in possible_categorical_columns:
        if column in df.columns:
            print()
            print(f"Top values for {column}:")
            print(df[column].value_counts(dropna=False).head(20))

            value_counts = df[column].value_counts(dropna=False).reset_index()
            value_counts.columns = [column, "count"]
            value_counts.to_csv(
                OUTPUT_DIR / f"{column.lower()}_value_counts.csv",
                index=False,
            )

    print()
    print("Exploration files saved to outputs/results/")


if __name__ == "__main__":
    main()