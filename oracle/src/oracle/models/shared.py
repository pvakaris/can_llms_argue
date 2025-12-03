from pathlib import Path

from oracle.models.oracle_config import ORACLE_FILE_POSTFIX, OUTPUT_DIR, PROMPT_CONFIG_FILE, INPUT_DIR, USE_INPUT_DIR, \
    PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG
from shared.parser import read_txt_file, extract_last_json_or_error, extract_last_json
from typing import Callable, Optional, Dict, Any
import json

def make_prompt(config: str, text: str) -> str:
    return f"{config}\n\nText to draw the graph from:\n\"\"\"{text}\"\"\"\n\n\"\"\""

def process_file(path: Path, output_path: Path, prompt_config_text: str, query_fn: Callable[[str], Optional[str]]) -> None:
    print(f"Processing file: {path.name}")
    text = read_txt_file(str(path))
    if not text:
        print(f" - Skipping {path.name}: empty or unreadable.")
        return

    prompt = make_prompt(prompt_config_text, text)

    if PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG:
        print("Model input:")
        print(prompt)

    output: Optional[str] = None
    try:
        print("Querying...")
        output = query_fn(prompt)
        print("The query was successful" if output is not None else "No response returned")
    except Exception as e:
        print("Querying failed with error: ", e)
        output = None

    if PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG:
        print("Model output:")
        print(output)

    parsed_output = extract_last_json(output)

    if PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG:
        print("Parsed model output as JSON:")
        print(parsed_output)

    base_name = path.stem
    out_name = f"{base_name}{ORACLE_FILE_POSTFIX}.json"
    out_path = output_path / out_name

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(parsed_output, f, indent=2, ensure_ascii=False)
        print(f"Wrote output to {OUTPUT_DIR}")
    except Exception as e:
        print(f"Failed to write output to file {OUTPUT_DIR}/{out_name}: {e}")


def interactive_mode(prompt_config: str,query_fn: Callable[[str], Optional[str]]) -> None:
    while True:
        print("Enter text to analyze (or 'exit' to quit):\n")
        user_input = input("> ")
        if user_input.lower() in ["exit", "quit"]:
            break

        prompt = make_prompt(prompt_config, user_input)

        output: Optional[str] = None
        try:
            print("\nPrompting...\n")
            output = query_fn(prompt)
            print("The prompt was successful" if output is not None else "No response returned")
        except Exception as e:
            print("Prompting failed with error:", e)
            output = None

        if PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG:
            print("Model output:")
            print(output)

        parsed_output: Dict[str, Any] = extract_last_json_or_error(output)

        if PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG:
            print("Parsed model output as JSON:")
            print(parsed_output)

        print("\n=== Extracted AIF graph ===\n")
        print(json.dumps(parsed_output, indent=2, ensure_ascii=False))
        print("\n----------------------------------------\n")

def run_with_query(
    query_fn: Callable[[str], Optional[str]],
    root: Optional[Path] = None,
    input_dir: str = INPUT_DIR,
    output_dir: str = OUTPUT_DIR,
    use_input_dir: bool = USE_INPUT_DIR,
) -> None:
    if root is None:
        root = Path(__file__).resolve().parents[3]

    prompt_config_path = root / PROMPT_CONFIG_FILE
    prompt_config_text = read_txt_file(prompt_config_path)

    if use_input_dir:
        input_path = root / input_dir
        output_path = root / output_dir
        output_path.mkdir(parents=True, exist_ok=True)

        if not input_path.exists():
            print(f"Input directory {input_path} does not exist. Exiting.")
            return

        txt_files = sorted([p for p in input_path.iterdir() if p.is_file() and p.suffix.lower() == ".txt"])
        if not txt_files:
            print(f"No .txt files found in {input_path}. Exiting.")
            return

        for in_path in txt_files:
            process_file(
                path=in_path,
                output_path=output_path,
                prompt_config_text=prompt_config_text,
                query_fn=query_fn,
            )

        print("\nAll files processed. Exiting...")

    else:
        interactive_mode(prompt_config_text, query_fn)
        print("Exiting...")
