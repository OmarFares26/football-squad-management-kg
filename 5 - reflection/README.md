# Reflection and Service

This folder contains the KG-backed service output, data-model
comparison, and RDF export stages.

## Inputs

- `2 - construction/graphs/squad_management_kg.graphml`
- `2 - construction/data/processed/premier_league_players.csv`
- `3 - ML/results/player_embeddings.csv`

## Scripts

- `src/service_output.py`: queries the GraphML KG to create a squad
  decision service output
- `src/data_model_comparison.py`: compares project representations and
  exports the graph as RDF/Turtle

## Outputs

- `results/`: service and data-model comparison tables
- `graphs/squad_management_kg.ttl`

Run this stage as part of the full pipeline from the project root:

```bash
python run_pipeline.py
```
