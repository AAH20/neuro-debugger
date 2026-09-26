import unittest
from neuro_debugger.models import StepType, ExecutionStep
from neuro_debugger.causality_dag import CausalityDAG
from neuro_debugger.time_travel_engine import TimeTravelEngine


class TestNeuroDebugger(unittest.TestCase):
    def setUp(self):
        self.engine = TimeTravelEngine()

    def test_record_and_step_traversal(self):
        s1 = self.engine.record_step(
            agent_id="agent-1",
            model_name="Claude Opus 5.5",
            step_type=StepType.THOUGHT,
            action_payload={"thought": "plan"},
            memory_state={"step": 1},
            active_variables={"var1": 10}
        )
        s2 = self.engine.record_step(
            agent_id="agent-2",
            model_name="GPT-6 Astra",
            step_type=StepType.TOOL_CALL,
            action_payload={"tool": "search"},
            memory_state={"step": 2},
            active_variables={"var1": 20}
        )
        self.assertEqual(len(self.engine.current_branch.steps), 2)
        self.assertEqual(self.engine.current_step_cursor, 2)

        # Step back
        back = self.engine.step_backward(1)
        self.assertIsNotNone(back)
        self.assertEqual(back.step_index, 1)
        self.assertEqual(self.engine.current_step_cursor, 1)

        # Step forward
        forward = self.engine.step_forward(1)
        self.assertIsNotNone(forward)
        self.assertEqual(forward.step_index, 2)

    def test_rewind_and_fork_branch(self):
        self.engine.record_step("a1", "Claude Opus 5.5", StepType.THOUGHT, {}, {"m": 1}, {"v": 1})
        self.engine.record_step("a2", "GPT-6 Astra", StepType.TOOL_CALL, {}, {"m": 2}, {"v": 2})
        self.engine.record_step("a3", "DeepSeek V4.1-Flash", StepType.TOOL_RESULT, {}, {"m": 3}, {"v": 3})

        # Rewind to step 2
        snapshot = self.engine.rewind_to(2)
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.memory_state["m"], 2)

        # Fork at step 2
        fork = self.engine.fork_branch(
            new_branch_id="speculative-1",
            fork_at_step=2,
            modified_prompt="Alternative branch prompt",
            state_overrides={"m": 999}
        )
        self.assertEqual(fork.branch_id, "speculative-1")
        self.assertEqual(len(fork.steps), 2)
        self.assertEqual(fork.steps[-1].snapshot.memory_state["m"], 999)
        self.assertEqual(self.engine.active_branch_id, "speculative-1")

    def test_causality_dag_trace(self):
        dag = CausalityDAG()
        # step 1
        s1 = ExecutionStep(
            step_index=1,
            agent_id="lead",
            model_name="Claude Opus 5.5",
            step_type=StepType.THOUGHT,
            action_payload={},
            snapshot=None,
            parent_step_ids=[]
        )
        dag.record_step(s1)

        # step 2 caused by 1
        s2 = ExecutionStep(
            step_index=2,
            agent_id="worker",
            model_name="GPT-6 Astra",
            step_type=StepType.TOOL_CALL,
            action_payload={},
            snapshot=None,
            parent_step_ids=[1]
        )
        dag.record_step(s2)

        # step 3 caused by 2
        s3 = ExecutionStep(
            step_index=3,
            agent_id="reviewer",
            model_name="Gemini 3.8 Flash Cyber",
            step_type=StepType.TOOL_RESULT,
            action_payload={},
            snapshot=None,
            parent_step_ids=[2]
        )
        dag.record_step(s3)

        root_cause = dag.trace_root_cause(3)
        self.assertEqual(root_cause, [1, 2, 3])

        blast = dag.trace_blast_radius(1)
        self.assertEqual(blast, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
