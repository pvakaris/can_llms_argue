from pathlib import Path

# Shared config parameters
PROMPT_CONFIG_FILE = Path("resources/oracle_config/config_aif.txt")
ORACLE_FILE_POSTFIX = "_oracle"
METADATA_FILE_POSTFIX = "_metadata"

USE_INPUT_DIR = True
INPUT_DIR = Path("resources/input")
OUTPUT_DIR = Path("resources/output")

PRINT_MODEL_INPUT_AND_OUTPUT_FOR_DEBUG = False

# Specific config parameters
USE_GPU = True
LLAMA_CONFIG = {
    "MODEL_NAME": "meta-llama/Llama-3.1-8B-Instruct",
    "MAX_TOKENS": 256,
    "TEMPERATURE": 0.3
}

GPT_CONFIG = {
    "MODEL_NAME" : "gpt-4o",
    "MAX_TOKENS" : 4096,
    "TEMPERATURE" : 0.3,
    "PROMPT_ID": "pmpt_6939bb21e7d881908d12e8f5363c41cf0e8623fe874c1b4d",
    "PROMPT_VERSION": "1"
}