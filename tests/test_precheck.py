import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plc_agent.candidate import StCandidate
from plc_agent.precheck import validate_candidate


class CandidatePrecheckTests(unittest.TestCase):
    def test_accepts_matching_interface(self):
        task = {
            "pou_name": "MotorControl",
            "pou_type": "FUNCTION_BLOCK",
            "interface": [
                {"direction": "input", "name": "StartBtn", "data_type": "BOOL"},
                {"direction": "output", "name": "Motor", "data_type": "BOOL"},
            ],
        }
        candidate = StCandidate(
            pou_name="MotorControl",
            pou_type="FUNCTION_BLOCK",
            declaration=(
                "FUNCTION_BLOCK MotorControl\n"
                "VAR_INPUT\n    StartBtn : BOOL;\nEND_VAR\n"
                "VAR_OUTPUT\n    Motor : BOOL;\nEND_VAR"
            ),
            implementation="Motor := StartBtn;",
        )

        self.assertEqual(validate_candidate(task, candidate), [])

    def test_reports_interface_without_starting_codesys(self):
        task = {
            "pou_name": "MotorControl",
            "pou_type": "FUNCTION_BLOCK",
            "interface": [
                {"direction": "input", "name": "StartBtn", "data_type": "BOOL"},
                {"direction": "output", "name": "Motor", "data_type": "BOOL"},
            ],
        }
        candidate = StCandidate(
            pou_name="MotorControl",
            pou_type="FUNCTION_BLOCK",
            declaration=(
                "FUNCTION_BLOCK MotorControl\n"
                "VAR_OUTPUT\n    StartBtn : BOOL;\nEND_VAR"
            ),
            implementation="StartBtn := FALSE;",
        )

        kinds = {error["kind"] for error in validate_candidate(task, candidate)}

        self.assertEqual(
            kinds,
            {"precheck_interface_direction", "precheck_missing_interface"},
        )


if __name__ == "__main__":
    unittest.main()
