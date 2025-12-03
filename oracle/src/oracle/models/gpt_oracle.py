import os
import re
import time
from openai import OpenAI
import sys
from dotenv import load_dotenv
from typing import Callable, Optional

from oracle.models.oracle_config import GPT_CONFIG
from oracle.models.shared import run_with_query

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("OPENAI_API_KEY environment variable is not set. Make sure the API key is in the .env file.")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

def make_chatgpt_query(
    model: str = GPT_CONFIG["MODEL_NAME"],
    max_tokens: int = GPT_CONFIG["MAX_TOKENS"],
    temperature: float = GPT_CONFIG["TEMPERATURE"],
    retries: int = 2,
    system_prompt: Optional[str] = None
) -> Callable[[str], Optional[str]]:

    def query_fn(prompt_text: str) -> Optional[str]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt_text})

        attempt = 0
        while attempt <= retries:
            try:
                resp = client.chat.completions.create(model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                n=1)

                return clean_json(resp.choices[0].message.content)

            except Exception as e:
                attempt += 1
                if attempt > retries:
                    print("ChatGPT error:", e)
                    return None
                time.sleep(1 + attempt)
        return None

    return query_fn

# OpenAI models if asked to return a json usually return the response as ```json{...the actual json}```
# This method cleans the response so that only the JSON object is returned
def clean_json(json_str: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)```", json_str, re.DOTALL)
    return match.group(1).strip() if match else json_str.strip()

def main(argv=None):
    print("Starting ChatGPT oracle with argv:", argv)

    gpt_query_fn = make_chatgpt_query()
    run_with_query(query_fn=gpt_query_fn)

if __name__ == "__main__":
    main()
