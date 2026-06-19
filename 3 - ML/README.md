# 3 - ML-based Representation

This section contains the Node2Vec representation of the Knowledge Graph.

## Contents

- `src/embeddings.py`: trains 32-dimensional Node2Vec embeddings
- `graphs/`: the KG enriched with `SIMILAR_TO` relationships
- `results/player_embeddings.csv`: one vector per player
- `results/player_embedding_similarities.csv`: top same-role similarities
- `results/kg_with_embeddings_*.csv`: enriched graph statistics

The script reads the base graph from `2 - construction/graphs/` and is
normally executed through the root `run_pipeline.py`.
