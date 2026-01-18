import os
from pathlib import Path
from shared.helper import env_bool
from dotenv import load_dotenv

load_dotenv()

PARTICIPANTS = int(os.getenv("DISCUSSION_PARTICIPANTS", 3))
QUESTION = os.getenv("DISCUSSION_QUESTION", "Should there be pineapples on pizza?")
MODEL = os.getenv("DISCUSSION_MODEL", "gemma3")
OUTPUT_LIMIT_PER_PARTICIPANT = os.getenv("DISCUSSION_OUTPUT_LIMIT_PER_PARTICIPANT", "Limit your answer to 4 sentences.")
PARTICIPANT_CONFIG = Path(os.getenv("DISCUSSION_PARTICIPANT_CONFIG", "resources/config/participant_config.txt"))
CYCLES = int(os.getenv("DISCUSSION_CYCLES", 1))
BASE_PORT = int(os.getenv("DISCUSSION_BASE_PORT", 11434))
HOST = os.getenv("DISCUSSION_HOST", "http://localhost")
OUTPUT_DIR = Path(os.getenv("DISCUSSION_OUTPUT_DIR", "resources/output"))
PRINT_OUTPUT = env_bool("DISCUSSION_PRINT_OUTPUT", False)
ADD_DATE_TO_RESULTS_FILE_POSTFIX = env_bool("DISCUSSION_ADD_DATE_TO_RESULTS_FILE_POSTFIX",True)
MAX_GLOBAL_HISTORY = int(os.getenv("DISCUSSION_MAX_GLOBAL_HISTORY", 50))
MAX_SELF_MEMORY = int(os.getenv("DISCUSSION_MAX_SELF_MEMORY", 5))