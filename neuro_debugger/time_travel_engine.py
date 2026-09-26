from typing import Dict, Any, List, Optional
import copy
from .models import ExecutionStep, StateSnapshot, ForkBranch, StepType
from .causality_dag import CausalityDAG


class TimeTravelEngine:
    """
    Reverse-execution and causality-forking engine for multi-agent swarms.
    Allows stepping backward, rewinding to arbitrary steps, inspecting historical memory,
    and branching speculative execution timelines.
    """

    def __init__(self, main_branch_id: str = "main"):
        self.branches: Dict[str, ForkBranch] = {
            main_branch_id: ForkBranch(branch_id=main_branch_id, source_branch_id=None, fork_point_step=0)
        }
        self.active_branch_id: str = main_branch_id
        self.current_step_cursor: int = 0
        self.causality_dag = CausalityDAG()

    @property
    def current_branch(self) -> ForkBranch:
        return self.branches[self.active_branch_id]

    def record_step(
        self,
        agent_id: str,
        model_name: str,
        step_type: StepType,
        action_payload: Dict[str, Any],
        memory_state: Dict[str, Any],
        active_variables: Dict[str, Any],
        parent_step_ids: Optional[List[int]] = None
    ) -> ExecutionStep:
        """Appends a new execution step to the active timeline."""
        step_idx = len(self.current_branch.steps) + 1
        snapshot = StateSnapshot(
            memory_state=copy.deepcopy(memory_state),
            active_variables=copy.deepcopy(active_variables),
            call_stack=[f"{agent_id}::{step_type.value}"]
        )

        parents = parent_step_ids if parent_step_ids is not None else ([step_idx - 1] if step_idx > 1 else [])

        step = ExecutionStep(
            step_index=step_idx,
            agent_id=agent_id,
            model_name=model_name,
            step_type=step_type,
            action_payload=action_payload,
            snapshot=snapshot,
            parent_step_ids=parents
        )

        self.current_branch.steps.append(step)
        self.current_step_cursor = step_idx
        self.causality_dag.record_step(step)
        return step

    def step_backward(self, count: int = 1) -> Optional[ExecutionStep]:
        """Steps backwards in agent execution history by `count` frames."""
        target_idx = max(1, self.current_step_cursor - count)
        if target_idx <= len(self.current_branch.steps):
            self.current_step_cursor = target_idx
            return self.current_branch.steps[target_idx - 1]
        return None

    def step_forward(self, count: int = 1) -> Optional[ExecutionStep]:
        """Steps forward along the recorded timeline."""
        target_idx = min(len(self.current_branch.steps), self.current_step_cursor + count)
        if target_idx <= len(self.current_branch.steps) and target_idx > 0:
            self.current_step_cursor = target_idx
            return self.current_branch.steps[target_idx - 1]
        return None

    def rewind_to(self, step_index: int) -> Optional[StateSnapshot]:
        """Rewinds the agent state to an exact historical step index."""
        if 1 <= step_index <= len(self.current_branch.steps):
            self.current_step_cursor = step_index
            return self.current_branch.steps[step_index - 1].snapshot
        return None

    def fork_branch(
        self,
        new_branch_id: str,
        fork_at_step: Optional[int] = None,
        modified_prompt: Optional[str] = None,
        state_overrides: Optional[Dict[str, Any]] = None
    ) -> ForkBranch:
        """
        Forks the causality timeline at a given step into a new speculative branch.
        Preserves original lineage while enabling what-if exploration.
        """
        target_step = fork_at_step if fork_at_step is not None else self.current_step_cursor
        if target_step > len(self.current_branch.steps):
            target_step = len(self.current_branch.steps)

        # Clone historical steps up to fork point
        historical_steps = [copy.deepcopy(s) for s in self.current_branch.steps[:target_step]]

        # Apply state overrides to the latest snapshot
        if state_overrides and historical_steps:
            last_snapshot = historical_steps[-1].snapshot
            last_snapshot.memory_state.update(state_overrides)

        new_branch = ForkBranch(
            branch_id=new_branch_id,
            source_branch_id=self.active_branch_id,
            fork_point_step=target_step,
            modified_prompt=modified_prompt,
            state_overrides=state_overrides or {},
            steps=historical_steps
        )

        self.branches[new_branch_id] = new_branch
        self.active_branch_id = new_branch_id
        self.current_step_cursor = target_step
        return new_branch

    def switch_branch(self, branch_id: str) -> bool:
        """Switches active timeline to a different branch."""
        if branch_id in self.branches:
            self.active_branch_id = branch_id
            self.current_step_cursor = len(self.branches[branch_id].steps)
            return True
        return False
