import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plc_agent.agent import run_compile_loop
from plc_agent.codesys_runner import CompileMessage, CompileResult
from plc_agent.model_client import ChatCompletion


class AgentLoopTests(unittest.TestCase):
    def test_repairs_after_compile_error_and_preserves_artifacts(self):
        model_outputs = [
            {
                "pou_name": "MotorControl",
                "pou_type": "FUNCTION_BLOCK",
                "declaration": "FUNCTION_BLOCK MotorControl",
                "implementation": "Motor := MissingSignal;",
            },
            {
                "pou_name": "MotorControl",
                "pou_type": "FUNCTION_BLOCK",
                "declaration": "FUNCTION_BLOCK MotorControl",
                "implementation": "Motor := FALSE;",
            },
        ]

        def fake_chat(**kwargs):
            payload = model_outputs.pop(0)
            content = json.dumps(payload)
            return ChatCompletion(
                content=content,
                model=kwargs["model"],
                usage={},
                raw_response={"choices": [{"message": {"content": content}}]},
            )

        compile_calls = []

        def fake_compile(**kwargs):
            compile_calls.append(kwargs)
            result_path = Path(kwargs["output_dir"]) / "compile_result.json"
            result_path.parent.mkdir()
            if len(compile_calls) == 1:
                messages = (
                    CompileMessage(
                        category="compile",
                        severity="error",
                        number="100",
                        text="unknown identifier",
                        object_name="MotorControl",
                        position="line 1",
                    ),
                )
                success = False
                returncode = 2
            else:
                messages = ()
                success = True
                returncode = 0
            return CompileResult(
                success=success,
                messages=messages,
                exception=None,
                replaced_pou="MotorControl",
                project_path=Path("candidate.project"),
                result_path=result_path,
                process_returncode=returncode,
            )

        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT / "tests") as temporary_directory:
            run_dir = Path(temporary_directory) / "run"
            result = run_compile_loop(
                task={"id": "fixture", "pou_type": "FUNCTION_BLOCK"},
                model="test-model",
                template_project="template.project",
                output_dir=run_dir,
                chat_function=fake_chat,
                compile_function=fake_compile,
            )

            self.assertEqual(result["final_status"], "compile_success")
            self.assertEqual(result["repairs"], 1)
            self.assertEqual(result["api_models"], ["test-model", "test-model"])
            self.assertTrue((run_dir / "attempt_00" / "model_response.json").is_file())
            self.assertTrue((run_dir / "attempt_01" / "candidate.json").is_file())
            repair_prompt = (run_dir / "attempt_01" / "prompt.txt").read_text(
                encoding="utf-8"
            )
            self.assertIn("unknown identifier", repair_prompt)


if __name__ == "__main__":
    unittest.main()
