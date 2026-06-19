from pathlib import Path

import networkx as nx
import pandas as pd
from node2vec import Node2Vec
from sklearn.metrics.pairwise import cosine_similarity


# Input graph from KG builder.
GRAPH_PATH = Path("outputs/graphs/squad_management_kg.graphml")

# Output folders.
GRAPHS_DIR = Path("outputs/graphs")
RESULTS_DIR = Path("outputs/results")

# Embedding settings.
EMBEDDING_DIMENSIONS = 32
WALK_LENGTH = 10
NUM_WALKS = 50
WINDOW_SIZE = 5
TOP_K_SIMILAR_PLAYERS = 3
RANDOM_SEED = 42


def convert_numeric_node_attributes(graph: nx.MultiDiGraph) -> None:
    """
    Convert numeric node attributes back to float after loading GraphML.

    GraphML stores attributes as strings, so we convert important
    numeric attributes again for cleaner outputs.
    """

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


def train_node2vec_embeddings(graph: nx.MultiDiGraph):
    """
    Train Node2Vec embeddings on an undirected copy of the Knowledge Graph.

    The actual KG stays directed for semantic correctness.
    For Node2Vec, we use an undirected copy because the method learns from
    graph neighborhoods and random walks.
    """

    embedding_graph = graph.to_undirected()

    node2vec = Node2Vec(
        embedding_graph,
        dimensions=EMBEDDING_DIMENSIONS,
        walk_length=WALK_LENGTH,
        num_walks=NUM_WALKS,
        workers=1,
        seed=RANDOM_SEED,
        quiet=True,
    )

    model = node2vec.fit(
        window=WINDOW_SIZE,
        min_count=1,
        batch_words=4,
        seed=RANDOM_SEED,
    )

    return model


def get_player_nodes(graph: nx.MultiDiGraph) -> list[str]:
    """
    Return all player node IDs from the graph.
    """

    return [
        node_id
        for node_id, node_data in graph.nodes(data=True)
        if node_data.get("node_type") == "Player"
    ]


def get_team_name(graph: nx.MultiDiGraph, player_id: str) -> str:
    """
    Return the team name of a player.
    """

    for _, target, edge_data in graph.out_edges(player_id, data=True):
        if edge_data.get("relationship") == "PLAYS_FOR":
            return graph.nodes[target].get("team_name", "Unknown")

    return "Unknown"


def create_player_embedding_table(
    graph: nx.MultiDiGraph,
    model,
    player_nodes: list[str],
) -> pd.DataFrame:
    """
    Create a table containing one embedding vector per player.
    """

    rows = []

    for player_id in player_nodes:
        player_data = graph.nodes[player_id]
        embedding = model.wv[player_id]

        row = {
            "player_id": player_id,
            "player_name": player_data.get("player_name"),
            "team_name": get_team_name(graph, player_id),
            "role_group": player_data.get("role_group"),
            "decision": player_data.get("decision"),
        }

        for index, value in enumerate(embedding):
            row[f"embedding_{index}"] = value

        rows.append(row)

    return pd.DataFrame(rows)


def find_similar_players(
    graph: nx.MultiDiGraph,
    model,
    player_nodes: list[str],
) -> pd.DataFrame:
    """
    Find similar players using cosine similarity between embeddings.

    Similarity is calculated only within the same role group.
    This makes the output more useful for football squad management.
    """

    rows = []

    for source_player_id in player_nodes:
        source_data = graph.nodes[source_player_id]
        source_role = source_data.get("role_group")
        source_vector = model.wv[source_player_id].reshape(1, -1)

        candidates = [
            candidate_id
            for candidate_id in player_nodes
            if candidate_id != source_player_id
            and graph.nodes[candidate_id].get("role_group") == source_role
        ]

        candidate_scores = []

        for candidate_id in candidates:
            candidate_vector = model.wv[candidate_id].reshape(1, -1)

            similarity_score = cosine_similarity(
                source_vector,
                candidate_vector,
            )[0][0]

            candidate_scores.append(
                {
                    "source_player_id": source_player_id,
                    "source_player_name": source_data.get("player_name"),
                    "source_team_name": get_team_name(graph, source_player_id),
                    "source_role_group": source_role,
                    "source_decision": source_data.get("decision"),
                    "similar_player_id": candidate_id,
                    "similar_player_name": graph.nodes[candidate_id].get(
                        "player_name"
                    ),
                    "similar_team_name": get_team_name(graph, candidate_id),
                    "similar_role_group": graph.nodes[candidate_id].get(
                        "role_group"
                    ),
                    "similar_decision": graph.nodes[candidate_id].get(
                        "decision"
                    ),
                    "similarity_score": similarity_score,
                }
            )

        top_candidates = sorted(
            candidate_scores,
            key=lambda row: row["similarity_score"],
            reverse=True,
        )[:TOP_K_SIMILAR_PLAYERS]

        rows.extend(top_candidates)

    return pd.DataFrame(rows)


def add_similarity_edges(
    graph: nx.MultiDiGraph,
    similar_players: pd.DataFrame,
) -> nx.MultiDiGraph:
    """
    Add SIMILAR_TO edges to a copy of the directed KG.

    A MultiDiGraph is used so SIMILAR_TO does not overwrite existing
    relationships such as COMPETES_WITH between the same two players.
    """

    graph_with_embeddings = nx.MultiDiGraph(graph)

    for _, row in similar_players.iterrows():
        graph_with_embeddings.add_edge(
            row["source_player_id"],
            row["similar_player_id"],
            relationship="SIMILAR_TO",
            similarity_score=float(row["similarity_score"]),
        )

    return graph_with_embeddings


def save_embedding_graph_statistics(graph: nx.MultiDiGraph) -> None:
    """
    Save simple statistics for the KG after adding SIMILAR_TO edges.
    """

    edge_types = [
        edge_data["relationship"]
        for _, _, edge_data in graph.edges(data=True)
    ]

    edge_counts = pd.Series(edge_types).value_counts().reset_index()
    edge_counts.columns = ["relationship", "count"]

    kg_embedding_stats = pd.DataFrame(
        [
            {
                "number_of_nodes": graph.number_of_nodes(),
                "number_of_edges": graph.number_of_edges(),
                "number_of_relationship_types": edge_counts.shape[0],
            }
        ]
    )

    edge_counts.to_csv(
        RESULTS_DIR / "kg_with_embeddings_edge_counts.csv",
        index=False,
    )

    kg_embedding_stats.to_csv(
        RESULTS_DIR / "kg_with_embeddings_stats.csv",
        index=False,
    )

    print("KG with embeddings statistics")
    print("-----------------------------")
    print(kg_embedding_stats.to_string(index=False))
    print()

    print("Edge counts:")
    print(edge_counts)
    print()


def main() -> None:
    # Create output folders if they do not exist.
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load the directed Knowledge Graph.
    graph = nx.read_graphml(GRAPH_PATH)

    # Convert numeric attributes after loading GraphML.
    convert_numeric_node_attributes(graph)

    # Get player nodes.
    player_nodes = get_player_nodes(graph)

    # Train Node2Vec embeddings.
    model = train_node2vec_embeddings(graph)

    # Save player embedding vectors.
    player_embeddings = create_player_embedding_table(
        graph,
        model,
        player_nodes,
    )

    player_embeddings_path = RESULTS_DIR / "player_embeddings.csv"
    player_embeddings.to_csv(player_embeddings_path, index=False)

    # Find similar players.
    similar_players = find_similar_players(
        graph,
        model,
        player_nodes,
    )

    similar_players_path = RESULTS_DIR / "player_embedding_similarities.csv"
    similar_players.to_csv(similar_players_path, index=False)

    # Add SIMILAR_TO edges to a new MultiDiGraph.
    graph_with_embeddings = add_similarity_edges(graph, similar_players)

    graph_with_embeddings_path = (
        GRAPHS_DIR / "squad_management_kg_with_embeddings.graphml"
    )

    nx.write_graphml(graph_with_embeddings, graph_with_embeddings_path)

    # Save graph statistics after adding embedding edges.
    save_embedding_graph_statistics(graph_with_embeddings)

    print("Knowledge Graph embeddings completed")
    print("------------------------------------")
    print(f"Players embedded: {len(player_nodes)}")
    print(f"Similar player rows: {similar_players.shape[0]}")
    print()
    print("Saved outputs:")
    print(player_embeddings_path)
    print(similar_players_path)
    print(graph_with_embeddings_path)


if __name__ == "__main__":
    main()
