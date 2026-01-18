import datetime
import json
from pathlib import Path
import requests

from discussion_module.discussion_config import HOST, BASE_PORT, PARTICIPANTS, CYCLES, MODEL, QUESTION, \
    PARTICIPANT_CONFIG, OUTPUT_LIMIT_PER_PARTICIPANT, PRINT_OUTPUT, OUTPUT_DIR, ADD_DATE_TO_RESULTS_FILE_POSTFIX, \
    MAX_SELF_MEMORY, MAX_GLOBAL_HISTORY
from shared.parser import read_txt_file

def build_endpoints(host, base_port, participants):
    return [f"{host}:{base_port + i}" for i in range(participants)]

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

def build_messages(
    participant_id,
    participant_config,
    question,
    discussion_history,
    participant_memory,
):
    messages = [
        {"role": "system", "content": participant_config},
        {"role": "user", "content": f"Question:\n{question}"},
    ]

    for past_answer in participant_memory.get(participant_id, []):
        messages.append({
            "role": "assistant",
            "content": f"(Your earlier response)\n{past_answer}"
        })

    for entry in discussion_history:
        if entry["participant"] != participant_id:
            messages.append({
                "role": "user",
                "content": (
                    f"Participant {entry['participant']} "
                    f"(cycle {entry['cycle']}) said:\n{entry['content']}"
                ),
            })
    return messages

def save_results(transcript):
    try:
        print("Saving the results...")
        root = Path(__file__).resolve().parents[2]
        output_dir = root / OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        postfix = f"_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}" if ADD_DATE_TO_RESULTS_FILE_POSTFIX else ""
        json_path = output_dir / f"discussion{postfix}.json"
        txt_path = output_dir / f"discussion{postfix}.txt"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(transcript, f, ensure_ascii=False, indent=2)

        with open(txt_path, "w", encoding="utf-8") as f:
            for entry in transcript:
                f.write(
                    f"participant{entry['participant']}: "
                    f"{entry['answer']}\n"
                )

        if PRINT_OUTPUT:
            name = OUTPUT_DIR / f"discussion{postfix}.json"
            print(f"Structured transcript saved as JSON: {name}")
            name = OUTPUT_DIR / f"discussion{postfix}.txt"
            print(f"Transcript saved as text: {name}")
        print("Results saved successfully.")
    except Exception as e:
        print("Failed to save results...")
        print(f"Error: {e}")

def run_discussion():
    print("Discussion started...")

    endpoints = build_endpoints(HOST, BASE_PORT, PARTICIPANTS)
    root = Path(__file__).resolve().parents[2]

    participant_config = read_txt_file(root / PARTICIPANT_CONFIG)
    if OUTPUT_LIMIT_PER_PARTICIPANT is not None:
        participant_config += f"\n{OUTPUT_LIMIT_PER_PARTICIPANT}"

    transcript = []
    discussion_history = []
    participant_memory = {i + 1: [] for i in range(PARTICIPANTS)}

    turn = 1

    for cycle in range(CYCLES):
        if PRINT_OUTPUT:
            print(f"\n=== Cycle {cycle + 1}/{CYCLES} ===")

        for i, endpoint in enumerate(endpoints):
            participant_id = i + 1

            messages = build_messages(
                participant_id=participant_id,
                participant_config=participant_config,
                question=QUESTION,
                discussion_history=discussion_history,
                participant_memory=participant_memory,
            )

            answer = chat(endpoint, MODEL, messages)

            entry = {
                "turn": turn,
                "cycle": cycle + 1,
                "participant": participant_id,
                "endpoint": endpoint,
                "answer": answer,
            }

            transcript.append(entry)
            discussion_history.append({
                "participant": participant_id,
                "cycle": cycle + 1,
                "content": answer,
            })

            participant_memory[participant_id].append(answer)
            discussion_history[:] = discussion_history[-MAX_GLOBAL_HISTORY:]
            participant_memory[participant_id] = (
                participant_memory[participant_id][-MAX_SELF_MEMORY:]
            )

            if PRINT_OUTPUT:
                print(
                    f"\nTurn {turn} | Participant {participant_id} | {endpoint}"
                )
                print(f"{answer}\n")

            turn += 1

    print("Discussion ended.")
    save_results(transcript)
    print("Exiting the discussion module...")
    return transcript

if __name__ == "__main__":
    run_discussion()
