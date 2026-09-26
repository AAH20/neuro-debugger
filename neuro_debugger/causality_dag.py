from typing import Dict, List, Optional, Set
from .models import ExecutionStep, CausalityNode


class CausalityDAG:
    """
    Tracks deterministic causality and influence flow across multi-agent swarms.
    Enables root-cause analysis and bidirectional dependency resolution.
    """

    def __init__(self):
        self.nodes: Dict[int, CausalityNode] = {}
        self.agent_timeline: Dict[str, List[int]] = {}

    def record_step(self, step: ExecutionStep) -> CausalityNode:
        """Records an execution step and updates causality forward and backward edges."""
        node = CausalityNode(
            step_id=step.step_index,
            agent_id=step.agent_id,
            caused_by=list(step.parent_step_ids),
            consequences=[]
        )

        # Update forward edges on parent nodes
        for parent_id in step.parent_step_ids:
            if parent_id in self.nodes:
                self.nodes[parent_id].consequences.append(step.step_index)

        self.nodes[step.step_index] = node

        if step.agent_id not in self.agent_timeline:
            self.agent_timeline[step.agent_id] = []
        self.agent_timeline[step.agent_id].append(step.step_index)

        return node

    def trace_root_cause(self, step_id: int) -> List[int]:
        """Traces the backward causal ancestry to identify the ultimate genesis of an action or bug."""
        visited: Set[int] = set()
        ancestry: List[int] = []

        def dfs(curr_id: int):
            if curr_id in visited or curr_id not in self.nodes:
                return
            visited.add(curr_id)
            ancestry.append(curr_id)
            for parent_id in self.nodes[curr_id].caused_by:
                dfs(parent_id)

        dfs(step_id)
        return sorted(ancestry)

    def trace_blast_radius(self, step_id: int) -> List[int]:
        """Calculates all downstream steps affected by a past action or state mutation."""
        visited: Set[int] = set()
        blast_radius: List[int] = []

        def dfs(curr_id: int):
            if curr_id in visited or curr_id not in self.nodes:
                return
            visited.add(curr_id)
            blast_radius.append(curr_id)
            for child_id in self.nodes[curr_id].consequences:
                dfs(child_id)

        dfs(step_id)
        return sorted(blast_radius)
