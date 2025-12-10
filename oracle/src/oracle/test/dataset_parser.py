from pathlib import Path
from typing import Dict, Any, List, Tuple

from .models import AIFNode, AIFEdge, AIFGraph
from .test_config import NODES_KEY, EDGES_KEY, ORACLE_FILE_POSTFIX
from shared.parser import read_json_file


def extract_nodes(aif_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    return aif_json.get(NODES_KEY, [])


def extract_edges(aif_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    return aif_json.get(EDGES_KEY, [])

def parse_aif_json(aif_json: Dict[str, Any]) -> AIFGraph:
    nodes = [AIFNode.from_dict(d) for d in extract_nodes(aif_json)]
    edges = [AIFEdge.from_dict(d) for d in extract_edges(aif_json)]
    return AIFGraph(nodes=nodes, edges=edges)

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