import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plc_agent.experiment_cli import _task_paths, _task_with_formal_spec


class ExperimentCliTests(unittest.TestCase):
    def test_formal_tasks_can_select_a_fixed_subset(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "tests") as temporary_directory:
            root = Path(temporary_directory)
            public = root / "data" / "tasks" / "public"
            public.mkdir(parents=True)
            for task_id in ("public_01", "public_02", "public_03"):
                (public / f"{task_id}.json").write_text("{}", encoding="utf-8")

            paths = _task_paths(
                root,
                "formal",
                {"formal_tasks": ["public_01", "public_03"]},
            )

        self.assertEqual([path.stem for path in paths], ["public_01", "public_03"])

    def test_attaches_only_model_relevant_spec_fields(self):
        task = {"id": "fixture", "requirements": "control a motor"}
        spec = {
            "state_semantics": "one scan per step",
            "propositions": {"safe": "safe input"},
            "assumptions": [],
            "properties": [
                {
                    "id": "fixture_p01",
                    "type": "safety",
                    "description": "stop when unsafe",
                    "ltl": "G(!safe -> X(!run))",
                    "tool_expression": None,
                }
            ],
            "review": {"status": "frozen"},
        }

        enriched = _task_with_formal_spec(task, spec)

        self.assertNotIn("formal_spec", task)
        self.assertNotIn("review", enriched["formal_spec"])
        self.assertNotIn(
            "tool_expression", enriched["formal_spec"]["properties"][0]
        )
        self.assertEqual(
            enriched["formal_spec"]["properties"][0]["id"], "fixture_p01"
        )


if __name__ == "__main__":
    unittest.main()
