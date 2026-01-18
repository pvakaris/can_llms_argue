import os
from collections import defaultdict
from pathlib import Path

from oracle.models.oracle_config import OUTPUT_DIR, ROOT_DIR
from shared.parser import write_json_file, read_json_file

def analyze_metadata_files():
    sums = defaultdict(float)
    counts = defaultdict(int)

    if ROOT_DIR and ROOT_DIR != "NONE":
        root = Path(ROOT_DIR)
    else:
        root = Path(__file__).resolve().parents[3]
    output_path = root / OUTPUT_DIR

    if not output_path.exists():
        print(f"Output directory {output_path} does not exist")
        return

    file_counter = 0
    for file in os.listdir(output_path):
        if file.endswith("metadata.json"):
            path = os.path.join(output_path, file)
            data = read_json_file(path)
            file_counter += 1
            for key, value in data.items():
                if key == "model":
                    continue

                if isinstance(value, (int, float)):
                    sums[key] += value
                    counts[key] += 1

    averages = {key: (sums[key] / counts[key]) for key in sums}

    output = {
        "sums": dict(sums),
        "averages": averages,
        "files_analysed": file_counter
    }

    output_path = os.path.join(output_path, "analysis.json")
    write_json_file(output_path, output)

def main(argv=None):
    print("Analysing metadata files...")
    analyze_metadata_files()
    print("Exiting...")

if __name__ == "__main__":
    main()