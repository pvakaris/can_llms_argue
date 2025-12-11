from pathlib import Path
from typing import Optional, Any, Dict

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from transformers.utils.logging import set_verbosity_error, set_verbosity_warning
from oracle.models.oracle_config import LLAMA_CONFIG, PROMPT_CONFIG_FILE
from oracle.models.shared import run_with_query
from shared.parser import read_txt_file

set_verbosity_error()
set_verbosity_warning()

# Made referencing https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_1/#-instruct-model-prompt-
def make_prompt_fn(text: str) -> str:
    root = Path(__file__).resolve().parents[3]
    prompt_config_path = root / PROMPT_CONFIG_FILE
    prompt_config_text = read_txt_file(prompt_config_path)
    return f'''
        {prompt_config_text} <|start_header_id|>user<|end_header_id|>
        {text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    '''

def main(argv=None):
    print("Starting Llama oracle with argv:", argv)

    # device = torch.device("mps") if USE_GPU and torch.backends.mps.is_available() else torch.device("cpu")
    # print(f"Using device: {device}")

    print(f"Loading tokenizer {LLAMA_CONFIG['MODEL_NAME']} ...")
    tokenizer = AutoTokenizer.from_pretrained(LLAMA_CONFIG["MODEL_NAME"])
    print("Successfully loaded the tokenizer")

    print(f"Loading model {LLAMA_CONFIG['MODEL_NAME']} ...")
    model = AutoModelForCausalLM.from_pretrained(
        LLAMA_CONFIG["MODEL_NAME"],
        # dtype=torch.bfloat16 if device.type == "mps" else torch.float32,
        # device_map=None
        device_map = {"": "cpu"}
    )
    # model.to(device)
    print("Successfully loaded the model")

    def llama_query_fn(prompt: str) -> Optional[Dict[str, Any]]:
        try:
            # message = generator(prompt)[0]["generated_text"]
            inputs = tokenizer(prompt, return_tensors="pt")
            input_ids = inputs["input_ids"].to(model.device)
            input_tokens = input_ids.shape[-1]

            outputs = model.generate(
                input_ids,
                attention_mask=inputs["attention_mask"],
                max_new_tokens=100_000,
                do_sample=False
            )

            message = tokenizer.decode(outputs[0], skip_special_tokens=True)

            output_tokens = outputs.shape[-1] - input_tokens
            total_tokens = input_tokens + output_tokens
            return {
                "message": message,
                "metadata": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "model": LLAMA_CONFIG["MODEL_NAME"]
                }
            }
        except Exception as e:
            print("LLama generator error:", e)
            return None

    run_with_query(query_fn=llama_query_fn, make_prompt_fn=make_prompt_fn)
if __name__ == "__main__":
    main()