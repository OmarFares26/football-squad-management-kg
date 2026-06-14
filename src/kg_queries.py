from pathlib import Path

import networkx as nx
import pandas as pd


# Input graph from KG builder.
GRAPH_PATH = Path("outputs/graphs/squad_management_kg.graphml")

# Output folder for query results.
RESULTS_DIR = Path("outputs/results")


def get_neighbors_by_relationship(
    graph: nx.DiGraph,
    node_id: str,
    relationship: str,
) -> list[str]:
    """
    Return all outgoing neighbors connected by a specific relationship.
    """

    neighbors = []

    for _, target, edge_data in graph.out_edges(node_id, data=True):
        if edge_data.get("relationship") == relationship:
            neighbors.append(target)

    return neighbors


def convert_numeric_node_attributes(graph: nx.DiGraph) -> None:
    """
    Convert numeric node attributes back to float after loading GraphML.

    GraphML stores attributes as strings, so we convert the important
    numeric attributes again for cleaner query outputs.
    """

    numeric_attributes = [
        "age",
        "minutes_played",
        "performance_score",
        "performance_percentile",
    ]

    for node_id, node_data in graph.nodes(data=True):
        for attribute in numeric_attributes:
            if attribute not in node_data:
                continue

            try:
                graph.nodes[node_id][attribute] = float(node_data[attribute])
            except (ValueError, TypeError):
                pass


def get_node_label(graph: nx.DiGraph, node_id: str) -> str:
    """
    Return a readable label for a node.
    """

    node_data = graph.nodes[node_id]
    node_type = node_data.get("node_type")

    if node_type == "Player":
        return node_data.get("player_name", node_id)

    if node_type == "Team":
        return node_data.get("team_name", node_id)

    if node_type == "RoleGroup":
        return node_data.get("role_group", node_id)

    if node_type == "SquadDecision":
        return node_data.get("decision", node_id)

    if node_type == "PerformanceLevel":
        return node_data.get("performance_level", node_id)

    return node_id


def query_players_by_decision(graph: nx.DiGraph, decision: str) -> pd.DataFrame:
    """
    Find all players with a specific squad decision.
    """

    decision_node = f"decision::{decision}"
    rows = []

    for player_id, target, edge_data in graph.edges(data=True):
        if (
            target == decision_node
            and edge_data.get("relationship") == "HAS_DECISION"
        ):
            player_data = graph.nodes[player_id]

            team_nodes = get_neighbors_by_relationship(
                graph,
                player_id,
                "PLAYS_FOR",
            )

            rows.append(
                {
                    "player_name": player_data.get("player_name"),
                    "team_name": get_node_label(graph, team_nodes[0]),
                    "role_group": player_data.get("role_group"),
                    "age": player_data.get("age"),
                    "minutes_played": player_data.get("minutes_played"),
                    "performance_percentile": player_data.get(
                        "performance_percentile"
                    ),
                    "decision": decision,
                }
            )

    return pd.DataFrame(rows).sort_values(
        by=["team_name", "role_group", "player_name"]
    )


def query_team_decisions(graph: nx.DiGraph, team_name: str) -> pd.DataFrame:
    """
    Find all squad decisions for one team.
    """

    rows = []

    for node_id, node_data in graph.nodes(data=True):
        if node_data.get("node_type") != "Player":
            continue

        team_nodes = get_neighbors_by_relationship(
            graph,
            node_id,
            "PLAYS_FOR",
        )

        if not team_nodes:
            continue

        player_team_name = get_node_label(graph, team_nodes[0])

        if player_team_name != team_name:
            continue

        decision_nodes = get_neighbors_by_relationship(
            graph,
            node_id,
            "HAS_DECISION",
        )

        performance_nodes = get_neighbors_by_relationship(
            graph,
            node_id,
            "HAS_PERFORMANCE_LEVEL",
        )

        rows.append(
            {
                "player_name": node_data.get("player_name"),
                "team_name": player_team_name,
                "role_group": node_data.get("role_group"),
                "age": node_data.get("age"),
                "minutes_played": node_data.get("minutes_played"),
                "performance_percentile": node_data.get(
                    "performance_percentile"
                ),
                "performance_level": get_node_label(graph, performance_nodes[0]),
                "decision": get_node_label(graph, decision_nodes[0]),
            }
        )

    return pd.DataFrame(rows).sort_values(
        by=["decision", "role_group", "player_name"]
    )


def query_competitors_for_player(
    graph: nx.DiGraph,
    player_name: str,
) -> pd.DataFrame:
    """
    Find same-team, same-role competitors for one player.
    """

    matching_player_ids = [
        node_id
        for node_id, node_data in graph.nodes(data=True)
        if node_data.get("node_type") == "Player"
        and node_data.get("player_name") == player_name
    ]

    if not matching_player_ids:
        return pd.DataFrame()

    player_id = matching_player_ids[0]
    player_data = graph.nodes[player_id]

    competitor_ids = get_neighbors_by_relationship(
        graph,
        player_id,
        "COMPETES_WITH",
    )

    rows = []

    for competitor_id in competitor_ids:
        competitor_data = graph.nodes[competitor_id]

        team_nodes = get_neighbors_by_relationship(
            graph,
            competitor_id,
            "PLAYS_FOR",
        )

        decision_nodes = get_neighbors_by_relationship(
            graph,
            competitor_id,
            "HAS_DECISION",
        )

        rows.append(
            {
                "player_name": competitor_data.get("player_name"),
                "team_name": get_node_label(graph, team_nodes[0]),
                "role_group": competitor_data.get("role_group"),
                "minutes_played": competitor_data.get("minutes_played"),
                "performance_percentile": competitor_data.get(
                    "performance_percentile"
                ),
                "decision": get_node_label(graph, decision_nodes[0]),
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    print(f"Competitors for {player_data.get('player_name')}")
    print(f"Role group: {player_data.get('role_group')}")
    print()

    return result.sort_values(
        by=["performance_percentile"],
        ascending=False,
    )


def main() -> None:
    # Create output folder if it does not exist.
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load the graph.
    graph = nx.read_graphml(GRAPH_PATH)

    # Convert numeric attributes back after GraphML loading.
    convert_numeric_node_attributes(graph)

    print("KG query examples")
    print("-----------------")
    print(f"Loaded graph: {GRAPH_PATH}")
    print()

    # Query 1: all players marked as Sell.
    sell_players = query_players_by_decision(graph, "Sell")
    sell_players.to_csv(RESULTS_DIR / "query_sell_players.csv", index=False)

    print("Query 1: Players marked as Sell")
    print(sell_players.head(10).to_string(index=False))
    print()

    # Query 2: squad decisions for Liverpool.
    team_name = "Liverpool"
    team_decisions = query_team_decisions(graph, team_name)
    team_decisions.to_csv(
        RESULTS_DIR / "query_liverpool_decisions.csv",
        index=False,
    )

    print(f"Query 2: Squad decisions for {team_name}")
    print(team_decisions.to_string(index=False))
    print()

    # Query 3: competitors for Mohamed Salah.
    player_name = "Mohamed Salah"
    competitors = query_competitors_for_player(graph, player_name)
    competitors.to_csv(
        RESULTS_DIR / "query_mohamed_salah_competitors.csv",
        index=False,
    )

    print(f"Query 3: Same-role competitors for {player_name}")
    print(competitors.to_string(index=False))
    print()

    print("Saved query outputs:")
    print(RESULTS_DIR / "query_sell_players.csv")
    print(RESULTS_DIR / "query_liverpool_decisions.csv")
    print(RESULTS_DIR / "query_mohamed_salah_competitors.csv")


if __name__ == "__main__":
    main()