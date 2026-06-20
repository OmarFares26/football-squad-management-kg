# KG Construction

This folder contains the data preparation, performance scoring,
Knowledge Graph construction, and graph-query stages.

## Inputs

- `data/raw/players_data_light-2024_2025.csv`
- `4 - logic/results/player_decisions.csv`

## Scripts

- `src/data_exploration.py`: inspects the source dataset
- `src/data_preprocessing.py`: cleans the data and creates role groups
- `src/performance_scoring.py`: calculates role-based performance features
- `src/kg_builder.py`: builds and exports the base `MultiDiGraph`
- `src/kg_queries.py`: runs graph queries and replacement traversal

## Outputs

- `data/processed/`: cleaned and scored player data
- `graphs/`: the base GraphML Knowledge Graph
- `results/`: exploration, graph statistics, and query outputs

Run this stage as part of the full pipeline from the project root:

```bash
python run_pipeline.py
```
