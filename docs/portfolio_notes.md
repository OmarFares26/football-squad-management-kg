# Portfolio Notes

## Project Title

Football Squad Management Knowledge Graph

## Project Goal

The goal of this project is to build a Knowledge Graph that supports
football squad-management decisions.

The project uses player statistics from the 2024/2025 season and
transforms them into a graph-based decision-support system. The system
focuses on Premier League players and produces explainable squad
recommendations such as:

- Keep
- Give More Chances
- Loan
- Sell
- Monitor

The final service output focuses on Liverpool as an example squad.

## Main Idea

The main idea is not only to score individual players, but to compare
players inside their squad context.

A player is not judged only by isolated statistics. Instead, the system
considers:

- the player's role group
- the player's minutes played
- the player's role-based performance
- the player's age group
- the player's competition inside the same team and same role group
- whether the player is blocked by a main same-role player
- whether the main same-role player is underperforming

This allows the system to reason about squad decisions in a more
explainable way.

## Dataset

The project uses a football player statistics dataset for the 2024/2025
season sourced from FBref via Kaggle.

The original dataset contains players from the top five European leagues.
For this project, the data is filtered to Premier League players only,
producing 562 players across 20 clubs after deduplication.

The dataset provides useful player information such as:

- player name
- team
- league
- raw position
- age
- minutes played
- matches played
- goals
- assists
- expected goals
- expected assisted goals
- tackles
- interceptions
- clearances
- blocks
- goalkeeper statistics (saves, save percentage, clean sheets,
  goals conceded)

The dataset does not include contract length, salary, transfer value,
injuries, or future potential. Therefore, the project does not claim to
make professional transfer-market decisions.

## Position and Role Handling

The original dataset provides raw position values such as:

- GK
- DF
- MF
- FW
- DF,MF
- MF,FW
- DF,FW

These raw positions are mapped into role groups:

- Goalkeeper
- Defender
- Midfielder
- Forward
- DefMidWingBack
- AttMidWinger
- WingBack

The role group is used for:

- Knowledge Graph structure
- role-based performance scoring
- same-role competition analysis
- squad decision rules

This keeps the project simple and avoids claiming exact tactical
positions that the dataset does not provide.

The WingBack group is small (14 players) because very few Premier
League players carry a pure DF/FW designation. This is acknowledged
as a limitation of the dataset's position encoding.

## Pipeline Overview

The project pipeline is:

1. Data exploration
2. Data preprocessing
3. Role-based performance scoring
4. Rule-based squad decision reasoning
5. Knowledge Graph construction
6. Knowledge Graph query examples
7. Service-style squad decision output
8. Knowledge Graph embeddings using Node2Vec
9. Data model comparison and RDF/Turtle export

## Data Preprocessing

The preprocessing step filters the dataset to Premier League players
and keeps the useful columns for the project.

It also creates:

- player IDs
- team IDs
- cleaned role groups
- cleaned column names
- processed CSV output

Players who transferred between two Premier League clubs mid-season
appear twice in the raw data. The row with the most minutes is kept
and the duplicate is removed.

Output file:

```text
data/processed/premier_league_players.csv
```

## Performance Scoring

The performance scoring step creates role-based performance scores.

Different role groups are scored with different metrics.

Examples:

- Forwards are mainly scored using goals and assists per 90.
- Defenders are scored using tackles, interceptions, clearances,
  and blocks per 90.
- Goalkeepers are scored using save percentage, clean sheets per 90,
  and goals against per 90.
- Hybrid roles use a combination of defensive and attacking metrics.

All metrics are normalized between 0 and 1 within each role group
before combining. The final raw score is then normalized again within
each role group to produce a final performance score between 0 and 1.

The score is not intended to be a professional scouting model. It is a
simple, explainable scoring layer for the Knowledge Graph project.

Output file:

```text
data/processed/player_scores.csv
```

## Rule-Based Squad Decisions

The rule engine adds inferred squad-management context.

It creates:

- age groups
- minutes groups
- performance levels
- same-role team averages
- competition status
- main same-role player
- blocked-by-main-player status
- final squad decision

The core reasoning idea is:

```text
same team + same role group = squad competition
```

Examples:

```text
Young player + low minutes + blocked by main same-role player
= Loan

Low or medium minutes + good performance + main same-role player
underperforming = Give More Chances

High minutes + at least promising performance = Keep

High minutes + poor performance + older than 29 = Sell
```

Output files:

```text
data/processed/player_decisions.csv
outputs/results/squad_decisions_all_players.csv
outputs/results/decision_counts.csv
outputs/results/decision_by_role.csv
```

## Knowledge Graph

The Knowledge Graph is built as a directed NetworkX `MultiDiGraph`.
This preserves multiple semantic relationships between the same
ordered pair of entities. For example, `COMPETES_WITH` and
`BLOCKED_BY_MAIN_PLAYER` can coexist between two players.

It contains node types such as:

- Player
- Team
- League
- RoleGroup
- AgeGroup
- MinutesGroup
- PerformanceLevel
- CompetitionStatus
- SquadDecision

It contains relationship types such as:

- PLAYS_FOR
- PLAYS_IN
- HAS_ROLE
- HAS_AGE_GROUP
- HAS_MINUTES_GROUP
- HAS_PERFORMANCE_LEVEL
- HAS_COMPETITION_STATUS
- HAS_DECISION
- COMPETES_WITH
- BLOCKED_BY_MAIN_PLAYER

The BLOCKED_BY_MAIN_PLAYER relationship makes the same-role competition
reasoning explicit in the graph. It transforms an analytical calculation
into a first-class graph structure that supports transparent reasoning.

Output files:

```text
outputs/graphs/squad_management_kg.graphml
outputs/results/kg_stats.csv
outputs/results/kg_node_counts.csv
outputs/results/kg_edge_counts.csv
```

## KG Query Examples

The project includes query examples to show that the graph can be used.

Example queries include:

- Find players marked as Sell.
- Show squad decisions for Liverpool.
- Find same-role competitors for Mohamed Salah.
- Show selected Liverpool players blocked by main same-role players.

Important examples:

```text
Conor Bradley -> blocked by Virgil van Dijk -> Loan
Jayden Danns -> blocked by Ryan Gravenberch -> Loan
Darwin Núñez -> blocked by Mohamed Salah -> Monitor
Andrew Robertson -> blocked by Virgil van Dijk -> Sell
```

Query output files:

```text
outputs/results/query_sell_players.csv
outputs/results/query_liverpool_decisions.csv
outputs/results/query_mohamed_salah_competitors.csv
outputs/results/query_blocked_by_main_player.csv
outputs/results/query_liverpool_blocked_examples.csv
```

## Service Output

The service output loads and queries the generated GraphML Knowledge
Graph to create a clean squad decision table for Liverpool.

This represents a simple KG-backed service-like result where a team is
selected and squad-management recommendations are retrieved from
player nodes and graph relationships such as `PLAYS_FOR`, `HAS_ROLE`,
and `HAS_DECISION`.

The Liverpool output includes:

- player name
- role group
- age group
- minutes group
- performance level
- same-role competition context
- final decision
- explanation

Output files:

```text
outputs/results/liverpool_squad_decision_service.csv
outputs/results/liverpool_squad_decision_summary.csv
```

## Knowledge Graph Embeddings

The project applies Node2Vec to create Knowledge Graph embeddings.

The Knowledge Graph remains directed for semantic correctness, but an
undirected copy is used for Node2Vec training because Node2Vec learns
from graph neighborhoods and random walks.

The embeddings are used to:

- create vector representations of player nodes
- calculate cosine similarity between players
- find similar players within the same role group
- add SIMILAR_TO edges to an embedding-enriched graph

The similarity is structural rather than stylistic. Players who share
similar graph neighborhoods — same role group, similar performance
level, similar competition situation — end up with similar embeddings.

Output files:

```text
outputs/results/player_embeddings.csv
outputs/results/player_embedding_similarities.csv
outputs/graphs/squad_management_kg_with_embeddings.graphml
outputs/results/kg_with_embeddings_stats.csv
outputs/results/kg_with_embeddings_edge_counts.csv
```

## Important Limitation

The system should be presented as:

```text
Knowledge Graph creation + competition-aware rule-based squad
decision support + KG embeddings
```

It should not be presented as:

```text
accurate professional football scouting system
```

The project is explainable and useful for demonstrating Knowledge Graph
concepts, but it is limited by the available dataset.

The dataset does not include:

- contract information
- wages
- market value
- injury history
-
