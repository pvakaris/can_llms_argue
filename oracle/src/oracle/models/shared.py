import time
from pathlib import Path

from oracle.models.oracle_config import ORACLE_FILE_POSTFIX, OUTPUT_DIR, INPUT_DIR, USE_INPUT_DIR, \
    PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG, METADATA_FILE_POSTFIX, ROOT_DIR
from shared.parser import read_txt_file, extract_last_json_or_error, extract_last_json, write_json_file
from typing import Callable, Optional, Dict, Any
import json

def run_with_query(
    query_fn: Callable[[str], Optional[Dict[str, Any]]],
    make_prompt_fn: Callable[[str], str],
    input_dir: str = INPUT_DIR,
    output_dir: str = OUTPUT_DIR,
    use_input_dir: bool = USE_INPUT_DIR,
) -> None:
    if ROOT_DIR and ROOT_DIR != "NONE":
        root = Path(ROOT_DIR)
    else:
        root = Path(__file__).resolve().parents[3]

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
                query_fn=query_fn,
                make_prompt_fn=make_prompt_fn,
            )

        print("\nAll files processed. Exiting...")

    else:
        interactive_mode(query_fn, make_prompt_fn)
        print("Exiting...")

def process_file(path: Path, output_path: Path, query_fn: Callable[[str], Optional[Dict[str, Any]]], make_prompt_fn: Callable[[str], str]) -> None:
    print(f"Processing file: {path.name}")
    text = read_txt_file(str(path))
    if not text:
        print(f" - Skipping {path.name}: empty or unreadable.")
        return

    prompt = make_prompt_fn(text)

    if PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG:
        print("Model input:")
        print(prompt)

    output: Optional[Dict[str, Any]] = None
    elapsed_time = 0
    try:
        print("Querying...")
        start = time.time()
        output = query_fn(prompt)
        elapsed_time = time.time() - start
        print("The query was successful" if output is not None else "No response returned")
    except Exception as e:
        print("Querying failed with error: ", e)
        output = None

    if PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG:
        print("Model output:")
        print(output)

    message = output.get("message")
    metadata = output.get("metadata")
    parsed_message = extract_last_json(message)

    if PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG:
        print("Parsed model output as JSON:")
        print(parsed_message)

    base_name = path.stem
    try:
        message_out_name = f"{base_name}{ORACLE_FILE_POSTFIX}.json"
        message_out_path = output_path / message_out_name
        write_json_file(message_out_path, parsed_message)

        if metadata is not None:
            metadata["elapsed_time"] = elapsed_time
            meta_out_name = f"{base_name}{ORACLE_FILE_POSTFIX}{METADATA_FILE_POSTFIX}.json"
            meta_out_path = output_path / meta_out_name
            write_json_file(meta_out_path, metadata)
        print(f"Wrote output to {OUTPUT_DIR}")
    except Exception as e:
        print(f"Failed to write output to file {OUTPUT_DIR}/{message_out_name}: {e}")

def interactive_mode(query_fn: Callable[[str], Optional[Dict[str, Any]]], make_prompt_fn: Callable[[str], str]) -> None:
    while True:
        print("Enter text to analyze (or 'exit' to quit):\n")
        user_input = input("> ")
        if user_input.lower() in ["exit", "quit"]:
            break

        prompt = make_prompt_fn(user_input)

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

# OpenAI models if asked to return a json usually return the response as ```json{...the actual json}```
# This method cleans the response so that only the JSON object is returned
def clean_json(json_str: str) -> str:
    start = json_str.find("```")
    if start == -1:
        return json_str.strip()

    end = json_str.find("```", start + 3)
    if end == -1:
        return json_str.strip()

    content = json_str[start + 3:end]
    if content.lstrip().startswith("json"):
        content = content.lstrip()[4:]

    return content.strip()


