from pathlib import Path
import subprocess
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_PATH = (
    PROJECT_ROOT
    / "2 - construction/data/raw/players_data_light-2024_2025.csv"
)

PIPELINE_STAGES = [
    ("Data exploration", "2 - construction/src/data_exploration.py"),
    ("Data preprocessing", "2 - construction/src/data_preprocessing.py"),
    ("Performance scoring", "2 - construction/src/performance_scoring.py"),
    ("Rule-based reasoning", "4 - logic/src/rule_engine.py"),
    ("Knowledge Graph construction", "2 - construction/src/kg_builder.py"),
    ("Embedding enrichment", "3 - ML/src/embeddings.py"),
    ("Knowledge Graph queries", "2 - construction/src/kg_queries.py"),
    ("KG-backed service output", "5 - reflection/src/service_output.py"),
    (
        "Data model comparison and RDF export",
        "5 - reflection/src/data_model_comparison.py",
    ),
]


def run_stage(stage_number: int, stage_name: str, script_path: str) -> None:
    """Run one pipeline stage."""

    print(flush=True)
    print(
        f"[{stage_number}/{len(PIPELINE_STAGES)}] {stage_name}",
        flush=True,
    )
    print("-" * (len(stage_name) + 6), flush=True)

    subprocess.run(
        [sys.executable, script_path],
        cwd=PROJECT_ROOT,
        check=True,
    )


def main() -> None:
    """Run the full pipeline in dependency order."""

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            "Raw dataset not found. Expected file: "
            f"{RAW_DATA_PATH.relative_to(PROJECT_ROOT)}"
        )

    start_time = time.perf_counter()

    print("Football Squad Management KG pipeline", flush=True)
    print("=====================================", flush=True)
    print(f"Python: {sys.executable}", flush=True)

    try:
        for stage_number, (stage_name, script_path) in enumerate(
            PIPELINE_STAGES,
            start=1,
        ):
            run_stage(stage_number, stage_name, script_path)
    except subprocess.CalledProcessError as error:
        print()
        print(
            f"Pipeline stopped because stage {error.cmd[-1]} "
            f"failed with exit code {error.returncode}.",
            file=sys.stderr,
        )
        raise SystemExit(error.returncode) from error

    elapsed_seconds = time.perf_counter() - start_time

    print()
    print("Pipeline completed successfully")
    print("===============================")
    print(f"Stages completed: {len(PIPELINE_STAGES)}")
    print(f"Elapsed time: {elapsed_seconds:.1f} seconds")
    print("Artifacts are organized in the numbered portfolio folders.")


if __name__ == "__main__":
    main()
