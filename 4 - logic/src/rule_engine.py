from pathlib import Path

import pandas as pd


INPUT_PATH = Path("2 - construction/data/processed/player_scores.csv")
PROCESSED_DATA_DIR = Path("4 - logic/results")
RESULTS_DIR = Path("4 - logic/results")


def get_age_group(age: float) -> str:
    """Map age to a decision-friendly age group."""

    if pd.isna(age):
        return "UnknownAge"

    if age < 23:
        return "Young"

    if age <= 29:
        return "Prime"

    if age <= 32:
        return "Senior"

    return "CriticalAge"


def get_minutes_group(minutes_played: float) -> str:
    """Map minutes played to a usage group."""

    if minutes_played < 900:
        return "LowMinutes"

    if minutes_played <= 1800:
        return "MediumMinutes"

    return "HighMinutes"


def get_competition_status(
    performance_score: float,
    same_role_team_average: float,
) -> str:
    """Compare a player with the same-team, same-role average."""

    if performance_score >= same_role_team_average:
        return "Competitive"

    return "Blocked"


def add_same_role_competition_context(df: pd.DataFrame) -> pd.DataFrame:
    """Add the main-player and blocking context used by the rules."""

    df = df.copy()

    df["main_same_role_player"] = ""
    df["main_same_role_minutes"] = 0.0
    df["main_same_role_performance_percentile"] = 0.0
    df["main_same_role_performance_level"] = ""
    df["is_main_same_role_player"] = False
    df["is_blocked_by_main_player"] = False
    df["main_player_underperforming"] = False

    grouped_players = df.groupby(["team_name", "role_group"])

    for _, group in grouped_players:
        main_player = group.sort_values(
            by=["minutes_played", "performance_score", "player_id"],
            ascending=[False, False, True],
        ).iloc[0]
        group_index = group.index

        df.loc[group_index, "main_same_role_player"] = main_player["player_name"]
        df.loc[group_index, "main_same_role_minutes"] = main_player["minutes_played"]
        df.loc[group_index, "main_same_role_performance_percentile"] = main_player[
            "performance_percentile"
        ]
        df.loc[group_index, "main_same_role_performance_level"] = main_player[
            "performance_level"
        ]

        df.loc[group_index, "is_main_same_role_player"] = (
            df.loc[group_index, "player_name"] == main_player["player_name"]
        )

        df.loc[group_index, "is_blocked_by_main_player"] = (
            (df.loc[group_index, "player_name"] != main_player["player_name"])
            & (df.loc[group_index, "minutes_played"] < main_player["minutes_played"])
            & (
                df.loc[group_index, "performance_score"]
                < main_player["performance_score"]
            )
        )

        df.loc[group_index, "main_player_underperforming"] = (
            main_player["performance_percentile"] < 40
        )

    return df


def decide_player(row: pd.Series) -> tuple[str, str]:
    """
    Apply squad decision rules in priority order.

    Rule priority:
    1. Keep regular contributor
    2. Sell veteran underperformer
    3. Give More Chances because main same-role player is underperforming
    4. Give More Chances because player is competitive
    5. Loan because young player is blocked
    6. Sell low-used older player
    7. Monitor
    """

    age = row["age"]
    minutes = row["minutes_played"]
    score = row["performance_score"]
    percentile = row["performance_percentile"]
    same_role_average = row["same_role_team_average"]

    is_main_same_role_player = row["is_main_same_role_player"]
    is_blocked_by_main_player = row["is_blocked_by_main_player"]
    main_player_underperforming = row["main_player_underperforming"]
    has_known_age = not pd.isna(age)

    # Keep regular contributors regardless of age.
    if minutes > 1800 and percentile >= 50:
        return (
            "Keep",
            "High minutes and at least promising role-based performance.",
        )

    # Sell older regulars with poor role-based performance.
    if has_known_age and minutes > 1800 and percentile < 40 and age > 29:
        return (
            "Sell",
            "High minutes, poor role-based performance, and older than 29.",
        )

    # Promote a strong backup when the main player is underperforming.
    if (
        not is_main_same_role_player
        and minutes < 1800
        and percentile >= 50
        and main_player_underperforming
    ):
        return (
            "Give More Chances",
            "Low or medium minutes, promising or good performance, and the main same-role player is underperforming.",
        )

    # Promote an underused player who compares well with role peers.
    if minutes < 1800 and percentile >= 50 and score >= same_role_average:
        return (
            "Give More Chances",
            "Under 1800 minutes, promising or good performance, and at or above the same-team role-group average.",
        )

    # Loan young, low-minute players blocked by the main player.
    if (
        has_known_age
        and age < 23
        and minutes < 900
        and is_blocked_by_main_player
    ):
        return (
            "Loan",
            "Young player with low minutes and blocked by the main same-role player.",
        )

    # Sell older, low-minute players with poor performance.
    if has_known_age and minutes < 900 and percentile < 40 and age > 29:
        return (
            "Sell",
            "Low minutes, poor role-based performance, and older than 29.",
        )

    # Monitor is the fallback when no stronger rule applies.
    return (
        "Monitor",
        "No strong keep, loan, sell, or give-more-chances rule was triggered.",
    )


def main() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_PATH)

    df["age_group"] = df["age"].apply(get_age_group)
    df["minutes_group"] = df["minutes_played"].apply(get_minutes_group)

    df["same_role_team_average"] = df.groupby(
        ["team_name", "role_group"]
    )["performance_score"].transform("mean")

    df["competition_status"] = df.apply(
        lambda row: get_competition_status(
            row["performance_score"],
            row["same_role_team_average"],
        ),
        axis=1,
    )

    df = add_same_role_competition_context(df)

    decisions = df.apply(decide_player, axis=1)

    df["decision"] = decisions.apply(lambda result: result[0])
    df["decision_reason"] = decisions.apply(lambda result: result[1])

    df["explanation"] = (
        df["player_name"]
        + " is classified as "
        + df["decision"]
        + " because: "
        + df["decision_reason"]
    )

    output_path = PROCESSED_DATA_DIR / "player_decisions.csv"
    df.to_csv(output_path, index=False)

    decision_counts = df["decision"].value_counts().reset_index()
    decision_counts.to_csv(RESULTS_DIR / "decision_counts.csv", index=False)

    decision_by_role = (
        df.groupby(["role_group", "decision"])
        .size()
        .reset_index(name="count")
    )
    decision_by_role.to_csv(RESULTS_DIR / "decision_by_role.csv", index=False)

    final_columns = [
        "player_name",
        "team_name",
        "raw_position",
        "role_group",
        "age",
        "age_group",
        "minutes_played",
        "minutes_group",
        "performance_score",
        "performance_percentile",
        "performance_level",
        "same_role_team_average",
        "competition_status",
        "main_same_role_player",
        "main_same_role_minutes",
        "main_same_role_performance_percentile",
        "main_same_role_performance_level",
        "is_main_same_role_player",
        "is_blocked_by_main_player",
        "main_player_underperforming",
        "decision",
        "explanation",
    ]

    final_table = df[final_columns].copy()
    final_table.to_csv(RESULTS_DIR / "squad_decisions_all_players.csv", index=False)

    print("Rule engine completed")
    print("---------------------")
    print(f"Players processed: {df.shape[0]}")
    print(f"Saved file: {output_path}")
    print()

    print("Decision counts:")
    print(decision_counts)
    print()

    print("Decision counts by role group:")
    print(decision_by_role)


if __name__ == "__main__":
    main()
