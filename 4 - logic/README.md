# 4 - Logic-based Representation

Derives explainable squad-management decisions from scored player data.

## Input

```text
2 - construction/data/processed/player_scores.csv
```

## Script

`src/rule_engine.py` derives:

- age and minutes groups
- same-team, same-role competition context
- the main player for each team and role
- blocked-player and underperforming-main-player indicators
- Keep, Give More Chances, Loan, Sell, or Monitor decisions

Rules are applied in a fixed priority order. The complete definitions
are in `docs/decision_rules.md`.

## Outputs

- `results/player_decisions.csv`: complete inferred decision data
- `results/squad_decisions_all_players.csv`: readable decision table
- `results/decision_counts.csv`: overall decision counts
- `results/decision_by_role.csv`: counts by role group

`player_decisions.csv` is then used by the construction section to add
inferred attributes and relationships to the KG.

Run this section through the root command: `python run_pipeline.py`.
