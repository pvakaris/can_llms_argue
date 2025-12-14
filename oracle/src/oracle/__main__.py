from __future__ import annotations

import argparse
import importlib
from typing import List

ORACLE_MAP = {
    "llama": "oracle.models.llama_oracle",
    "gpt": "oracle.models.gpt_oracle",
    "uva": "oracle.models.uva_oracle",
}

TESTER = "oracle.test.graph_comparison"
ANALYSER = "oracle.models.result_calculator"

def call_module_main(module_path: str, argv: List[str] or None = None):
    module = importlib.import_module(module_path)
    if hasattr(module, "main"):
        return module.main(argv)
    raise SystemExit(f"Module {module_path} has no callable main(argv=None).")

def main(argv: List[str] or None = None):
    parser = argparse.ArgumentParser(prog="oracle", description="Run oracle models or tester")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("test", help="Run the AIF graph comparison tool")
    sub.add_parser("analyse", help="Run the AIF graph metadata analysis")
    model_parser = sub.add_parser("model", help="Run a model")
    model_parser.add_argument("-m", "--model", choices=list(ORACLE_MAP.keys()),required=True, help="Which model to run")
    model_parser.add_argument("rest", nargs=argparse.REMAINDER, help="Extra args for the model")

    args = parser.parse_args(argv)

    if args.command == "analyse":
        return call_module_main(ANALYSER)

    if args.command == "test":
        return call_module_main(TESTER)

    if args.command == "model":
        module_path = ORACLE_MAP[args.model]
        return call_module_main(module_path, args.rest or None)
    return None

if __name__ == "__main__":
    main()
