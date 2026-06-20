# Football Squad Management Knowledge Graph

This project builds a Knowledge Graph from 2024/25 football statistics.
It produces squad decisions, graph queries, similar-player results, a
KG-backed service, and an RDF export.

Each player receives one decision:

- Keep
- Give More Chances
- Loan
- Sell
- Monitor

## Pipeline

```text
Raw data -> preprocessing -> scoring -> rules -> KG construction
-> Node2Vec -> graph queries -> service -> model comparison and RDF export
```

## Structure

```text
2 - construction/   dataset, preprocessing, scoring, base KG, and queries
3 - ML/             Node2Vec embeddings and embedding-enriched KG
4 - logic/          rule-based reasoning and inferred decisions
5 - reflection/     KG service, data-model comparison, and LO reflection
```

Each numbered folder contains its own `README.md`.

## Setup

Python 3.12 was used during development.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows:

```text
.venv\Scripts\activate
```

The included dataset is located at:

```text
2 - construction/data/raw/players_data_light-2024_2025.csv
```

## Run

From the project root:

```bash
python run_pipeline.py
```

The nine-stage pipeline takes approximately 15-20 seconds. A successful
run ends with:

```text
Pipeline completed successfully
Stages completed: 9
```

The main generated artifacts are located in:

```text
2 - construction/graphs/   base Knowledge Graph
2 - construction/results/  KG statistics and query results
3 - ML/graphs/             embedding and replacement-enriched graphs
3 - ML/results/            embeddings and similar-player results
4 - logic/results/         rule-based squad decisions
5 - reflection/graphs/     RDF/Turtle export
5 - reflection/results/    service and data-model comparison outputs
```

Detailed explanations and learning-outcome evidence are provided in
the portfolio PDF.
