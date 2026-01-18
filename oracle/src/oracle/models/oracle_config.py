import os
from pathlib import Path
from shared.helper import env_bool
from dotenv import load_dotenv

load_dotenv()

# Shared config parameters
PROMPT_CONFIG_FILE = Path(os.getenv("ORACLE_PROMPT_CONFIG_FILE", "resources/oracle_config/config_aif_llama_old.txt"))
ORACLE_FILE_POSTFIX = os.getenv("ORACLE_FILE_POSTFIX", "_oracle")
METADATA_FILE_POSTFIX = os.getenv("ORACLE_METADATA_FILE_POSTFIX", "_metadata")

ROOT_DIR = os.getenv("ORACLE_ROOT_DIR", "NONE") # NONE = use relative path three layers up. Override if needed
USE_INPUT_DIR = env_bool("ORACLE_USE_INPUT_DIR", True)
INPUT_DIR = Path(os.getenv("ORACLE_INPUT_DIR", "resources/input"))
OUTPUT_DIR = Path(os.getenv("ORACLE_OUTPUT_DIR", "resources/output"))

PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG = env_bool("ORACLE_PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG",False)
USE_GPU = env_bool("ORACLE_USE_GPU", True)

# Specific config parameters

LLAMA_CONFIG = {
    "MODEL_NAME": os.getenv("ORACLE_LLAMA_MODEL_NAME", "meta-llama/Llama-3.1-70B-Instruct"),
    "MAX_TOKENS": int(os.getenv("ORACLE_LLAMA_MAX_TOKENS", 32000)),
    "TEMPERATURE": float(os.getenv("ORACLE_LLAMA_TEMPERATURE", 0.5))
}

GPT_CONFIG = {
    "MODEL_NAME": os.getenv("ORACLE_GPT_MODEL_NAME", "gpt-4o"),
    "MAX_TOKENS": int(os.getenv("ORACLE_GPT_MAX_TOKENS", 4096)),
    "TEMPERATURE": float(os.getenv("ORACLE_GPT_TEMPERATURE", 0.3)),
    "PROMPT_ID": os.getenv("ORACLE_GPT_PROMPT_ID", "pmpt_6939bb21e7d881908d12e8f5363c41cf0e8623fe874c1b4d"),
    "PROMPT_VERSION": os.getenv("ORACLE_GPT_PROMPT_VERSION", "2"),
    "USE_PROMPT": env_bool("ORACLE_GPT_USE_PROMPT", True)
}

UVA_CONFIG = {
    "MODEL_NAME": os.getenv("ORACLE_UVA_MODEL_NAME", "gpt-5.1"),
    "MAX_TOKENS": int(os.getenv("ORACLE_UVA_MAX_TOKENS", 4096)),
    "TEMPERATURE": float(os.getenv("ORACLE_UVA_TEMPERATURE", 0.3))
}
