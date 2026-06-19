# Knowledge Graph Schema

## Purpose

This file describes the schema of the Football Squad Management
Knowledge Graph.

The schema explains:

- node types
- relationship types
- important node attributes
- inferred graph knowledge
- how the graph supports squad-management decisions

The graph is built in:

```text
src/kg_builder.py
```

The main output graph is:

```text
outputs/graphs/squad_management_kg.graphml
```

The embedding-enriched graph is:

```text
outputs/graphs/squad_management_kg_with_embeddings.graphml
```

## Graph Type

The Knowledge Graph is built as a directed multigraph using NetworkX
`MultiDiGraph`.

This means relationships have a direction.

Example:

```text
Player -> PLAYS_FOR -> Team
Player -> HAS_DECISION -> SquadDecision
Player -> BLOCKED_BY_MAIN_PLAYER -> Player
```

A directed graph is used because KG relationships have semantic
direction. The multigraph model allows multiple relationship types to
coexist between the same ordered pair of entities. For example, one
player can both `COMPETES_WITH` and be `BLOCKED_BY_MAIN_PLAYER` by
another player without either edge overwriting the other.

For embeddings, an undirected copy of the graph is used only during
Node2Vec training.

## Node Types

The graph contains 9 node types:

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

## Player Nodes

Player nodes represent football players.

Each player node contains original and inferred attributes.

Important attributes include:

```text
player_name
raw_position
role_group
age
age_group
minutes_played
minutes_group
performance_score
performance_percentile
performance_level
same_role_team_average
competition_status
main_same_role_player
main_same_role_minutes
main_same_role_performance_percentile
main_same_role_performance_level
is_main_same_role_player
is_blocked_by_main_player
main_player_underperforming
decision
explanation
```

Player nodes are the central nodes of the graph.

## Team Nodes

Team nodes represent Premier League teams.

Example:

```text
Liverpool
Arsenal
Chelsea
Manchester City
```

Players are connected to teams through:

```text
Player -> PLAYS_FOR -> Team
```

Teams are also connected to the league through:

```text
Team -> PLAYS_IN -> League
```

## League Node

The graph contains one league node:

```text
eng Premier League
```

Players and teams connect to the league.

Relationships:

```text
Player -> PLAYS_IN -> League
Team -> PLAYS_IN -> League
```

## RoleGroup Nodes

RoleGroup nodes represent cleaned role groups derived from the
dataset's raw position values.

Role groups include:

```text
Goalkeeper
Defender
Midfielder
Forward
DefMidWingBack
AttMidWinger
WingBack
```

Players connect to role groups through:

```text
Player -> HAS_ROLE -> RoleGroup
```

Role groups are important because performance scoring and squad
competition are calculated inside the same role group.

## AgeGroup Nodes

AgeGroup nodes represent inferred age categories.

Age groups:

```text
Young
Prime
Senior
CriticalAge
```

Mapping:

```text
age < 23       -> Young
age <= 29      -> Prime
age <= 32      -> Senior
age > 32       -> CriticalAge
```

Relationship:

```text
Player -> HAS_AGE_GROUP -> AgeGroup
```

## MinutesGroup Nodes

MinutesGroup nodes represent inferred playing-time categories.

Minutes groups:

```text
LowMinutes
MediumMinutes
HighMinutes
```

Mapping:

```text
minutes < 900        -> LowMinutes
minutes <= 1800      -> MediumMinutes
minutes > 1800       -> HighMinutes
```

Relationship:

```text
Player -> HAS_MINUTES_GROUP -> MinutesGroup
```

## PerformanceLevel Nodes

PerformanceLevel nodes represent inferred role-based performance
categories.

Performance levels:

```text
Good
Promising
Average
Poor
```

Mapping:

```text
performance_percentile >= 60       -> Good
50 <= performance_percentile < 60  -> Promising
40 <= performance_percentile < 50  -> Average
performance_percentile < 40        -> Poor
```

Relationship:

```text
Player -> HAS_PERFORMANCE_LEVEL -> PerformanceLevel
```

## CompetitionStatus Nodes

CompetitionStatus nodes represent whether a player is competitive
inside their team and role group.

Values:

```text
Competitive
Blocked
```

Mapping:

```text
performance_score >= same_role_team_average -> Competitive
performance_score < same_role_team_average  -> Blocked
```

Relationship:

```text
Player -> HAS_COMPETITION_STATUS -> CompetitionStatus
```

## SquadDecision Nodes

SquadDecision nodes represent the final squad-management
recommendation.

Decision values:

```text
Keep
Give More Chances
Loan
Sell
Monitor
```

Relationship:

```text
Player -> HAS_DECISION -> SquadDecision
```

## Relationship Types

The base graph contains these relationship types:

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

The embedding-enriched graph also adds:

```text
SIMILAR_TO
```

## PLAYS_FOR

```text
Player -> PLAYS_FOR -> Team
```

The player belongs to a team.

Example:

```text
Mohamed Salah -> PLAYS_FOR -> Liverpool
```

## PLAYS_IN

```text
Player -> PLAYS_IN -> League
Team -> PLAYS_IN -> League
```

The player or team belongs to the Premier League.

Example:

```text
Liverpool -> PLAYS_IN -> eng Premier League
```

## HAS_ROLE

```text
Player -> HAS_ROLE -> RoleGroup
```

The player is assigned to a cleaned role group.

Example:

```text
Mohamed Salah -> HAS_ROLE -> Forward
```

## HAS_AGE_GROUP

```text
Player -> HAS_AGE_GROUP -> AgeGroup
```

The player is assigned to an inferred age group.

Example:

```text
Mohamed Salah -> HAS_AGE_GROUP -> Senior
```

## HAS_MINUTES_GROUP

```text
Player -> HAS_MINUTES_GROUP -> MinutesGroup
```

The player is assigned to a playing-time category.

Example:

```text
Mohamed Salah -> HAS_MINUTES_GROUP -> HighMinutes
```

## HAS_PERFORMANCE_LEVEL

```text
Player -> HAS_PERFORMANCE_LEVEL -> PerformanceLevel
```

The player is assigned to a role-based performance level.

Example:

```text
Mohamed Salah -> HAS_PERFORMANCE_LEVEL -> Good
```

## HAS_COMPETITION_STATUS

```text
Player -> HAS_COMPETITION_STATUS -> CompetitionStatus
```

The player is either competitive or blocked compared with same-role
teammates.

Example:

```text
Conor Bradley -> HAS_COMPETITION_STATUS -> Blocked
```

## HAS_DECISION

```text
Player -> HAS_DECISION -> SquadDecision
```

The player receives a final squad-management decision.

Example:

```text
Conor Bradley -> HAS_DECISION -> Loan
```

## COMPETES_WITH

```text
Player -> COMPETES_WITH -> Player
```

Two players are in the same team and same role group.

Because the graph is directed, this relationship is added in both
directions.

Example:

```text
Mohamed Salah -> COMPETES_WITH -> Diogo Jota
Diogo Jota -> COMPETES_WITH -> Mohamed Salah
```

## BLOCKED_BY_MAIN_PLAYER

```text
Player -> BLOCKED_BY_MAIN_PLAYER -> Player
```

A player is blocked by the main player in the same team and role group.

The main player is the player with the most minutes in the same team
and role group.

A player is blocked if:

```text
player is not the main same-role player
AND player has fewer minutes than the main same-role player
AND player has a lower performance score than the main same-role player
```

This relationship is particularly notable because it transforms an
analytical calculation into an explicit graph structure that supports
transparent reasoning.

Examples:

```text
Conor Bradley -> BLOCKED_BY_MAIN_PLAYER -> Virgil van Dijk
Jayden Danns -> BLOCKED_BY_MAIN_PLAYER -> Ryan Gravenberch
Darwin Núñez -> BLOCKED_BY_MAIN_PLAYER -> Mohamed Salah
Andrew Robertson -> BLOCKED_BY_MAIN_PLAYER -> Virgil van Dijk
```

## SIMILAR_TO

```text
Player -> SIMILAR_TO -> Player
```

This relationship is added only in the embedding-enriched graph.

It is created using:

```text
Node2Vec embeddings
cosine similarity
same-role player filtering
```

The system finds the top 3 similar players for each player within
the same role group.

The similarity is structural rather than stylistic. Players who share
similar graph neighborhoods — same role group, similar performance
level, similar competition situation — end up with similar embeddings.

The embedding-enriched graph remains a `MultiDiGraph`, so `SIMILAR_TO`
edges can coexist with relationships such as `COMPETES_WITH` and
`BLOCKED_BY_MAIN_PLAYER`.

Example:

```text
Mohamed Salah -> SIMILAR_TO -> Cody Gakpo
Mohamed Salah -> SIMILAR_TO -> Luis Díaz
```

## Base KG Statistics

Graph file: squad_management_kg.graphml

```text
608 nodes
7794 edges
9 node types
10 relationship types
```

## Embedding-Enriched KG Statistics

Graph file: squad_management_kg_with_embeddings.graphml

```text
608 nodes
9480 edges
9 node types
11 relationship types
1686 SIMILAR_TO edges
```

The number of SIMILAR_TO edges comes from:

```text
562 players × 3 similar players = 1686 similarity rows
```

## Why This Schema Supports the Project

The schema supports squad-management decisions because it combines:

```text
raw football data
role groups
inferred performance levels
same-role competition
blocked-player reasoning
final decisions
embedding-based similarity
```

The graph does not only store original data. It also stores inferred
knowledge that supports explainable decisions.

## Main Portfolio Message

```text
The graph models players, teams, role groups, performance categories,
squad decisions, and same-role competition. The BLOCKED_BY_MAIN_PLAYER
relationship makes the decision reasoning explicit in the graph.
```
