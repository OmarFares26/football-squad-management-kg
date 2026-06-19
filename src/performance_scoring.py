from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path("data/processed/premier_league_players.csv")
PROCESSED_DATA_DIR = Path("data/processed")
RESULTS_DIR = Path("outputs/results")


def safe_per_90(value: pd.Series, nineties_played: pd.Series) -> pd.Series:
    """Calculate a per-90 value, returning 0 when no minutes were played."""

    return (value / nineties_played.replace(0, np.nan)).fillna(0)


def normalize_column(df: pd.DataFrame, column: str) -> pd.Series:
    """Scale one column to the 0-1 range."""

    min_value = df[column].min()
    max_value = df[column].max()

    if max_value == min_value:
        return pd.Series(0.0, index=df.index)

    return (df[column] - min_value) / (max_value - min_value)


def add_normalized_metric_by_role(
    df: pd.DataFrame,
    metric: str,
) -> pd.DataFrame:
    """Normalize one metric separately within each role group."""

    normalized_column = f"normalized_{metric}"

    df[normalized_column] = 0.0

    for role_group in df["role_group"].unique():
        role_mask = df["role_group"] == role_group
        role_players = df.loc[role_mask]

        df.loc[role_mask, normalized_column] = normalize_column(
            role_players,
            metric,
        )

    return df


def add_role_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate the project's role-based performance score."""

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

    for metric in metrics_to_normalize:
        scored_df = add_normalized_metric_by_role(scored_df, metric)

    scored_df["raw_performance_score"] = 0.0

    # Goalkeeper score: save percentage + clean sheets - goals against.
    goalkeeper_mask = scored_df["role_group"] == "Goalkeeper"
    scored_df.loc[goalkeeper_mask, "raw_performance_score"] = (
        scored_df.loc[goalkeeper_mask, "normalized_save_percentage"]
        + scored_df.loc[goalkeeper_mask, "normalized_clean_sheets_per_90"]
        - scored_df.loc[goalkeeper_mask, "normalized_goals_against_per_90"]
    )

    # Defender score: tackles + interceptions + clearances + blocks.
    defender_mask = scored_df["role_group"] == "Defender"
    scored_df.loc[defender_mask, "raw_performance_score"] = (
        scored_df.loc[defender_mask, "normalized_tackles_per_90"]
        + scored_df.loc[defender_mask, "normalized_interceptions_per_90"]
        + scored_df.loc[defender_mask, "normalized_clearances_per_90"]
        + scored_df.loc[defender_mask, "normalized_blocks_per_90"]
    )

    # DefMidWingBack score: defensive actions + assists.
    def_mid_wing_back_mask = scored_df["role_group"] == "DefMidWingBack"
    scored_df.loc[def_mid_wing_back_mask, "raw_performance_score"] = (
        scored_df.loc[def_mid_wing_back_mask, "normalized_tackles_per_90"]
        + scored_df.loc[def_mid_wing_back_mask, "normalized_interceptions_per_90"]
        + scored_df.loc[def_mid_wing_back_mask, "normalized_clearances_per_90"]
        + scored_df.loc[def_mid_wing_back_mask, "normalized_assists_per_90"]
    )

    # Midfielder score: defensive actions + goals + assists.
    midfielder_mask = scored_df["role_group"] == "Midfielder"
    scored_df.loc[midfielder_mask, "raw_performance_score"] = (
        scored_df.loc[midfielder_mask, "normalized_tackles_per_90"]
        + scored_df.loc[midfielder_mask, "normalized_interceptions_per_90"]
        + scored_df.loc[midfielder_mask, "normalized_goals_per_90"]
        + scored_df.loc[midfielder_mask, "normalized_assists_per_90"]
    )

    # AttMidWinger score: goals + assists + tackles.
    att_mid_winger_mask = scored_df["role_group"] == "AttMidWinger"
    scored_df.loc[att_mid_winger_mask, "raw_performance_score"] = (
        scored_df.loc[att_mid_winger_mask, "normalized_goals_per_90"]
        + scored_df.loc[att_mid_winger_mask, "normalized_assists_per_90"]
        + scored_df.loc[att_mid_winger_mask, "normalized_tackles_per_90"]
    )

    # Forward score: goals + assists.
    forward_mask = scored_df["role_group"] == "Forward"
    scored_df.loc[forward_mask, "raw_performance_score"] = (
        scored_df.loc[forward_mask, "normalized_goals_per_90"]
        + scored_df.loc[forward_mask, "normalized_assists_per_90"]
    )

    # WingBack score: defensive and attacking contribution.
    wing_back_mask = scored_df["role_group"] == "WingBack"
    scored_df.loc[wing_back_mask, "raw_performance_score"] = (
        scored_df.loc[wing_back_mask, "normalized_tackles_per_90"]
        + scored_df.loc[wing_back_mask, "normalized_interceptions_per_90"]
        + scored_df.loc[wing_back_mask, "normalized_assists_per_90"]
        + scored_df.loc[wing_back_mask, "normalized_goals_per_90"]
    )

    scored_df["performance_score"] = 0.0

    for role_group in scored_df["role_group"].unique():
        role_mask = scored_df["role_group"] == role_group
        role_players = scored_df.loc[role_mask]

        scored_df.loc[role_mask, "performance_score"] = normalize_column(
            role_players,
            "raw_performance_score",
        )

    scored_df["performance_percentile"] = (
        scored_df.groupby("role_group")["performance_score"]
        .rank(pct=True)
        .mul(100)
        .round(2)
    )

    # The 40th-50th percentile remains Average between Poor and Promising.
    scored_df["performance_level"] = "Average"

    scored_df.loc[scored_df["performance_percentile"] >= 60, "performance_level"] = (
        "Good"
    )

    scored_df.loc[
        (scored_df["performance_percentile"] >= 50)
        & (scored_df["performance_percentile"] < 60),
        "performance_level",
    ] = "Promising"

    scored_df.loc[scored_df["performance_percentile"] < 40, "performance_level"] = (
        "Poor"
    )

    return scored_df


def main() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)
    scored_df = add_role_scores(df)

    output_path = PROCESSED_DATA_DIR / "player_scores.csv"
    scored_df.to_csv(output_path, index=False)

    score_summary = (
        scored_df.groupby("role_group")["performance_score"]
        .agg(["count", "min", "mean", "max"])
        .reset_index()
    )
    score_summary.to_csv(
        RESULTS_DIR / "performance_score_summary.csv",
        index=False,
    )

    level_counts = (
        scored_df.groupby(["role_group", "performance_level"])
        .size()
        .reset_index(name="count")
    )
    level_counts.to_csv(
        RESULTS_DIR / "performance_level_counts.csv",
        index=False,
    )

    print("Performance scoring completed")
    print("-----------------------------")
    print(f"Players scored: {scored_df.shape[0]}")
    print(f"Saved file: {output_path}")
    print()

    print("Score summary by role group:")
    print(score_summary)
    print()

    print("Performance level counts:")
    print(level_counts)


if __name__ == "__main__":
    main()
