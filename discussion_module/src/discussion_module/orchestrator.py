import datetime
import json
from pathlib import Path

import requests

from discussion_module.discussion_config import HOST, BASE_PORT, PARTICIPANTS, CYCLES, MODEL, QUESTION, \
    PARTICIPANT_CONFIG, OUTPUT_LIMIT_PER_PARTICIPANT, PRINT_OUTPUT, OUTPUT_DIR, ADD_DATE_TO_RESULTS_FILE_POSTFIX
from shared.parser import read_txt_file, write_json_file


def build_endpoints(host, base_port, participants):
    return [
        f"{host}:{base_port + i}"
        for i in range(participants)
    ]

def chat(endpoint, model, messages):
    response = requests.post(
        f"{endpoint}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]

def print_results(transcript):
    try:
        print("Saving the results...")
        root = Path(__file__).resolve().parents[2]
        output_dir = root / OUTPUT_DIR

        postfix = f"_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}" if ADD_DATE_TO_RESULTS_FILE_POSTFIX else ""
        out_json = output_dir / f"discussion{postfix}.json"
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)
        if PRINT_OUTPUT:
            name = OUTPUT_DIR / f"discussion{postfix}.json"
            print(f"Structured transcript saved as JSON: {name}")

        out_txt = output_dir / f"discussion{postfix}.txt"
        with open(out_txt, "w", encoding="utf-8") as f:
            for entry in transcript:
                line = f"participant{entry['participant']}: {entry['answer']}\n"
                f.write(line)
        if PRINT_OUTPUT:
            name = OUTPUT_DIR / f"discussion{postfix}.json"
            print(f"Transcript saved as text: {name}")
        print("Results saved successfully...")
    except Exception as e:
        print("Failed to save results...")
        print(f"Error: {e}")

def run_discussion():
    print("Discussion started...")
    endpoints = build_endpoints(HOST, BASE_PORT, PARTICIPANTS)
    transcript = []
    last_answer = None
    turn = 1
    root = Path(__file__).resolve().parents[2]
    participant_config = read_txt_file(root / PARTICIPANT_CONFIG)

    if OUTPUT_LIMIT_PER_PARTICIPANT is not None:
        participant_config += f"\n{OUTPUT_LIMIT_PER_PARTICIPANT}"

    for cycle in range(CYCLES):
        if PRINT_OUTPUT:
            print(f"Cycle {cycle + 1}/{CYCLES}")
        for i, endpoint in enumerate(endpoints):
            messages = [
                {
                    "role": "system",
                    "content": participant_config
                },
                {
                    "role": "user",
                    "content": f"Question:\n{QUESTION}"
                },
            ]

            if last_answer:
                messages.append(
                    {
                        "role": "user",
                        "content": f"Previous answer:\n{last_answer}",
                    }
                )

            answer = chat(endpoint, MODEL, messages)
            entry = {
                "turn": turn,
                "cycle": cycle + 1,
                "participant": i + 1,
                "endpoint": endpoint,
                "answer": answer,
            }

            transcript.append(entry)
            if PRINT_OUTPUT:
                print(
                    f"\nTurn {turn} | Participant {i + 1} | {endpoint}"
                )
                print(answer)

            last_answer = answer
            turn += 1

    print("Discussion ended...")
    print_results(transcript)
    print("Exiting the discussion module...")
    return transcript

if __name__ == "__main__":
    run_discussion()
