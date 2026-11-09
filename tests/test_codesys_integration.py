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

    def test_function_block_valid_and_invalid_candidates(self):
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
            declaration_path=fixtures / "valid_fb_declaration.st",
            implementation_path=fixtures / "valid_fb_implementation.st",
            output_dir=evidence_root / f"{timestamp}_function_block_valid",
            pou_name="MotorControl",
            pou_type="FUNCTION_BLOCK",
        )
        self.assertTrue(valid.success)
        self.assertEqual(valid.replaced_pou, "MotorControl")
        self.assertEqual(valid.errors, ())

        invalid = compile_project(
            template_project=template,
            declaration_path=fixtures / "invalid_fb_declaration.st",
            implementation_path=fixtures / "invalid_fb_implementation.st",
            output_dir=evidence_root / f"{timestamp}_function_block_invalid",
            pou_name="MotorControl",
            pou_type="FUNCTION_BLOCK",
        )
        self.assertFalse(invalid.success)
        self.assertGreaterEqual(len(invalid.errors), 1)
        self.assertEqual(invalid.errors[0].object_name, "MotorControl")
        self.assertIsNotNone(invalid.errors[0].position)

    def test_custom_type_and_inout_binding(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_root = (
            PROJECT_ROOT
            / "experiments"
            / "raw"
            / "environment_validation"
        )
        template = PROJECT_ROOT / "codesys" / "template" / "测试工程.project"
        fixtures = PROJECT_ROOT / "tests" / "fixtures" / "codesys"
        compile_context = {
            "custom_types": [
                {
                    "name": "ST_Pump",
                    "kind": "STRUCT",
                    "fields": [
                        {"name": "priority", "data_type": "INT"},
                        {"name": "selection", "data_type": "BOOL"},
                        {"name": "RunComd", "data_type": "BOOL"},
                    ],
                }
            ],
            "inout_bindings": [
                {
                    "parameter": "pumpGroup",
                    "variable": "candidatePumpGroup",
                    "data_type": "ARRAY[1..5] OF ST_Pump",
                }
            ],
        }

        valid = compile_project(
            template_project=template,
            declaration_path=fixtures / "special_fb_declaration.st",
            implementation_path=fixtures / "special_fb_valid_implementation.st",
            output_dir=evidence_root / f"{timestamp}_special_interface_valid",
            pou_name="PumpGroupControl",
            pou_type="FUNCTION_BLOCK",
            compile_context=compile_context,
        )
        self.assertTrue(valid.success)
        self.assertEqual(valid.errors, ())

        invalid = compile_project(
            template_project=template,
            declaration_path=fixtures / "special_fb_declaration.st",
            implementation_path=fixtures / "special_fb_invalid_implementation.st",
            output_dir=evidence_root / f"{timestamp}_special_interface_invalid",
            pou_name="PumpGroupControl",
            pou_type="FUNCTION_BLOCK",
            compile_context=compile_context,
        )
        self.assertFalse(invalid.success)
        self.assertGreaterEqual(len(invalid.errors), 1)
        self.assertEqual(invalid.errors[0].object_name, "PumpGroupControl")

    def test_fixed_fifo_inout_binding(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_root = (
            PROJECT_ROOT
            / "experiments"
            / "raw"
            / "environment_validation"
        )
        template = PROJECT_ROOT / "codesys" / "template" / "测试工程.project"
        fixtures = PROJECT_ROOT / "tests" / "fixtures" / "codesys"
        compile_context = {
            "custom_types": [],
            "inout_bindings": [
                {
                    "parameter": "item",
                    "variable": "candidateItem",
                    "data_type": "DINT",
                },
                {
                    "parameter": "buffer",
                    "variable": "candidateBuffer",
                    "data_type": "ARRAY[1..10] OF DINT",
                },
            ],
        }

        valid = compile_project(
            template_project=template,
            declaration_path=fixtures / "fifo_fb_declaration.st",
            implementation_path=fixtures / "fifo_fb_valid_implementation.st",
            output_dir=evidence_root / f"{timestamp}_fifo_interface_valid",
            pou_name="FifoQueueProbe",
            pou_type="FUNCTION_BLOCK",
            compile_context=compile_context,
        )
        self.assertTrue(valid.success)

        invalid = compile_project(
            template_project=template,
            declaration_path=fixtures / "fifo_fb_declaration.st",
            implementation_path=fixtures / "fifo_fb_invalid_implementation.st",
            output_dir=evidence_root / f"{timestamp}_fifo_interface_invalid",
            pou_name="FifoQueueProbe",
            pou_type="FUNCTION_BLOCK",
            compile_context=compile_context,
        )
        self.assertFalse(invalid.success)
        self.assertGreaterEqual(len(invalid.errors), 1)
        self.assertEqual(invalid.errors[0].object_name, "FifoQueueProbe")


if __name__ == "__main__":
    unittest.main()
