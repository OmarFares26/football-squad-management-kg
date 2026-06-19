from pathlib import Path

import networkx as nx
import pandas as pd


# Input Knowledge Graph from the KG construction step.
GRAPH_PATH = Path("outputs/graphs/squad_management_kg.graphml")

# Output folder for service-style results.
RESULTS_DIR = Path("outputs/results")

# Team used for the final service output.
SELECTED_TEAM = "Liverpool"


SERVICE_COLUMNS = [
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


def get_related_value(
    graph: nx.MultiDiGraph,
    node_id: str,
    relationship: str,
    attribute: str,
):
    """
    Return an attribute from a node reached through a KG relationship.
    """

    for _, target, edge_data in graph.out_edges(node_id, data=True):
        if edge_data.get("relationship") == relationship:
            return graph.nodes[target].get(attribute)

    return None


def create_service_table(
    graph: nx.MultiDiGraph,
    team_name: str,
) -> pd.DataFrame:
    """
    Create a clean squad decision table for one team.

    This table represents a simple service output:
    a user selects a team and receives squad-management recommendations.
    """

    rows = []

    for player_id, player_data in graph.nodes(data=True):
        if player_data.get("node_type") != "Player":
            continue

        player_team_name = get_related_value(
            graph,
            player_id,
            "PLAYS_FOR",
            "team_name",
        )

        if player_team_name != team_name:
            continue

        rows.append(
            {
                "player_name": player_data.get("player_name"),
                "team_name": player_team_name,
                "raw_position": player_data.get("raw_position"),
                "role_group": get_related_value(
                    graph,
                    player_id,
                    "HAS_ROLE",
                    "role_group",
                ),
                "age": player_data.get("age"),
                "age_group": get_related_value(
                    graph,
                    player_id,
                    "HAS_AGE_GROUP",
                    "age_group",
                ),
                "minutes_played": player_data.get("minutes_played"),
                "minutes_group": get_related_value(
                    graph,
                    player_id,
                    "HAS_MINUTES_GROUP",
                    "minutes_group",
                ),
                "performance_level": get_related_value(
                    graph,
                    player_id,
                    "HAS_PERFORMANCE_LEVEL",
                    "performance_level",
                ),
                "performance_percentile": player_data.get(
                    "performance_percentile"
                ),
                "competition_status": get_related_value(
                    graph,
                    player_id,
                    "HAS_COMPETITION_STATUS",
                    "competition_status",
                ),
                "main_same_role_player": player_data.get(
                    "main_same_role_player"
                ),
                "main_same_role_minutes": player_data.get(
                    "main_same_role_minutes"
                ),
                "main_same_role_performance_percentile": player_data.get(
                    "main_same_role_performance_percentile"
                ),
                "main_same_role_performance_level": player_data.get(
                    "main_same_role_performance_level"
                ),
                "is_main_same_role_player": player_data.get(
                    "is_main_same_role_player"
                ),
                "is_blocked_by_main_player": player_data.get(
                    "is_blocked_by_main_player"
                ),
                "main_player_underperforming": player_data.get(
                    "main_player_underperforming"
                ),
                "decision": get_related_value(
                    graph,
                    player_id,
                    "HAS_DECISION",
                    "decision",
                ),
                "explanation": player_data.get("explanation"),
            }
        )

    service_table = pd.DataFrame(rows, columns=SERVICE_COLUMNS)

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

    # Load the Knowledge Graph.
    graph = nx.read_graphml(GRAPH_PATH)

    # Query the KG to create the final service output for the selected team.
    service_table = create_service_table(graph, SELECTED_TEAM)

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
