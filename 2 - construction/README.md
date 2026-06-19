# 2 - KG Construction

Prepares the dataset and builds the base Knowledge Graph.

## Input

```text
data/raw/players_data_light-2024_2025.csv
```

## Scripts

- `src/data_exploration.py`: inspects the source data
- `src/data_preprocessing.py`: cleans players and creates role groups
- `src/performance_scoring.py`: calculates role-based performance scores
- `src/kg_builder.py`: builds the base `MultiDiGraph`
- `src/kg_queries.py`: runs example queries

KG construction also uses
`4 - logic/results/player_decisions.csv`.

## Outputs

- `data/processed/`: cleaned and scored player tables
- `graphs/squad_management_kg.graphml`: base Knowledge Graph
- `results/`: exploration, KG statistics, and query outputs
- `docs/kg_schema.md`: node, relationship, and graph-model documentation

Run this section through the root command: `python run_pipeline.py`.
