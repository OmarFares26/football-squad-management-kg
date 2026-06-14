from pathlib import Path

import numpy as np
import pandas as pd


# Input file from the preprocessing step.
INPUT_PATH = Path("data/processed/premier_league_players.csv")

# Output folder for processed data.
PROCESSED_DATA_DIR = Path("data/processed")

# Output folder for result summaries.
RESULTS_DIR = Path("outputs/results")


def safe_per_90(value: pd.Series, nineties_played: pd.Series) -> pd.Series:
    """
    Calculate a per-90 value safely.

    If a player has 0 minutes, we return 0 instead of dividing by 0.
    """

    return (value / nineties_played.replace(0, np.nan)).fillna(0)


def normalize_column(df: pd.DataFrame, column: str) -> pd.Series:
    """
    Normalize one column between 0 and 1.

    This makes different metrics comparable.
    For example, goals and tackles can then be added together.
    """

    min_value = df[column].min()
    max_value = df[column].max()

    # If all values are the same, return 0 for everyone.
    if max_value == min_value:
        return pd.Series(0.0, index=df.index)

    return (df[column] - min_value) / (max_value - min_value)


def add_normalized_metric_by_position(
    df: pd.DataFrame,
    metric: str,
) -> pd.DataFrame:
    """
    Normalize one metric inside each position group.

    This keeps the comparison fair:
    forwards are compared with forwards,
    defenders with defenders,
    midfielders with midfielders,
    and goalkeepers with goalkeepers.
    """

    normalized_column = f"normalized_{metric}"

    # Start with 0 for all players.
    df[normalized_column] = 0.0

    # Normalize separately inside each position group.
    for position_group in df["broad_position_group"].unique():
        position_mask = df["broad_position_group"] == position_group
        position_players = df.loc[position_mask]

        df.loc[position_mask, normalized_column] = normalize_column(
            position_players,
            metric,
        )

    return df


def add_position_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a simple performance score based on the player's broad position group.

    The score is not a professional scouting model.
    It is a simple rule-based indicator for this Knowledge Graph project.
    """

    scored_df = df.copy()

    # Create per-90 metrics for outfield players.
    scored_df["goals_per_90"] = safe_per_90(
        scored_df["goals"], scored_df["nineties_played"]
    )
    scored_df["assists_per_90"] = safe_per_90(
        scored_df["assists"], scored_df["nineties_played"]
    )
    scored_df["tackles_per_90"] = safe_per_90(
        scored_df["tackles"], scored_df["nineties_played"]
    )
    scored_df["interceptions_per_90"] = safe_per_90(
        scored_df["interceptions"], scored_df["nineties_played"]
    )
    scored_df["clearances_per_90"] = safe_per_90(
        scored_df["clearances"], scored_df["nineties_played"]
    )
    scored_df["blocks_per_90"] = safe_per_90(
        scored_df["blocks"], scored_df["nineties_played"]
    )

    # Create per-90 metrics for goalkeepers.
    scored_df["clean_sheets_per_90"] = safe_per_90(
        scored_df["clean_sheets"], scored_df["nineties_played"]
    )
    scored_df["goals_against_per_90"] = safe_per_90(
        scored_df["goals_against"], scored_df["nineties_played"]
    )

    # These are the metrics we normalize before combining them.
    metrics_to_normalize = [
        "goals_per_90",
        "assists_per_90",
        "tackles_per_90",
        "interceptions_per_90",
        "clearances_per_90",
        "blocks_per_90",
        "save_percentage",
        "clean_sheets_per_90",
        "goals_against_per_90",
    ]

    # Normalize each metric inside each position group.
    for metric in metrics_to_normalize:
        scored_df = add_normalized_metric_by_position(scored_df, metric)

    # Start with an empty raw score.
    scored_df["raw_performance_score"] = 0.0

    # Forward score: goals + assists.
    forward_mask = scored_df["broad_position_group"] == "Forward"
    scored_df.loc[forward_mask, "raw_performance_score"] = (
        scored_df.loc[forward_mask, "normalized_goals_per_90"]
        + scored_df.loc[forward_mask, "normalized_assists_per_90"]
    )

    # Midfielder score: goals + assists + tackles + interceptions.
    midfielder_mask = scored_df["broad_position_group"] == "Midfielder"
    scored_df.loc[midfielder_mask, "raw_performance_score"] = (
        scored_df.loc[midfielder_mask, "normalized_goals_per_90"]
        + scored_df.loc[midfielder_mask, "normalized_assists_per_90"]
        + scored_df.loc[midfielder_mask, "normalized_tackles_per_90"]
        + scored_df.loc[midfielder_mask, "normalized_interceptions_per_90"]
    )

    # Defender score: tackles + interceptions + clearances + blocks.
    defender_mask = scored_df["broad_position_group"] == "Defender"
    scored_df.loc[defender_mask, "raw_performance_score"] = (
        scored_df.loc[defender_mask, "normalized_tackles_per_90"]
        + scored_df.loc[defender_mask, "normalized_interceptions_per_90"]
        + scored_df.loc[defender_mask, "normalized_clearances_per_90"]
        + scored_df.loc[defender_mask, "normalized_blocks_per_90"]
    )

    # Goalkeeper score: save percentage + clean sheets - goals against.
    goalkeeper_mask = scored_df["broad_position_group"] == "Goalkeeper"
    scored_df.loc[goalkeeper_mask, "raw_performance_score"] = (
        scored_df.loc[goalkeeper_mask, "normalized_save_percentage"]
        + scored_df.loc[goalkeeper_mask, "normalized_clean_sheets_per_90"]
        - scored_df.loc[goalkeeper_mask, "normalized_goals_against_per_90"]
    )

    # Normalize the final raw score inside each position group.
    scored_df["performance_score"] = 0.0

    for position_group in scored_df["broad_position_group"].unique():
        position_mask = scored_df["broad_position_group"] == position_group
        position_players = scored_df.loc[position_mask]

        scored_df.loc[position_mask, "performance_score"] = normalize_column(
            position_players,
            "raw_performance_score",
        )

    # Add a percentile inside each position group.
    scored_df["performance_percentile"] = (
        scored_df.groupby("broad_position_group")["performance_score"]
        .rank(pct=True)
        .mul(100)
        .round(2)
    )

    # Add a simple performance label for later rule-based reasoning.
    # Players between the 40th and 50th percentile stay as "Average".
    # This is intentional: they are not poor enough to be marked as Poor,
    # and not strong enough to be marked as Promising or Good.
    # In the rule engine, these players will usually fall into Monitor.
    scored_df["performance_level"] = "Average"

    # Good performance means the player is above the 60th percentile.
    scored_df.loc[scored_df["performance_percentile"] >= 60, "performance_level"] = (
        "Good"
    )

    # Promising performance means the player is between the 50th and 60th percentile.
    scored_df.loc[
        (scored_df["performance_percentile"] >= 50)
        & (scored_df["performance_percentile"] < 60),
        "performance_level",
    ] = "Promising"

    # Poor performance means the player is below the 40th percentile.
    scored_df.loc[scored_df["performance_percentile"] < 40, "performance_level"] = (
        "Poor"
    )

    return scored_df


def main() -> None:
    # Create output folders if they do not exist.
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load cleaned Premier League data.
    df = pd.read_csv(INPUT_PATH)

    # Add performance scores.
    scored_df = add_position_scores(df)

    # Save the full scored dataset.
    output_path = PROCESSED_DATA_DIR / "player_scores.csv"
    scored_df.to_csv(output_path, index=False)

    # Save a small summary for the report.
    score_summary = (
        scored_df.groupby("broad_position_group")["performance_score"]
        .agg(["count", "min", "mean", "max"])
        .reset_index()
    )
    score_summary.to_csv(
        RESULTS_DIR / "performance_score_summary.csv",
        index=False,
    )

    # Save performance level counts.
    level_counts = (
        scored_df.groupby(["broad_position_group", "performance_level"])
        .size()
        .reset_index(name="count")
    )
    level_counts.to_csv(
        RESULTS_DIR / "performance_level_counts.csv",
        index=False,
    )

    # Print a simple summary.
    print("Performance scoring completed")
    print("-----------------------------")
    print(f"Players scored: {scored_df.shape[0]}")
    print(f"Saved file: {output_path}")
    print()
    print("Score summary by position:")
    print(score_summary)
    print()
    print("Performance level counts:")
    print(level_counts)


if __name__ == "__main__":
    main()