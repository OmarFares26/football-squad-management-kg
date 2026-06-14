from pathlib import Path

import pandas as pd


# Input file from the rule engine step.
INPUT_PATH = Path("data/processed/player_decisions.csv")

# Output folder for service-style results.
RESULTS_DIR = Path("outputs/results")

# Team used for the final service output.
SELECTED_TEAM = "Liverpool"


def create_service_table(df: pd.DataFrame, team_name: str) -> pd.DataFrame:
    """
    Create a clean squad decision table for one team.

    This table represents a simple service output:
    a user selects a team and receives squad-management recommendations.
    """

    team_df = df[df["team_name"] == team_name].copy()

    service_columns = [
        "player_name",
        "team_name",
        "raw_position",
        "role_group",
        "age",
        "age_group",
        "minutes_played",
        "minutes_group",
        "performance_level",
        "performance_percentile",
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

    service_table = team_df[service_columns].copy()

    # Sort output so the clearest action decisions are easy to inspect.
    # Monitor is placed last because it is the neutral fallback decision.
    decision_order = {
        "Keep": 1,
        "Give More Chances": 2,
        "Loan": 3,
        "Sell": 4,
        "Monitor": 5,
    }

    service_table["decision_order"] = service_table["decision"].map(decision_order)

    service_table = service_table.sort_values(
        by=["decision_order", "role_group", "performance_percentile"],
        ascending=[True, True, False],
    )

    service_table = service_table.drop(columns=["decision_order"])

    return service_table


def create_service_summary(service_table: pd.DataFrame) -> pd.DataFrame:
    """
    Create a small summary of the service output.
    """

    decision_summary = service_table["decision"].value_counts().reset_index()
    decision_summary.columns = ["decision", "count"]

    return decision_summary


def main() -> None:
    # Create output folder if it does not exist.
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load player decision data.
    df = pd.read_csv(INPUT_PATH)

    # Create final service output for the selected team.
    service_table = create_service_table(df, SELECTED_TEAM)

    # Create summary table.
    service_summary = create_service_summary(service_table)

    # Save outputs.
    service_output_path = RESULTS_DIR / "liverpool_squad_decision_service.csv"
    service_summary_path = RESULTS_DIR / "liverpool_squad_decision_summary.csv"

    service_table.to_csv(service_output_path, index=False)
    service_summary.to_csv(service_summary_path, index=False)

    # Print readable output.
    print("Squad decision service output")
    print("-----------------------------")
    print(f"Selected team: {SELECTED_TEAM}")
    print(f"Players in service output: {service_table.shape[0]}")
    print()

    print("Decision summary:")
    print(service_summary.to_string(index=False))
    print()

    print("Service table preview:")
    print(service_table.to_string(index=False))
    print()

    print("Saved outputs:")
    print(service_output_path)
    print(service_summary_path)


if __name__ == "__main__":
    main()