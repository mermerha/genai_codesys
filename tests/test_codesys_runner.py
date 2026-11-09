import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plc_agent.codesys_runner import compile_project, execute_tests


class CodesysRunnerTests(unittest.TestCase):
    def test_direct_runner_copies_template_and_parses_result(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "tests") as temporary_directory:
            root = Path(temporary_directory)
            executable = root / "codesys_stub.txt"
            template = root / "template.project"
            script = root / "compile_project.py"
            declaration = root / "declaration.st"
            implementation = root / "implementation.st"
            for path in (executable, template, script, declaration, implementation):
                path.write_text("fixture", encoding="utf-8")

            output_dir = root / "run"

            def fake_run(command, **kwargs):
                result_path = Path(kwargs["env"]["PLC_AGENT_RESULT_PATH"])
                result_path.write_text(
                    json.dumps(
                        {
                            "success": True,
                            "exception": None,
                            "replaced_pou": "PLC_PRG",
                            "project_path": kwargs["env"]["PLC_AGENT_PROJECT_PATH"],
                            "messages": [],
                        }
                    ),
                    encoding="utf-8",
                )
                return __import__("subprocess").CompletedProcess(command, 0, "", "")

            with patch("plc_agent.codesys_runner.subprocess.run", side_effect=fake_run):
                result = compile_project(
                    template_project=template,
                    declaration_path=declaration,
                    implementation_path=implementation,
                    output_dir=output_dir,
                    codesys_exe=executable,
                    script_path=script,
                )

            self.assertTrue(result.success)
            self.assertEqual(result.process_returncode, 0)
            self.assertTrue((output_dir / "candidate.project").is_file())
            self.assertTrue((output_dir / "process_result.json").is_file())

    def test_function_block_type_is_passed_to_codesys(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "tests") as temporary_directory:
            root = Path(temporary_directory)
            files = []
            for name in (
                "codesys_stub.txt",
                "template.project",
                "compile_project.py",
                "declaration.st",
                "implementation.st",
            ):
                path = root / name
                path.write_text("fixture", encoding="utf-8")
                files.append(path)

            compile_context = {
                "custom_types": [
                    {
                        "name": "ST_Pump",
                        "kind": "STRUCT",
                        "fields": [
                            {"name": "RunComd", "data_type": "BOOL"}
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

            def fake_run(command, **kwargs):
                self.assertEqual(kwargs["env"]["PLC_AGENT_POU_NAME"], "MotorControl")
                self.assertEqual(kwargs["env"]["PLC_AGENT_POU_TYPE"], "FUNCTION_BLOCK")
                context_path = Path(
                    kwargs["env"]["PLC_AGENT_COMPILE_CONTEXT_PATH"]
                )
                self.assertEqual(
                    json.loads(context_path.read_text(encoding="utf-8")),
                    compile_context,
                )
                result_path = Path(kwargs["env"]["PLC_AGENT_RESULT_PATH"])
                result_path.write_text(
                    json.dumps(
                        {
                            "success": True,
                            "exception": None,
                            "replaced_pou": "MotorControl",
                            "project_path": kwargs["env"]["PLC_AGENT_PROJECT_PATH"],
                            "messages": [],
                        }
                    ),
                    encoding="utf-8",
                )
                return __import__("subprocess").CompletedProcess(command, 0, "", "")

            with patch("plc_agent.codesys_runner.subprocess.run", side_effect=fake_run):
                result = compile_project(
                    template_project=files[1],
                    declaration_path=files[3],
                    implementation_path=files[4],
                    output_dir=root / "run",
                    codesys_exe=files[0],
                    script_path=files[2],
                    pou_name="MotorControl",
                    pou_type="FUNCTION_BLOCK",
                    compile_context=compile_context,
                )

            self.assertTrue(result.success)
            self.assertTrue((root / "run" / "compile_context.json").is_file())

    def test_existing_output_directory_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "tests") as temporary_directory:
            root = Path(temporary_directory)
            existing_output = root / "existing"
            existing_output.mkdir()
            files = []
            for name in (
                "codesys_stub.txt",
                "template.project",
                "compile_project.py",
                "declaration.st",
                "implementation.st",
            ):
                path = root / name
                path.write_text("fixture", encoding="utf-8")
                files.append(path)

            with self.assertRaises(FileExistsError):
                compile_project(
                    template_project=files[1],
                    declaration_path=files[3],
                    implementation_path=files[4],
                    output_dir=existing_output,
                    codesys_exe=files[0],
                    script_path=files[2],
                )

    def test_execute_tests_passes_request_and_reads_result(self):
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "tests") as temporary_directory:
            root = Path(temporary_directory)
            files = {}
            for name in (
                "codesys_stub.txt",
                "template.project",
                "execute_tests.py",
                "declaration.st",
                "implementation.st",
            ):
                path = root / name
                path.write_text("fixture", encoding="utf-8")
                files[name] = path

            task = {
                "id": "fixture",
                "pou_name": "MotorControl",
                "pou_type": "FUNCTION_BLOCK",
                "interface": [],
                "custom_types": [],
            }
            tests = {
                "task_id": "fixture",
                "tests": [
                    {"id": "tc01", "initial_state": {}, "steps": []}
                ],
            }

            def fake_run(command, **kwargs):
                request_path = Path(kwargs["env"]["PLC_AGENT_TEST_REQUEST_PATH"])
                request = json.loads(request_path.read_text(encoding="utf-8"))
                self.assertEqual(request["task"]["id"], "fixture")
                self.assertEqual(request["settle_ms"], 25)
                result_path = Path(kwargs["env"]["PLC_AGENT_RESULT_PATH"])
                result_path.write_text(
                    json.dumps(
                        {
                            "success": True,
                            "compile_success": True,
                            "test_passed": 1,
                            "test_total": 1,
                            "exception": None,
                        }
                    ),
                    encoding="utf-8",
                )
                return __import__("subprocess").CompletedProcess(command, 0, "", "")

            with patch("plc_agent.codesys_runner.subprocess.run", side_effect=fake_run):
                result = execute_tests(
                    template_project=files["template.project"],
                    declaration_path=files["declaration.st"],
                    implementation_path=files["implementation.st"],
                    task=task,
                    tests=tests,
                    output_dir=root / "run",
                    codesys_exe=files["codesys_stub.txt"],
                    script_path=files["execute_tests.py"],
                    settle_ms=25,
                )

            self.assertTrue(result.success)
            self.assertTrue(result.compile_success)
            self.assertEqual(result.test_passed, 1)
            self.assertEqual(result.test_total, 1)
            self.assertTrue((root / "run" / "test_request.json").is_file())


if __name__ == "__main__":
    unittest.main()
