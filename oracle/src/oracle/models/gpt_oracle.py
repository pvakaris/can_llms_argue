import os
import time
from pathlib import Path

from openai import OpenAI
import sys
from dotenv import load_dotenv
from typing import Callable, Optional, Dict, Any

from oracle.models.oracle_config import GPT_CONFIG, PROMPT_CONFIG_FILE, ROOT_DIR
from oracle.models.shared import run_with_query, clean_json
from shared.parser import read_txt_file

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("OPENAI_API_KEY environment variable is not set. Make sure the API key is in the .env file.")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

def make_chatgpt_query(
    model: str = GPT_CONFIG["MODEL_NAME"],
    temperature: float = GPT_CONFIG["TEMPERATURE"],
    retries: int = 2,
) -> Callable[[str], Optional[str]]:

    def query_fn(prompt_text: str) -> Optional[Dict[str, Any]]:
        attempt = 0
        while attempt <= retries:
            try:
                resp = None
                message = None
                if GPT_CONFIG["USE_PROMPT"] is not None and GPT_CONFIG["USE_PROMPT"] is True:
                    print("Using predefined prompt...")
                    resp = client.responses.create(
                        prompt={
                            "id": GPT_CONFIG["PROMPT_ID"],
                            "version": GPT_CONFIG["PROMPT_VERSION"]
                        },
                        input=prompt_text
                    )
                    message = resp.output[1].content[0].text
                else:
                    print("Using local config to construct the prompt")
                    resp = client.responses.create(
                        model=model,
                        input=prompt_text,
                        temperature=temperature,
                    )
                    message = resp.output[0].content[0].text

                metadata = {
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                    "total_tokens": resp.usage.total_tokens,
                    "model": resp.model
                }

                return {
                    "message": clean_json(message),
                    "metadata": metadata
                }
            except Exception as e:
                print(e)
                attempt += 1
                if attempt > retries:
                    print("ChatGPT error:", e)
                    return None
                time.sleep(1 + attempt)
        return None

    return query_fn

def make_prompt_fn(text: str) -> str:
    if GPT_CONFIG["USE_PROMPT"] is not None and GPT_CONFIG["USE_PROMPT"] is True:
        return text

    if ROOT_DIR and ROOT_DIR != "NONE":
        root = Path(ROOT_DIR)
    else:
        root = Path(__file__).resolve().parents[3]
    prompt_config_path = root / PROMPT_CONFIG_FILE
    config = read_txt_file(prompt_config_path)
    return f"{config}\n\nInput text:\n\"\"\"{text}\"\"\"\n\n\"\"\""

def main(argv=None):
    print("Starting ChatGPT oracle with argv:", argv)

    gpt_query_fn = make_chatgpt_query()
    run_with_query(query_fn=gpt_query_fn, make_prompt_fn=make_prompt_fn)

if __name__ == "__main__":
    main()
