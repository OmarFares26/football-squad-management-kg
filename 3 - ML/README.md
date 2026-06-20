# 3 - ML-based Representation

Creates Node2Vec embeddings and adds `SIMILAR_TO` relationships.

## Input

```text
2 - construction/graphs/squad_management_kg.graphml
```

## Script

`src/embeddings.py` trains 32-dimensional embeddings on an undirected
copy of the KG and finds the top three similar players per role group.

## Outputs

- `results/player_embeddings.csv`: 562 player vectors
- `results/player_embedding_similarities.csv`: 1,686 similarity rows
- `graphs/squad_management_kg_with_embeddings.graphml`: enriched KG
- `graphs/squad_management_kg_with_replacements.graphml`: enriched KG with
  materialized `RECOMMENDED_REPLACEMENT` traversal results
- `results/kg_with_embeddings_*.csv`: graph statistics

Run this section through the root command: `python run_pipeline.py`.
