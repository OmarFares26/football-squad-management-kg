# 2 - KG Construction

This section contains the dataset preparation, scoring, base Knowledge
Graph construction, and graph query examples.

## Contents

- `src/`: exploration, preprocessing, scoring, KG construction, and queries
- `data/raw/`: expected location of the source dataset
- `data/processed/`: cleaned and scored player tables
- `graphs/`: the base GraphML Knowledge Graph
- `results/`: exploration, KG statistics, and query outputs
- `docs/kg_schema.md`: node, relationship, and graph-model documentation

The raw dataset must be placed at:

```text
2 - construction/data/raw/players_data_light-2024_2025.csv
```

Run the complete project from the repository root:

```bash
python run_pipeline.py
```
