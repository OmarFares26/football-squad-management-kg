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

Run the complete pipeline from the project root:

```bash
python run_pipeline.py
```

Before running the pipeline, place the raw dataset at:

```text
data/raw/players_data_light-2024_2025.csv
```

The pipeline executes all stages in dependency order and stops immediately if any stage fails. Generated graphs are written to outputs/graphs/, and generated results are written to outputs/results/.

## Main Learning Outcomes

The project targets the following learning outcomes:

- LO1: Knowledge Graph embeddings
- LO2: Logical knowledge in Knowledge Graphs
- LO4: Knowledge Graph data models
- LO5: Knowledge Graph architectures
- LO6: Scalable reasoning methods in Knowledge Graphs
- LO7: Knowledge Graph creation
- LO8: Knowledge Graph evolution
- LO9: Real-world Knowledge Graph applications
- LO11: Services through a Knowledge Graph
- LO12: Connections between Knowledge Graphs, ML, and AI

The two main exceeded learning outcomes are planned to be:

- LO2: Logical rule-based squad decisions
- LO7: Creation of the football squad Knowledge Graph
