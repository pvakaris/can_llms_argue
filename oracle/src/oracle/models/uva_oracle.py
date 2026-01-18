import os
import time
from pathlib import Path

import openai
import sys
from dotenv import load_dotenv
from typing import Callable, Optional, Dict, Any

from oracle.models.oracle_config import PROMPT_CONFIG_FILE, UVA_CONFIG, ROOT_DIR
from oracle.models.shared import run_with_query, clean_json
from shared.parser import read_txt_file

load_dotenv()
API_KEY = os.getenv("UVA_AI_API_KEY")

if not API_KEY:
    print("UVA_AI_API_KEY environment variable is not set. Make sure the API key is in the .env file.")
    sys.exit(1)

client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://ai-research-proxy.azurewebsites.net"
)

def make_uva_query(
    model: str = UVA_CONFIG["MODEL_NAME"],
    temperature: float = UVA_CONFIG["TEMPERATURE"],
    retries: int = 2,
) -> Callable[[str], Optional[str]]:

    def query_fn(prompt_text: str) -> Optional[Dict[str, Any]]:
        attempt = 0
        if ROOT_DIR and ROOT_DIR != "NONE":
            root = Path(ROOT_DIR)
        else:
            root = Path(__file__).resolve().parents[3]
        prompt_config_path = root / PROMPT_CONFIG_FILE
        config = read_txt_file(prompt_config_path)

        while attempt <= retries:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "developer",
                            "content": config
                        },
                        {
                            "role": "user",
                            "content": prompt_text,
                        }
                    ],
                    temperature=temperature,
                )

                message_text = response.choices[0].message.content
                metadata = {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                    "model": response.model
                }

                return {
                    "message": clean_json(message_text),
                    "metadata": metadata
                }
            except Exception as e:
                print(e)
                attempt += 1
                if attempt > retries:
                    print("UvA oracle error:", e)
                    return None
                time.sleep(1 + attempt)
        return None
    return query_fn

def make_prompt_fn(text: str) -> str:
    return text

def main(argv=None):
    print("Starting UvA oracle with argv:", argv)

    query_fn = make_uva_query()
    run_with_query(query_fn=query_fn, make_prompt_fn=make_prompt_fn)

if __name__ == "__main__":
    main()
