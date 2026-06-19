from collections import Counter
from pathlib import Path
from urllib.parse import quote

import networkx as nx
import pandas as pd
from rdflib import Graph, Literal, Namespace, RDF, URIRef


PLAYERS_PATH = Path("data/processed/premier_league_players.csv")
GRAPH_PATH = Path("outputs/graphs/squad_management_kg.graphml")
EMBEDDINGS_PATH = Path("outputs/results/player_embeddings.csv")

RESULTS_DIR = Path("outputs/results")
GRAPHS_DIR = Path("outputs/graphs")

COMPARISON_PATH = RESULTS_DIR / "data_model_comparison.csv"
EXAMPLES_PATH = RESULTS_DIR / "data_model_comparison_examples.csv"
RDF_PATH = GRAPHS_DIR / "squad_management_kg.ttl"

KG = Namespace("https://example.org/football-kg/")
RESOURCE = Namespace("https://example.org/football-kg/resource/")
PROPERTY = Namespace("https://example.org/football-kg/property/")
CLASS = Namespace("https://example.org/football-kg/class/")

RDF_ATTRIBUTES = [
    "player_name",
    "team_name",
    "league_name",
    "role_group",
    "age_group",
    "minutes_group",
    "performance_level",
    "competition_status",
    "decision",
    "raw_position",
    "age",
    "minutes_played",
    "performance_score",
    "performance_percentile",
    "explanation",
]


def resource_uri(node_id: str) -> URIRef:
    """Create a stable URI for one graph node."""

    return URIRef(f"{RESOURCE}{quote(str(node_id), safe='')}")


def property_uri(property_name: str) -> URIRef:
    """Create a stable URI for one relationship or attribute."""

    return URIRef(f"{PROPERTY}{quote(str(property_name).lower(), safe='')}")


def class_uri(node_type: str) -> URIRef:
    """Create a stable URI for one node type."""

    return URIRef(f"{CLASS}{quote(str(node_type), safe='')}")


def export_rdf(graph: nx.MultiDiGraph) -> Graph:
    """
    Convert the implemented property graph into a simple RDF graph.

    Nodes become URI resources, node types become rdf:type statements,
    graph relationships become RDF predicates, and selected attributes
    become literal values.
    """

    rdf_graph = Graph()
    rdf_graph.bind("kg", KG)
    rdf_graph.bind("resource", RESOURCE)
    rdf_graph.bind("property", PROPERTY)
    rdf_graph.bind("class", CLASS)

    for node_id, node_data in sorted(graph.nodes(data=True)):
        subject = resource_uri(node_id)
        node_type = node_data.get("node_type")

        if node_type:
            rdf_graph.add((subject, RDF.type, class_uri(node_type)))

        for attribute in RDF_ATTRIBUTES:
            value = node_data.get(attribute)
            if value is not None and value != "":
                rdf_graph.add(
                    (
                        subject,
                        property_uri(attribute),
                        Literal(value),
                    )
                )

    edges = sorted(
        graph.edges(keys=True, data=True),
        key=lambda edge: (
            str(edge[0]),
            str(edge[1]),
            str(edge[3].get("relationship", "")),
            str(edge[2]),
        ),
    )

    for source, target, _, edge_data in edges:
        relationship = edge_data.get("relationship")
        if relationship:
            rdf_graph.add(
                (
                    resource_uri(source),
                    property_uri(relationship),
                    resource_uri(target),
                )
            )

    rdf_graph.serialize(destination=RDF_PATH, format="turtle")
    return rdf_graph


def find_example_player(
    players: pd.DataFrame,
    graph: nx.MultiDiGraph,
) -> tuple[pd.Series, str, str]:
    """Choose a readable player and team example from the actual artifacts."""

    preferred_players = players[players["player_name"] == "Mohamed Salah"]
    player = (
        preferred_players.iloc[0]
        if not preferred_players.empty
        else players.iloc[0]
    )

    player_id = player["player_id"]
    team_targets = [
        target
        for _, target, edge_data in graph.out_edges(player_id, data=True)
        if edge_data.get("relationship") == "PLAYS_FOR"
    ]

    team_id = team_targets[0]
    return player, player_id, team_id


def count_parallel_relationship_pairs(graph: nx.MultiDiGraph) -> int:
    """
    Count ordered node pairs connected by multiple relationship types.
    """

    relationship_pairs = {}

    for source, target, edge_data in graph.edges(data=True):
        relationship_pairs.setdefault((source, target), set()).add(
            edge_data.get("relationship")
        )

    return sum(
        len(relationships) > 1
        for relationships in relationship_pairs.values()
    )


def create_comparison_table(
    players: pd.DataFrame,
    graph: nx.MultiDiGraph,
    embeddings: pd.DataFrame,
    rdf_graph: Graph,
) -> pd.DataFrame:
    """Create the main cross-community data-model comparison."""

    node_types = sorted(
        {
            node_data.get("node_type")
            for _, node_data in graph.nodes(data=True)
            if node_data.get("node_type")
        }
    )
    relationship_types = sorted(
        {
            edge_data.get("relationship")
            for _, _, edge_data in graph.edges(data=True)
            if edge_data.get("relationship")
        }
    )
    embedding_columns = [
        column
        for column in embeddings.columns
        if column.startswith("embedding_")
    ]
    parallel_pairs = count_parallel_relationship_pairs(graph)

    rows = [
        {
            "model": "Tabular / CSV",
            "community": "Database and data science",
            "implementation_status": "Implemented",
            "actual_artifact": str(PLAYERS_PATH),
            "measured_statistics": (
                f"{players.shape[0]} rows; {players.shape[1]} columns; "
                f"{players['player_id'].nunique()} player IDs; "
                f"{players['team_id'].nunique()} team IDs"
            ),
            "basic_unit": "Row and column",
            "entity_identity": "player_id and team_id columns",
            "relationship_representation": (
                "Foreign-key-like values repeated in rows; graph relations "
                "are not first-class objects"
            ),
            "attribute_handling": "Typed columns in one player table",
            "query_style": "Pandas filtering, grouping, joins, and aggregation",
            "multiple_relationship_support": (
                "Possible through additional tables or columns, but not "
                "explicit in this CSV"
            ),
            "temporal_support": (
                "Season is implicit in the dataset filename; no validity "
                "intervals"
            ),
            "ml_suitability": "High for feature engineering and matrix models",
            "explainability": "Readable rows, but graph context is duplicated",
            "information_gain_or_loss": (
                "Compact for statistics; loses explicit traversable "
                "relationships"
            ),
            "football_use_case_suitability": (
                "Good for preprocessing, scoring, and aggregate statistics"
            ),
        },
        {
            "model": "Property graph / NetworkX MultiDiGraph",
            "community": "Graph database and Knowledge Graph",
            "implementation_status": "Main implemented KG model",
            "actual_artifact": str(GRAPH_PATH),
            "measured_statistics": (
                f"{graph.number_of_nodes()} nodes; "
                f"{graph.number_of_edges()} edges; "
                f"{len(node_types)} node types; "
                f"{len(relationship_types)} relationship types; "
                f"{parallel_pairs} ordered pairs with multiple relation types"
            ),
            "basic_unit": "Attributed node and directed relationship",
            "entity_identity": "Stable graph node IDs",
            "relationship_representation": (
                "Named, directed, first-class edges such as PLAYS_FOR and "
                "BLOCKED_BY_MAIN_PLAYER"
            ),
            "attribute_handling": "Key-value attributes on nodes and edges",
            "query_style": "NetworkX traversal and relationship filtering",
            "multiple_relationship_support": (
                "Yes; MultiDiGraph preserves parallel semantic relations"
            ),
            "temporal_support": "Not currently modeled",
            "ml_suitability": (
                "Useful as structural input for graph algorithms and "
                "embeddings"
            ),
            "explainability": "High because entities and relations are explicit",
            "information_gain_or_loss": (
                "Gains explicit connected context; requires graph traversal "
                "instead of simple rows"
            ),
            "football_use_case_suitability": (
                "Best current model for competition-aware squad decisions "
                "and queries"
            ),
        },
        {
            "model": "RDF / Turtle",
            "community": "Semantic Web",
            "implementation_status": "Implemented export",
            "actual_artifact": str(RDF_PATH),
            "measured_statistics": (
                f"{len(rdf_graph)} RDF triples exported from "
                f"{graph.number_of_nodes()} nodes and "
                f"{graph.number_of_edges()} property-graph edges"
            ),
            "basic_unit": "Subject-predicate-object triple",
            "entity_identity": "Stable HTTP-style URIs",
            "relationship_representation": "URI predicates between resources",
            "attribute_handling": "Predicates with typed literal values",
            "query_style": "SPARQL-compatible RDF query model",
            "multiple_relationship_support": (
                "Yes; multiple predicates can connect the same resources"
            ),
            "temporal_support": (
                "Can be added with Season resources, named graphs, or "
                "validity predicates"
            ),
            "ml_suitability": (
                "Requires conversion or RDF-aware embedding methods for ML"
            ),
            "explainability": (
                "High semantic interoperability; schema is currently simple"
            ),
            "information_gain_or_loss": (
                "Gains URI-based interoperability; selected GraphML "
                "attributes are exported"
            ),
            "football_use_case_suitability": (
                "Useful for semantic integration and linking with external "
                "football data"
            ),
        },
        {
            "model": "Embedding / vector",
            "community": "Machine learning",
            "implementation_status": "Implemented derived representation",
            "actual_artifact": str(EMBEDDINGS_PATH),
            "measured_statistics": (
                f"{embeddings.shape[0]} embedded players; "
                f"{len(embedding_columns)} dimensions per player"
            ),
            "basic_unit": "Dense numeric vector",
            "entity_identity": "player_id linked to one embedding row",
            "relationship_representation": (
                "Relations are encoded indirectly through graph-neighborhood "
                "proximity"
            ),
            "attribute_handling": (
                "Symbolic attributes are compressed into learned coordinates"
            ),
            "query_style": "Cosine similarity and nearest-neighbor search",
            "multiple_relationship_support": (
                "Captured indirectly, without preserving relation labels"
            ),
            "temporal_support": "Not modeled in the current embeddings",
            "ml_suitability": "High for similarity and downstream ML features",
            "explainability": (
                "Lower; individual vector dimensions have no direct meaning"
            ),
            "information_gain_or_loss": (
                "Gains numeric similarity; loses explicit symbolic semantics"
            ),
            "football_use_case_suitability": (
                "Useful for structural similar-player discovery"
            ),
        },
        {
            "model": "Temporal Knowledge Graph",
            "community": "Temporal databases and Knowledge Graph research",
            "implementation_status": "Design comparison / future extension",
            "actual_artifact": "Not implemented",
            "measured_statistics": (
                "Current dataset represents one 2024/2025 season snapshot"
            ),
            "basic_unit": (
                "Time-qualified entity, relationship, event, or snapshot"
            ),
            "entity_identity": (
                "Stable entity IDs combined with season or validity context"
            ),
            "relationship_representation": (
                "Season-specific edges or statements with valid_from and "
                "valid_to"
            ),
            "attribute_handling": (
                "Values attached to Season nodes, events, or validity periods"
            ),
            "query_style": (
                "Time-filtered graph queries and longitudinal comparison"
            ),
            "multiple_relationship_support": (
                "Yes, including repeated relations valid at different times"
            ),
            "temporal_support": (
                "Core feature through Season nodes or validity intervals"
            ),
            "ml_suitability": (
                "Useful for forecasting and temporal link prediction"
            ),
            "explainability": (
                "High when changes and validity periods are explicit"
            ),
            "information_gain_or_loss": (
                "Would gain transfer and performance history; requires "
                "multi-season data"
            ),
            "football_use_case_suitability": (
                "Best future model for transfers, squad evolution, and "
                "season-over-season decisions"
            ),
        },
    ]

    return pd.DataFrame(rows)


def create_examples_table(
    players: pd.DataFrame,
    graph: nx.MultiDiGraph,
    embeddings: pd.DataFrame,
) -> pd.DataFrame:
    """Create equivalent examples grounded in one actual player."""

    player, player_id, team_id = find_example_player(players, graph)
    embedding_row = embeddings[embeddings["player_id"] == player_id].iloc[0]
    embedding_columns = [
        column
        for column in embeddings.columns
        if column.startswith("embedding_")
    ]
    vector_preview = ", ".join(
        f"{float(embedding_row[column]):.4f}"
        for column in embedding_columns[:4]
    )

    relationship_counts = Counter(
        edge_data.get("relationship")
        for _, _, edge_data in graph.edges(data=True)
    )

    return pd.DataFrame(
        [
            {
                "model": "Tabular / CSV",
                "actual_example": (
                    f"player_id={player_id}; "
                    f"player_name={player['player_name']}; "
                    f"team_name={player['team_name']}; "
                    f"role_group={player['role_group']}"
                ),
                "source_artifact": str(PLAYERS_PATH),
                "evidence": (
                    f"{players.shape[0]} player rows and "
                    f"{players.shape[1]} columns"
                ),
            },
            {
                "model": "Property graph / NetworkX MultiDiGraph",
                "actual_example": (
                    f"{player_id} -[PLAYS_FOR]-> {team_id}"
                ),
                "source_artifact": str(GRAPH_PATH),
                "evidence": (
                    f"PLAYS_FOR edges={relationship_counts['PLAYS_FOR']}; "
                    f"graph is multigraph={graph.is_multigraph()}"
                ),
            },
            {
                "model": "RDF / Turtle",
                "actual_example": (
                    f"<{resource_uri(player_id)}> "
                    f"<{property_uri('PLAYS_FOR')}> "
                    f"<{resource_uri(team_id)}> ."
                ),
                "source_artifact": str(RDF_PATH),
                "evidence": "Real RDF triple generated from the GraphML edge",
            },
            {
                "model": "Embedding / vector",
                "actual_example": (
                    f"{player_id} -> [{vector_preview}, ...]"
                ),
                "source_artifact": str(EMBEDDINGS_PATH),
                "evidence": (
                    f"{len(embedding_columns)} learned dimensions for this "
                    "player"
                ),
            },
            {
                "model": "Temporal Knowledge Graph",
                "actual_example": (
                    f"{player_id} -[PLAYS_FOR, season=2024/2025]-> {team_id}"
                ),
                "source_artifact": "Design example based on current snapshot",
                "evidence": (
                    "Not implemented; illustrates a Season node or "
                    "time-qualified relation"
                ),
            },
        ]
    )


def main() -> None:
    """Generate data-model comparison evidence from project artifacts."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

    players = pd.read_csv(PLAYERS_PATH)
    graph = nx.read_graphml(GRAPH_PATH)
    embeddings = pd.read_csv(EMBEDDINGS_PATH)

    rdf_graph = export_rdf(graph)
    comparison = create_comparison_table(
        players,
        graph,
        embeddings,
        rdf_graph,
    )
    examples = create_examples_table(players, graph, embeddings)

    comparison.to_csv(COMPARISON_PATH, index=False)
    examples.to_csv(EXAMPLES_PATH, index=False)

    print("Knowledge Graph data model comparison completed")
    print("-----------------------------------------------")
    print(f"Models compared: {comparison.shape[0]}")
    print(f"CSV rows inspected: {players.shape[0]}")
    print(f"Property graph nodes: {graph.number_of_nodes()}")
    print(f"Property graph edges: {graph.number_of_edges()}")
    print(f"RDF triples exported: {len(rdf_graph)}")
    print(
        "Embedding dimensions: "
        f"{sum(column.startswith('embedding_') for column in embeddings.columns)}"
    )
    print()
    print("Saved outputs:")
    print(COMPARISON_PATH)
    print(EXAMPLES_PATH)
    print(RDF_PATH)


if __name__ == "__main__":
    main()
