# Football Squad Management Knowledge Graph

This project builds a Football Squad Management Knowledge Graph using 2024/25 football player statistics.

The goal is to create a Knowledge Graph that connects players, teams, leagues, positions, season statistics, inferred performance categories, squad context, and final squad-management decisions.

The system recommends one decision for each player:

- Keep
- Give More Chances
- Loan
- Sell
- Monitor

## Project Pipeline

Raw player statistics
-> Data preprocessing
-> Performance scoring
-> Rule-based reasoning
-> Knowledge Graph construction
-> Knowledge Graph queries and squad-decision service output
-> Embedding enrichment and similar-player search
-> Data model comparison and RDF/Turtle export

## Portfolio Structure

The repository follows the lecturer's example portfolio structure:

```text
2 - construction/   dataset, preprocessing, scoring, base KG, and queries
3 - ML/             Node2Vec embeddings and embedding-enriched KG
4 - logic/          rule-based reasoning and inferred decisions
5 - reflection/     KG service, data-model comparison, and LO reflection
```

Each numbered folder contains its own `README.md`.

## Running the Project

Run the complete pipeline from the project root:

```bash
python run_pipeline.py
```

Before running the pipeline, place the raw dataset at:

```text
2 - construction/data/raw/players_data_light-2024_2025.csv
```

The pipeline executes all nine stages in dependency order and stops if
any stage fails. Generated artifacts remain in the numbered section
that provides the corresponding portfolio evidence.

The repository includes the dataset and generated graph artifacts so
the submitted ZIP is self-contained and reproducible.

## Implementation Notes

- The KG uses a directed NetworkX `MultiDiGraph`, allowing multiple
  relationships such as `COMPETES_WITH` and
  `BLOCKED_BY_MAIN_PLAYER` between the same entities.
- The squad-decision service loads and queries the generated GraphML
  KG rather than reading the processed decision CSV directly.
- The LO4 comparison stage inspects the project’s CSV, `MultiDiGraph`,
  RDF/Turtle, embedding, and temporal-design representations. It writes
  `data_model_comparison.csv`, `data_model_comparison_examples.csv`,
  and `squad_management_kg.ttl`.

## Learning Outcome Mapping

The two focus learning outcomes are:

- LO2: Logical rule-based squad decisions
- LO7: Creation of the football squad Knowledge Graph

The project demonstrates basic proficiency in:

- LO1: Knowledge Graph embeddings
- LO4: Comparison of KG data models
- LO5: Knowledge Graph architectures
- LO6: Scalable reasoning methods in Knowledge Graphs
- LO8: Knowledge Graph evolution
- LO9: Real-world Knowledge Graph applications
- LO11: Services through a Knowledge Graph
- LO12: Connections between Knowledge Graphs, ML, and AI

LO3 (Graph Neural Networks) and LO10 (financial Knowledge Graph
applications) are not claimed.
