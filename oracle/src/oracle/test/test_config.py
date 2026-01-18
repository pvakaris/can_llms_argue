import os
from pathlib import Path
from shared.helper import env_bool
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.getenv("TEST_ROOT_DIR", "NONE") # NONE = use relative path three layers up. Override if needed
NODES_KEY = os.getenv("TEST_NODES_KEY", "nodes")
EDGES_KEY = os.getenv("TEST_EDGES_KEY", "edges")
GED_TIMEOUT = float(os.getenv("TEST_GED_TIMEOUT", 20.0))
GED_ROUND_FLOAT_TO = int(os.getenv("TEST_GED_ROUND_FLOAT_TO", 2))
PRINT_RESULT = env_bool("TEST_PRINT_RESULT", True)
SAVE_AS_CSV = env_bool("TEST_SAVE_AS_CSV", True)
RESOURCES_DIR = Path(os.getenv("TEST_RESOURCES_DIR", "resources/benchmark_test_data"))
ORACLE_FILE_POSTFIX = os.getenv("TEST_ORACLE_FILE_POSTFIX", "_oracle")
RESULT_FILE_PREFIX = os.getenv("TEST_RESULT_FILE_PREFIX", "results")
ADD_DATE_TO_RESULTS_FILE_POSTFIX = env_bool("TEST_ADD_DATE_TO_RESULTS_FILE_POSTFIX",True)