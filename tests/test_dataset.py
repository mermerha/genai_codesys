import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plc_agent.codesys_runner import validate_test_document


class DatasetTests(unittest.TestCase):
    def test_all_shared_tests_use_only_public_interfaces(self):
        for kind in ("public", "custom"):
            for tests_path in sorted(
                (PROJECT_ROOT / "data" / "test_cases" / kind).glob("*.json")
            ):
                task_path = PROJECT_ROOT / "data" / "tasks" / kind / tests_path.name
                task = json.loads(task_path.read_text(encoding="utf-8"))
                tests = json.loads(tests_path.read_text(encoding="utf-8"))
                with self.subTest(task=task["id"]):
                    validate_test_document(task, tests, minimum_advance_ms=50)

    def test_custom_tasks_record_provenance_rationale_and_diversity(self):
        allowed_sources = {
            "self_conceived",
            "experience_based",
            "synthetic",
            "public_web",
        }
        for task_path in sorted(
            (PROJECT_ROOT / "data" / "tasks" / "custom").glob("*.json")
        ):
            task = json.loads(task_path.read_text(encoding="utf-8"))
            provenance = task["provenance"]
            with self.subTest(task=task["id"]):
                self.assertIn(provenance["source_type"], allowed_sources)
                self.assertTrue(provenance["creation_process"])
                self.assertTrue(provenance["human_modifications"])
                self.assertTrue(provenance["review_process"])
                if provenance["source_type"] == "public_web":
                    self.assertTrue(provenance["source_url"])
                self.assertTrue(task["plc_rationale"].strip())
                self.assertGreaterEqual(len(task["diversity_tags"]), 3)


if __name__ == "__main__":
    unittest.main()
