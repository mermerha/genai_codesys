import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plc_agent.codesys_runner import compile_project


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


if __name__ == "__main__":
    unittest.main()
