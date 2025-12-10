from typing import Optional, Any, Dict

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from transformers.utils.logging import set_verbosity_error, set_verbosity_warning
from oracle.models.oracle_config import LLAMA_CONFIG, USE_GPU
from oracle.models.shared import run_with_query

set_verbosity_error()
set_verbosity_warning()

def main(argv=None):
    print("Starting Llama oracle with argv:", argv)

    device = torch.device("mps") if USE_GPU and torch.backends.mps.is_available() else torch.device("cpu")
    print(f"Using device: {device}")

    print(f"Loading tokenizer {LLAMA_CONFIG['MODEL_NAME']} ...")
    tokenizer = AutoTokenizer.from_pretrained(LLAMA_CONFIG["MODEL_NAME"])
    print("Successfully loaded the tokenizer")

    print(f"Loading model {LLAMA_CONFIG['MODEL_NAME']} ...")
    model = AutoModelForCausalLM.from_pretrained(
        LLAMA_CONFIG["MODEL_NAME"],
        dtype=torch.bfloat16 if device.type == "mps" else torch.float32,
        device_map=None
    )
    model.to(device)
    print("Successfully loaded the model")

    print("Creating a pipeline ...")

    # generator = pipeline(
    #     "text-generation",
    #     model=model,
    #     tokenizer=tokenizer,
    #     # max_new_tokens=LLAMA_CONFIG["MAX_TOKENS"],
    #     temperature=LLAMA_CONFIG["TEMPERATURE"],
    #     device=0 if device.type == "mps" else -1,
    #     pad_token_id=tokenizer.eos_token_id
    # )

    def llama_query_fn(prompt: str) -> Optional[str]:
        try:
            # message = generator(prompt)[0]["generated_text"]
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            input_tokens = inputs["input_ids"].shape[1]
            print(f"Input tokens: {input_tokens}")
            outputs = model.generate(
                **inputs,
                max_new_tokens=LLAMA_CONFIG["MAX_TOKENS"],
                temperature=LLAMA_CONFIG["TEMPERATURE"],
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )

            print(outputs)

            message = tokenizer.decode(outputs[0], skip_special_tokens=True)

            total_tokens = outputs.shape[1]
            output_tokens = total_tokens - input_tokens
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

    run_with_query(query_fn=llama_query_fn)
if __name__ == "__main__":
    main()
