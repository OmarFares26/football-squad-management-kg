from pathlib import Path

import networkx as nx
import pandas as pd


GRAPH_PATH = Path("2 - construction/graphs/squad_management_kg.graphml")
EMBEDDING_GRAPH_PATH = Path(
    "3 - ML/graphs/squad_management_kg_with_embeddings.graphml"
)
REPLACEMENT_GRAPH_PATH = Path(
    "3 - ML/graphs/squad_management_kg_with_replacements.graphml"
)
RESULTS_DIR = Path("2 - construction/results")
TARGET_TEAM = "Liverpool"


def get_neighbors_by_relationship(
    graph: nx.MultiDiGraph,
    node_id: str,
    relationship: str,
) -> list[str]:
    """Return outgoing neighbors for one relationship type."""

    neighbors = []

    for _, target, edge_data in graph.out_edges(node_id, data=True):
        if edge_data.get("relationship") == relationship:
            neighbors.append(target)

    return neighbors


def convert_numeric_node_attributes(graph: nx.MultiDiGraph) -> None:
    """Restore numeric node attributes after loading GraphML."""

    numeric_attributes = [
        "age",
        "minutes_played",
        "performance_score",
        "performance_percentile",
        "same_role_team_average",
        "main_same_role_minutes",
        "main_same_role_performance_percentile",
    ]

    for node_id, node_data in graph.nodes(data=True):
        for attribute in numeric_attributes:
            if attribute not in node_data:
                continue

            try:
                graph.nodes[node_id][attribute] = float(node_data[attribute])
            except (ValueError, TypeError):
                pass


def get_node_label(graph: nx.MultiDiGraph, node_id: str) -> str:
    """Return the readable label for a node."""

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


def query_players_by_decision(
    graph: nx.MultiDiGraph,
    decision: str,
) -> pd.DataFrame:
    """Find players with a specific squad decision."""

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


def query_team_decisions(
    graph: nx.MultiDiGraph,
    team_name: str,
) -> pd.DataFrame:
    """Find all squad decisions for one team."""

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
    graph: nx.MultiDiGraph,
    player_name: str,
) -> pd.DataFrame:
    """Find a player's same-team, same-role competitors."""

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


def query_blocked_by_main_player(graph: nx.MultiDiGraph) -> pd.DataFrame:
    """Find players linked through BLOCKED_BY_MAIN_PLAYER."""

    rows = []

    for player_id, main_player_id, edge_data in graph.edges(data=True):
        if edge_data.get("relationship") != "BLOCKED_BY_MAIN_PLAYER":
            continue

        player_data = graph.nodes[player_id]
        main_player_data = graph.nodes[main_player_id]

        team_nodes = get_neighbors_by_relationship(
            graph,
            player_id,
            "PLAYS_FOR",
        )

        decision_nodes = get_neighbors_by_relationship(
            graph,
            player_id,
            "HAS_DECISION",
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
                "decision": get_node_label(graph, decision_nodes[0]),
                "blocked_by_player": main_player_data.get("player_name"),
                "blocked_by_minutes": main_player_data.get("minutes_played"),
                "blocked_by_performance_percentile": main_player_data.get(
                    "performance_percentile"
                ),
            }
        )

    return pd.DataFrame(rows).sort_values(
        by=["team_name", "role_group", "player_name"]
    )


def find_replacement_candidates(
    graph: nx.MultiDiGraph,
    player_id: str,
    max_hops: int = 2,
) -> list[tuple[str, int, str]]:
    """Traverse SIMILAR_TO edges to find suitable replacement candidates."""

    if player_id not in graph:
        return []

    decision = graph.nodes[player_id].get("decision")
    if decision not in ("Sell", "Loan"):
        return []

    visited = {player_id}
    frontier = {player_id}
    candidates = []

    for hop in range(1, max_hops + 1):
        next_frontier = set()

        for node_id in frontier:
            for _, neighbor_id, edge_data in graph.out_edges(
                node_id,
                data=True,
            ):
                if (
                    edge_data.get("relationship") != "SIMILAR_TO"
                    or neighbor_id in visited
                ):
                    continue

                visited.add(neighbor_id)
                next_frontier.add(neighbor_id)

                candidate_decision = graph.nodes[neighbor_id].get("decision")
                if candidate_decision in ("Keep", "Give More Chances"):
                    candidates.append(
                        (neighbor_id, hop, candidate_decision)
                    )

        frontier = next_frontier

        if not frontier:
            break

    return candidates


def find_team_players_by_decision(
    graph: nx.MultiDiGraph,
    team_name: str,
    decisions: tuple[str, ...] = ("Sell", "Loan"),
) -> pd.DataFrame:
    """Find a team's players through PLAYS_FOR and filter by decision."""

    team_ids = [
        node_id
        for node_id, node_data in graph.nodes(data=True)
        if node_data.get("node_type") == "Team"
        and node_data.get("team_name") == team_name
    ]

    rows = []

    for team_id in team_ids:
        for player_id, _, edge_data in graph.in_edges(team_id, data=True):
            player_data = graph.nodes[player_id]

            if (
                edge_data.get("relationship") != "PLAYS_FOR"
                or player_data.get("node_type") != "Player"
                or player_data.get("decision") not in decisions
            ):
                continue

            rows.append(
                {
                    "player_id": player_id,
                    "player_name": player_data.get("player_name"),
                    "decision": player_data.get("decision"),
                }
            )

    return pd.DataFrame(
        rows,
        columns=["player_id", "player_name", "decision"],
    ).sort_values(by=["decision", "player_name"])


def add_replacement_edges(
    graph: nx.MultiDiGraph,
    players_df: pd.DataFrame,
    max_hops: int = 2,
) -> pd.DataFrame:
    """Add RECOMMENDED_REPLACEMENT edges and return their output rows."""

    rows = []
    eligible_players = players_df[
        players_df["decision"].isin(["Sell", "Loan"])
    ]

    for _, player in eligible_players.iterrows():
        player_id = player["player_id"]

        for candidate_id, hops, candidate_decision in (
            find_replacement_candidates(graph, player_id, max_hops)
        ):
            graph.add_edge(
                player_id,
                candidate_id,
                relationship="RECOMMENDED_REPLACEMENT",
                hops=hops,
                candidate_decision=candidate_decision,
            )

            rows.append(
                {
                    "player": player["player_name"],
                    "candidate": graph.nodes[candidate_id].get(
                        "player_name",
                        candidate_id,
                    ),
                    "hops": hops,
                    "candidate_decision": candidate_decision,
                }
            )

    return pd.DataFrame(
        rows,
        columns=["player", "candidate", "hops", "candidate_decision"],
    )


def query_team_replacement_candidates(
    team_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run replacement traversal for a team's Sell and Loan players."""

    graph = nx.read_graphml(EMBEDDING_GRAPH_PATH)
    convert_numeric_node_attributes(graph)

    selected_players = find_team_players_by_decision(
        graph,
        team_name,
    )

    replacements = add_replacement_edges(graph, selected_players)
    nx.write_graphml(graph, REPLACEMENT_GRAPH_PATH)

    sorted_replacements = replacements.sort_values(
        by=["player", "hops", "candidate"],
    ).reset_index(drop=True)

    return selected_players.reset_index(drop=True), sorted_replacements


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    graph = nx.read_graphml(GRAPH_PATH)
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

    # Query 4: players blocked by main same-role players.
    blocked_players = query_blocked_by_main_player(graph)
    blocked_players.to_csv(
        RESULTS_DIR / "query_blocked_by_main_player.csv",
        index=False,
    )

    # Portfolio-friendly examples from the selected team.
    selected_liverpool_players = [
        "Conor Bradley",
        "Jayden Danns",
        "Darwin Núñez",
        "Andrew Robertson",
    ]

    blocked_liverpool_examples = blocked_players[
        blocked_players["player_name"].isin(selected_liverpool_players)
    ].copy()

    blocked_liverpool_examples.to_csv(
        RESULTS_DIR / "query_liverpool_blocked_examples.csv",
        index=False,
    )

    print("Query 4: Selected Liverpool blocked-player examples")
    print(blocked_liverpool_examples.to_string(index=False))
    print()

    print("Saved query outputs:")
    print(RESULTS_DIR / "query_sell_players.csv")
    print(RESULTS_DIR / "query_liverpool_decisions.csv")
    print(RESULTS_DIR / "query_mohamed_salah_competitors.csv")
    print(RESULTS_DIR / "query_blocked_by_main_player.csv")
    print(RESULTS_DIR / "query_liverpool_blocked_examples.csv")
    print()

    selected_players, replacements = query_team_replacement_candidates(
        TARGET_TEAM
    )
    team_slug = TARGET_TEAM.lower().replace(" ", "_")
    replacement_output_path = (
        RESULTS_DIR / f"replacement_candidates_{team_slug}.csv"
    )
    replacements.to_csv(replacement_output_path, index=False)

    print(f"Query 5: {TARGET_TEAM} replacement candidates")
    print("Selected Sell/Loan players:")
    if selected_players.empty:
        print("None")
    else:
        print(
            selected_players[["player_name", "decision"]].to_string(
                index=False
            )
        )
    print()

    if replacements.empty:
        print("No candidates found within two SIMILAR_TO hops.")
    else:
        print(replacements.to_string(index=False))
    print()
    print("Saved replacement outputs:")
    print(replacement_output_path)
    print(REPLACEMENT_GRAPH_PATH)


if __name__ == "__main__":
    main()
