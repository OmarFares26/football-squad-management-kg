# ML-based Representation

This folder contains the graph-embedding and similarity-enrichment
stage.

## Input

- `2 - construction/graphs/squad_management_kg.graphml`

## Script

- `src/embeddings.py`: trains Node2Vec embeddings, calculates
  same-role player similarity, and adds `SIMILAR_TO` relationships

## Outputs

- `results/`: player embeddings, similarity results, and graph statistics
- `graphs/squad_management_kg_with_embeddings.graphml`
- `graphs/squad_management_kg_with_replacements.graphml`

Run this stage as part of the full pipeline from the project root:

```bash
python run_pipeline.py
```
