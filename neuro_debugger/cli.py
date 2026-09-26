import argparse
import sys
import json
from .time_travel_engine import TimeTravelEngine
from .models import StepType


def main():
    parser = argparse.ArgumentParser(description="neuro-debugger: Time-Travel Reverse Debugger & Causality Forker for Swarms")
    parser.add_argument("--demo", action="store_true", help="Run an interactive time-travel simulation session")
    args = parser.parse_args()

    engine = TimeTravelEngine()

    print("=== neuro-debugger v1.0.0 (Frontier September 2026) ===")
    print("[*] Initializing Causality DAG and Time-Travel Engine...")

    # Simulate multi-agent steps
    s1 = engine.record_step(
        agent_id="architect",
        model_name="Claude Opus 5.5",
        step_type=StepType.THOUGHT,
        action_payload={"reasoning": "Analyze system requirements for microservice mesh"},
        memory_state={"phase": "design", "tokens_used": 450},
        active_variables={"service_count": 4}
    )
    print(f"[Step {s1.step_index}] {s1.agent_id} ({s1.model_name}): {s1.action_payload['reasoning']}")

    s2 = engine.record_step(
        agent_id="coder",
        model_name="GPT-6 Astra",
        step_type=StepType.TOOL_CALL,
        action_payload={"tool": "write_file", "path": "gateway.go"},
        memory_state={"phase": "coding", "tokens_used": 1200},
        active_variables={"files_written": 1}
    )
    print(f"[Step {s2.step_index}] {s2.agent_id} ({s2.model_name}): called {s2.action_payload['tool']}")

    s3 = engine.record_step(
        agent_id="verifier",
        model_name="DeepSeek V4.1-Flash",
        step_type=StepType.STATE_MUTATION,
        action_payload={"error": "Detected potential deadlock in channel multiplexing"},
        memory_state={"phase": "verification", "status": "failed"},
        active_variables={"deadlock_risk": 0.89}
    )
    print(f"[Step {s3.step_index}] {s3.agent_id} ({s3.model_name}): {s3.action_payload['error']}")

    print("\n[*] Stepping backwards in time to Step 2...")
    rewound_step = engine.step_backward(1)
    if rewound_step:
        print(f"[Rewind] Cursor now at Step {rewound_step.step_index} | Memory State: {rewound_step.snapshot.memory_state}")

    print("\n[*] Forking timeline at Step 2 into speculative branch 'fix-deadlock'...")
    forked = engine.fork_branch(
        new_branch_id="fix-deadlock",
        fork_at_step=2,
        modified_prompt="Avoid unbuffered channels; use lock-free queue.",
        state_overrides={"architecture_pattern": "lock_free"}
    )
    print(f"[Fork] Created branch '{forked.branch_id}' from parent step {forked.fork_point_step}")

    s4 = engine.record_step(
        agent_id="coder",
        model_name="GPT-6 Astra",
        step_type=StepType.TOOL_CALL,
        action_payload={"tool": "write_file", "path": "gateway_lockfree.go"},
        memory_state={"phase": "coding", "pattern": "lock_free"},
        active_variables={"deadlock_risk": 0.0}
    )
    print(f"[Branch: fix-deadlock Step {s4.step_index}] {s4.agent_id}: {s4.action_payload['tool']}")

    blast_radius = engine.causality_dag.trace_blast_radius(1)
    root_cause = engine.causality_dag.trace_root_cause(3)
    print(f"\n[*] Causality Analysis:")
    print(f"    - Root cause of Step 3: {root_cause}")
    print(f"    - Blast radius of Step 1: {blast_radius}")
    print("[*] neuro-debugger run completed successfully.")


if __name__ == "__main__":
    main()
