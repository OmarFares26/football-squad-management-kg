# Logic-based Representation

This folder contains the rule-based squad reasoning stage.

## Input

- `2 - construction/data/processed/player_scores.csv`

## Script

- `src/rule_engine.py`: derives squad context, applies ordered decision
  rules, and creates explanations

## Outputs

- `results/player_decisions.csv`
- `results/squad_decisions_all_players.csv`
- `results/decision_counts.csv`
- `results/decision_by_role.csv`

The decision output is used by the construction stage when building the
Knowledge Graph.

Run this stage as part of the full pipeline from the project root:

```bash
python run_pipeline.py
```
