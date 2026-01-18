from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from .models import AIFNode, AIFEdge, AIFGraph
from .test_config import NODES_KEY, EDGES_KEY, ORACLE_FILE_POSTFIX
from shared.parser import read_json_file

import logging

logger = logging.getLogger(__name__)

def extract_nodes(aif_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    nodes = aif_json.get(NODES_KEY, [])
    return nodes if isinstance(nodes, list) else []


def extract_edges(aif_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    edges = aif_json.get(EDGES_KEY, [])
    return edges if isinstance(edges, list) else []

def parse_aif_json(aif_json: Any) -> Optional[AIFGraph]:
    try:
        if not isinstance(aif_json, dict):
            return None

        raw_nodes = extract_nodes(aif_json)
        raw_edges = extract_edges(aif_json)

        if not all(isinstance(n, dict) for n in raw_nodes):
            return None
        if not all(isinstance(e, dict) for e in raw_edges):
            return None

        nodes = [AIFNode.from_dict(d) for d in raw_nodes]
        edges = [AIFEdge.from_dict(d) for d in raw_edges]

        return AIFGraph(nodes=nodes, edges=edges)

    except Exception as e:
        print("Failed to parse AIF JSON: %s", e)
        return None

def get_aif_graph_from_path(path: str) -> AIFGraph:
    obj = read_json_file(path)
    return parse_aif_json(obj)

def find_pairs(resources_dir: Path) -> List[Tuple[Path, Path]]:
    pairs: List[Tuple[Path, Path]] = []
    for bench in sorted(resources_dir.glob("*.json")):
        if bench.name.endswith(f"{ORACLE_FILE_POSTFIX}.json"):
            continue
        oracle = resources_dir / f"{bench.stem}{ORACLE_FILE_POSTFIX}.json"
        if oracle.exists():
            pairs.append((bench, oracle))
    return pairs