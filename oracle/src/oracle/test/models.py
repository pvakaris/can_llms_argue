from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
import networkx as nx


"""
    Represents an AIF node
    Known attributes: nodeID, text, type, timestamp, scheme, schemeID (AIFdb)
    Unknown attributes are collected in `extras`
"""
@dataclass(frozen=True)
class AIFNode:

    node_id: str
    text: Optional[str] = None
    type: Optional[str] = None
    timestamp: Optional[str] = None
    scheme: Optional[str] = None
    scheme_id: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict, compare=False, hash=False)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> AIFNode:
        mapping = {
            "nodeID": "node_id",
            "text": "text",
            "type": "type",
            "timestamp": "timestamp",
            "scheme": "scheme",
            "schemeID": "scheme_id",
        }

        base = {}
        for json_key, field_name in mapping.items():
            if json_key in d:
                base[field_name] = d[json_key]

        extras = {k: v for k, v in d.items() if k not in mapping}

        return AIFNode(**base, extras=extras)

    def to_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out.update(self.extras)
        return out

    def normalised_text(self) -> str:
        if not self.text:
            return ""
        return " ".join(self.text.strip().lower().split())

    def is_scheme_node(self) -> bool:
        t = (self.type or "").lower()
        return any(k in t for k in ("s-node", "ca", "ra", "pa", "sa", "scheme"))

    def is_info_node(self) -> bool:
        t = (self.type or "").lower()
        return any(k in t for k in ("i-node", "i", "info", "information"))

"""
    Represents an AIF edge
    Known attributes: edgeID, fromID, toID, formEdgeID
    Unknown attributes are collected in `extras`
"""
@dataclass(frozen=True)
class AIFEdge:

    edge_id: str
    from_id: str
    to_id: str
    form_edge_id: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict, compare=False, hash=False)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> AIFEdge:
        mapping = {
            "edgeID": "edge_id",
            "fromID": "from_id",
            "toID": "to_id",
            "formEdgeID": "form_edge_id",
        }

        base = {}
        for json_key, field_name in mapping.items():
            if json_key in d:
                base[field_name] = d[json_key]

        extras = {k: v for k, v in d.items() if k not in mapping}

        return AIFEdge(**base, extras=extras)

    def to_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out.update(self.extras)
        return out

"""
    Represents an AIF graph consisting of nodes and edges
    Can be seamlessly converted to an networkx.DiGraph
"""
class AIFGraph:

    def __init__(self, nodes: List[AIFNode] = None, edges: List[AIFEdge] = None):
        self.nodes: Dict[str, AIFNode] = {}
        self.edges: List[AIFEdge] = []
        if nodes:
            for n in nodes:
                self.add_node(n)
        if edges:
            for e in edges:
                self.add_edge(e)

    @classmethod
    def from_dict_lists(cls, nodes_list: List[Dict[str, Any]], edges_list: List[Dict[str, Any]]) -> AIFGraph:
        nodes = [AIFNode.from_dict(d) for d in nodes_list]
        edges = [AIFEdge.from_dict(d) for d in edges_list]
        return cls(nodes=nodes, edges=edges)

    def add_node(self, node: AIFNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, edge: AIFEdge) -> None:
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[AIFNode]:
        return self.nodes.get(node_id)

    def to_networkx(self, attach_objects: bool = True) -> nx.DiGraph:
        graph = nx.DiGraph()
        for nid, node in self.nodes.items():
            if attach_objects:
                graph.add_node(nid, obj=node)
            else:
                graph.add_node(nid, **node.to_dict())

        for edge in self.edges:
            if attach_objects:
                graph.add_edge(edge.from_id, edge.to_id, obj=edge)
            else:
                graph.add_edge(edge.from_id, edge.to_id, **edge.to_dict())

        return graph