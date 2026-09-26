from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time
import uuid


class StepType(str, Enum):
    THOUGHT = "thought"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    STATE_MUTATION = "state_mutation"
    MESSAGE_SENT = "message_sent"
    BRANCH_FORK = "branch_fork"


@dataclass
class StateSnapshot:
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    memory_state: Dict[str, Any] = field(default_factory=dict)
    active_variables: Dict[str, Any] = field(default_factory=dict)
    call_stack: List[str] = field(default_factory=list)


@dataclass
class ExecutionStep:
    step_index: int
    agent_id: str
    model_name: str  # Claude Opus 5.5, GPT-6 Astra, DeepSeek V4.1-Flash
    step_type: StepType
    action_payload: Dict[str, Any]
    snapshot: StateSnapshot
    parent_step_ids: List[int] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalityNode:
    step_id: int
    agent_id: str
    caused_by: List[int]
    consequences: List[int] = field(default_factory=list)
    entropy_score: float = 0.0


@dataclass
class ForkBranch:
    branch_id: str
    source_branch_id: Optional[str]
    fork_point_step: int
    created_at: float = field(default_factory=time.time)
    modified_prompt: Optional[str] = None
    state_overrides: Dict[str, Any] = field(default_factory=dict)
    steps: List[ExecutionStep] = field(default_factory=list)
