import os
import sys
import unittest
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plc_agent.codesys_runner import compile_project


@unittest.skipUnless(
    os.environ.get("RUN_CODESYS_INTEGRATION") == "1",
    "set RUN_CODESYS_INTEGRATION=1 to launch CODESYS",
)
class CodesysIntegrationTests(unittest.TestCase):
    def test_valid_and_invalid_candidates(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_root = (
            PROJECT_ROOT
            / "experiments"
            / "raw"
            / "environment_validation"
        )
        template = PROJECT_ROOT / "codesys" / "template" / "测试工程.project"
        fixtures = PROJECT_ROOT / "tests" / "fixtures" / "codesys"

        valid = compile_project(
            template_project=template,
            declaration_path=fixtures / "valid_declaration.st",
            implementation_path=fixtures / "valid_implementation.st",
            output_dir=evidence_root / f"{timestamp}_python_valid",
        )
        self.assertTrue(valid.success)
        self.assertEqual(valid.process_returncode, 0)
        self.assertEqual(valid.errors, ())

        invalid = compile_project(
            template_project=template,
            declaration_path=fixtures / "invalid_declaration.st",
            implementation_path=fixtures / "invalid_implementation.st",
            output_dir=evidence_root / f"{timestamp}_python_invalid",
        )
        self.assertFalse(invalid.success)
        self.assertEqual(invalid.process_returncode, 2)
        self.assertGreaterEqual(len(invalid.errors), 1)
        self.assertEqual(invalid.errors[0].object_name, "PLC_PRG")
        self.assertIsNotNone(invalid.errors[0].position)


if __name__ == "__main__":
    unittest.main()
