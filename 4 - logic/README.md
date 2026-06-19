# 4 - Logic-based Representation

This section contains the rule-based squad decision logic.

## Contents

- `src/rule_engine.py`: derives competition context and squad decisions
- `docs/decision_rules.md`: rule definitions, priority, and limitations
- `results/player_decisions.csv`: complete inferred decision data
- `results/squad_decisions_all_players.csv`: portfolio-facing decision table
- `results/decision_*.csv`: decision summaries

The rule engine reads scored players from `2 - construction/data/processed/`.
Its output is then used to construct the base Knowledge Graph.
