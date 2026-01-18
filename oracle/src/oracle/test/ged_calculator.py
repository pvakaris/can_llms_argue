from typing import Dict, Any, Optional
import time
import networkx as nx
from difflib import SequenceMatcher

from .models import AIFNode, AIFEdge, AIFGraph

"""
    Implementation inspired by: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.similarity.graph_edit_distance.html
    Article: https://hal.science/hal-01168816/
"""
def text_similarity_ratio(a: str, b: str) -> float:
    # Return a 0..1 similarity ratio using difflib.SequenceMatcher
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

def node_subst_cost(attr1: Dict[str, Any], attr2: Dict[str, Any]) -> float:
    type1, text1 = extract_type_text(attr1)
    type2, text2 = extract_type_text(attr2)

    sim = text_similarity_ratio(text1, text2)
    text_similar = sim > 0.95
    types_match = (type1 and type2 and type1 == type2)

    if text_similar and types_match:
        return 0.0

    if text_similar and not types_match:
        return 1.0 - sim

    if types_match and not text_similar:
        return 1.0 - sim

    # Types are different and texts are dissimilar
    return 1.0

def extract_type_text(attr: Dict[str, Any]) -> tuple[str, str]:
    n: Optional[AIFNode] = attr.get("obj")

    if n:
        node_type = (n.type or "").strip().lower()
        text = n.normalised_text()
    else:
        node_type = (attr.get("type") or "").strip().lower()
        text = (attr.get("text") or "").strip().lower()

    return node_type, text

def node_ins_cost(attr: Dict[str, Any]) -> float:
    return 0.5

def node_del_cost(attr: Dict[str, Any]) -> float:
    return 0.5

def edge_subst_cost(attr1: Dict[str, Any], attr2: Dict[str, Any]) -> float:
    return 0.5

def edge_ins_cost(attr: Dict[str, Any]) -> float:
    return 0.5

def edge_del_cost(attr: Dict[str, Any]) -> float:
    return 0.5

def compute_ged_from_aif_graphs(aif1: AIFGraph, aif2: AIFGraph, timeout: float, round_digits: int) -> tuple[
    float, float]:
    graph_1 = aif1.to_networkx(attach_objects=True)
    graph_2 = aif2.to_networkx(attach_objects=True)
    return compute_ged(graph_1, graph_2, timeout=timeout, round_digits=round_digits)

def compute_ged(
    graph_1: nx.DiGraph,
    graph_2: nx.DiGraph,
    timeout: Optional[float] = 5.0,
    *,
    node_subst=node_subst_cost,
    node_ins=node_ins_cost,
    node_del=node_del_cost,
    edge_subst=edge_subst_cost,
    edge_ins=edge_ins_cost,
    edge_del=edge_del_cost,
    round_digits: int = 2
) -> tuple[float, float]:

    start = time.time()
    ged_result = None

    try:
        ged_result = nx.graph_edit_distance(
            graph_1,
            graph_2,
            node_subst_cost=node_subst,
            node_ins_cost=node_ins,
            node_del_cost=node_del,
            edge_subst_cost=edge_subst,
            edge_ins_cost=edge_ins,
            edge_del_cost=edge_del,
            timeout=timeout,
        )
    except Exception as ex:
        print("  An exception occured when calculating the GED:", ex)

    elapsed = time.time() - start
    if ged_result is None:
        return -1.0, elapsed
    return round(float(ged_result), round_digits), elapsed
