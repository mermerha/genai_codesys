import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plc_agent.candidate import StCandidate


class CandidateTests(unittest.TestCase):
    def test_parses_fenced_function_block_json(self):
        payload = {
            "pou_name": "MotorControl",
            "pou_type": "function_block",
            "declaration": "FUNCTION_BLOCK MotorControl",
            "implementation": "Motor := StartBtn;",
        }

        candidate = StCandidate.from_model_text(
            "```json\n" + json.dumps(payload) + "\n```"
        )

        self.assertEqual(candidate.pou_name, "MotorControl")
        self.assertEqual(candidate.pou_type, "FUNCTION_BLOCK")

    def test_rejects_extra_fields(self):
        payload = {
            "pou_name": "MotorControl",
            "pou_type": "FUNCTION_BLOCK",
            "declaration": "FUNCTION_BLOCK MotorControl",
            "implementation": "Motor := StartBtn;",
            "explanation": "extra text",
        }

        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            StCandidate.from_model_text(json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
