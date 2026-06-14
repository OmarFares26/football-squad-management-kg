from pathlib import Path

import networkx as nx
import pandas as pd


# Input file from the rule engine step.
INPUT_PATH = Path("data/processed/player_decisions.csv")

# Output folders.
GRAPHS_DIR = Path("outputs/graphs")
RESULTS_DIR = Path("outputs/results")


def add_node_if_missing(
    graph: nx.DiGraph,
    node_id: str,
    node_type: str,
    **attributes,
) -> None:
    """
    Add a node to the graph if it does not already exist.
    """

    if not graph.has_node(node_id):
        graph.add_node(
            node_id,
            node_type=node_type,
            **attributes,
        )


def add_player_nodes(graph: nx.DiGraph, df: pd.DataFrame) -> None:
    """
    Add player nodes and their direct/inferred attributes.

    The player node stores both original data and inferred reasoning context,
    such as same-role competition information.
    """

    for _, row in df.iterrows():
        graph.add_node(
            row["player_id"],
            node_type="Player",
            player_name=row["player_name"],
            raw_position=row["raw_position"],
            role_group=row["role_group"],
            age=row["age"],
            age_group=row["age_group"],
            minutes_played=row["minutes_played"],
            minutes_group=row["minutes_group"],
            performance_score=row["performance_score"],
            performance_percentile=row["performance_percentile"],
            performance_level=row["performance_level"],
            same_role_team_average=row["same_role_team_average"],
            competition_status=row["competition_status"],
            main_same_role_player=row["main_same_role_player"],
            main_same_role_minutes=row["main_same_role_minutes"],
            main_same_role_performance_percentile=row[
                "main_same_role_performance_percentile"
            ],
            main_same_role_performance_level=row[
                "main_same_role_performance_level"
            ],
            is_main_same_role_player=bool(row["is_main_same_role_player"]),
            is_blocked_by_main_player=bool(row["is_blocked_by_main_player"]),
            main_player_underperforming=bool(row["main_player_underperforming"]),
            decision=row["decision"],
            explanation=row["explanation"],
        )


def add_context_nodes_and_edges(graph: nx.DiGraph, df: pd.DataFrame) -> None:
    """
    Add context nodes and connect players to them.

    These nodes represent the main KG concepts:
    Team, League, RoleGroup, AgeGroup, MinutesGroup,
    PerformanceLevel, CompetitionStatus, and SquadDecision.
    """

    for _, row in df.iterrows():
        player_id = row["player_id"]

        team_id = f"team::{row['team_id']}"
        league_id = f"league::{row['league_name']}"
        role_id = f"role::{row['role_group']}"
        age_group_id = f"age_group::{row['age_group']}"
        minutes_group_id = f"minutes_group::{row['minutes_group']}"
        performance_level_id = f"performance_level::{row['performance_level']}"
        competition_status_id = f"competition_status::{row['competition_status']}"
        decision_id = f"decision::{row['decision']}"

        add_node_if_missing(
            graph,
            team_id,
            "Team",
            team_name=row["team_name"],
        )

        add_node_if_missing(
            graph,
            league_id,
            "League",
            league_name=row["league_name"],
        )

        add_node_if_missing(
            graph,
            role_id,
            "RoleGroup",
            role_group=row["role_group"],
        )

        add_node_if_missing(
            graph,
            age_group_id,
            "AgeGroup",
            age_group=row["age_group"],
        )

        add_node_if_missing(
            graph,
            minutes_group_id,
            "MinutesGroup",
            minutes_group=row["minutes_group"],
        )

        add_node_if_missing(
            graph,
            performance_level_id,
            "PerformanceLevel",
            performance_level=row["performance_level"],
        )

        add_node_if_missing(
            graph,
            competition_status_id,
            "CompetitionStatus",
            competition_status=row["competition_status"],
        )

        add_node_if_missing(
            graph,
            decision_id,
            "SquadDecision",
            decision=row["decision"],
        )

        # Player context edges.
        graph.add_edge(player_id, team_id, relationship="PLAYS_FOR")
        graph.add_edge(player_id, league_id, relationship="PLAYS_IN")
        graph.add_edge(player_id, role_id, relationship="HAS_ROLE")
        graph.add_edge(player_id, age_group_id, relationship="HAS_AGE_GROUP")
        graph.add_edge(player_id, minutes_group_id, relationship="HAS_MINUTES_GROUP")
        graph.add_edge(
            player_id,
            performance_level_id,
            relationship="HAS_PERFORMANCE_LEVEL",
        )
        graph.add_edge(
            player_id,
            competition_status_id,
            relationship="HAS_COMPETITION_STATUS",
        )
        graph.add_edge(player_id, decision_id, relationship="HAS_DECISION")

        # Team context edge.
        graph.add_edge(team_id, league_id, relationship="PLAYS_IN")


def add_competition_edges(graph: nx.DiGraph, df: pd.DataFrame) -> None:
    """
    Add COMPETES_WITH edges between players in the same team and role group.

    Because the graph is directed, competition is added in both directions.
    """

    grouped_players = df.groupby(["team_name", "role_group"])

    for _, group in grouped_players:
        player_ids = group["player_id"].tolist()

        for index, player_id in enumerate(player_ids):
            for other_player_id in player_ids[index + 1:]:
                graph.add_edge(
                    player_id,
                    other_player_id,
                    relationship="COMPETES_WITH",
                )
                graph.add_edge(
                    other_player_id,
                    player_id,
                    relationship="COMPETES_WITH",
                )


def add_main_player_edges(graph: nx.DiGraph, df: pd.DataFrame) -> None:
    """
    Add BLOCKED_BY_MAIN_PLAYER edges.

    These edges make the same-role competition reasoning explicit in the KG.
    """

    for _, row in df.iterrows():
        if not bool(row["is_blocked_by_main_player"]):
            continue

        player_id = row["player_id"]
        team_name = row["team_name"]
        role_group = row["role_group"]
        main_player_name = row["main_same_role_player"]

        main_player_rows = df[
            (df["team_name"] == team_name)
            & (df["role_group"] == role_group)
            & (df["player_name"] == main_player_name)
        ]

        if main_player_rows.empty:
            continue

        main_player_id = main_player_rows.iloc[0]["player_id"]

        graph.add_edge(
            player_id,
            main_player_id,
            relationship="BLOCKED_BY_MAIN_PLAYER",
        )


def save_graph_statistics(graph: nx.DiGraph) -> None:
    """
    Save simple graph statistics for the portfolio.
    """

    node_counts = pd.Series(
        nx.get_node_attributes(graph, "node_type")
    ).value_counts().reset_index()

    node_counts.columns = ["node_type", "count"]
    node_counts.to_csv(RESULTS_DIR / "kg_node_counts.csv", index=False)

    edge_types = [
        edge_data["relationship"]
        for _, _, edge_data in graph.edges(data=True)
    ]

    edge_counts = pd.Series(edge_types).value_counts().reset_index()
    edge_counts.columns = ["relationship", "count"]
    edge_counts.to_csv(RESULTS_DIR / "kg_edge_counts.csv", index=False)

    kg_stats = pd.DataFrame(
        [
            {
                "number_of_nodes": graph.number_of_nodes(),
                "number_of_edges": graph.number_of_edges(),
                "number_of_node_types": node_counts.shape[0],
                "number_of_relationship_types": edge_counts.shape[0],
            }
        ]
    )

    kg_stats.to_csv(RESULTS_DIR / "kg_stats.csv", index=False)

    print("Knowledge Graph statistics")
    print("--------------------------")
    print(kg_stats.to_string(index=False))
    print()

    print("Node counts:")
    print(node_counts)
    print()

    print("Edge counts:")
    print(edge_counts)


def main() -> None:
    # Create output folders if they do not exist.
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load player decision data.
    df = pd.read_csv(INPUT_PATH)

    # Create a directed graph.
    # This is more semantically correct for a Knowledge Graph.
    graph = nx.DiGraph()

    # Build the graph.
    add_player_nodes(graph, df)
    add_context_nodes_and_edges(graph, df)
    add_competition_edges(graph, df)
    add_main_player_edges(graph, df)

    # Save the graph.
    graph_path = GRAPHS_DIR / "squad_management_kg.graphml"
    nx.write_graphml(graph, graph_path)

    # Save graph statistics.
    save_graph_statistics(graph)

    print()
    print("Knowledge Graph creation completed")
    print("----------------------------------")
    print(f"Saved graph: {graph_path}")


if __name__ == "__main__":
    main()