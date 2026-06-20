# Football Squad Management Knowledge Graph

This project builds a Knowledge Graph from football player, team, and
performance data to support explainable squad-management decisions. The
pipeline preprocesses the dataset, calculates role-based performance,
applies decision rules, constructs and queries the graph, creates
Node2Vec embeddings, produces a KG-backed service output, and exports an
RDF representation.

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

From the project root:

```bash
python run_pipeline.py
```

## Project Structure

```text
2 - construction/   data preparation, scoring, KG construction, and queries
3 - ML/             Node2Vec embeddings and graph enrichment
4 - logic/          rule-based squad reasoning and decision outputs
5 - reflection/     KG-backed service, RDF export, and model comparison
run_pipeline.py     runs the complete pipeline
requirements.txt    Python dependencies
```

Each numbered folder contains a short README describing its inputs,
scripts, and generated artifacts.
