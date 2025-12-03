import datetime
from pathlib import Path

from .dataset_parser import get_aif_graph_from_path, find_pairs
from .ged_calculator import compute_ged_from_aif_graphs
from .test_config import GED_TIMEOUT, GED_ROUND_FLOAT_TO, PRINT_RESULT, SAVE_AS_CSV, ORACLE_FILE_POSTFIX, RESOURCES_DIR, \
    RESULT_FILE_PREFIX, ADD_DATE_TO_RESULTS_FILE_POSTFIX
from shared.helper import format_elapsed_time
import csv
from typing import Any, Dict, List

"""
    Uses benchmark_tester_config and resources folder to measure GED between pairs of AIF graphs
"""
def calculate_ged():

    resources_dir = Path(__file__).resolve().parents[3] / RESOURCES_DIR

    if not resources_dir.exists():
        print(f"Resources directory {RESOURCES_DIR} not found")
        return None

    pairs = find_pairs(resources_dir)
    if not pairs:
        print(f"No AIF graph pairs found in {RESOURCES_DIR} directory (expected <name>.json and <name>{ORACLE_FILE_POSTFIX}.json).")
        return None

    results: List[Dict[str, Any]] = []

    print(f"Starting the comparison of all the pairs in {RESOURCES_DIR} directory...")
    for bench_path, oracle_path in pairs:

        graph_a = get_aif_graph_from_path(str(bench_path))
        graph_b = get_aif_graph_from_path(str(oracle_path))

        ged_value, elapsed = compute_ged_from_aif_graphs(
            graph_a,
            graph_b,
            timeout=GED_TIMEOUT,
            round_digits=GED_ROUND_FLOAT_TO
        )

        results.append({
            "benchmark_graph": bench_path.name,
            "oracle_graph": oracle_path.name,
            "ged": ged_value,
            "elapsed": elapsed,
        })

        if PRINT_RESULT:
            print(f"\nComparing {bench_path.name} with {oracle_path.name}")
            if ged_value != -1.0:
                print("  GED:", ged_value)
                print("  Elapsed:", format_elapsed_time(elapsed))

    if SAVE_AS_CSV:
        postfix = f"_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}" if ADD_DATE_TO_RESULTS_FILE_POSTFIX else ""
        out_csv = resources_dir / "ged_results" / f"{RESULT_FILE_PREFIX}{postfix}.csv"
        out_csv.parent.mkdir(parents=True, exist_ok=True)

        with out_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["benchmark_graph", "oracle_graph", "ged", "elapsed"])
            for r in results:
                writer.writerow([
                    r["benchmark_graph"],
                    r["oracle_graph"],
                    r["ged"],
                    r["elapsed"],
                ])
        if PRINT_RESULT:
            print(f"\nSaved results to {out_csv} successfully...")

    print("Finished the comparison...")
    return results

def main(argv=None):
    print("Starting the comparison tool with argv=", argv)
    calculate_ged()
    print("Exiting...")

if __name__ == "__main__":
    main()