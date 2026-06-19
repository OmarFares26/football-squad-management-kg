# Learning Outcomes Evidence

## Purpose

This file maps the project work to the Knowledge Graphs course learning
outcomes.

The project aims to make only claims that are supported by the actual
implementation. It provides two focus outcomes, basic evidence for
seven additional outcomes, and limited discussion for LO4.

The two strongest learning outcomes in this project are:

```text
LO7: Apply a system to create a Knowledge Graph
LO2: Understand and apply logical knowledge in Knowledge Graphs
```

## Project Summary

Project title:

```text
Football Squad Management Knowledge Graph
```

The project builds a Knowledge Graph for football squad-management
decisions using real 2024/2025 Premier League player statistics.

The system:

```text
1.  loads and preprocesses football player statistics
2.  maps raw positions to role groups
3.  calculates role-based performance scores
4.  infers age groups, minutes groups, performance levels,
    and competition status
5.  compares players inside the same team and same role group
6.  creates squad-management decisions
7.  builds a directed MultiDiGraph Knowledge Graph
8.  adds competition-aware relationships
9.  queries the Knowledge Graph
10. creates a service-style output by querying the GraphML KG
11. applies Node2Vec embeddings for player similarity
```

## Target Learning Outcomes

The project claims focus or basic proficiency in the following 9
learning outcomes:

```text
LO1
LO2
LO5
LO6
LO7
LO8
LO9
LO11
LO12
```

LO4 is included only as limited supporting discussion of tabular and
property-graph representations.

The project does not claim:

```text
LO3: Graph Neural Networks
LO10: Financial Knowledge Graph applications
```

---

## LO1 — Understand and Apply Knowledge Graph Embeddings

### Evidence

Files:

```text
src/embeddings.py
outputs/results/player_embeddings.csv
outputs/results/player_embedding_similarities.csv
outputs/graphs/squad_management_kg_with_embeddings.graphml
outputs/results/kg_with_embeddings_stats.csv
outputs/results/kg_with_embeddings_edge_counts.csv
```

### What Was Done

Node2Vec is used to create vector representations for player nodes.

The workflow is:

```text
1. load the Knowledge Graph
2. create an undirected copy for Node2Vec training
3. train player node embeddings
4. calculate cosine similarity between player embeddings
5. keep top 3 similar players within the same role group
6. add SIMILAR_TO edges to an embedding-enriched graph
```

### Why This Supports LO1

The project does not only describe KG embeddings. It applies them.

The embedding output contains:

```text
562 embedded players
1686 similar-player rows
1686 SIMILAR_TO edges
```

The embedding-enriched graph contains:

```text
608 nodes
9480 edges
11 relationship types
```

### Level

```text
Basic proficiency
```

The project applies Node2Vec and uses the embeddings for player
similarity. It does not deeply compare multiple embedding models,
so this is basic evidence.

---

## LO2 — Understand and Apply Logical Knowledge in Knowledge Graphs

### Evidence

This is one of the two strongest learning outcomes in the project.

Files:

```text
src/rule_engine.py
src/kg_builder.py
src/kg_queries.py
docs/decision_rules.md
outputs/results/squad_decisions_all_players.csv
outputs/results/query_blocked_by_main_player.csv
outputs/results/query_liverpool_blocked_examples.csv
```

### What Was Done

The project creates logical inferred knowledge from raw player
statistics.

Examples of inferred knowledge:

```text
age_group
minutes_group
performance_level
competition_status
main_same_role_player
is_blocked_by_main_player
main_player_underperforming
decision
explanation
```

The project also creates explicit graph relationships for reasoning:

```text
Player -> BLOCKED_BY_MAIN_PLAYER -> Player
Player -> HAS_DECISION -> SquadDecision
Player -> HAS_PERFORMANCE_LEVEL -> PerformanceLevel
Player -> HAS_COMPETITION_STATUS -> CompetitionStatus
```

### Example Rule

```text
IF player is young
AND player has low minutes
AND player is blocked by the main same-role player
THEN Loan
```

Example:

```text
Conor Bradley -> blocked by Virgil van Dijk -> Loan
Jayden Danns -> blocked by Ryan Gravenberch -> Loan
```

### Another Example Rule

```text
IF player has low or medium minutes
AND player has promising or good performance
AND the main same-role player is underperforming
THEN Give More Chances
```

Example:

```text
Wataru Endo -> Give More Chances
```

### Why This Supports LO2

The project uses explicit rule-based reasoning to infer new facts from
existing facts.

The reasoning follows a multi-step inference chain:

```text
raw statistics
-> performance score
-> competition status
-> blocked-by-main-player
-> final decision
```

Each step infers new knowledge from the previous one. This means the
graph is not only a data container. It contains inferred knowledge and
relationships that support decisions.

The BLOCKED_BY_MAIN_PLAYER relationship is especially important because
it turns same-role competition reasoning into explicit KG structure.

### Level

```text
Focus outcome / strong evidence
```

This learning outcome is strongly supported because the project applies
multi-step logical rules, creates inferred entities and relationships,
and uses them in final decisions and KG queries.

---

## LO4 — Compare Different Knowledge Graph Data Models

### Evidence

Files:

```text
docs/kg_schema.md
docs/portfolio_notes.md
src/kg_builder.py
```

### What Was Done

The project works with different data representations:

```text
raw CSV table
processed CSV table
directed property multigraph
embedding-enriched graph
```

The raw dataset starts as tabular data, where each row is a
player-season record.

The Knowledge Graph transforms this into nodes and relationships.

Examples:

```text
CSV column: team_name
KG representation: Player -> PLAYS_FOR -> Team

CSV column: role_group
KG representation: Player -> HAS_ROLE -> RoleGroup

CSV decision value
KG representation: Player -> HAS_DECISION -> SquadDecision
```

### Why This Supports LO4

The project shows the difference between a table-based representation
and a graph-based representation.

In the table, squad competition is stored as derived columns.

In the graph, squad competition is represented as explicit
relationships:

```text
COMPETES_WITH
BLOCKED_BY_MAIN_PLAYER
```

### Level

```text
Limited discussion only
```

The project compares tabular and property-graph representations in
practice. It does not implement or deeply compare RDF, relational,
temporal, and other KG data models. LO4 should therefore not be
presented as a substantial implementation outcome.

---

## LO5 — Design and Implement Architectures of a Knowledge Graph

### Evidence

Files:

```text
src/data_preprocessing.py
src/performance_scoring.py
src/rule_engine.py
src/kg_builder.py
src/kg_queries.py
src/service_output.py
src/embeddings.py
run_pipeline.py
docs/kg_schema.md
```

### What Was Done

The project implements a full KG architecture with clear stage
separation.

Pipeline:

```text
Raw data
-> preprocessing
-> role-based scoring
-> rule-based reasoning
-> KG construction
-> KG queries
-> service output
-> embeddings
```

Each file has one clear responsibility:

```text
data_preprocessing.py    cleans and prepares the data
performance_scoring.py   creates role-based performance scores
rule_engine.py           creates inferred decisions and context
kg_builder.py            builds the Knowledge Graph
kg_queries.py            queries the graph
service_output.py        queries the GraphML KG for service output
embeddings.py            applies Node2Vec embeddings
run_pipeline.py          executes every stage in dependency order
```

### Why This Supports LO5

The project is not a single script. It has a designed pipeline where
each stage produces artifacts used by the next stage. The architecture
is clear and reproducible.

### Level

```text
Basic proficiency
```

---

## LO6 — Describe and Apply Scalable Reasoning Methods in Knowledge
Graphs

### Evidence

Files:

```text
src/rule_engine.py
src/kg_builder.py
outputs/results/decision_counts.csv
outputs/results/decision_by_role.csv
```

### What Was Done

The project applies rule-based reasoning over all Premier League
players in the dataset.

The reasoning is applied systematically across:

```text
562 players
20 Premier League teams
7 role groups
```

The rules infer:

```text
age groups
minutes groups
competition status
blocked-by-main-player status
squad decisions
```

### Why This Supports LO6

The project applies reasoning over a full processed dataset, not only
one manually chosen example.

The reasoning is scalable because it uses grouped operations by:

```text
team_name
role_group
```

This allows the system to reason across all teams and role groups
systematically.

### Level

```text
Basic proficiency
```

The reasoning is scalable in a practical dataset-processing sense.
It does not implement advanced distributed or semantic reasoning,
so this is basic evidence.

---

## LO7 — Apply a System to Create a Knowledge Graph

### Evidence

This is one of the two strongest learning outcomes in the project.

Files:

```text
src/kg_builder.py
outputs/graphs/squad_management_kg.graphml
outputs/results/kg_stats.csv
outputs/results/kg_node_counts.csv
outputs/results/kg_edge_counts.csv
docs/kg_schema.md
```

### What Was Done

The project creates a directed `MultiDiGraph` Knowledge Graph from
processed football data. The multigraph model preserves different
relationship types between the same ordered pair of entities.

The graph contains:

```text
608 nodes
7794 edges
9 node types
10 relationship types
```

Node types:

```text
Player
Team
League
RoleGroup
AgeGroup
MinutesGroup
PerformanceLevel
CompetitionStatus
SquadDecision
```

Relationship types:

```text
PLAYS_FOR
PLAYS_IN
HAS_ROLE
HAS_AGE_GROUP
HAS_MINUTES_GROUP
HAS_PERFORMANCE_LEVEL
HAS_COMPETITION_STATUS
HAS_DECISION
COMPETES_WITH
BLOCKED_BY_MAIN_PLAYER
```

### Why This Supports LO7

The project applies a working system that creates a KG from real data.

It includes:

```text
data cleaning
entity creation
relationship creation
inferred nodes
inferred relationships
graph export
graph statistics
```

The BLOCKED_BY_MAIN_PLAYER relationship is particularly notable because
it transforms an analytical calculation into an explicit graph structure
that supports transparent reasoning.

### Level

```text
Focus outcome / strong evidence
```

This learning outcome is strongly supported because the project builds
a complete, meaningful, and documented KG with multiple node and
relationship types, including competition-aware inferred relationships.

---

## LO8 — Apply a System to Evolve a Knowledge Graph

### Evidence

Files:

```text
src/rule_engine.py
src/kg_builder.py
src/embeddings.py
outputs/graphs/squad_management_kg.graphml
outputs/graphs/squad_management_kg_with_embeddings.graphml
```

### What Was Done

The project evolves the graph in stages.

Base KG:

```text
outputs/graphs/squad_management_kg.graphml
608 nodes, 7794 edges, 10 relationship types
```

Embedding-enriched KG:

```text
outputs/graphs/squad_management_kg_with_embeddings.graphml
608 nodes, 9480 edges, 11 relationship types
```

The graph evolves by adding:

```text
inferred squad decision nodes
BLOCKED_BY_MAIN_PLAYER relationships
SIMILAR_TO relationships from Node2Vec embeddings
```

### Why This Supports LO8

The graph is not static. It starts from processed player data, becomes
a base KG, and is then enriched with embedding-based similarity
relationships.

### Level

```text
Basic proficiency
```

The project shows KG evolution through enrichment. It does not
implement continuous updates over time, so this is basic evidence.

---

## LO9 — Describe and Design Real-World Applications of Knowledge
Graphs

### Evidence

Files:

```text
src/service_output.py
outputs/results/liverpool_squad_decision_service.csv
outputs/results/liverpool_squad_decision_summary.csv
docs/portfolio_notes.md
```

### What Was Done

The project designs a real-world football squad-management application.

The application answers questions such as:

```text
Which players should be kept?
Which young players should be loaned?
Which underused players deserve more chances?
Which older underperforming players could be sold?
Which players are blocked by main same-role players?
```

The service output focuses on Liverpool as an example.

### Why This Supports LO9

The project connects KG concepts to a realistic use case: squad
planning and decision support. The output is understandable for a
football analyst or squad planner.

### Level

```text
Basic proficiency
```

---

## LO11 — Apply a System to Provide Services Through a Knowledge Graph

### Evidence

Files:

```text
src/service_output.py
src/kg_queries.py
outputs/results/liverpool_squad_decision_service.csv
outputs/results/query_liverpool_decisions.csv
outputs/results/query_liverpool_blocked_examples.csv
```

### What Was Done

The project creates service-style outputs by loading and querying the
generated GraphML Knowledge Graph.

The main service output is:

```text
outputs/results/liverpool_squad_decision_service.csv
```

It provides:

```text
player name
role group
age group
minutes group
performance level
same-role competition context
decision
explanation
```

The service selects a team through `PLAYS_FOR` relationships and
retrieves role, grouping, performance, competition, and decision
values from player nodes and related KG concept nodes.

### Why This Supports LO11

The project provides a user-facing result directly from the KG. Both
the service output and query examples answer specific
squad-management questions by traversing the GraphML graph.

### Level

```text
Basic proficiency
```

The project provides a KG-backed service-like output but does not
implement a web API or interactive user interface, so this remains
basic evidence.

---

## LO12 — Describe Connections Between Knowledge Graphs, Machine
Learning, and AI

### Evidence

Files:

```text
src/performance_scoring.py
src/rule_engine.py
src/embeddings.py
outputs/results/player_embeddings.csv
outputs/results/player_embedding_similarities.csv
```

### What Was Done

The project combines:

```text
Knowledge Graphs
rule-based reasoning
role-based scoring
Knowledge Graph embeddings
cosine similarity
```

The KG provides structure and explainability.

The rule engine provides symbolic reasoning.

Node2Vec provides vector representations and similarity analysis.

### Why This Supports LO12

The project clearly shows how KG structure can be combined with
AI/ML-style methods.

The final system uses:

```text
symbolic reasoning for decisions
embeddings for similarity exploration
```

This distinction is important because the project does not overclaim
that embeddings make the final decisions. Rules produce explainable
decisions. Embeddings produce structural similarity. Both are grounded
in the KG.

### Level

```text
Basic proficiency
```

---

## Learning Outcomes Not Targeted

### LO3 — Understand and Apply Graph Neural Networks

This project does not implement Graph Neural Networks. It uses Node2Vec
embeddings, but not a GNN model. Therefore LO3 is not claimed.

### LO10 — Describe Financial Knowledge Graph Applications

This project is about football squad management. It does not address
financial KG applications. Therefore LO10 is not claimed.

---

## Summary Table

| LO   | Level    | Main Evidence                                                              |
|------|----------|----------------------------------------------------------------------------|
| LO1  | Basic    | Node2Vec player embeddings and SIMILAR_TO edges                            |
| LO2  | Focus    | multi-step rule-based inferred KG knowledge and BLOCKED_BY_MAIN_PLAYER     |
| LO4  | Limited  | tabular versus property-graph discussion; no broad data-model comparison    |
| LO5  | Basic    | reproducible end-to-end architecture through `run_pipeline.py`              |
| LO6  | Basic    | scalable rule-based reasoning over 562 players, 20 teams, 7 role groups    |
| LO7  | Focus    | directed multigraph with 608 nodes, 7794 edges, 10 relationship types       |
| LO8  | Basic    | base KG enriched with embedding similarity edges                           |
| LO9  | Basic    | football squad-management KG application                                   |
| LO11 | Basic    | Liverpool service output queried directly from the GraphML KG               |
| LO12 | Basic    | KG + rules + embeddings connection                                         |

---

## Final Portfolio Claim

```text
A competition-aware football squad-management Knowledge Graph that
combines KG creation, multi-step logical reasoning, service-style
decision output, and Node2Vec-based similarity.
```

The strongest learning outcomes are:

```text
LO7: Apply a system to create a Knowledge Graph
LO2: Understand and apply logical knowledge in Knowledge Graphs
```

Recommended final mapping:

```text
Focus:
LO2, LO7

Basic proficiency:
LO1, LO5, LO6, LO8, LO9, LO11, LO12

Limited discussion only:
LO4

Not included:
LO3, LO10
```
