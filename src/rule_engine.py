from pathlib import Path

import pandas as pd


# Input file from the performance scoring step.
INPUT_PATH = Path("data/processed/player_scores.csv")

# Output folder for processed data.
PROCESSED_DATA_DIR = Path("data/processed")

# Output folder for result summaries.
RESULTS_DIR = Path("outputs/results")


def get_age_group(age: float) -> str:
    """
    Convert age into a simple age group.

    These groups are used for explaining squad decisions.
    """

    if age < 23:
        return "Young"

    if age <= 29:
        return "Prime"

    if age <= 32:
        return "Senior"

    return "CriticalAge"


def get_minutes_group(minutes_played: float) -> str:
    """
    Convert minutes played into a simple minutes group.

    This helps explain if a player was heavily used,
    partly used, or barely used.
    """

    if minutes_played < 900:
        return "LowMinutes"

    if minutes_played <= 1800:
        return "MediumMinutes"

    return "HighMinutes"


def get_competition_status(
    performance_score: float,
    same_role_team_average: float,
) -> str:
    """
    Compare a player against teammates in the same role group.

    This gives the decision context inside the squad.
    """

    if performance_score >= same_role_team_average:
        return "Competitive"

    return "Blocked"


def decide_player(row: pd.Series) -> tuple[str, str]:
    """
    Apply squad decision rules in priority order.

    Rule priority:
    1. Keep regular contributor
    2. Sell veteran underperformer
    3. Give More Chances
    4. Loan
    5. Sell low-used older player
    6. Monitor

    Age is not a condition for Keep.
    A player with high minutes and at least promising performance
    is kept regardless of age.

    Age matters in Sell rules, where poor performance and older age
    together justify selling.
    """

    age = row["age"]
    minutes = row["minutes_played"]
    score = row["performance_score"]
    percentile = row["performance_percentile"]
    same_role_average = row["same_role_team_average"]

    # Keep:
    # Regular player with at least promising role-based performance.
    # Age is not a factor here because high usage and solid performance
    # usually means the player is still important for the squad.
    if minutes > 1800 and percentile >= 50:
        return (
            "Keep",
            "High minutes and at least promising role-based performance.",
        )

    # Sell veteran underperformer:
    # Older player with regular minutes but poor role-based performance.
    # This closes the gap where older high-minute underperformers
    # would otherwise only be monitored.
    if minutes > 1800 and percentile < 40 and age > 29:
        return (
            "Sell",
            "Regular minutes, poor role-based performance, and older than 29.",
        )

    # Give More Chances:
    # Underused player who performs well compared with same-role teammates.
    # This player deserves more game time based on their per-90 contribution.
    if minutes < 1800 and percentile >= 50 and score >= same_role_average:
        return (
            "Give More Chances",
            "Under 1800 minutes, promising or good performance, and competitive within the same role group.",
        )

    # Loan:
    # Young player with low minutes who is blocked by same-role teammates.
    # A loan gives the player regular game time for development,
    # even if current performance is not yet strong.
    if age < 23 and minutes < 900 and score < same_role_average:
        return (
            "Loan",
            "Young player with low minutes and blocked by same-role teammates.",
        )

    # Sell low-used older player:
    # Older player with low minutes and poor role-based performance.
    # This player has limited future value for the squad.
    if minutes < 900 and percentile < 40 and age > 29:
        return (
            "Sell",
            "Low minutes, poor role-based performance, and older than 29.",
        )

    # Monitor:
    # Default decision when no stronger rule applies.
    # This player does not clearly fit Keep, Sell, Loan, or Give More Chances.
    return (
        "Monitor",
        "No strong keep, loan, sell, or give-more-chances rule was triggered.",
    )


def main() -> None:
    # Create output folders if they do not exist.
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load scored player data.
    df = pd.read_csv(INPUT_PATH)

    # Add age groups.
    df["age_group"] = df["age"].apply(get_age_group)

    # Add minutes groups.
    df["minutes_group"] = df["minutes_played"].apply(get_minutes_group)

    # Calculate same-team, same-role average performance.
    df["same_role_team_average"] = df.groupby(
        ["team_name", "role_group"]
    )["performance_score"].transform("mean")

    # Add competition status based on same-role teammates.
    df["competition_status"] = df.apply(
        lambda row: get_competition_status(
            row["performance_score"],
            row["same_role_team_average"],
        ),
        axis=1,
    )

    # Apply decision rules.
    decisions = df.apply(decide_player, axis=1)

    # Split decision result into two columns.
    df["decision"] = decisions.apply(lambda result: result[0])
    df["decision_reason"] = decisions.apply(lambda result: result[1])

    # Create a readable explanation for the final output.
    df["explanation"] = (
        df["player_name"]
        + " is classified as "
        + df["decision"]
        + " because: "
        + df["decision_reason"]
    )

    # Save the full decision dataset.
    output_path = PROCESSED_DATA_DIR / "player_decisions.csv"
    df.to_csv(output_path, index=False)

    # Save decision counts for the report.
    decision_counts = df["decision"].value_counts().reset_index()
    decision_counts.to_csv(RESULTS_DIR / "decision_counts.csv", index=False)

    # Save decision counts by role group.
    decision_by_role = (
        df.groupby(["role_group", "decision"])
        .size()
        .reset_index(name="count")
    )
    decision_by_role.to_csv(RESULTS_DIR / "decision_by_role.csv", index=False)

    # Save a clean final table for the service output.
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
        "decision",
        "explanation",
    ]

    final_table = df[final_columns].copy()
    final_table.to_csv(RESULTS_DIR / "squad_decisions_all_players.csv", index=False)

    # Print a simple summary.
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