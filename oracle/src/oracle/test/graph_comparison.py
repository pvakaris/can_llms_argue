import datetime
from pathlib import Path
from statistics import mean

from shared.parser import write_json_file
from .dataset_parser import get_aif_graph_from_path, find_pairs
from .ged_calculator import compute_ged_from_aif_graphs
from .test_config import GED_TIMEOUT, GED_ROUND_FLOAT_TO, PRINT_RESULT, SAVE_AS_CSV, ORACLE_FILE_POSTFIX, RESOURCES_DIR, \
    RESULT_FILE_PREFIX, ADD_DATE_TO_RESULTS_FILE_POSTFIX, ROOT_DIR
from shared.helper import format_elapsed_time
import csv
from typing import Any, Dict, List

"""
    Uses benchmark_tester_config and resources folder to measure GED between pairs of AIF graphs
"""
def calculate_ged():
    if ROOT_DIR and ROOT_DIR != "NONE":
        root = Path(ROOT_DIR)
    else:
        root = Path(__file__).resolve().parents[3]
    resources_dir = root / RESOURCES_DIR

    if not resources_dir.exists():
        print(f"Resources directory {RESOURCES_DIR} not found")
        return None

    pairs = find_pairs(resources_dir)
    if not pairs:
        print(f"No AIF graph pairs found in {RESOURCES_DIR} directory (expected <name>.json and <name>{ORACLE_FILE_POSTFIX}.json).")
        return None

    print(f"Starting the comparison of all the pairs in {RESOURCES_DIR} directory...")
    results: List[Dict[str, Any]] = compute_pair_results(pairs)

    if SAVE_AS_CSV:
        postfix = f"_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}" if ADD_DATE_TO_RESULTS_FILE_POSTFIX else ""
        out_csv = resources_dir / "ged_results" / f"{RESULT_FILE_PREFIX}{postfix}.csv"
        out_csv.parent.mkdir(parents=True, exist_ok=True)

        with out_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["benchmark_graph", "oracle_graph", "ged", "elapsed", "notes"])
            for r in results:
                writer.writerow([
                    r["benchmark_graph"],
                    r["oracle_graph"],
                    r["ged"],
                    r["elapsed"],
                    r["notes"],
                ])
        write_results_summary_json(results, resources_dir)
        if PRINT_RESULT:
            print(f"\nSaved results to ged_results/{RESULT_FILE_PREFIX}{postfix}.csv successfully...")

    print("Finished the comparison...")
    return results

def compute_pair_results(pairs) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for bench_path, oracle_path in pairs:
        graph_a = get_aif_graph_from_path(str(bench_path))
        graph_b = get_aif_graph_from_path(str(oracle_path))

        if graph_a is None or graph_b is None:
            ged_value = -1
            elapsed = -1
            notes = "Corrupt json"
        else:
            ged_value, elapsed = compute_ged_from_aif_graphs(
                graph_a,
                graph_b,
                timeout=GED_TIMEOUT,
                round_digits=GED_ROUND_FLOAT_TO
            )
            notes = "Success"

        results.append({
            "benchmark_graph": bench_path.name,
            "oracle_graph": oracle_path.name,
            "ged": ged_value,
            "elapsed": elapsed,
            "notes": notes
        })

        if PRINT_RESULT:
            print(f"\nComparing {bench_path.name} with {oracle_path.name}")
            if ged_value != -1.0:
                print("  GED:", ged_value)
                print("  Elapsed:", format_elapsed_time(elapsed))
    return results

def write_results_summary_json(results, resources_dir):
    total_comparisons = len(results)

    successful = [
        r for r in results
        if r.get("ged") != -1 and r.get("elapsed") != -1
    ]

    failed_comparisons = total_comparisons - len(successful)
    successful_comparisons = len(successful)

    if successful_comparisons > 0:
        average_ged = mean(r["ged"] for r in successful)
        average_elapsed = mean(r["elapsed"] for r in successful)
        total_elapsed = sum(r["elapsed"] for r in successful)
    else:
        average_ged = 0.0
        average_elapsed = 0.0
        total_elapsed = 0.0

    summary = {
        "average_ged": average_ged,
        "average_elapsed": average_elapsed,
        "total_elapsed": total_elapsed,
        "total_comparisons": total_comparisons,
        "successful_comparisons": successful_comparisons,
        "failed_comparisons": failed_comparisons,
    }

    postfix = f"_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}" if ADD_DATE_TO_RESULTS_FILE_POSTFIX else ""
    out_json = resources_dir / "ged_results" / f"{RESULT_FILE_PREFIX}{postfix}.json"
    write_json_file(out_json, summary)
    if PRINT_RESULT:
        print(f"Saved result summary to ged_results/{RESULT_FILE_PREFIX}{postfix}.json successfully...")

def main(argv=None):
    print("Starting the comparison tool with argv=", argv)
    calculate_ged()
    print("Exiting...")

if __name__ == "__main__":
    main()