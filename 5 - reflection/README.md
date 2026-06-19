# 5 - Reflection and Service

Contains the KG-backed service, data-model comparison, RDF export, and
supporting portfolio notes.

## Inputs

- `2 - construction/graphs/squad_management_kg.graphml`
- `2 - construction/data/processed/premier_league_players.csv`
- `3 - ML/results/player_embeddings.csv`

## Scripts

- `src/service_output.py`: creates Liverpool recommendations from the KG
- `src/data_model_comparison.py`: compares CSV, property graph, RDF,
  vectors, and a future temporal design

## Outputs

- `results/liverpool_squad_decision_service.csv`
- `results/liverpool_squad_decision_summary.csv`
- `results/data_model_comparison.csv`
- `results/data_model_comparison_examples.csv`
- `graphs/squad_management_kg.ttl`: RDF/Turtle export

## Documentation

- `docs/learning_outcomes.md`: final LO evidence and mapping
- `docs/portfolio_notes.md`: project narrative and limitations

Run this section through the root command: `python run_pipeline.py`.
The full academic discussion is provided in the portfolio PDF.
