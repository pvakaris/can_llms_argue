from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Dict, Any
from jsonfinder import jsonfinder

def read_json_file(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed reading {path}: {e}")
        return {}

def write_json_file(path: Path, content):
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                pass
        json.dump(content, f, indent=2, ensure_ascii=False)

def read_txt_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Failed reading {path}: {e}")
        return ""

def extract_last_json_or_error(result_text: str):
    if not result_text:
        return {"error": "No output returned from LLM", "output": ""}

    matches = re.findall(r"\{.*\}", result_text, flags=re.DOTALL)
    if matches:
        last_json_str = matches[-1].strip()
        try:
            parsed = json.loads(last_json_str)
            return parsed
        except json.JSONDecodeError as e:
            return {
                "error": f"JSON parse failed: {e}",
                "output": last_json_str
            }
    else:
        return {"error": "No JSON found", "raw_output": result_text}

def extract_last_json(result_text):
    found = list(jsonfinder(result_text))
    for _, _, obj in reversed(found):
        if obj is not None:
            return obj
    return {"error": "No JSON found"}
