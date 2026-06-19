from pathlib import Path

import pandas as pd


RAW_DATA_PATH = Path("data/raw/players_data_light-2024_2025.csv")
PROCESSED_DATA_DIR = Path("data/processed")


def map_role_group(raw_position: str) -> str:
    """Map raw positions to the role groups used throughout the project."""

    if pd.isna(raw_position):
        return "Unknown"

    positions = [position.strip() for position in str(raw_position).split(",")]

    # A set treats reversed combinations such as FW,MF and MF,FW equally.
    position_set = set(positions)

    if position_set == {"GK"}:
        return "Goalkeeper"

    if position_set == {"DF"}:
        return "Defender"

    if position_set == {"MF"}:
        return "Midfielder"

    if position_set == {"FW"}:
        return "Forward"

    if position_set == {"DF", "MF"}:
        return "DefMidWingBack"

    if position_set == {"MF", "FW"}:
        return "AttMidWinger"

    if position_set == {"DF", "FW"}:
        return "WingBack"

    return "Unknown"


def main() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RAW_DATA_PATH)

    premier_league_df = df[df["Comp"] == "eng Premier League"].copy()

    # Transferred players can have two rows; keep the row with more minutes.
    premier_league_df = (
        premier_league_df.sort_values("Min", ascending=False)
        .drop_duplicates(subset=["Player"], keep="first")
        .copy()
    )

    premier_league_df["player_id"] = (
        premier_league_df["Player"].str.lower().str.replace(" ", "_", regex=False)
        + "_"
        + premier_league_df["Squad"].str.lower().str.replace(" ", "_", regex=False)
    )

    premier_league_df["team_id"] = (
        premier_league_df["Squad"].str.lower().str.replace(" ", "_", regex=False)
    )

    premier_league_df["role_group"] = premier_league_df["Pos"].apply(map_role_group)

    useful_columns = [
        "player_id",
        "team_id",
        "Player",
        "Nation",
        "Pos",
        "role_group",
        "Squad",
        "Comp",
        "Age",
        "MP",
        "Starts",
        "Min",
        "90s",
        "Gls",
        "Ast",
        "xG",
        "xAG",
        "Tkl",
        "Int",
        "Clr",
        "Blocks_stats_defense",
        "GA",
        "Saves",
        "Save%",
        "CS",
    ]

    cleaned_df = premier_league_df[useful_columns].copy()

    cleaned_df = cleaned_df.rename(
        columns={
            "Player": "player_name",
            "Nation": "nationality",
            "Pos": "raw_position",
            "Squad": "team_name",
            "Comp": "league_name",
            "Age": "age",
            "MP": "matches_played",
            "Starts": "games_started",
            "Min": "minutes_played",
            "90s": "nineties_played",
            "Gls": "goals",
            "Ast": "assists",
            "xG": "expected_goals",
            "xAG": "expected_assisted_goals",
            "Tkl": "tackles",
            "Int": "interceptions",
            "Clr": "clearances",
            "Blocks_stats_defense": "blocks",
            "GA": "goals_against",
            "Saves": "saves",
            "Save%": "save_percentage",
            "CS": "clean_sheets",
        }
    )

    # Goalkeeper-only statistics are missing for outfield players.
    numeric_columns = [
        "age",
        "matches_played",
        "games_started",
        "minutes_played",
        "nineties_played",
        "goals",
        "assists",
        "expected_goals",
        "expected_assisted_goals",
        "tackles",
        "interceptions",
        "clearances",
        "blocks",
        "goals_against",
        "saves",
        "save_percentage",
        "clean_sheets",
    ]

    cleaned_df[numeric_columns] = cleaned_df[numeric_columns].fillna(0)

    output_path = PROCESSED_DATA_DIR / "premier_league_players.csv"
    cleaned_df.to_csv(output_path, index=False)

    print("Preprocessing completed")
    print("-----------------------")
    print(f"Players after deduplication: {cleaned_df.shape[0]}")
    print(f"Columns kept: {cleaned_df.shape[1]}")
    print()

    print("Role groups:")
    print(cleaned_df["role_group"].value_counts())
    print()

    print(f"Saved file: {output_path}")


if __name__ == "__main__":
    main()
